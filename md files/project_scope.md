# Book Your Physio
## Project Scope & Technical Specification

**Document Version:** 1.0  
**Project:** Book Your Physio  
**Backend:** Django + Django REST Framework  
**Database:** PostgreSQL  
**Frontend:** React.js *(planned)*  
**Authentication:** JWT  
**Architecture:** Modular Django Backend / REST APIs  
**Primary Goal:** Build a scalable physiotherapy appointment platform suitable for real-world usage and SDE2-level backend/system-design discussions.

---

# 1. Project Overview

**Book Your Physio** is a healthcare appointment platform that allows patients to discover physiotherapists based on location, specialization, experience, consultation fee, availability, and other criteria.

Patients can:

- Register and log in.
- Maintain their profile.
- Search for physiotherapists.
- Find nearby physiotherapists.
- View physiotherapist profiles.
- View available services and consultation fees.
- Check availability.
- Book appointments.
- Cancel/reschedule appointments.
- Make payments.
- View appointment history.
- Receive notifications.
- Submit reviews and ratings.

Physiotherapists can:

- Register on the platform.
- Create and manage their professional profile.
- Provide license and professional information.
- Define services and consultation fees.
- Configure availability.
- Manage appointments.
- View patient information relevant to appointments.
- Receive notifications.
- Track appointment history.

Administrators can:

- Verify physiotherapists.
- Manage users.
- Manage physiotherapist profiles.
- Monitor appointments.
- Manage platform-level configuration.
- Handle reported issues.
- View operational information.

---

# 2. Problem Statement

Finding an appropriate physiotherapist can be difficult because patients may not know:

- Which physiotherapists are nearby.
- Whether a physiotherapist is verified.
- What services they provide.
- How much consultation costs.
- When they are available.
- Whether they have relevant experience.
- Whether other patients have reviewed them.

The platform aims to provide a centralized system where patients can discover and book physiotherapy services conveniently.

---

# 3. Project Goals

## Primary Goals

1. Build a secure backend API.
2. Support patient, physiotherapist, and admin roles.
3. Provide physiotherapist discovery and search.
4. Support location-based physiotherapist discovery.
5. Implement appointment booking.
6. Prevent appointment conflicts.
7. Support physiotherapist verification.
8. Provide a clean and scalable backend architecture.
9. Follow SOLID principles.
10. Keep business logic separate from HTTP/API handling.

## Technical Goals

The project should demonstrate knowledge of:

- Python
- Django
- Django REST Framework
- PostgreSQL
- JWT authentication
- Redis
- Caching
- Background jobs
- API design
- Database design
- Transactions
- Concurrency
- System design
- Docker
- AWS
- Logging and monitoring
- Scalability

---

# 4. Target Users

The platform will have three primary roles.

## 4.1 Patient

Patients can:

- Register.
- Login/logout.
- Manage profile.
- Search physiotherapists.
- Find nearby physiotherapists.
- View physiotherapist profiles.
- View services.
- View consultation fees.
- View availability.
- Book appointments.
- Cancel appointments.
- Reschedule appointments.
- Make payments.
- View appointment history.
- Receive notifications.
- Submit reviews.

---

## 4.2 Physiotherapist

Physiotherapists can:

- Register.
- Login/logout.
- Maintain professional profile.
- Submit license information.
- Add experience.
- Add biography.
- Configure location.
- Add services.
- Configure consultation fees.
- Configure availability.
- View appointments.
- Accept/manage appointments where applicable.
- Mark appointments as completed.
- View relevant patient information.
- Receive notifications.

A newly registered physiotherapist will initially have:

```text
PENDING
```

verification status.

An administrator can subsequently:

```text
PENDING
   |
   +----> VERIFIED
   |
   +----> REJECTED
```

Only verified physiotherapists should normally be discoverable by patients.

---

## 4.3 Admin

Administrators can:

- View users.
- View physiotherapists.
- Verify physiotherapists.
- Reject physiotherapists.
- Manage platform data.
- Monitor appointments.
- Manage reported problems.
- Manage operational configuration.

---

# 5. High-Level User Flow

## Patient Flow

```text
Register
   |
Login
   |
Complete Profile
   |
Select Location
   |
Find Nearby Physiotherapists
   |
Search / Filter
   |
View Physiotherapist
   |
View Services
   |
View Availability
   |
Select Slot
   |
Book Appointment
   |
Payment
   |
Appointment Confirmation
   |
Notification
   |
Consultation
   |
Review / Rating
```

---

## Physiotherapist Flow

```text
Register
   |
Submit Professional Details
   |
Verification Pending
   |
Admin Review
   |
Verified
   |
Complete Profile
   |
Add Services
   |
Configure Availability
   |
Receive Appointments
   |
Manage Appointment
   |
Complete Consultation
```

---

## Admin Flow

```text
Admin Login
   |
Dashboard
   |
View Pending Physiotherapists
   |
Review Documents / Details
   |
Approve / Reject
   |
Monitor Platform
```

