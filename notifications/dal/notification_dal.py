from django.utils import timezone

from notifications.models import Notification


class NotificationDal:
    @staticmethod
    def create_many(recipients, notification_type, title, message, data):
        notifications = [
            Notification(
                recipient=recipient,
                notification_type=notification_type,
                title=title,
                message=message,
                data=data,
            )
            for recipient in recipients
        ]
        return Notification.objects.bulk_create(notifications)

    @staticmethod
    def list_for_user(user, is_read=None):
        notifications = Notification.objects.filter(recipient=user)
        if is_read is not None:
            notifications = notifications.filter(is_read=is_read)
        return list(notifications)

    @staticmethod
    def get_for_user(user, notification_id):
        try:
            return Notification.objects.get(id=notification_id, recipient=user)
        except Notification.DoesNotExist:
            return None

    @staticmethod
    def unread_count(user):
        return Notification.objects.filter(recipient=user, is_read=False).count()

    @staticmethod
    def mark_read(notification):
        if not notification.is_read:
            notification.is_read = True
            notification.read_at = timezone.now()
            notification.save(update_fields=["is_read", "read_at"])
        return notification

    @staticmethod
    def mark_read_by_type_and_data(notification_type, **data):
        # Marks every recipient's unread notification of this type whose data matches,
        # e.g. mark_read_by_type_and_data(TYPE, physiotherapist_id=12)
        lookups = {f"data__{key}": value for key, value in data.items()}
        return Notification.objects.filter(
            notification_type=notification_type,
            is_read=False,
            **lookups,
        ).update(is_read=True, read_at=timezone.now())
