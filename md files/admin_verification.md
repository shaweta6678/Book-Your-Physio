# Physiotherapist Admin Verification — Design

Status: **Draft for review** · Branch: `physio/admin_verification` · 28 Sep 2026

This covers what happens after a physiotherapist registers: their account starts as `PENDING`, the admins get a notification, and an admin reviews the profile and approves or rejects it and if it rejects then add the reason for rejection as well. Until they are approved, the physiotherapist can log in and manage their own profile, but they cannot reach patient data, appointments or booking.

Decisions already made:

- A new `notifications` Django app handles notifications.
- A new `administration` Django app owns admin workflows, starting with physiotherapist review. It can't be named `admin`, because that label is taken by `django.contrib.admin`. Its URLs live under `/api/admin/`, which is separate from Django's own `/admin/` site.
- The approved status stays `VERIFIED`, matching the existing enum and `project_scope.md`. The endpoint is still called `/approve/`.

---

## 1. Flow

```text
POST /accounts/register/  (role = PHYSIOTHERAPIST)
        │
        ▼
UserRegistrationView ── transaction.atomic() ─────────────────────────┐
        │  UserDal.create_user(...)                                    │
        │  PhysiotherapistDal.create_physiotherapist(...)              │
        │        verification_status = PENDING   (model default)       │
        │  AdminNotificationService.physiotherapist_registered(physio) │
        │        └─ NotificationService.notify(admins, ...)            │
        │              └─ DatabaseChannel → Notification rows          │
        └──────────────────────────────────────────────────────────────┘
        │
        ▼
Admin: GET /api/notifications/              🔔 "New Physiotherapist Registration"
Admin: GET /api/admin/physiotherapists/<id>/     review the profile
        │
   ┌────┴─────────────────────┐
   ▼                          ▼
POST .../<id>/approve/     POST .../<id>/reject/   {"reason": "..."}
   │                          │
VERIFIED                   REJECTED
verified_by / verified_at  verified_by / verified_at / rejection_reason
   │                          │
   └── physio gets a notification with the decision ──┘
```

**Why the notification is created inside the registration transaction:** the DB channel only writes rows, so registration and notification succeed or fail together. You never get a physio with no admin notification, and you never get a notification for a physio whose registration rolled back. Any later channel that makes outside calls (email, SMS) should wrap its send in `transaction.on_commit()`, so a slow or failing email server can't roll back or block a registration.

**Why not a `post_save` signal:** signals would also decouple registration from notifications, but they are implicit. They fire from fixtures, from the admin site and from tests, and a reader of the view can't see that they happen. An explicit service call keeps things just as decoupled, because the view only knows `AdminNotificationService`, and it is easy to find.

---

## 2. Data model

### 2.1 `accounts.Physiotherapist`: three new fields (migration `0003`)

| Field | Type | Purpose |
|---|---|---|
| `verified_by` | `FK(User, null=True, blank=True, on_delete=SET_NULL, related_name="verified_physiotherapists")` | Admin who made the decision |
| `verified_at` | `DateTimeField(null=True, blank=True)` | When the decision was made |
| `rejection_reason` | `TextField(blank=True)` | Required on reject, cleared on approve |

`verification_status` stays as it is (`PENDING` / `VERIFIED` / `REJECTED`, default `PENDING`). This is a change to `accounts/models.py` plus a new migration. Both are guarded in CLAUDE.md, so **approving this doc approves that change.**

### 2.2 `notifications.Notification` (new app, migration `0001`)

| Field | Type | Notes |
|---|---|---|
| `recipient` | `FK(User, on_delete=CASCADE, related_name="notifications")` | One row per recipient |
| `notification_type` | `CharField(max_length=50, choices=NotificationType)` | Enum, see below |
| `title` | `CharField(max_length=200)` | "New Physiotherapist Registration" |
| `message` | `TextField(blank=True)` | Human-readable body |
| `data` | `JSONField(default=dict, blank=True)` | Snapshot for the dashboard card, e.g. `physiotherapist_id`, name, license, experience |
| `is_read` | `BooleanField(default=False)` | |
| `read_at` | `DateTimeField(null=True, blank=True)` | |
| `created_at` | `DateTimeField(auto_now_add=True)` | |