---

# 6. Functional Scope

# Module 1 — Accounts & Authentication

This module is already scoped and forms the foundation of the application.

## Features

### Registration

Patients and physiotherapists can register.

Patient registration:

```text
first_name
last_name
email
phone_number
password
role
```

Physiotherapist registration additionally requires:

```text
license_number
bio
experience_years
consultation_fee
```

---

### Login

Login using:

```text
email
password
```

The backend returns:

```text
access token
refresh token
user information
```

---

### Logout

Logout invalidates the refresh token using JWT blacklist functionality.

---

### JWT Authentication

The application uses:

```text
djangorestframework-simplejwt
```

Access tokens are used for API authorization.

Refresh tokens are used to obtain new access tokens.

---

### Email Validation

The system should:

- Normalize email.
- Check whether email already exists.
- Reject duplicate registrations.

---

### Role-Based Access

Supported roles:

```text
PATIENT
PHYSIOTHERAPIST
ADMIN
```

---

# Module 2 — Patient Profile

Patients should be able to manage personal information.

## Profile Information

```text
first_name
last_name
email
phone_number
date_of_birth
gender
address
city
state
pincode
emergency_contact_name
emergency_contact_phone
```

## APIs

```http
GET /api/patients/me/
PATCH /api/patients/me/
```

Potential future APIs:

```http
POST /api/patients/me/profile-picture/
DELETE /api/patients/me/profile-picture/
```

---

# Module 3 — Physiotherapist Profile

Physiotherapists should have a professional profile.

## Profile Information

```text
name
license_number
bio
experience_years
consultation_fee
verification_status
location
```

Additional information may include:

```text
specializations
languages
clinic_name
clinic_address
profile_picture
```

## APIs

```http
GET /api/physiotherapists/me/
PATCH /api/physiotherapists/me/
```

---

# Module 4 — Physiotherapist Verification

A physiotherapist cannot immediately become publicly discoverable.

## Verification Lifecycle

```text
PENDING
   |
   +---- VERIFIED
   |
   +---- REJECTED
```

## Admin APIs

```http
GET /api/admin/physiotherapists/pending/
POST /api/admin/physiotherapists/{id}/verify/
POST /api/admin/physiotherapists/{id}/reject/
```

## Verification Requirements

Potential verification information:

- License number.
- Professional registration.
- Experience.
- Identity/professional documentation.

The exact document-verification process can be expanded later.

---

# Module 5 — Physiotherapist Location

Location is an important feature of the application.

Physiotherapists should have geographic coordinates.

## Database Fields

```python
latitude
longitude
```

Recommended initial implementation:

```python
latitude = models.DecimalField(
    max_digits=9,
    decimal_places=6,
    null=True,
    blank=True,
)

longitude = models.DecimalField(
    max_digits=9,
    decimal_places=6,
    null=True,
    blank=True,
)
```

---

# Module 6 — Nearby Physiotherapist Search

A patient can share their current location.

Example:

```text
Patient Latitude: 28.4595
Patient Longitude: 77.0266
```

The frontend sends coordinates to Django.

```http
GET /api/physiotherapists/nearby/?latitude=28.4595&longitude=77.0266
```

The backend calculates distance between the patient and physiotherapists.

Initial implementation:

```text
Haversine Formula
```

Later production implementation:

```text
PostgreSQL + PostGIS
```

---

## Nearby Search Flow

```text
Patient
   |
   | latitude + longitude
   v
Django API
   |
   v
Validate coordinates
   |
   v
Find verified physiotherapists
   |
   v
Calculate distance
   |
   v
Filter by radius
   |
   v
Sort by distance
   |
   v
Return results
```

Example response:

```json
{
    "results": [
        {
            "id": 10,
            "name": "Priya Mehta",
            "experience_years": 5,
            "consultation_fee": 800,
            "distance_km": 1.8
        }
    ]
}
```

---

# Module 7 — Physiotherapist Search

Patients should be able to search by:

- Name
- Specialization
- Location
- Experience
- Consultation fee

Example:

```http
GET /api/physiotherapists/?search=Priya
```

---

# Module 8 — Physiotherapist Filters

Supported filters:

```text
minimum experience
maximum experience
minimum consultation fee
maximum consultation fee
specialization
location
distance
```

Example:

```http
GET /api/physiotherapists/?min_experience=5
```

or:

```http
GET /api/physiotherapists/?min_fee=500&max_fee=1000
```

---

# Module 9 — Physiotherapy Services

A physiotherapist may provide multiple services.

Examples:

```text
Sports Rehabilitation
Back Pain Treatment
Post-Surgery Rehabilitation
Neck Pain Treatment
Arthritis Therapy
Posture Correction
```

Instead of storing all services directly on the physiotherapist table, services should eventually have their own entity.

## Possible Model

```text
Service
-------
id
name
description
duration
```

Relationship:

