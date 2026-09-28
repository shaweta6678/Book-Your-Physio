from django.conf import settings
from django.db import models

from .enums import NotificationType


class Notification(models.Model):
    # One row per recipient. `data` is a snapshot for the client (e.g. physiotherapist_id),
    # so this app never needs a foreign key into other apps.

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="notifications")
    notification_type = models.CharField(max_length=50,choices=[(t.value, t.name) for t in NotificationType])
    title = models.CharField(max_length=200)
    message = models.TextField(blank=True)
    data = models.JSONField(default=dict, blank=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [
            models.Index(fields=["recipient", "is_read", "-created_at"]),
        ]
