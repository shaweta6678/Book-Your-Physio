from rest_framework.permissions import BasePermission

from accounts.dal.account_dal import PhysiotherapistDal
from accounts.enums import UserRole, VerificationStatus


class IsPhysiotherapist(BasePermission):
    message = "Only physiotherapists can access this resource."

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and user.role == UserRole.PHYSIOTHERAPIST.value
        )


class IsVerifiedPhysiotherapist(IsPhysiotherapist):
    # For patient data, appointments, availability, booking: everything except the physio's own profile
    message = "Your profile is awaiting admin verification."

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            # Permission instances are created per request, so this doesn't leak between requests
            self.message = IsPhysiotherapist.message
            return False
        physiotherapist = PhysiotherapistDal.get_physiotherapist_by_user(request.user)
        return bool(
            physiotherapist
            and physiotherapist.verification_status == VerificationStatus.VERIFIED.value
        )
