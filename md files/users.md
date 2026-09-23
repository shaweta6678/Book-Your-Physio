# Users Module — Book Your Physio

## Overview

The `users` module handles authentication, user accounts, roles, and basic profile information for the Book Your Physio platform.

The platform has three primary user types:

- **Patient** — books physiotherapy appointments.
- **Physiotherapist** — provides physiotherapy services and manages availability.
- **Admin** — manages the platform and verifies physiotherapists.

---

## User Roles

| Role | Description |
|---|---|
| `PATIENT` | Can search physiotherapists and book appointments |
| `PHYSIO` | Can manage profile, availability, and appointments |
| `ADMIN` | Can manage users, physiotherapists, and platform operations |

---

## User Model

We will use a **custom Django User model** based on `AbstractUser`.

### Fields

| Field | Type | Description |
|---|---|---|
| `id` | BigAutoField | Primary key |
| `username` | String | Unique username |
| `email` | Email | User email |
| `first_name` | String | First name |
| `last_name` | String | Last name |
| `phone_number` | String | Contact number |
| `role` | Enum | Patient / Physio / Admin |
| `is_active` | Boolean | Whether the account is active |
| `is_staff` | Boolean | Django admin access |
| `date_joined` | DateTime | Account creation time |
| `updated_at` | DateTime | Last update time |

---

## Django Model

```python
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    class Role(models.TextChoices):
        PATIENT = "PATIENT", "Patient"
        PHYSIO = "PHYSIO", "Physiotherapist"
        ADMIN = "ADMIN", "Admin"

    phone_number = models.CharField(
        max_length=15,
        blank=True
    )

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.PATIENT
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.username
```

---

# Authentication

The API will use token-based authentication.

Recommended approach:

```text
Client
   |
   | Login
   ↓
Django API
   |
   | Access Token
   ↓
Client
```

The client sends the token with subsequent requests:

```http
Authorization: Bearer <access_token>
```

---

# API Endpoints

## Register

```http
POST /api/users/register/
```

### Request

```json
{
    "username": "john",
    "email": "john@example.com",
    "password": "StrongPassword123",
    "phone_number": "9876543210",
    "role": "PATIENT"
}
```

### Response

```json
{
    "message": "User registered successfully"
}
```

---

## Login

```http
POST /api/users/login/
```

### Request

```json
{
    "username": "john",
    "password": "StrongPassword123"
}
```

### Response

```json
{
    "access": "<access_token>",
    "refresh": "<refresh_token>"
}
```

---

## Get Current User

```http
GET /api/users/me/
```

### Response

```json
{
    "id": 1,
    "username": "john",
    "email": "john@example.com",
    "phone_number": "9876543210",
    "role": "PATIENT"
}
```

---

## Update Profile

```http
PATCH /api/users/me/
```

### Request

```json
{
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "9876543210"
}
```

---

# Permissions

## Patient

Patients can:

- Register
- Login
- View/update their profile
- Search physiotherapists
- View physiotherapist profiles
- View available slots
- Book appointments
- Cancel appointments
- View appointment history
- Submit reviews

---

## Physiotherapist

Physiotherapists can:

- Register
- Login
- Manage their profile
- Manage specializations
- Manage consultation fees
- Manage availability
- View appointments
- Accept/reject appointments
- Mark appointments as completed

---

## Admin

Admins can:

- View users
- Activate/deactivate users
- Verify physiotherapists
- Manage physiotherapist profiles
- Manage appointments
- Manage reviews
- Access Django admin

---

# Security Requirements

The users module should follow these rules:

### Password

Never store passwords directly.

Django's password hashing mechanism must be used.

```python
user.set_password(password)
```

Never:

```python
user.password = password
```

---

### Email

Email should be unique.

```python
email = models.EmailField(unique=True)
```

We can enforce this at the database level.

---

### Role-based access

API permissions should prevent users from accessing resources belonging to other users.

For example:

```text
Patient A
   ↓
Can view Patient A appointments

Patient A
   ↓
Cannot view Patient B appointments
```

---

# Future Enhancements

The users module can later support:

- Email verification
- Phone OTP
- Forgot password
- Password reset
- Social login
- Profile photo
- Multiple addresses
- Emergency contact
- Account deletion
- Login history
- Device/session management
- Two-factor authentication

---

# Initial Database Relationship

```text
                    User
                     |
          ┌──────────┴──────────┐
          |                     |
       PATIENT                PHYSIO
          |                     |
          |                     |
          ↓                     ↓
    Appointments          Physiotherapist
                                |
                                ↓
                           Availability
```

---

# Development Order

Implement the users module in this order:

1. Create custom `User` model
2. Configure `AUTH_USER_MODEL`
3. Create migrations
4. Create User serializer
5. Create registration API
6. Create login API
7. Add JWT authentication
8. Create `/me/` API
9. Add role-based permissions
10. Write unit/API tests

---

## Important

The custom User model should be created **before the first migration** of the project.

In `settings.py`:

```python
AUTH_USER_MODEL = "accounts.User"
```

If the app is named `users` instead of `accounts`, use:

```python
AUTH_USER_MODEL = "users.User"
```

Choose the app name now and keep it consistent throughout the project.