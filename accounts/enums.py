from enum import Enum

class UserRole(Enum):
    PATIENT = "PATIENT"
    PHYSIOTHERAPIST = "PHYSIOTHERAPIST"
    ADMIN = "ADMIN"

class VerificationStatus(Enum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"