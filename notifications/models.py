from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.utils import timezone
from notifications.utils import send_to_user


class Notification(models.Model):
    added = models.DateTimeField(default=timezone.now)
    title = models.CharField(max_length=255)
    description = models.TextField()
    data = models.JSONField(blank=True, null=True)
    users = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return self.title


@receiver(m2m_changed, sender=Notification.users.through)
def users_changed(sender, instance, action, reverse, model, pk_set, **kwargs):
    """
    Quand des utilisateurs sont ajoutés à une notification,
    on crée les UserNotification et on envoie la notification via send_to_user.
    """
    if action == "post_add":
        users = instance.users.all()
        print(f"Utilisateurs associés à la notification ({instance}): {users}")

        for user in users:
            UserNotification.objects.create(user=user, notification=instance)
            send_to_user(user.username, instance.title, instance.description, instance.data)


class UserNotification(models.Model):
    """
    Table intermédiaire pour suivre si un utilisateur a lu une notification.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE)
    read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.notification.title}"
