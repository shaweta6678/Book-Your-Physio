from rest_framework.exceptions import NotFound

from accounts.dal.account_dal import UserDal
from notifications.channels import DatabaseChannel
from notifications.dal.notification_dal import NotificationDal
from notifications.enums import NotificationType


class NotificationService:
    """Sends one notification through every configured channel."""

    def __init__(self, channels=None):
        self.channels = channels or [DatabaseChannel()]

    def notify(self, recipients, notification_type, title, message="", data=None):
        recipients = list(recipients)
        if not recipients:
            return
        for channel in self.channels:
            channel.send(recipients, notification_type.value, title, message, data or {})


class AdminNotificationService:
    """Decides what admins and physiotherapists are told about verification, not how it is delivered."""

    def __init__(self, notification_service=None, admin_provider=None):
        self.notification_service = notification_service or NotificationService()
        self.admin_provider = admin_provider or UserDal.list_admins

    @staticmethod
    def _full_name(user):
        return f"{user.first_name} {user.last_name}".strip()

    def physiotherapist_registered(self, physiotherapist):
        user = physiotherapist.user
        name = self._full_name(user)
        self.notification_service.notify(
            recipients=self.admin_provider(),
            notification_type=NotificationType.PHYSIOTHERAPIST_REGISTERED,
            title="New Physiotherapist Registration",
            message=f"{name} registered and is awaiting review.",
            data={
                "physiotherapist_id": physiotherapist.id,
                "name": name,
                "license_number": physiotherapist.license_number,
                "experience_years": physiotherapist.experience_years,
                "registered_at": physiotherapist.created_at.isoformat(),
            },
        )

    def resolve_registration(self, physiotherapist):
        # Once one admin decides, the card is stale for every admin
        NotificationDal.mark_read_by_type_and_data(
            NotificationType.PHYSIOTHERAPIST_REGISTERED.value,
            physiotherapist_id=physiotherapist.id,
        )

    def physiotherapist_verified(self, physiotherapist):
        self.notification_service.notify(
            recipients=[physiotherapist.user],
            notification_type=NotificationType.PHYSIOTHERAPIST_VERIFIED,
            title="Profile verified",
            message="Your profile has been verified. You now have full access to the platform.",
            data={"physiotherapist_id": physiotherapist.id},
        )

    def physiotherapist_rejected(self, physiotherapist, reason):
        self.notification_service.notify(
            recipients=[physiotherapist.user],
            notification_type=NotificationType.PHYSIOTHERAPIST_REJECTED,
            title="Profile rejected",
            message=f"Your profile was not approved. Reason: {reason}",
            data={"physiotherapist_id": physiotherapist.id, "reason": reason},
        )


class NotificationInboxService:
    """A user's own notifications."""

    @staticmethod
    def to_dict(notification):
        return {
            "id": notification.id,
            "notification_type": notification.notification_type,
            "title": notification.title,
            "message": notification.message,
            "data": notification.data,
            "is_read": notification.is_read,
            "read_at": notification.read_at,
            "created_at": notification.created_at,
        }

    @staticmethod
    def list_notifications(user, is_read=None):
        notifications = NotificationDal.list_for_user(user, is_read=is_read)
        return [NotificationInboxService.to_dict(n) for n in notifications]

    @staticmethod
    def unread_count(user):
        return NotificationDal.unread_count(user)

    @staticmethod
    def mark_read(user, notification_id):
        # Another user's notification is reported as missing, not forbidden
        notification = NotificationDal.get_for_user(user, notification_id)
        if notification is None:
            raise NotFound({"error": "Notification not found."})
        notification = NotificationDal.mark_read(notification)
        return NotificationInboxService.to_dict(notification)