Index: `(recipient, is_read, -created_at)` for the unread list and unread count. Default ordering is `-created_at`.

```python
# notifications/enums.py
class NotificationType(Enum):
    PHYSIOTHERAPIST_REGISTERED = "PHYSIOTHERAPIST_REGISTERED"
    PHYSIOTHERAPIST_VERIFIED = "PHYSIOTHERAPIST_VERIFIED"
    PHYSIOTHERAPIST_REJECTED = "PHYSIOTHERAPIST_REJECTED"
```

**Design choices:**

- **One row per admin (fan-out), rather than one shared row per role.** This keeps read/unread tracking per admin with no extra join table. The cost is that an admin added *later* won't see old notifications. That's fine, because the **pending list endpoint, not the notification feed, is the source of truth for the review queue.** For the same reason, physios who registered before this feature ships need no backfill: they appear in the pending list anyway.
- **`data` is a snapshot, and the status in it goes stale.** The dashboard card should use `data.physiotherapist_id` for its View, Approve and Reject buttons, and read the live status from the admin detail endpoint. When a physio is approved or rejected, the service marks that physio's open `PHYSIOTHERAPIST_REGISTERED` notifications as read for **all** admins, so the other admins don't act on a card that has already been decided.
- **A generic `data` field instead of an FK to `Physiotherapist`.** The `notifications` app then never imports `physiotherapists`, `administration` or `accounts.Physiotherapist`, so dependencies only point into it (accounts / administration → notifications).

### 2.3 Who counts as an admin

`UserRole.ADMIN` already exists, and registration already refuses it. **Gotcha:** `createsuperuser` makes users with `role = PATIENT` (the model default). The admin check is therefore:

```python
user.is_authenticated and (user.role == UserRole.ADMIN.value or user.is_superuser)
```

The same rule selects the notification recipients (`is_active=True` as well).

---

## 3. Module layout

```text
accounts/
    models.py              + verified_by, verified_at, rejection_reason
    migrations/0003_...    new
    dal/account_dal.py     + UserDal.list_admins()
                           + PhysiotherapistDal.get_by_id(id)
                           + PhysiotherapistDal.get_by_id_for_update(id)   select_for_update
                           + PhysiotherapistDal.list_by_status(status)     select_related("user")
    views.py               + one call in UserRegistrationView (inside the existing atomic block)

administration/            new app, no models of its own yet (so no migrations)
    apps.py
    permissions.py         IsPlatformAdmin
    services.py            PhysiotherapistVerificationService
    validators.py          validate_rejection(data), validate_status_filter(value)
    views.py               AdminPhysiotherapistListView, AdminPhysiotherapistDetailView,
                           ApprovePhysiotherapistView, RejectPhysiotherapistView
    urls.py                physiotherapists/ routes
    tests.py               verification tests

notifications/             new app
    apps.py, models.py, enums.py
    dal/notification_dal.py    NotificationDal: create_many, list_for_user, unread_count,
                               mark_read, mark_read_by_type_and_data
    channels.py            NotificationChannel (base), DatabaseChannel
    services.py            NotificationService, AdminNotificationService
    views.py, urls.py, tests.py
    migrations/0001_initial.py

physiotherapists/
    permissions.py         + IsVerifiedPhysiotherapist
    services.py            to_dict gains rejection_reason (for /me/)
    tests.py               + access-gate tests

book_your_physio/
    settings.py            INSTALLED_APPS += "notifications", "administration"   (approved)
    urls.py                + path("api/notifications/", include("notifications.urls"))
                           + path("api/admin/", include("administration.urls"))
```