```text
Physiotherapist
       |
       | many-to-many
       v
Service
```

A physiotherapist can configure:

```text
service
price
duration
```

---

# Module 10 — Consultation Fees

Initially, the physiotherapist has:

```text
consultation_fee
```

As the application grows, pricing can become service-specific.

Example:

```text
Initial Consultation       ₹800
Follow-up Consultation     ₹600
Sports Rehabilitation      ₹1200
```

Potential future model:

```text
PhysiotherapistService
----------------------
physiotherapist
service
price
duration
```

---

# Module 11 — Physiotherapist Availability

Physiotherapists should configure their working schedule.

Example:

```text
Monday
09:00 - 13:00
14:00 - 18:00

Tuesday
09:00 - 13:00
14:00 - 18:00
```

Potential model:

```text
Availability
------------
physiotherapist
day_of_week
start_time
end_time
```

---

# Module 12 — Appointment Slots

The system should expose available appointment slots.

Example:

```text
10:00 AM
10:30 AM
11:00 AM
11:30 AM
```

Slot generation should consider:

- Physiotherapist availability.
- Existing appointments.
- Appointment duration.
- Buffer time.
- Holidays/unavailable periods.

---

# Module 13 — Appointment Booking

Patients can book available slots.

Example:

```http
POST /api/appointments/
```

Request:

```json
{
    "physiotherapist_id": 10,
    "service_id": 2,
    "appointment_date": "2026-10-15",
    "start_time": "10:00"
}
```

---

# Module 14 — Appointment Lifecycle

Appointments should have statuses.

```text
PENDING
CONFIRMED
CANCELLED
COMPLETED
NO_SHOW
```

Potential flow:

```text
PENDING
   |
   v
CONFIRMED
   |
   v
COMPLETED
```

Cancellation:

```text
PENDING / CONFIRMED
        |
        v
    CANCELLED
```

---

# Module 15 — Prevent Double Booking

This is an important backend/system-design requirement.

Example:

```text
Patient A ----> 10:00 AM
Patient B ----> 10:00 AM
```

The system must prevent both bookings from succeeding for the same physiotherapist and slot.

Possible approach:

```text
Database transaction
+
Row-level locking
+
Database constraints
```

For example:

```python
transaction.atomic()
```

combined with:

```python
select_for_update()
```

The exact implementation will be decided when the Appointment module is built.

This is also an important SDE2 interview topic because it demonstrates understanding of concurrency.

---

# Module 16 — Appointment Management

## Patient

Patients can:

```text
View upcoming appointments
View past appointments
Cancel appointment
Reschedule appointment
View appointment details
```

## Physiotherapist

Physiotherapists can:

```text
View upcoming appointments
View appointment history
View appointment details
Update appointment status
Mark appointment completed
```

---

# Module 17 — Payment

Payment integration can be introduced after appointment booking.

Potential payment provider:

```text
Razorpay
Stripe
```

Payment lifecycle:

```text
Appointment Created
       |
       v
Payment Pending
       |
       v
Payment Processing
       |
       v
Payment Successful
       |
       v
Appointment Confirmed
```

Payment failure:

```text
Payment Failed
       |
       v
Appointment remains unconfirmed
```

Payment information should not store sensitive card information.

---

# Module 18 — Notifications

Users should receive notifications for important events.

Examples:

```text
Registration
Appointment booked
Appointment confirmed
Appointment cancelled
Appointment rescheduled
Payment successful
Appointment reminder
Physiotherapist verification
```

Notification channels:

```text
In-app
Email
SMS
Push notifications
```

Initial implementation can use email/in-app notifications.

---

# Module 19 — Appointment Reminders

The system should send reminders before appointments.

Example:

```text
24 hours before
1 hour before
```

This is a good use case for:

```text
Background jobs
Celery
Redis
```

---

# Module 20 — Reviews & Ratings

After a completed appointment, a patient can submit a review.

Example:

```text
Rating: 5
Comment: Very helpful consultation.
```

Rules:

- Only patients with completed appointments can review.
- One review per appointment.
- Rating should be within the supported range.
- Reviews should be associated with the relevant physiotherapist.

---

# Module 21 — Admin Dashboard

Admin functionality should include:

## Users

```text
View users
Search users
View user details
Deactivate users
```

## Physiotherapists

```text
Pending verification
Verified
Rejected
```

## Appointments

```text
Upcoming
Completed
Cancelled
```

## Platform Monitoring

Potential metrics:

```text
Total patients
Total physiotherapists
Verified physiotherapists
Total appointments
Completed appointments
Cancelled appointments
Revenue
```

---

# 7. API Scope

The API structure should follow resource-oriented REST principles.

## Accounts

```http
POST /api/accounts/register/
POST /api/accounts/login/
POST /api/accounts/logout/
```

## Patient

```http
GET   /api/patients/me/
PATCH /api/patients/me/
```

## Physiotherapist

