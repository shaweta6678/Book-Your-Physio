from django.contrib.auth import get_user_model,authenticate
from django.db import transaction

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken


from accounts.validators import validate_registration_data

from .enums import UserRole
from .models import Patient, Physiotherapist
from accounts.dal.account_dal import UserDal, PatientDal, PhysiotherapistDal

User = get_user_model()


class UserRegistrationView(APIView):

    def post(self, request):

        # Common user fields
        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name")
        email = request.data.get("email")
        phone_number = request.data.get("phone_number")
        password = request.data.get("password")
        role = request.data.get("role")

        # Physiotherapist-specific fields
        if role == UserRole.PHYSIOTHERAPIST.value:
            license_number = request.data.get("license_number")
            bio = request.data.get("bio")
            experience_years = request.data.get("experience_years")
            consultation_fee = request.data.get("consultation_fee")
            if not license_number or not experience_years or not consultation_fee:
                return Response(
                    {
                        "error": "License number, experience years, and consultation fee are required for physiotherapists."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # -----------------------------------------
        # Validate common required fields
        # -----------------------------------------
        validated_data = validate_registration_data(
            request.data
        )
       
        # -----------------------------------------
        # Validate physiotherapist fields
        # -----------------------------------------

        if role == UserRole.PHYSIOTHERAPIST.value:

            license_number = license_number.strip()

            # Check duplicate license number
            if Physiotherapist.objects.filter(license_number=license_number).exists():
                return Response(
                    {
                        "error": "License number already exists."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Convert experience to integer
            try:
                experience_years = int(experience_years)
            except (TypeError, ValueError):
                return Response(
                    {
                        "error": "Experience years must be a valid number."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if experience_years < 0:
                return Response(
                    {
                        "error": "Experience years cannot be negative."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Convert consultation fee to decimal
            try:
                consultation_fee = float(consultation_fee)
            except (TypeError, ValueError):
                return Response(
                    {
                        "error": "Consultation fee must be a valid number."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if consultation_fee < 0:
                return Response(
                    {
                        "error": "Consultation fee cannot be negative."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # -----------------------------------------
        # Create User + Profile atomically
        # -----------------------------------------

        with transaction.atomic():

            user = UserDal.create_user(
                email=validated_data["email"],
                password=validated_data["password"],
                first_name=validated_data["first_name"],
                last_name=validated_data["last_name"],
                phone_number=validated_data.get("phone_number"),
                role=validated_data["role"],
            )

            # -------------------------------------
            # Create Patient profile
            # -------------------------------------

            if role == UserRole.PATIENT.value:
                PatientDal.create_patient(user=user)

            # -------------------------------------
            # Create Physiotherapist profile
            # -------------------------------------

            elif role == UserRole.PHYSIOTHERAPIST.value:

                PhysiotherapistDal.create_physiotherapist(user=user, 
                                                          license_number=license_number, 
                                                          bio=bio or "", experience_years=experience_years, 
                                                          consultation_fee=consultation_fee)

        # -----------------------------------------
        # Success response
        # -----------------------------------------

        return Response(
            {
                "message": "User registered successfully.",
                "user": {
                    "id": user.id,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "phone_number": user.phone_number,
                    "role": user.role,
                },
            },
            status=status.HTTP_201_CREATED,
        )

class UserLoginView(APIView):

    def post(self, request):

        email = request.data.get("email")
        password = request.data.get("password")

        if not email:
            return Response({"error": "Email is required."},status=status.HTTP_400_BAD_REQUEST)

        if not password:
            return Response({"error": "Password is required."},status=status.HTTP_400_BAD_REQUEST)

        email = email.lower().strip()

        # Check whether user exists
        user = UserDal.get_user_by_email(email)

        if user is None:
            return Response({"error": "No account found with this email. Please register first."},status=status.HTTP_404_NOT_FOUND)

        # Check password
        user = authenticate(request,email=email,password=password)

        if user is None:
            return Response({ "error": "Invalid password or email"},status=status.HTTP_401_UNAUTHORIZED)

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "message": "Login successful.",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "id": user.id,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "phone_number": user.phone_number,
                    "role": user.role,
                },
            },
            status=status.HTTP_200_OK,
        )

class UserLogoutView(APIView):

    def post(self, request):

        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response({"error": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({"message": "Logout successful."},status=status.HTTP_200_OK)

        except Exception:
            return Response({"error": "Invalid or expired refresh token."},status=status.HTTP_400_BAD_REQUEST)