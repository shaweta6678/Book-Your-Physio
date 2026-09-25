from accounts.models import Patient, Physiotherapist, User


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
    def update_physiotherapist(physiotherapist, **kwargs):
        for field, value in kwargs.items():
            setattr(physiotherapist, field, value)
        physiotherapist.save()
        return physiotherapist