```http
GET   /api/physiotherapists/
GET   /api/physiotherapists/{id}/
GET   /api/physiotherapists/me/
PATCH /api/physiotherapists/me/
GET   /api/physiotherapists/nearby/
```

## Services

```http
GET  /api/services/
POST /api/physiotherapists/me/services/
PATCH /api/physiotherapists/me/services/{id}/
DELETE /api/physiotherapists/me/services/{id}/
```

## Availability

```http
GET  /api/physiotherapists/me/availability/
POST /api/physiotherapists/me/availability/
PATCH /api/physiotherapists/me/availability/{id}/
DELETE /api/physiotherapists/me/availability/{id}/
```

## Appointments

```http
POST /api/appointments/
GET  /api/appointments/
GET  /api/appointments/{id}/
PATCH /api/appointments/{id}/
POST /api/appointments/{id}/cancel/
POST /api/appointments/{id}/reschedule/
```

## Reviews

```http
POST /api/appointments/{id}/review/
GET  /api/physiotherapists/{id}/reviews/
```

## Admin

```http
GET  /api/admin/physiotherapists/pending/
POST /api/admin/physiotherapists/{id}/verify/
POST /api/admin/physiotherapists/{id}/reject/
GET  /api/admin/users/
GET  /api/admin/appointments/
```

---

# 8. Database Scope

Initial entities:

```text
User
Patient
Physiotherapist
Service
PhysiotherapistService
Availability
Appointment
Payment
Review
Notification
```

---

# 9. High-Level Entity Relationship

```text
                     User
                      |
             +--------+--------+
             |                 |
          Patient       Physiotherapist
                               |
                  +------------+------------+
                  |            |            |
               Service    Availability   Location
                  |
        PhysiotherapistService
                  |
             Appointment
                  |
          +-------+-------+
          |               |
       Payment         Review
```

---

# 10. Current Database Design

## User

```text
id
email
password
first_name
last_name
phone_number
role
created_at
updated_at
```

---

## Patient

```text
id
user_id
date_of_birth
gender
address
city
state
pincode
emergency_contact_name
emergency_contact_phone
created_at
updated_at
```

---

## Physiotherapist

```text
id
user_id
license_number
bio
experience_years
consultation_fee
verification_status
latitude
longitude
created_at
updated_at
```

---

# 11. Architecture

The backend should follow a modular architecture.

```text
React Frontend
       |
       v
Django REST API
       |
       +------------------+
       |                  |
       v                  v
Authentication       API Views
                         |
                         v
                    Validators
                         |
                         v
                      Services
                         |
                         v
                    Repositories
                         |
                         v
                    PostgreSQL
```

---

# 12. Django Project Structure

Recommended structure:

```text
book-your-physio/
│
├── manage.py
│
├── book_your_physio/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── accounts/
│   ├── models.py
│   ├── enums.py
│   ├── validators.py
│   ├── views.py
│   ├── urls.py
│   ├── services.py
│   ├── permissions.py
│   └── ...
│
├── physiotherapists/
│   ├── models.py
│   ├── views.py
│   ├── validators.py
│   ├── services.py
│   ├── repositories.py
│   ├── permissions.py
│   └── urls.py
│
├── appointments/
│   ├── models.py
│   ├── views.py
│   ├── validators.py
│   ├── services.py
│   ├── repositories.py
│   ├── permissions.py
│   └── urls.py
│
├── services/
│   ├── models.py
│   ├── views.py
│   ├── validators.py
│   └── urls.py
│
├── notifications/
│   ├── models.py
│   ├── services.py
│   └── ...
│
└── payments/
    ├── models.py
    ├── services.py
    └── ...
```

---

# 13. Responsibility Separation

The project should avoid putting all logic inside views.

## Views

Responsible for:

```text
HTTP request
Authentication
Calling validation
Calling service layer
Returning HTTP response
```

Views should remain thin.

---

## Validators

Responsible for:

```text
Required fields
Input format
Business input validation
Data normalization
```

---

## Services

Responsible for:

```text
Business logic
Multi-step operations
Transactions
Workflow coordination
```

Example:

```text
AppointmentService
BookingService
PaymentService
NotificationService
```

---

## Repositories

Repositories can be introduced when database queries become sufficiently complex.

Responsibilities:

```text
Complex queries
Filtering
Nearby search
Database-specific operations
```

Avoid creating repositories for trivial CRUD operations purely for abstraction.

---

## Permissions

Responsible for authorization.

Examples:

```text
IsPatient
IsPhysiotherapist
IsAdmin
IsVerifiedPhysiotherapist
```

---

# 14. SOLID Principles

## Single Responsibility Principle

Each component should have one primary responsibility.

Example:

```text
View       -> HTTP
Validator  -> Validation
Service    -> Business logic
Repository -> Data access
```

---

## Open/Closed Principle

The system should allow new functionality without unnecessarily modifying existing functionality.

Example:

```text
DistanceCalculationStrategy
```

