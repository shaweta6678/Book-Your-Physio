from rest_framework.exceptions import ValidationError


def validate_is_read_filter(value):
    # None means "no filter"; the query string only carries text
    if value is None or value == "":
        return None
    normalised = str(value).strip().lower()
    if normalised == "true":
        return True
    if normalised == "false":
        return False
    raise ValidationError({"error": "is_read must be true or false."})
