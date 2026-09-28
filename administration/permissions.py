from rest_framework.permissions import BasePermission

from accounts.enums import UserRole


class IsPlatformAdmin(BasePermission):
    message = "Only admins can access this resource."

    def has_permission(self, request, view):
        user = request.user
        # createsuperuser leaves role at the PATIENT default, so superusers count as admins too
        return bool(
            user
            and user.is_authenticated
            and (user.role == UserRole.ADMIN.value or user.is_superuser)
        )