could later support:

```text
Haversine
PostGIS
External Maps API
```

without rewriting the entire discovery module.

---

## Liskov Substitution Principle

Interfaces/abstractions should allow implementations to be substituted without breaking expected behavior.

---

## Interface Segregation Principle

Avoid large interfaces containing unrelated operations.

---

## Dependency Inversion Principle

Higher-level business logic should not be tightly coupled to implementation details.

For example:

```text
AppointmentService
       |
       v
PaymentService interface
       |
       +---- Razorpay
       |
       +---- Stripe
```

This should only be introduced when multiple implementations actually become necessary.

---

# 15. Design Patterns

The project should use patterns where they solve real problems.

## Service Layer

Used for business workflows.

Example:

```text
AppointmentService
PhysiotherapistService
PaymentService
```

---

## Repository Pattern

Used for complex data access.

Example:

```text
PhysiotherapistRepository
```

can handle:

```text
search
filter
nearby lookup
ordering
pagination
```

---

## Strategy Pattern

Potential use:

```text
DistanceCalculationStrategy
```

Implementations:

```text
HaversineDistanceStrategy
PostGISDistanceStrategy
```

Only introduce this if multiple calculation mechanisms become necessary.

---

## Factory Pattern

Potential use for notification providers:

```text
EmailNotification
SMSNotification
PushNotification
```

---

## Observer/Event-Driven Pattern

Useful for:

```text
Appointment booked
       |
       +--> Notification
       +--> Email
       +--> Analytics
```

This can later be implemented using:

```text
Celery
Redis
Kafka
```

depending on scale.

---

# 16. Security Requirements

## Authentication

Use:

```text
JWT
```

---

## Password Security

Passwords must never be stored as plain text.

Django's password hashing should be used.

---

## Authorization

Every protected API should verify:

```text
Authenticated user
+
Correct role
+
Resource ownership
```

Example:

A patient must not be able to modify another patient's profile.

---

## Physiotherapist Verification

Unverified physiotherapists should not appear in public discovery APIs.

---

## Input Validation

All client input must be validated.

Never trust:

```text
request.data
```

directly.

---

## Sensitive Information

Do not expose:

- Passwords
- JWT secrets
- Payment credentials
- Internal administrative information

---

# 17. Performance Requirements

The system should be designed to support increasing traffic.

Important areas:

```text
Database indexes
Caching
Pagination
Efficient queries
Connection pooling
Async processing
```

---

# 18. Database Optimization

Indexes should be considered for:

```text
User.email
Physiotherapist.license_number
Physiotherapist.verification_status
Physiotherapist.latitude
Physiotherapist.longitude
Appointment.physiotherapist
Appointment.appointment_date
Appointment.status
```

The exact indexes should be determined based on actual query patterns.

---

# 19. Redis

Redis can be used for:

## OTP

```text
OTP
   |
Redis
   |
TTL
```

Example:

```text
otp:user:123
TTL = 5 minutes
```

---

## Caching

Potential cached information:

```text
Popular physiotherapists
Physiotherapist search results
Services
Availability
```

Caching should not be used blindly for appointment availability because stale availability can cause incorrect booking behavior.

---

## Rate Limiting

Redis can support:

```text
Login attempts
OTP requests
API requests
```

---

# 20. OTP Authentication

Potential future flow:

```text
User enters phone/email
        |
        v
Generate OTP
        |
        v
Store OTP in Redis
        |
        v
Send OTP
        |
        v
User enters OTP
        |
        v
Validate OTP
        |
        v
Authenticate
```

OTP should have:

```text
Expiration
Attempt limit
Rate limit
One-time usage
```

---

# 21. Background Processing

Long-running operations should not block API requests.

Examples:

```text
Send email
Send SMS
Appointment reminders
Generate reports
Process payment webhook
```

Potential technology:

```text
Celery + Redis
```

---

# 22. Kafka

Kafka can be introduced if the system grows into an event-driven architecture.

Example:

```text
Appointment Created
        |
        v
Kafka
        |
        +---- Notification Service
        |
        +---- Analytics Service
        |
        +---- Email Service
        |
        +---- Audit Service
```

Kafka is **not required for the MVP**.

It is an advanced scalability component.

---

# 23. Appointment Concurrency

Appointment booking is one of the most important system-design problems in this project.

Potential race condition:

```text
Patient A ----+
              |
              +---- 10:00 slot
              |
Patient B ----+
```

Both requests may arrive simultaneously.

The system must guarantee:

```text
One slot = One confirmed appointment
```

Possible solution:

```text
transaction.atomic()
+
select_for_update()
+
database constraints
```

Redis distributed locks may be considered later if required by the architecture.

---

# 24. Location Architecture

## MVP

Use:

```text
latitude
longitude
```

and calculate distance using Haversine.

## Scale-up

Move to:

```text
PostgreSQL
+
PostGIS
+
Spatial Index
```

This will allow efficient geographic queries.

