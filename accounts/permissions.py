from rest_framework.permissions import BasePermission

from accounts.enums import UserRole


class IsPatient(BasePermission):
    message = "Only patients can access this resource."

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and user.role == UserRole.PATIENT.value
        )
