from rest_framework.exceptions import NotFound

from accounts.dal.account_dal import PhysiotherapistDal

from .validators import validate_profile_update


class PhysiotherapistProfileService:

    @staticmethod
    def _get_profile_or_404(user):
        physiotherapist = PhysiotherapistDal.get_physiotherapist_by_user(user)
        if physiotherapist is None:
            raise NotFound({"error": "Physiotherapist profile not found."})
        return physiotherapist

    @staticmethod
    def _decimal_to_str(value):
        # DRF's JSON encoder turns Decimal into float; keep money and coordinates exact
        return None if value is None else str(value)

    @staticmethod
    def to_dict(physiotherapist):
        user = physiotherapist.user
        return {
            "id": physiotherapist.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "phone_number": user.phone_number,
            "license_number": physiotherapist.license_number,
            "bio": physiotherapist.bio,
            "experience_years": physiotherapist.experience_years,
            "consultation_fee": PhysiotherapistProfileService._decimal_to_str(physiotherapist.consultation_fee),
            "verification_status": physiotherapist.verification_status,
            "latitude": PhysiotherapistProfileService._decimal_to_str(physiotherapist.latitude),
            "longitude": PhysiotherapistProfileService._decimal_to_str(physiotherapist.longitude),
        }

    @staticmethod
    def get_my_profile(user):
        physiotherapist = PhysiotherapistProfileService._get_profile_or_404(user)
        return PhysiotherapistProfileService.to_dict(physiotherapist)

    @staticmethod
    def update_my_profile(user, data):
        physiotherapist = PhysiotherapistProfileService._get_profile_or_404(user)
        validated_data = validate_profile_update(data)
        physiotherapist = PhysiotherapistDal.update_physiotherapist(physiotherapist, **validated_data)
        return PhysiotherapistProfileService.to_dict(physiotherapist)
