# CLAUDE.md

Guidance for Claude and other AI coding assistants working in this repository.

## 1. Project Overview / Context

**Book Your Physio** is a backend API for booking physiotherapy appointments.

- **Patients** find physiotherapists and book sessions.
- **Physiotherapists** manage their profile, fees and availability.
- **Admins** verify physiotherapists and run the platform.

It is in early development. Only the `accounts` app exists: a custom `User`, `Patient` and `Physiotherapist` profiles, and register / login / logout endpoints. Search, availability, booking and reviews are planned but not built.

**Tech stack**

| Part | Choice |
|---|---|
| Language | Python 3.9 |
| Framework | Django 4.2 |
| API | Django REST Framework 3.16 (`APIView`, no serializers) |
| Auth | JWT via `djangorestframework-simplejwt` 5.5 |
| Database | PostgreSQL via `psycopg2-binary` |
| Config | `book_your_physio/.env` loaded with `python-dotenv` |

Further reading: `md files/project_scope.md` (master project scope, roadmap and build order; the physiotherapist module is next), `README.md` (setup, endpoints, known issues), `md files/accounts.md` (accounts module design), `md files/users.md` (original users plan).

## 2. Exact Build, Test, and Run Commands

```bash
# One-time setup (there is no requirements.txt yet)
python3 -m venv venv
source venv/bin/activate
pip install "Django>=4.2,<5.0" djangorestframework djangorestframework-simplejwt psycopg2-binary python-dotenv

# Database config: create book_your_physio/.env with
# DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT

# Run
python manage.py migrate
python manage.py runserver          # http://127.0.0.1:8000/

# Check and test
python manage.py check
python manage.py makemigrations --check --dry-run   # confirms models and migrations agree
python manage.py test accounts
```

There is no linter, formatter, CI or test suite configured yet. `accounts/tests.py` is empty. New tests should use DRF's `APITestCase`.

## 3. Code Style & Guardrails

- **Python 3.9 compatible.** No `match` statements, no `X | Y` unions at runtime.
- **No DRF serializers.** Input is validated by plain functions in `validators.py` that raise `rest_framework.exceptions.ValidationError` and return a cleaned dict.
- **Views are `APIView` classes** with explicit `post` / `get` methods.
- **All ORM access goes through the DAL** in `accounts/dal/account_dal.py`: `@staticmethod`s on `UserDal`, `PatientDal`, `PhysiotherapistDal`. Views do not call `Model.objects` directly. DAL getters return `None` instead of raising `DoesNotExist`.
- **Choices are Python `Enum`s** in `enums.py` (`UserRole`, `VerificationStatus`), not Django `TextChoices`. Always compare with `.value`, e.g. `UserRole.PATIENT.value`. Never hard-code role strings.
- **Error responses** are `{"error": "<message>"}`. **Success responses** carry a `message` and, where relevant, a `user` object (`id`, `first_name`, `last_name`, `email`, `phone_number`, `role`).
- **Multi-model writes** (user plus profile) go inside `transaction.atomic()`.
- **Passwords** are set only through `create_user()` or `set_password()`.
- **Emails** are normalised with `.lower().strip()` before lookup or save.
- Get the user model with `get_user_model()` or from `accounts.models`, never `django.contrib.auth.models.User`.
- Keep changes small and scoped to the request.

### SOLID and design patterns (without over-engineering)

Follow SOLID and use design patterns when building a new module, but only where they solve a problem that exists today. The simplest design that keeps each layer to one job wins.

**Layers of a new module.** Mirror `accounts/`:

| File | One job |
|---|---|
| `models.py` | Data structure only; no business logic |
| `enums.py` | Choices and domain constants |
| `validators.py` | Check and normalise input, return a cleaned dict |
| `services.py` | Business logic, multi-step workflows, `transaction.atomic()` (add only when the view would otherwise hold that logic) |
| `dal/<module>_dal.py` | All ORM queries |
| `permissions.py` | Role and ownership checks (`IsPatient`, `IsPhysiotherapist`, `IsVerifiedPhysiotherapist`) |
| `views.py` | Thin: read the request, call validator, service or DAL, return the response |

