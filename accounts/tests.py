from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.dal.account_dal import PatientDal, UserDal
from accounts.enums import UserRole


class PatientProfileViewTests(APITestCase):

    def setUp(self):
        self.url = reverse("accounts:patient-profile")
        self.patient_user = UserDal.create_user(
            email="patient@example.com", password="Test@12345", first_name="Rahul",
            last_name="Sharma", phone_number="9876543210", role=UserRole.PATIENT.value,
        )
        PatientDal.create_patient(user=self.patient_user, city="Delhi", gender="Male")

    def test_patient_gets_own_profile(self):
        self.client.force_authenticate(self.patient_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "patient@example.com")
        self.assertEqual(response.data["city"], "Delhi")
        self.assertIsNone(response.data["date_of_birth"])

    def test_unauthenticated_is_rejected(self):
        response = self.client.get(self.url)
        self.assertIn(response.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

    def test_physiotherapist_is_forbidden(self):
        physio = UserDal.create_user(
            email="physio@example.com", password="Test@12345", first_name="Priya",
            last_name="Yadav", phone_number="", role=UserRole.PHYSIOTHERAPIST.value,
        )
        self.client.force_authenticate(physio)
        self.assertEqual(self.client.get(self.url).status_code, status.HTTP_403_FORBIDDEN)

    def test_patient_without_profile_gets_404(self):
        user = UserDal.create_user(
            email="noprofile@example.com", password="Test@12345", first_name="X",
            last_name="Y", phone_number="", role=UserRole.PATIENT.value,
        )
        self.client.force_authenticate(user)
        self.assertEqual(self.client.get(self.url).status_code, status.HTTP_404_NOT_FOUND)
