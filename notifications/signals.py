# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Notification, UserNotification

@receiver(post_save, sender=Notification)
def create_user_notifications(sender, instance, created, **kwargs):
    if created:
        for user in instance.users.all():
            UserNotification.objects.create(user=user, notification=instance)
