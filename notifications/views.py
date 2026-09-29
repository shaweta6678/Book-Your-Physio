from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .services import NotificationInboxService
from .validators import validate_is_read_filter


class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        is_read = validate_is_read_filter(request.query_params.get("is_read"))
        notifications = NotificationInboxService.list_notifications(request.user, is_read=is_read)
        return Response({"notifications": notifications}, status=status.HTTP_200_OK)


class UnreadNotificationCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        count = NotificationInboxService.unread_count(request.user)
        return Response({"unread_count": count}, status=status.HTTP_200_OK)


class MarkNotificationReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, notification_id):
        notification = NotificationInboxService.mark_read(request.user, notification_id)
        return Response(
            {
                "message": "Notification marked as read.",
                "notification": notification,
            },
            status=status.HTTP_200_OK,
        )
