# Book Your Physio

A backend API for booking physiotherapy appointments. Patients will be able to find physiotherapists and book sessions; physiotherapists will manage their profile and availability; admins will verify physiotherapists and run the platform.

> **Status: early development.** Only user accounts (register, login, logout) exist so far. Booking, availability, search and reviews are planned but not built yet. See [Known issues](#known-issues) before relying on the current endpoints.

## Tech stack

| Part | Choice |
|---|---|
| Language | Python 3.9 |
| Framework | Django 4.2 |
| API | Django REST Framework 3.16 |
| Auth | JWT via `djangorestframework-simplejwt` 5.5 |
| Database | PostgreSQL (`psycopg2-binary`) |
| Config | `.env` file loaded with `python-dotenv` |

## Project layout

```text
Book-Your-Physio/
├── manage.py
├── book_your_physio/        # Django project: settings, root urls, wsgi/asgi
│   ├── settings.py
│   └── urls.py              # /admin/ and /accounts/
├── accounts/                # The only app so far
│   ├── models.py            # User, Patient, Physiotherapist
│   ├── enums.py             # UserRole, VerificationStatus
│   ├── validators.py        # Registration input validation
│   ├── views.py             # Register / login / logout API views
│   ├── urls.py
│   ├── dal/account_dal.py   # Data access layer (all ORM calls go here)
│   └── migrations/
└── md files/                # Design notes
    ├── users.md             # Users module design and roadmap
    └── claude.md            # Guidance for AI coding assistants
```

## Getting started

### 1. Prerequisites

- Python 3.9 or newer
- A running PostgreSQL server and an empty database for the project

### 2. Create a virtual environment and install packages

There is no `requirements.txt` yet, so install the packages directly:

```bash
python3 -m venv venv
source venv/bin/activate
pip install "Django>=4.2,<5.0" djangorestframework djangorestframework-simplejwt psycopg2-binary python-dotenv
```

### 3. Configure the database

Create a `.env` file at `book_your_physio/.env`, next to `settings.py`. That is where `load_dotenv()` looks first, and it is the only location the existing `.gitignore` covers, so a `.env` in the repository root would **not** be ignored.

```dotenv
DB_NAME=book_your_physio
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

### 4. Migrate and run

```bash
python manage.py migrate
python manage.py createsuperuser   # optional, for /admin/
python manage.py runserver
```

The API is then available at `http://127.0.0.1:8000/`.

## Data model

All models live in `accounts/models.py`.

- **User**: a custom user (`AUTH_USER_MODEL = "accounts.User"`) extending Django's `AbstractUser`. Adds a unique `email`, `phone_number`, `role` and timestamps. On registration the `username` is set to the email.
- **Patient**: one-to-one profile for users with role `PATIENT` (date of birth, gender, address, emergency contact). Created empty at registration.
- **Physiotherapist**: one-to-one profile for users with role `PHYSIOTHERAPIST` (`license_number` (unique), `bio`, `experience_years`, `consultation_fee`, `verification_status`). New profiles start as `PENDING`.

Roles (`accounts/enums.py`): `PATIENT`, `PHYSIOTHERAPIST`, `ADMIN`. Only `PATIENT` and `PHYSIOTHERAPIST` can be chosen at registration.

## API endpoints

All endpoints accept and return JSON. Errors come back as `{"error": "<message>"}`.

### `POST /accounts/register/`

Creates a user and the matching profile in one transaction.

Required for everyone: `first_name`, `last_name`, `email`, `password`, `role`. Optional: `phone_number`.

Additionally required when `role` is `PHYSIOTHERAPIST`: `license_number`, `experience_years`, `consultation_fee`. Optional: `bio`.

```json
{
  "first_name": "Asha",
  "last_name": "Rao",
  "email": "asha@example.com",
  "password": "StrongPassword123",
  "phone_number": "9876543210",
  "role": "PHYSIOTHERAPIST",
  "license_number": "PT-12345",
  "experience_years": 5,
  "consultation_fee": 800
}
```

Returns `201` with `message` and a `user` object (`id`, `first_name`, `last_name`, `email`, `phone_number`, `role`).

### `POST /accounts/login/`

```json
{ "email": "asha@example.com", "password": "StrongPassword123" }
```

Intended to return `200` with `access` and `refresh` JWTs plus the `user` object. Returns `404` if no account has that email. **Currently always returns `401`; see Known issues.**

### `POST /accounts/logout/`

```json
{ "refresh": "<refresh_token>" }
```

Intended to blacklist the refresh token. **Currently fails; see Known issues.**

### `/admin/`

The Django admin site. No models are registered in it yet.

## Known issues

These were found by reading and running the current code (checked 2026-09-28). They are listed here so nobody is surprised; they have not been fixed.

1. **Login always fails with 401.** `UserLoginView` calls `authenticate(request, email=..., password=...)`, but the default auth backend looks users up by `username`, so the `email` argument is ignored.
2. **Registering without `phone_number` returns a 500 error.** The view passes `None` for a missing phone number, but the database column does not allow nulls.
3. **A physiotherapist with 0 years of experience cannot register.** `0` is treated as "missing" by the required-field check.
4. **Logout never succeeds.** Token blacklisting needs `rest_framework_simplejwt.token_blacklist` in `INSTALLED_APPS`, which is not installed, so every logout returns `400`.
5. **No permission classes on endpoints**, and no authenticated endpoints exist yet (no `/me/`).
6. **Development-only settings.** `SECRET_KEY` is hard-coded in `settings.py`, `DEBUG = True` and `ALLOWED_HOSTS` is empty. Do not deploy as is.
7. **Repository housekeeping.** There is no `requirements.txt`, the `.gitignore` only lives inside `book_your_physio/`, and a macOS `venv/` and `.DS_Store` files are committed.
8. **No tests.** `accounts/tests.py` is empty and there is no CI.

## Roadmap

The design for the users module, including `/me/`, role-based permissions and future features, is in [`md files/users.md`](md%20files/users.md). Note that it describes planned paths under `/api/users/` and a role called `PHYSIO`; the code currently uses `/accounts/` and `PHYSIOTHERAPIST`.

Planned beyond users:

- Physiotherapist search and public profiles
- Availability slots
- Appointment booking, cancellation and history
- Admin verification of physiotherapists
- Reviews
