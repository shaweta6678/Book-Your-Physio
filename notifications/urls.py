from django.urls import path
from .views import MarkNotificationReadView, NotificationListView, UnreadNotificationCountView

app_name = "notifications"


urlpatterns = [
    path("", NotificationListView.as_view(), name="list"),
    path("unread-count/", UnreadNotificationCountView.as_view(), name="unread-count"),
    path("<int:notification_id>/read/", MarkNotificationReadView.as_view(), name="mark-read"),
]