Example conceptual query:

```text
Find verified physiotherapists
within 10 km
of patient coordinates
ordered by distance.
```

---

# 25. Pagination

Large result sets should never be returned in one API response.

Example:

```http
GET /api/physiotherapists/?page=1&page_size=20
```

Pagination should be applied to:

```text
Physiotherapist list
Appointments
Reviews
Notifications
Admin user list
```

---

# 26. Error Handling

The API should use consistent error responses.

Example:

```json
{
    "error": "User with this email already exists."
}
```

For validation:

```json
{
    "error": "Consultation fee must be a valid number."
}
```

For authentication:

```json
{
    "error": "Invalid password."
}
```

For authorization:

```json
{
    "error": "You do not have permission to perform this action."
}
```

---

# 27. HTTP Status Codes

Use appropriate status codes.

```text
200 OK
201 CREATED
204 NO CONTENT
400 BAD REQUEST
401 UNAUTHORIZED
403 FORBIDDEN
404 NOT FOUND
409 CONFLICT
422 UNPROCESSABLE ENTITY
500 INTERNAL SERVER ERROR
```

---

# 28. Logging

The application should maintain structured logs for:

```text
Authentication failures
Appointment creation
Payment events
Verification actions
Application errors
External API failures
```

Do not log:

```text
Passwords
JWT secrets
OTP values
Payment credentials
Sensitive personal information
```

---

# 29. Testing Scope

Testing should include:

## Unit Tests

```text
Validators
Services
Business logic
Distance calculation
Appointment rules
```

## API Tests

```text
Registration
Login
Logout
Profile APIs
Search
Nearby search
Appointment booking
Cancellation
Reviews
```

## Integration Tests

```text
Database
JWT
Redis
Payment gateway
Notification system
```

---

# 30. Deployment

Potential production architecture:

```text
                    Internet
                       |
                       v
                  Load Balancer
                       |
              +--------+--------+
              |                 |
           Django            Django
           Server             Server
              |                 |
              +--------+--------+
                       |
                       v
                   PostgreSQL
                       |
              +--------+--------+
              |                 |
            Redis             S3
```

Potential AWS components:

```text
EC2 / ECS
RDS PostgreSQL
S3
CloudWatch
Load Balancer
```

---

# 31. Docker

The application should eventually be containerized.

Potential containers:

```text
django
postgres
redis
celery
```

Development architecture:

```text
Docker Compose
       |
       +---- Django
       +---- PostgreSQL
       +---- Redis
       +---- Celery
```

---

# 32. CI/CD

Potential pipeline:

```text
Developer
   |
Git Push
   |
GitHub
   |
GitHub Actions
   |
+----------------+
| Tests          |
| Linting        |
| Build Docker   |
| Security Scan  |
+----------------+
   |
Deployment
```

---

# 33. API Versioning

The API should be designed so that future versions can be introduced.

Example:

```text
/api/v1/accounts/
/api/v1/physiotherapists/
/api/v1/appointments/
```

This is preferable when the API becomes externally consumed and backward compatibility becomes important.

---

# 34. MVP Scope

The first working version should contain:

## Authentication

- Patient registration
- Physiotherapist registration
- Login
- Logout
- JWT authentication

## Patient

- Patient profile
- Update profile

## Physiotherapist

- Professional profile
- Profile update
- Verification status
- Admin verification

## Discovery

- Physiotherapist listing
- Search
- Experience filtering
- Fee filtering
- Location
- Nearby physiotherapist search

## Appointment

- Availability
- Slot generation
- Appointment booking
- Appointment cancellation
- Appointment history

## Reviews

- Review after completed appointment
- Rating

---

# 35. Phase 1 — Completed

## Accounts

Current scope:

```text
User model
Patient model
Physiotherapist model
UserRole enum
VerificationStatus enum
Registration
Validation
Login
JWT
Logout
Refresh token blacklist
Role handling
```

---

# 36. Phase 2 — Current Next Module

## Physiotherapist Module

Implementation order:

```text
1. Physiotherapist profile
2. Profile update
3. Permissions
4. Admin verification
5. Physiotherapist listing
6. Search
7. Filters
8. Location
9. Nearby search
10. Pagination
```

---

# 37. Phase 3 — Services

Implement:

```text
Service
PhysiotherapistService
Service listing
Service creation
Service update
Service deletion
Pricing
Duration
```

---

# 38. Phase 4 — Availability

Implement:

```text
Working hours
Availability
Blocked periods
Slot generation
```

---

# 39. Phase 5 — Appointments

Implement:

```text
Appointment model
Booking
Cancellation
Rescheduling
Appointment status
Concurrency handling
Appointment history
```

This phase will contain some of the most important backend design challenges.

---

# 40. Phase 6 — Payments

Implement:

```text
Payment model
Payment initiation
Payment verification
Payment webhook
Payment status
Refund handling
```

---

# 41. Phase 7 — Notifications

