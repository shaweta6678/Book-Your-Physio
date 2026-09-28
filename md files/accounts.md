# Book Your Physio
## Accounts Module Documentation

### 1. Module Overview

The `accounts` module is responsible for user identity, registration, authentication, and role-specific profiles.

The module currently supports:

- User registration
- Patient profile creation
- Physiotherapist profile creation
- Email-based authentication
- JWT login
- JWT logout using refresh-token blacklisting
- Role validation
- Physiotherapist-specific registration validation
- Physiotherapist verification status
- Atomic creation of users and profiles

### 2. Module Structure

```text
accounts/
│
├── models.py
├── enums.py
├── validators.py
├── views.py
├── urls.py
└── ...
```

Responsibilities:

| File | Responsibility |
|---|---|
| `models.py` | Database models |
| `enums.py` | User and verification enums |
| `validators.py` | Registration input validation |
| `views.py` | API request/response handling and application flow |
| `urls.py` | Accounts API routing |

The module intentionally does **not** use DRF serializers at this stage. Validation is handled through a dedicated `validators.py` file.

---

# 3. User Model

The `User` model extends Django's `AbstractUser`.

Conceptually:

```text
User
├── id
├── first_name
├── last_name
├── email
├── phone_number
├── role
├── password
├── created_at
└── updated_at
```

Important authentication configuration:

```python
username = None

USERNAME_FIELD = "email"
REQUIRED_FIELDS = []
```

Email is unique:

```python
email = models.EmailField(unique=True)
```

This allows users to authenticate using:

```text
email + password
```

instead of:

```text
username + password
```

---

# 4. User Roles

The project uses an Enum for user roles.

```python
from enum import Enum


class UserRole(Enum):
    PATIENT = "PATIENT"
    PHYSIOTHERAPIST = "PHYSIOTHERAPIST"
    ADMIN = "ADMIN"
```

The role is stored as a string value in the database.

Example:

```text
PATIENT
PHYSIOTHERAPIST
ADMIN
```

The Enum is used in application logic:

```python
if user.role == UserRole.PATIENT.value:
    ...
```

rather than hardcoding role strings throughout the application.

---

# 5. Verification Status

Physiotherapists have a verification status.

```python
class VerificationStatus(Enum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"
```

The initial status of a newly registered physiotherapist is:

```text
PENDING
```

The intended lifecycle is:

```text
Registration
      │
      ▼
   PENDING
      │
      ▼
Admin Review
   │      │
   ▼      ▼
VERIFIED REJECTED
```

Only verified physiotherapists should eventually be exposed to patients for booking.

---

# 6. Patient Profile

A patient profile is linked to the central `User` through a One-to-One relationship.

```text
User
 │
 │ OneToOne
 ▼
Patient
```

The patient contains patient-specific information such as:

- Date of birth
- Gender
- Address
- City
- State
- Pincode
- Emergency contact
- Emergency contact phone

The common authentication information remains in the `User` table.

---

# 7. Physiotherapist Profile

A physiotherapist profile is also linked to `User` using a One-to-One relationship.

```text
User
 │
 │ OneToOne
 ▼
Physiotherapist
```

The profile contains:

- License number
- Bio
- Experience
- Consultation fee
- Verification status
- Created timestamp
- Updated timestamp

The important distinction is:

```text
User
    → authentication/common information

Physiotherapist
    → physiotherapist-specific information
```

---

# 8. Registration API

### Endpoint

```text
POST /api/accounts/register/
```

The registration API is implemented using:

```python
class UserRegistrationView(APIView):
```

The API does not use serializers.

Instead:

```text
request.data
     │
     ▼
validate_registration_data()
     │
     ▼
validated_data
     │
     ▼
UserRegistrationView
     │
     ▼
Database
```

---

# 9. Registration Validation

Registration validation is kept separate from the API view.

File:

```text
accounts/validators.py
```

Main function:

```python
validate_registration_data(data)
```

Responsibilities include:

- Required field validation
- Email normalization
- Duplicate email checking
- Role validation
- Physiotherapist-specific validation
- License-number uniqueness
- Experience validation
- Consultation-fee validation

The validator returns cleaned/validated data to the view.

This keeps the API view focused on application flow rather than becoming a large validation function.

---

# 10. Common Registration Fields

The following fields are required for every registration:

```text
first_name
last_name
email
password
role
```

`phone_number` is optional.

Example:

```json
{
    "first_name": "Rahul",
    "last_name": "Sharma",
    "email": "rahul@example.com",
    "phone_number": "9876543210",
    "password": "Test@12345",
    "role": "PATIENT"
}
```

---

# 11. Physiotherapist Registration

When:

```python
role == UserRole.PHYSIOTHERAPIST.value
```

additional fields are required.

### Required

```text
license_number
experience_years
consultation_fee
```

### Optional

```text
bio
```

Example:

```json
{
    "first_name": "Priya",
    "last_name": "Yadav",
    "email": "priya_physio@example.com",
    "phone_number": "9876543211",
    "password": "Test@12345",
    "role": "PHYSIOTHERAPIST",
    "license_number": "PT-2026-002",
    "bio": "Experienced physiotherapist specializing in sports rehabilitation.",
    "experience_years": 5,
    "consultation_fee": 800
}
```

---

# 12. Atomic Registration

User registration creates multiple database records.

For a patient:

```text
User
 +
Patient
```

For a physiotherapist:

```text
User
 +
Physiotherapist
```

Therefore the creation is wrapped inside:

```python
with transaction.atomic():
```

This guarantees that the operations succeed or fail together.

Example:

```text
User creation
      │
      ▼
Profile creation
      │
      ├── Success → COMMIT
      │
      └── Failure → ROLLBACK
```

This prevents situations such as:

```text
User exists
but
Physiotherapist profile does not exist
```

---

# 13. Login API

### Endpoint

```text
POST /api/accounts/login/
```

The login API:

1. Validates email
2. Validates password
3. Checks whether the email exists
4. Authenticates the password
5. Generates JWT tokens
6. Returns user information

Example request:

```json
{
    "email": "priya_physio@example.com",
    "password": "Test@12345"
}
```

---

# 14. Email Existence Check

The login flow explicitly checks whether an account exists.

If the email does not exist:

```json
{
    "error": "No account found with this email. Please register first."
}
```

If the email exists but the password is incorrect:

```json
{
    "error": "Invalid password."
}
```

For a production authentication system, account-enumeration considerations should eventually be addressed by returning a generic authentication error.

---

# 15. JWT Authentication

After successful authentication, the API generates:

```text
Access Token
Refresh Token
```

Example response:

```json
{
    "message": "Login successful.",
    "access": "<access-token>",
    "refresh": "<refresh-token>",
    "user": {
        "id": 4,
        "first_name": "Priya",
        "last_name": "Yadav",
        "email": "priya_physio@example.com",
        "phone_number": "9876543211",
        "role": "PHYSIOTHERAPIST"
    }
}
```

The access token is used for authenticated APIs.

The refresh token is used to obtain new access tokens.

---

# 16. Logout API

### Endpoint

```text
POST /api/accounts/logout/
```

The client sends the refresh token.

The refresh token is then blacklisted.

Conceptually:

```text
Refresh Token
      │
      ▼
Blacklist
      │
      ▼
Cannot be used for future token refresh
```

This requires:

```python
"rest_framework_simplejwt.token_blacklist"
```

in `INSTALLED_APPS`.

Migrations must be applied after enabling the blacklist application.

---

# 17. API Authentication Configuration

The project uses JWT authentication as the default DRF authentication mechanism.

Conceptually:

```python
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
}
```

Public authentication APIs explicitly override the default:

```python
permission_classes = [AllowAny]
```

For example:

```python
class UserRegistrationView(APIView):
    permission_classes = [AllowAny]
```

and:

```python
class UserLoginView(APIView):
    permission_classes = [AllowAny]
```

This means:

```text
Default API
    → Authentication required

Register
    → Public

Login
    → Public
```

---

# 18. Current Accounts APIs

| Method | Endpoint | Purpose | Authentication |
|---|---|---|---|
| POST | `/api/accounts/register/` | Register user | Public |
| POST | `/api/accounts/login/` | Login | Public |
| POST | `/api/accounts/logout/` | Logout | Authenticated |
| GET | `/api/accounts/me/` | Current user | Authenticated |

The exact `/me/` implementation can be expanded as the module evolves.

---

# 19. SOLID Principles

The Accounts module follows these principles.

### Single Responsibility Principle

Different responsibilities are separated:

```text
validators.py
    → validation

views.py
    → API flow

models.py
    → persistence/data structure

enums.py
    → constants/domain values
```

The registration view should not become responsible for every validation rule.

---

### Open/Closed Principle

The validation logic can be extended without turning the view into a large conditional block.

For example, additional physiotherapist validation can be added to the validation layer.

---

### Dependency Inversion

Business logic should gradually be moved away from direct HTTP concerns.

The long-term direction is:

```text
APIView
   ↓
Service
   ↓
Repository / Query layer
   ↓
Model
```

This allows business logic to be tested without requiring an HTTP request.

---

# 20. Design Patterns

The Accounts module currently uses simple patterns rather than forcing unnecessary abstractions.

### Service Layer

As the module grows, registration/authentication business logic can move into services.

For example:

```text
UserRegistrationView
        ↓
UserRegistrationService
        ↓
User / Patient / Physiotherapist
```

This keeps views thin.

### Transaction Pattern

`transaction.atomic()` is used for multi-model operations.

This guarantees consistency during registration.

### Permission-Based Access Control

DRF permission classes are used to separate authorization from business logic.

---

# 21. Error Handling

The APIs should consistently return appropriate HTTP status codes.

Examples:

```text
400 BAD REQUEST
```

For invalid input.

```text
401 UNAUTHORIZED
```

For invalid authentication credentials.

```text
404 NOT FOUND
```

When an explicitly requested resource doesn't exist.

```text
201 CREATED
```

After successful registration.

```text
200 OK
```

After successful login/logout or successful retrieval.

---

# 22. Accounts Module Design Goal

The final responsibility boundary should look like:

```text
                    ACCOUNTS MODULE
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
       Identity       Authentication      Profiles
          │                │                │
          ▼                ▼                ▼
        User          JWT Login/Logout   Patient
                                           │
                                           ▼
                                    Physiotherapist
```

The Accounts module should remain responsible for **identity and authentication**.

Domain-specific functionality should eventually move to its appropriate modules.

For example:

```text
accounts
    → users/authentication

physiotherapists
    → physiotherapist discovery/profile

appointments
    → appointment booking

notifications
    → notifications

payments
    → payments

```

This separation will help keep the overall application maintainable as Book Your Physio grows.
