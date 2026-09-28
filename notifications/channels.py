from notifications.dal.notification_dal import NotificationDal


class NotificationChannel:
    """One way of delivering a notification (database, email, SMS, ...)."""

    def send(self, recipients, notification_type, title, message, data):
        raise NotImplementedError


class DatabaseChannel(NotificationChannel):
    # Writes rows only, so it is safe to call inside the caller's transaction.
    # Channels that call outside services (email, SMS) should wrap their send in
    # transaction.on_commit() so a failure there cannot roll back the caller.

    def send(self, recipients, notification_type, title, message, data):
        NotificationDal.create_many(recipients, notification_type, title, message, data)