Implement:

```text
In-app notifications
Email
Appointment reminders
Background jobs
Celery
Redis
```

---

# 42. Phase 8 — Reviews

Implement:

```text
Ratings
Reviews
Review validation
Review listing
Average rating
```

---

# 43. Phase 9 — Admin

Implement:

```text
Admin dashboard APIs
User management
Physiotherapist verification
Appointment monitoring
Platform statistics
```

---

# 44. Phase 10 — Production Readiness

Implement:

```text
Docker
AWS
CI/CD
Logging
Monitoring
Caching
Database optimization
Security hardening
API documentation
```

---

# 45. MVP vs Future Scope

| Feature | MVP | Future |
|---|---:|---:|
| Registration | Yes | — |
| JWT Authentication | Yes | — |
| Patient Profile | Yes | — |
| Physiotherapist Profile | Yes | — |
| Verification | Yes | Advanced document verification |
| Search | Yes | Advanced ranking |
| Filters | Yes | Personalized recommendations |
| Nearby Search | Yes | PostGIS |
| Services | Yes | Packages |
| Availability | Yes | Advanced scheduling |
| Appointment | Yes | Recurring appointments |
| Payment | Later MVP | Multiple gateways |
| Notifications | Basic | Multi-channel |
| Reviews | Yes | Advanced moderation |
| Redis | Later | Advanced caching |
| Celery | Later | — |
| Kafka | No | Yes |
| React Frontend | Later | Yes |
| Mobile App | No | Future |
| AI Recommendations | No | Future |

---

# 46. Out of Scope — Initial Version

The following should not be implemented initially:

```text
Mobile application
AI diagnosis
Medical diagnosis
Electronic medical records
Insurance integration
Hospital management
Video consultation
Complex recommendation engine
Multi-country payment systems
Large-scale Kafka architecture
Microservices
```

These can be considered only after the core platform is stable.

---

# 47. Future Enhancements

Potential future features:

## Teleconsultation

```text
Video consultation
Chat
Prescription sharing
```

## AI Recommendations

```text
Patient symptoms
     |
     v
Recommendation Engine
     |
     v
Potential physiotherapy services
```

This should be treated as a future feature and not as a medical diagnosis system.

---

## Multiple Locations

A physiotherapist could work at multiple clinics.

Instead of:

```text
Physiotherapist -> Location
```

the model can evolve to:

```text
Physiotherapist
       |
       +---- Location 1
       |
       +---- Location 2
       |
       +---- Location 3
```

---

# 48. Scalability Roadmap

## Stage 1

```text
Django
PostgreSQL
```

## Stage 2

```text
Django
PostgreSQL
Redis
```

## Stage 3

```text
Django
PostgreSQL
Redis
Celery
```

## Stage 4

```text
Load Balancer
Multiple Django instances
RDS
Redis
Celery
S3
```

## Stage 5

```text
Event-driven architecture
Kafka
Dedicated services
Advanced monitoring
```

The project should **not start with microservices**.

The initial architecture should remain modular and simple enough to develop and debug quickly.

---

# 49. Important SDE2-Level Design Problems

This project intentionally contains several problems that can be discussed in backend interviews.

## Problem 1 — Authentication

Questions:

```text
How does JWT work?
Why access + refresh tokens?
How do you invalidate JWT?
Why blacklist refresh tokens?
```

---

## Problem 2 — Nearby Search

Questions:

```text
How do you find nearby physiotherapists?
How does Haversine work?
Why use PostGIS?
How does spatial indexing improve performance?
```

---

## Problem 3 — Appointment Booking

Questions:

```text
How do you prevent double booking?
What happens if two users book simultaneously?
Where should transaction boundaries exist?
When should row locks be used?
```

---

## Problem 4 — Caching

Questions:

```text
What should be cached?
What should not be cached?
How do you invalidate cache?
What happens when cached data becomes stale?
```

---

## Problem 5 — Notifications

Questions:

```text
Should notification sending block API response?
How would you process notifications asynchronously?
Why use Celery?
When would Kafka be useful?
```

---

## Problem 6 — Scalability

Questions:

```text
How would you handle 10,000 concurrent users?
How would you scale Django?
How would you scale PostgreSQL?
Where would Redis fit?
How would you handle database connection limits?
```

---

# 50. Key System Design Concepts Demonstrated

This project can demonstrate:

```text
REST API Design
Authentication
Authorization
JWT
RBAC
Database Design
Transactions
Concurrency
Distributed Systems
Caching
Message Queues
Event-Driven Architecture
Geospatial Queries
Pagination
Indexing
Async Processing
Horizontal Scaling
Cloud Deployment
Observability
```

---

# 51. Definition of Done

A module should be considered complete when:

```text
Model implemented
       |
Migration created
       |
Validation implemented
       |
Business logic implemented
       |
Permissions implemented
       |
API implemented
       |
URLs configured
       |
Unit tests added
       |
API tests added
       |
Error handling added
       |
Documentation updated
```

