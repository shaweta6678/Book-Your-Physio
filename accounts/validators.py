from rest_framework.exceptions import ValidationError

from .enums import UserRole
from .models import Physiotherapist, User


def validate_registration_data(data):
    required_fields = {
        "first_name": data.get("first_name"),
        "last_name": data.get("last_name"),
        "email": data.get("email"),
        "password": data.get("password"),
        "role": data.get("role"),
    }
    for field_name, value in required_fields.items():
        if not value:
            raise ValidationError({"error": f"{field_name.replace('_', ' ').title()} is required."})

    email = required_fields["email"].lower().strip()
    if User.objects.filter(email=email).exists():
        raise ValidationError({"error": "User with this email already exists."})

    allowed_roles = {UserRole.PATIENT.value, UserRole.PHYSIOTHERAPIST.value}
    role = required_fields["role"]
    if role not in allowed_roles:
        raise ValidationError({"error": "Invalid role."})

    validated_data = {
        **required_fields,
        "email": email,
        # phone_number is blank=True but not null=True, so default to ""
        "phone_number": data.get("phone_number") or "",
    }

    if role == UserRole.PHYSIOTHERAPIST.value:
        license_number = data.get("license_number")
        bio = data.get("bio")
        experience_years = data.get("experience_years")
        consultation_fee = data.get("consultation_fee")

        if not license_number:
            raise ValidationError({"error": "License number is required."})
        if not experience_years:
            raise ValidationError({"error": "Experience years is required."})
        if consultation_fee is None or consultation_fee == "":
            raise ValidationError({"error": "Consultation fee is required."})

        license_number = str(license_number).strip()
        if not license_number:
            raise ValidationError({"error": "License number is required."})
        if Physiotherapist.objects.filter(license_number=license_number).exists():
            raise ValidationError({"error": "License number already exists."})

        try:
            experience_years = int(experience_years)
        except (TypeError, ValueError):
            raise ValidationError({"error": "Experience years must be a valid number."})
        if experience_years < 0:
            raise ValidationError({"error": "Experience years cannot be negative."})

        try:
            consultation_fee = float(consultation_fee)
        except (TypeError, ValueError):
            raise ValidationError({"error": "Consultation fee must be a valid number."})
        if consultation_fee < 0:
            raise ValidationError({"error": "Consultation fee cannot be negative."})

        validated_data.update(
            {
                "license_number": license_number,
                "bio": bio or "",
                "experience_years": experience_years,
                "consultation_fee": consultation_fee,
            }
        )

    return validated_data