**SOLID in practice**

- **Single responsibility:** a view does not validate fields or run queries; a validator does not save; a DAL method does not decide business rules.
- **Open/closed:** add a new rule or a new role by adding a validator function, a permission class or an enum value, not by growing an `if/elif` chain in a view.
- **Liskov substitution:** subclasses (permission classes, strategies) keep the parent's inputs, outputs and error behaviour.
- **Interface segregation:** keep DAL and service classes per model or workflow (`PatientDal`, `BookingService`), not one class that does everything.
- **Dependency inversion:** services call the DAL, never `Model.objects`, so logic can be tested without HTTP.

**Patterns this project uses, and when**

- **Service layer:** when a workflow touches more than one model or needs a transaction (booking, verification, payment).
- **Data access layer (repository):** always, for ORM access, as in `accounts/dal/`.
- **Strategy:** only when there are two real implementations now (for example Haversine and PostGIS distance). One implementation means a plain function.
- **Factory:** only when choosing among several providers at runtime (email, SMS, push).
- **Observer / events:** only once a second side effect needs to react to the same event. Until then, call the function directly.

**Do not over-engineer**

- No abstract base classes, interfaces or factories with a single implementation.
- No generic "base service" or "base DAL" until three modules repeat the same code.
- No Redis, Celery, Kafka or PostGIS until the scope doc's phase for them is reached.
- Prefer a plain function over a class that has one method and no state.
- If a pattern is added, say in one line in the PR why it is needed now.

## 4. The "Weird" Codebase Quirks

- **Email login on a username model.** `User` still has Django's `username` field as `USERNAME_FIELD`. Registration copies the email into `username`. The login view calls `authenticate(email=...)`, which the default backend ignores, so login currently always returns 401.
- **Docs describe the target, not the code.** `md files/project_scope.md` marks accounts as complete (including refresh-token blacklisting), and `md files/accounts.md` describes `USERNAME_FIELD = "email"`, `/api/accounts/...` paths, a `/me/` endpoint, default `IsAuthenticated` permissions and token blacklisting. On `main` the paths are `/accounts/...`, there is no `/me/`, no permission classes are set, and `token_blacklist` is not installed (so logout always fails). `users.md` also uses the role name `PHYSIO`, while the code uses `PHYSIOTHERAPIST`. When docs and code disagree, the code is what runs.
- **Validation is duplicated.** `UserRegistrationView` repeats most physiotherapist checks that `validate_registration_data()` already performs. Both treat `experience_years = 0` as missing.
- **`phone_number` can reach the database as `None`**, which fails on the non-null column and returns a 500.
- **The `.gitignore` lives in `book_your_physio/`** and only ignores `book_your_physio/.env`. A `.env` in the repo root would be committed.
- **A macOS `venv/` and `.DS_Store` files are committed.** Ignore them; never edit or add to them.

## 5. Safety Boundaries

Ask before touching any of these:

- `book_your_physio/settings.py`, especially `AUTH_USER_MODEL`, `INSTALLED_APPS`, `DATABASES` and `REST_FRAMEWORK`.
- `accounts/models.py` field changes, and anything under `accounts/migrations/`. Never edit `0001_initial.py`; model changes need a new migration. Changing `USERNAME_FIELD` or removing `username` needs a migration plan agreed first.
- Authentication and token logic in `accounts/views.py` (login, logout, JWT settings).
- `.env` files and secrets. Never commit them, print them, or hard-code credentials.
- `venv/`: do not modify, regenerate or delete it.
- Git history and branches: do not force-push, rewrite history, or push to `main` directly.
- Adding new dependencies or new Django apps.