**Dependency direction:** `administration` → `accounts` (DAL), `physiotherapists` (reuses `PhysiotherapistProfileService.to_dict`), `notifications`. Nothing imports `administration`. The physiotherapists app stays focused on what a physio does for themselves, and every admin-only action goes in one place, guarded by `IsPlatformAdmin`.

---

## 4. Notification service (Strategy + Facade)

```python
# notifications/channels.py
class NotificationChannel:
    """Strategy: one way of delivering a notification."""
    def send(self, recipients, notification_type, title, message, data):
        raise NotImplementedError


class DatabaseChannel(NotificationChannel):
    def send(self, recipients, notification_type, title, message, data):
        NotificationDal.create_many(recipients, notification_type, title, message, data)

# later: EmailChannel, SmsChannel. Each wraps its send in transaction.on_commit()


# notifications/services.py
class NotificationService:
    def __init__(self, channels=None):
        self.channels = channels or [DatabaseChannel()]

    def notify(self, recipients, notification_type, title, message="", data=None):
        for channel in self.channels:
            channel.send(recipients, notification_type.value, title, message, data or {})


class AdminNotificationService:
    """Facade: knows *what* to tell admins, not *how* it is delivered."""
    def __init__(self, notification_service=None):
        self.notification_service = notification_service or NotificationService()

    def physiotherapist_registered(self, physiotherapist): ...
    def physiotherapist_verified(self, physiotherapist): ...    # tells the physio
    def physiotherapist_rejected(self, physiotherapist): ...    # tells the physio, with the reason
    def resolve_registration(self, physiotherapist): ...        # marks admin cards read
```

These services are instance-based, unlike the existing `@staticmethod` services, because they take their channels by injection. Adding email later means `NotificationService(channels=[DatabaseChannel(), EmailChannel()])`, with no change to registration or verification code. Tests can pass in a fake channel.

`physiotherapist_registered` builds the dashboard card data:

```json
{
  "physiotherapist_id": 12,
  "name": "Dr. Priya Sharma",
  "license_number": "PHY12345",
  "experience_years": 5,
  "registered_at": "2026-09-28T10:15:00Z"
}
```

---

## 5. Verification service

```python
# administration/services.py
class PhysiotherapistVerificationService:
    list_physiotherapists(status)          # default PENDING
    get_physiotherapist(physio_id)         # 404 if missing
    approve(admin_user, physio_id)
    reject(admin_user, physio_id, data)    # data validated by validate_rejection
```

**State transitions.** Only these are allowed:

```text
PENDING ──approve──▶ VERIFIED
PENDING ──reject───▶ REJECTED
```

Any other transition returns **409 Conflict**: `{"error": "Physiotherapist is already VERIFIED."}`.

`approve` and `reject` each run inside `transaction.atomic()`:

1. `PhysiotherapistDal.get_by_id_for_update(id)` takes a row lock, so two admins clicking at the same moment can't both succeed. The second one gets a 409.
2. Check that the status is `PENDING`.
3. Update `verification_status`, `verified_by`, `verified_at = timezone.now()`, and `rejection_reason` (set on reject, `""` on approve).
4. `AdminNotificationService.resolve_registration(physio)` and `physiotherapist_verified/rejected(physio)`.

`to_dict` for the admin view extends `PhysiotherapistProfileService.to_dict` with `verified_by` (id and name), `verified_at`, `rejection_reason` and the user's `date_joined`. The physio's own `/me/` response also gets `rejection_reason`, so a rejected physio can see why.

---

## 6. API

All responses follow the existing conventions: errors are `{"error": "..."}`, and successes carry a `message` plus the object.

### 6.1 Admin review (`IsPlatformAdmin`)

