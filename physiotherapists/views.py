from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .permissions import IsPhysiotherapist
from .services import PhysiotherapistProfileService


class MyPhysiotherapistProfileView(APIView):
    permission_classes = [IsPhysiotherapist]

    def get(self, request):
        profile = PhysiotherapistProfileService.get_my_profile(request.user)
        return Response(profile, status=status.HTTP_200_OK)

    def patch(self, request):
        profile = PhysiotherapistProfileService.update_my_profile(request.user, request.data)
        return Response(
            {
                "message": "Profile updated successfully.",
                "profile": profile,
            },
            status=status.HTTP_200_OK,
        )
