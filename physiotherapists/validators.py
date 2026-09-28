from decimal import Decimal, InvalidOperation

from rest_framework.exceptions import ValidationError

# Fields a physiotherapist may change through the general profile API.
# email, role, verification_status and license_number are deliberately excluded.
UPDATABLE_FIELDS = {"bio", "experience_years", "consultation_fee", "latitude", "longitude"}


def _to_decimal(value, field_label):
    # bool is a subclass of int, so reject it explicitly
    if isinstance(value, bool):
        raise ValidationError({"error": f"{field_label} must be a valid number."})
    try:
        number = Decimal(str(value).strip())
    except (InvalidOperation, TypeError, ValueError):
        raise ValidationError({"error": f"{field_label} must be a valid number."})
    if not number.is_finite():
        raise ValidationError({"error": f"{field_label} must be a valid number."})
    return number


def validate_profile_update(data):
    if not data:
        raise ValidationError({"error": "No fields provided to update."})

    not_allowed = sorted(set(data.keys()) - UPDATABLE_FIELDS)
    if not_allowed:
        raise ValidationError({"error": f"These fields cannot be updated: {', '.join(not_allowed)}."})

    validated_data = {}

    if "bio" in data:
        bio = data.get("bio")
        if bio is None:
            bio = ""
        if not isinstance(bio, str):
            raise ValidationError({"error": "Bio must be text."})
        validated_data["bio"] = bio.strip()

    if "experience_years" in data:
        experience_years = data.get("experience_years")
        if isinstance(experience_years, bool):
            raise ValidationError({"error": "Experience years must be a valid number."})
        try:
            experience_years = int(experience_years)
        except (TypeError, ValueError):
            raise ValidationError({"error": "Experience years must be a valid number."})
        if experience_years < 0:
            raise ValidationError({"error": "Experience years cannot be negative."})
        validated_data["experience_years"] = experience_years

    if "consultation_fee" in data:
        consultation_fee = data.get("consultation_fee")
        if consultation_fee is None or consultation_fee == "":
            raise ValidationError({"error": "Consultation fee cannot be empty."})
        consultation_fee = _to_decimal(consultation_fee, "Consultation fee")
        if consultation_fee < 0:
            raise ValidationError({"error": "Consultation fee cannot be negative."})
        # matches DecimalField(max_digits=10, decimal_places=2)
        if consultation_fee >= Decimal("100000000"):
            raise ValidationError({"error": "Consultation fee is too large."})
        validated_data["consultation_fee"] = consultation_fee.quantize(Decimal("0.01"))

    if "latitude" in data or "longitude" in data:
        if "latitude" not in data or "longitude" not in data:
            raise ValidationError({"error": "Latitude and longitude must be provided together."})

        latitude = data.get("latitude")
        longitude = data.get("longitude")

        # Sending both as null clears the location
        if latitude is None and longitude is None:
            validated_data["latitude"] = None
            validated_data["longitude"] = None
        elif latitude is None or longitude is None:
            raise ValidationError({"error": "Latitude and longitude must be provided together."})
        else:
            latitude = _to_decimal(latitude, "Latitude")
            longitude = _to_decimal(longitude, "Longitude")
            if not Decimal("-90") <= latitude <= Decimal("90"):
                raise ValidationError({"error": "Latitude must be between -90 and 90."})
            if not Decimal("-180") <= longitude <= Decimal("180"):
                raise ValidationError({"error": "Longitude must be between -180 and 180."})
            validated_data["latitude"] = latitude.quantize(Decimal("0.000001"))
            validated_data["longitude"] = longitude.quantize(Decimal("0.000001"))

    return validated_data