| Method | Path | Body | Success | Errors |
|---|---|---|---|---|
| GET | `/api/admin/physiotherapists/?status=PENDING` | none | `200 {"physiotherapists": [...]}` | 400 bad status |
| GET | `/api/admin/physiotherapists/<id>/` | none | `200 {profile}` | 404 |
| POST | `/api/admin/physiotherapists/<id>/approve/` | `{}` | `200 {"message": "Physiotherapist approved.", "profile": {...}}` | 404, 409 |
| POST | `/api/admin/physiotherapists/<id>/reject/` | `{"reason": "License could not be verified."}` | `200 {"message": "Physiotherapist rejected.", "profile": {...}}` | 400 missing/blank reason, 404, 409 |

`status` accepts `PENDING`, `VERIFIED` or `REJECTED`, and defaults to `PENDING`. There is no pagination for now. Add it when the list gets long.

### 6.2 Notifications (`IsAuthenticated`, and a user only ever sees their own)

| Method | Path | Success |
|---|---|---|
| GET | `/api/notifications/?is_read=false` | `200 {"notifications": [...]}` |
| GET | `/api/notifications/unread-count/` | `200 {"unread_count": 3}` |
| POST | `/api/notifications/<id>/read/` | `200 {"message": "Notification marked as read."}` |

A notification that belongs to another user returns **404, not 403**, so the API doesn't reveal which ids exist.

Shape of one notification:

```json
{
  "id": 41,
  "notification_type": "PHYSIOTHERAPIST_REGISTERED",
  "title": "New Physiotherapist Registration",
  "message": "Dr. Priya Sharma registered and is awaiting review.",
  "data": { "physiotherapist_id": 12, "name": "Dr. Priya Sharma", "license_number": "PHY12345", "experience_years": 5, "registered_at": "2026-09-28T10:15:00Z" },
  "is_read": false,
  "created_at": "2026-09-28T10:15:00Z"
}
```

---

## 7. Access rules for unverified physiotherapists

| Capability | PENDING | REJECTED | VERIFIED |
|---|---|---|---|
| Log in | ✅ | ✅ (so they can see the reason) | ✅ |
| `GET /me/` | ✅ | ✅ | ✅ |
| `PATCH /me/` | ✅ | ✅ (see open question 2) | ✅ |
| Own notifications | ✅ | ✅ | ✅ |
| Patient data, appointments, availability | ❌ 403 | ❌ 403 | ✅ |
| Visible in patient search | ❌ | ❌ | ✅ |

This is enforced with a new permission, applied to every future physio endpoint except `/me/`:

```python
class IsVerifiedPhysiotherapist(IsPhysiotherapist):
    message = "Your profile is awaiting admin verification."
    # IsPhysiotherapist check, plus profile.verification_status == VERIFIED
```

Search, availability and booking don't exist yet, so right now this permission only guards something once those modules are built. They must use it, and search must filter on `VERIFIED`. **Login itself doesn't change.**

---

## 8. SOLID and patterns

| Principle / pattern | Where |
|---|---|
| **SRP** | Registration creates accounts. `AdminNotificationService` decides what admins are told. Channels deliver. `VerificationService` owns the status transitions. The DAL owns the ORM. |
| **OCP** | New delivery channels (email, SMS, push) are added as new `NotificationChannel` subclasses, without editing registration or verification. |
| **LSP** | Every channel follows the same `send()` contract. `IsVerifiedPhysiotherapist` narrows `IsPhysiotherapist` without changing its meaning. |
| **ISP** | Views only see a small facade (`physiotherapist_registered`, `approve`, `reject`), not the notification plumbing. |
| **DIP** | Services receive their channels and collaborators through the constructor, with defaults, and tests inject fakes. `notifications` doesn't depend on `physiotherapists`. |
| **Strategy** | `NotificationChannel` |
| **Facade** | `AdminNotificationService` |
| **State (lightweight)** | The allowed-transition check in `VerificationService` |

---

## 9. Tests (`APITestCase`)