---

# 52. Project Success Criteria

The project will be considered successful when a patient can complete the following flow:

```text
Register
   ↓
Login
   ↓
Provide location
   ↓
Find nearby physiotherapists
   ↓
Search/filter
   ↓
View physiotherapist
   ↓
View services
   ↓
View available slots
   ↓
Book appointment
   ↓
Receive confirmation
   ↓
Attend appointment
   ↓
Complete appointment
   ↓
Submit review
```

And a physiotherapist can:

```text
Register
   ↓
Get verified
   ↓
Manage profile
   ↓
Add services
   ↓
Configure availability
   ↓
Receive appointment
   ↓
Complete appointment
```

Administrators can:

```text
Login
   ↓
Review physiotherapists
   ↓
Verify/reject
   ↓
Monitor platform
```

---

# 53. Development Philosophy

The project should follow these principles:

### 1. Build incrementally

Do not implement the entire architecture upfront.

### 2. Keep views thin

Business logic should not live inside large API views.

### 3. Validate input separately

Use dedicated validation functions/classes.

### 4. Use transactions where required

Especially for:

```text
Registration
Appointment booking
Payment workflows
```

### 5. Optimize when needed

Do not introduce Redis, Kafka, PostGIS, or microservices simply for the sake of using them.

### 6. Prefer simple architecture first

Start with:

```text
Modular Monolith
```

and evolve based on actual requirements.

### 7. Design for change

Use SOLID principles and appropriate abstractions where they provide real value.

---

# 54. Current Project Status

## Completed

```text
[x] Project setup
[x] PostgreSQL configuration
[x] Custom User model
[x] Patient model
[x] Physiotherapist model
[x] User roles
[x] Verification status
[x] Registration API
[x] Registration validation
[x] Patient profile creation
[x] Physiotherapist profile creation
[x] JWT login
[x] JWT logout
[x] Refresh token blacklist
```

## In Progress / Next

```text
[ ] Physiotherapist profile APIs
[ ] Physiotherapist permissions
[ ] Admin verification
[ ] Physiotherapist listing
[ ] Search
[ ] Filters
[ ] Location
[ ] Nearby physiotherapist search
```

## Upcoming

```text
[ ] Services
[ ] Availability
[ ] Appointments
[ ] Booking concurrency
[ ] Payments
[ ] Notifications
[ ] Reviews
[ ] Admin APIs
[ ] Redis
[ ] Celery
[ ] Docker
[ ] AWS deployment
[ ] CI/CD
```

---

# 55. Final Architecture Vision

The final system is intended to evolve approximately as follows:

```text
                         React Frontend
                              |
                              v
                       API Gateway / LB
                              |
                +-------------+-------------+
                |                           |
                v                           v
          Django API 1                  Django API 2
                |                           |
                +-------------+-------------+
                              |
              +---------------+---------------+
              |               |               |
              v               v               v
          PostgreSQL        Redis           S3
              |
              |
       +------+-------+
       |              |
       v              v
   Appointments    User Data

              Background Processing
                       |
                       v
                 Celery + Redis

              Event Architecture
                       |
                       v
                     Kafka
                       |
         +-------------+-------------+
         |             |             |
         v             v             v
   Notifications   Analytics      Audit
```

This is the **long-term architecture**, not the architecture that needs to be built immediately.

---

# 56. Final Scope Summary

**Book Your Physio** will initially be developed as a **Django modular monolith** with PostgreSQL and JWT authentication.

The core product will focus on:

```text
Authentication
      +
Patient Management
      +
Physiotherapist Management
      +
Verification
      +
Location-Based Discovery
      +
Services
      +
Availability
      +
Appointments
      +
Payments
      +
Notifications
      +
Reviews
      +
Administration
```

The technical architecture will evolve progressively toward:

```text
Redis
Celery
PostGIS
Docker
AWS
CI/CD
Kafka
Event-driven processing
```

only when those technologies solve a real requirement.

The project should remain **simple enough to build, strong enough to demonstrate real backend engineering, and structured enough to serve as an SDE2 system-design portfolio project.**

---

# 57. Recommended Implementation Order

The implementation sequence is:

```text
1. Accounts
       ↓
2. Physiotherapist
       ↓
3. Services
       ↓
4. Availability
       ↓
5. Appointments
       ↓
6. Payments
       ↓
7. Notifications
       ↓
8. Reviews
       ↓
9. Admin
       ↓
10. Redis
       ↓
11. Celery
       ↓
12. Docker
       ↓
13. AWS
       ↓
14. Performance Optimization
       ↓
15. Advanced System Design
```

**Current position:**

```text
Accounts
   ↓
Physiotherapist  ← NEXT
   ↓
Services
   ↓
Availability
   ↓
Appointments
```

This document should be treated as the **master project scope**. Individual module documents can then describe the detailed implementation of each module without changing the overall project direction.
