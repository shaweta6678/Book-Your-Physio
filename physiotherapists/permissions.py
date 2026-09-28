from rest_framework.permissions import BasePermission

from accounts.enums import UserRole


class IsPhysiotherapist(BasePermission):
    message = "Only physiotherapists can access this resource."

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and user.role == UserRole.PHYSIOTHERAPIST.value
        )