**Registration → notification**
- Physio registration creates one `PHYSIOTHERAPIST_REGISTERED` notification per active admin (role ADMIN and superuser), with the correct `data`.
- Patient registration creates no notification.
- With no admins, registration still succeeds and creates no rows.
- If the notification write fails, the user and profile are rolled back.

**Admin endpoints** (`administration/tests.py`)
- 401 when not logged in. 403 for a patient and for a physio.
- The list defaults to PENDING, filters by status, and returns 400 on an invalid status.
- Approve: PENDING → VERIFIED, sets `verified_by` and `verified_at`, marks the admin cards read, and notifies the physio.
- Reject: requires a non-blank reason (400 otherwise), stores the reason, and notifies the physio with it.
- Approving or rejecting a non-PENDING physio returns 409. An unknown id returns 404.

**Notifications**
- A user only sees their own. Another user's id returns 404 on `/read/`.
- `unread-count` and `?is_read=false` stay consistent after mark-read.

**Access**
- `IsVerifiedPhysiotherapist` lets VERIFIED through and returns 403 for PENDING and REJECTED. This is tested against a small test-only view until a real endpoint exists.
- A physio can't change `verification_status` through `PATCH /me/`. This test already exists and stays.

---

## 10. Out of scope for this branch

- Extracting a `RegistrationService` out of `UserRegistrationView`. It's worth doing (the view also repeats validation that `validate_registration_data` already does), but it's a separate refactor. This branch only adds one call inside the existing atomic block.
- Email, SMS and push channels.
- Django-admin (`/admin/`) actions for approve/reject. These could call the same service later.
- Pagination.
- The later `administration` features in section 12.

---

## 12. What the `administration` app owns later

This branch only builds physiotherapist review, but the app is laid out so these can be added as new service, view and URL modules without reshaping it:

| Feature | Rough design | Things to decide first |
|---|---|---|
| **Suspend / reinstate physiotherapist** | Add `SUSPENDED` to `VerificationStatus`. Transitions: `VERIFIED → SUSPENDED` (reason required), `SUSPENDED → VERIFIED`. `IsVerifiedPhysiotherapist` already blocks anyone who isn't `VERIFIED`, so a suspension takes effect right away. | What happens to their upcoming appointments |
| **Activate / deactivate users** | Toggle `User.is_active`. simplejwt's `JWTAuthentication` refuses inactive users, so their existing access tokens stop working on the next request. Outstanding refresh tokens should also be blacklisted. | Whether an admin can deactivate another admin, and never themselves |
| **Admin dashboard** | `GET /api/admin/dashboard/`: counts by verification status, new registrations this week, and unread admin notifications. | Which numbers the dashboard should show |
| **Manage patients, complaints, reports** | New modules inside `administration/`, reusing `IsPlatformAdmin`. Complaints will need their own model, and that will be this app's first migration. | Complaint model design |

A shared `AdminActionLog` model (actor, action, target, reason, timestamp) will be worth adding once there is more than one kind of admin action. Until then, `verified_by`, `verified_at` and `rejection_reason` on `Physiotherapist` cover the audit trail for review.

---

## 11. Open questions

1. **Re-review after rejection.** Should a REJECTED physio be able to fix their profile and go back to `PENDING` (for example with a `POST /me/resubmit/` that notifies admins again), or is rejection final for now? *Suggestion: final for this branch, with resubmission as a follow-up.*
2. **Profile edits by REJECTED physios.** Should `PATCH /me/` stay open for them? It only matters if resubmission exists. *Suggestion: leave it open.*
3. **Suspension in this branch?** Revoking a VERIFIED physio (for example when a license lapses) is handled by *suspend* in section 12, not by moving them to REJECTED. Should suspend ship in this branch or the next one? *Suggestion: next branch, because it needs a decision on what happens to appointments, and appointments don't exist yet.*
4. **Should the edits a PENDING physio makes after registering notify admins again?** *Suggestion: no, because admins read the live profile at review time.*
