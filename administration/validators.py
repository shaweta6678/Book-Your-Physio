from rest_framework.exceptions import ValidationError

from accounts.enums import VerificationStatus


def validate_status_filter(value):
    if value is None or value == "":
        return VerificationStatus.PENDING.value
    normalised = str(value).strip().upper()
    allowed = {status.value for status in VerificationStatus}
    if normalised not in allowed:
        raise ValidationError({"error": f"Status must be one of: {', '.join(sorted(allowed))}."})
    return normalised


def validate_rejection(data):
    reason = data.get("reason")
    if reason is None or not isinstance(reason, str) or not reason.strip():
        raise ValidationError({"error": "Rejection reason is required."})
    return {"reason": reason.strip()}
