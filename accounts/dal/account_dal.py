from django.db.models import Q

from accounts.enums import UserRole
from accounts.models import Patient, Physiotherapist, PhysiotherapistVerification, User


class UserDal:
    @staticmethod
    def create_user(email, password, first_name, last_name, phone_number, role):
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            role=role,
        )
        return user

    @staticmethod
    def get_user_by_email(email):
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return None

    @staticmethod
    def list_admins():
        # createsuperuser leaves role at the PATIENT default, so superusers count as admins too
        return list(
            User.objects.filter(is_active=True).filter(
                Q(role=UserRole.ADMIN.value) | Q(is_superuser=True)
            )
        )

    @staticmethod
    def update_user(user, **kwargs):
        for field, value in kwargs.items():
            setattr(user, field, value)
        user.save()
        return user
    


class PatientDal:
    @staticmethod
    def create_patient(user, **kwargs):
        patient = Patient.objects.create(user=user, **kwargs)
        return patient

    @staticmethod
    def get_patient_by_user(user):
        try:
            return Patient.objects.get(user=user)
        except Patient.DoesNotExist:
            return None

    @staticmethod
    def update_patient(patient, **kwargs):
        for field, value in kwargs.items():
            setattr(patient, field, value)
        patient.save()
        return patient


class PhysiotherapistDal:
    @staticmethod
    def create_physiotherapist(user, **kwargs):
        physiotherapist = Physiotherapist.objects.create(user=user, **kwargs)
        return physiotherapist

    @staticmethod
    def get_physiotherapist_by_user(user):
        try:
            return Physiotherapist.objects.get(user=user)
        except Physiotherapist.DoesNotExist:
            return None

    @staticmethod
    def get_by_id(physiotherapist_id):
        try:
            return (
                Physiotherapist.objects.select_related("user")
                .prefetch_related("verification_history__reviewed_by")
                .get(id=physiotherapist_id)
            )
        except Physiotherapist.DoesNotExist:
            return None

    @staticmethod
    def get_by_id_for_update(physiotherapist_id):
        # Must be called inside transaction.atomic(); locks the row until commit
        try:
            return Physiotherapist.objects.select_for_update().get(id=physiotherapist_id)
        except Physiotherapist.DoesNotExist:
            return None

    @staticmethod
    def list_by_status(verification_status):
        return list(
            Physiotherapist.objects.select_related("user")
            .prefetch_related("verification_history__reviewed_by")
            .filter(verification_status=verification_status)
            .order_by("created_at")
        )

    @staticmethod
    def update_physiotherapist(physiotherapist, **kwargs):
        for field, value in kwargs.items():
            setattr(physiotherapist, field, value)
        physiotherapist.save()
        return physiotherapist


class PhysiotherapistVerificationDal:
    @staticmethod
    def create_verification(physiotherapist, status, reviewed_by, rejection_reason=""):
        verification = PhysiotherapistVerification.objects.create(
            physiotherapist=physiotherapist,
            status=status,
            reviewed_by=reviewed_by,
            rejection_reason=rejection_reason,
        )
        return verification

    @staticmethod
    def get_latest_for_physiotherapist(physiotherapist):
        # Meta.ordering puts the newest review first
        return PhysiotherapistVerification.objects.filter(physiotherapist=physiotherapist).first()
