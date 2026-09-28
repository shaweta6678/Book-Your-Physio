from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.dal.account_dal import PatientDal, PhysiotherapistDal, UserDal
from accounts.enums import UserRole, VerificationStatus


class MyPhysiotherapistProfileTests(APITestCase):

    def setUp(self):
        self.url = reverse("physiotherapists:me")

        self.physio_user = UserDal.create_user(
            email="priya@example.com",
            password="secret123",
            first_name="Priya",
            last_name="Mehta",
            phone_number="9876543210",
            role=UserRole.PHYSIOTHERAPIST.value,
        )
        self.physio = PhysiotherapistDal.create_physiotherapist(
            user=self.physio_user,
            license_number="PT-2026-001",
            bio="Experienced physiotherapist",
            experience_years=5,
            consultation_fee=800,
        )

        self.patient_user = UserDal.create_user(
            email="rahul@example.com",
            password="secret123",
            first_name="Rahul",
            last_name="Sharma",
            phone_number="",
            role=UserRole.PATIENT.value,
        )
        PatientDal.create_patient(user=self.patient_user)

    def authenticate(self, user):
        token = RefreshToken.for_user(user).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    # ---------- GET /me/ ----------

    def test_get_requires_authentication(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patient_cannot_access(self):
        self.authenticate(self.patient_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_physiotherapist_gets_own_profile(self):
        self.authenticate(self.physio_user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "id": self.physio.id,
                "first_name": "Priya",
                "last_name": "Mehta",
                "email": "priya@example.com",
                "phone_number": "9876543210",
                "license_number": "PT-2026-001",
                "bio": "Experienced physiotherapist",
                "experience_years": 5,
                "consultation_fee": "800.00",
                "verification_status": VerificationStatus.PENDING.value,
                "latitude": None,
                "longitude": None,
            },
        )

    def test_physiotherapist_without_profile_gets_404(self):
        orphan = UserDal.create_user(
            email="orphan@example.com",
            password="secret123",
            first_name="No",
            last_name="Profile",
            phone_number="",
            role=UserRole.PHYSIOTHERAPIST.value,
        )
        self.authenticate(orphan)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ---------- PATCH /me/ ----------

    def test_physiotherapist_updates_profile(self):
        self.authenticate(self.physio_user)
        response = self.client.patch(
            self.url,
            {
                "bio": "Sports rehabilitation specialist",
                "experience_years": 6,
                "consultation_fee": 900,
                "latitude": 28.4595,
                "longitude": 77.0266,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        profile = response.json()["profile"]
        self.assertEqual(profile["bio"], "Sports rehabilitation specialist")
        self.assertEqual(profile["experience_years"], 6)
        self.assertEqual(profile["consultation_fee"], "900.00")
        self.assertEqual(profile["latitude"], "28.459500")
        self.assertEqual(profile["longitude"], "77.026600")

        self.physio.refresh_from_db()
        self.assertEqual(self.physio.experience_years, 6)
        self.assertEqual(str(self.physio.latitude), "28.459500")

    def test_partial_update_keeps_other_fields(self):
        self.authenticate(self.physio_user)
        response = self.client.patch(self.url, {"experience_years": 0}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.physio.refresh_from_db()
        self.assertEqual(self.physio.experience_years, 0)
        self.assertEqual(self.physio.bio, "Experienced physiotherapist")

    def test_protected_fields_cannot_be_updated(self):
        self.authenticate(self.physio_user)
        for field, value in [
            ("email", "hacker@example.com"),
            ("role", UserRole.ADMIN.value),
            ("verification_status", VerificationStatus.VERIFIED.value),
            ("license_number", "PT-FAKE"),
            ("user_id", self.patient_user.id),
        ]:
            response = self.client.patch(self.url, {field: value}, format="json")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, field)

        self.physio.refresh_from_db()
        self.assertEqual(self.physio.verification_status, VerificationStatus.PENDING.value)
        self.assertEqual(self.physio.license_number, "PT-2026-001")

    def test_invalid_values_are_rejected(self):
        self.authenticate(self.physio_user)
        for payload in [
            {},
            {"experience_years": -1},
            {"experience_years": "abc"},
            {"consultation_fee": -5},
            {"consultation_fee": "abc"},
            {"consultation_fee": None},
            {"latitude": 28.45},
            {"latitude": 91, "longitude": 77},
            {"latitude": 28, "longitude": 181},
            {"latitude": 28, "longitude": None},
        ]:
            response = self.client.patch(self.url, payload, format="json")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, payload)
            self.assertIn("error", response.json())

    def test_location_can_be_cleared(self):
        self.physio.latitude = "28.459500"
        self.physio.longitude = "77.026600"
        self.physio.save()

        self.authenticate(self.physio_user)
        response = self.client.patch(self.url, {"latitude": None, "longitude": None}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.physio.refresh_from_db()
        self.assertIsNone(self.physio.latitude)
        self.assertIsNone(self.physio.longitude)

    def test_patient_cannot_update(self):
        self.authenticate(self.patient_user)
        response = self.client.patch(self.url, {"bio": "hi"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
