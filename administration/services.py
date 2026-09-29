from django.db import transaction
from rest_framework.exceptions import NotFound

from accounts.dal.account_dal import PhysiotherapistDal, PhysiotherapistVerificationDal
from accounts.enums import VerificationStatus
from notifications.services import AdminNotificationService
from physiotherapists.services import PhysiotherapistProfileService

from .exceptions import Conflict
from .validators import validate_rejection


class PhysiotherapistVerificationService:
    """Admin review of physiotherapist registrations. Only PENDING profiles can be decided."""

    def __init__(self, admin_notification_service=None):
        self.admin_notification_service = admin_notification_service or AdminNotificationService()

    # ---------- serialisation ----------

    @staticmethod
    def _review_to_dict(review):
        reviewer = review.reviewed_by
        return {
            "id": review.id,
            "status": review.status,
            "rejection_reason": review.rejection_reason,
            "reviewed_at": review.reviewed_at,
            "reviewed_by": None if reviewer is None else {
                "id": reviewer.id,
                "first_name": reviewer.first_name,
                "last_name": reviewer.last_name,
                "email": reviewer.email,
            },
        }

    @staticmethod
    def to_dict(physiotherapist, include_history=False):
        # verification_history is prefetched by the DAL and ordered newest first
        history = list(physiotherapist.verification_history.all())
        data = PhysiotherapistProfileService.to_dict(physiotherapist)
        data["registered_at"] = physiotherapist.user.date_joined
        data["latest_review"] = (
            PhysiotherapistVerificationService._review_to_dict(history[0]) if history else None
        )
        if include_history:
            data["verification_history"] = [
                PhysiotherapistVerificationService._review_to_dict(review) for review in history
            ]
        return data

    # ---------- reads ----------

    @staticmethod
    def _get_or_404(physiotherapist_id):
        physiotherapist = PhysiotherapistDal.get_by_id(physiotherapist_id)
        if physiotherapist is None:
            raise NotFound({"error": "Physiotherapist not found."})
        return physiotherapist

    def list_physiotherapists(self, verification_status):
        physiotherapists = PhysiotherapistDal.list_by_status(verification_status)
        return [self.to_dict(physiotherapist) for physiotherapist in physiotherapists]

    def get_physiotherapist(self, physiotherapist_id):
        physiotherapist = self._get_or_404(physiotherapist_id)
        return self.to_dict(physiotherapist, include_history=True)

    # ---------- decisions ----------

    @staticmethod
    def _lock_pending(physiotherapist_id):
        # Row lock: if two admins decide at once, the second sees the new status and gets 409
        physiotherapist = PhysiotherapistDal.get_by_id_for_update(physiotherapist_id)
        if physiotherapist is None:
            raise NotFound({"error": "Physiotherapist not found."})
        if physiotherapist.verification_status != VerificationStatus.PENDING.value:
            raise Conflict({"error": f"Physiotherapist is already {physiotherapist.verification_status}."})
        return physiotherapist

    def _decide(self, admin_user, physiotherapist_id, new_status, rejection_reason=""):
        with transaction.atomic():
            physiotherapist = self._lock_pending(physiotherapist_id)
            PhysiotherapistDal.update_physiotherapist(physiotherapist, verification_status=new_status)
            PhysiotherapistVerificationDal.create_verification(
                physiotherapist=physiotherapist,
                status=new_status,
                reviewed_by=admin_user,
                rejection_reason=rejection_reason,
            )
            self.admin_notification_service.resolve_registration(physiotherapist)
            if new_status == VerificationStatus.VERIFIED.value:
                self.admin_notification_service.physiotherapist_verified(physiotherapist)
            else:
                self.admin_notification_service.physiotherapist_rejected(physiotherapist, rejection_reason)
        return self.get_physiotherapist(physiotherapist_id)

    def approve(self, admin_user, physiotherapist_id):
        return self._decide(admin_user, physiotherapist_id, VerificationStatus.VERIFIED.value)

    def reject(self, admin_user, physiotherapist_id, data):
        validated_data = validate_rejection(data)
        return self._decide(
            admin_user,
            physiotherapist_id,
            VerificationStatus.REJECTED.value,
            rejection_reason=validated_data["reason"],
        )
