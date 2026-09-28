from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .permissions import IsPlatformAdmin
from .services import PhysiotherapistVerificationService
from .validators import validate_status_filter


class AdminPhysiotherapistListView(APIView):
    permission_classes = [IsPlatformAdmin]

    def get(self, request):
        verification_status = validate_status_filter(request.query_params.get("status"))
        physiotherapists = PhysiotherapistVerificationService().list_physiotherapists(verification_status)
        return Response({"physiotherapists": physiotherapists}, status=status.HTTP_200_OK)


class AdminPhysiotherapistDetailView(APIView):
    permission_classes = [IsPlatformAdmin]

    def get(self, request, physiotherapist_id):
        profile = PhysiotherapistVerificationService().get_physiotherapist(physiotherapist_id)
        return Response(profile, status=status.HTTP_200_OK)


class ApprovePhysiotherapistView(APIView):
    permission_classes = [IsPlatformAdmin]

    def post(self, request, physiotherapist_id):
        profile = PhysiotherapistVerificationService().approve(request.user, physiotherapist_id)
        return Response(
            {
                "message": "Physiotherapist approved.",
                "profile": profile,
            },
            status=status.HTTP_200_OK,
        )


class RejectPhysiotherapistView(APIView):
    permission_classes = [IsPlatformAdmin]

    def post(self, request, physiotherapist_id):
        profile = PhysiotherapistVerificationService().reject(request.user, physiotherapist_id, request.data)
        return Response(
            {
                "message": "Physiotherapist rejected.",
                "profile": profile,
            },
            status=status.HTTP_200_OK,
        )
