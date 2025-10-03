from django.db import models
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
import datetime
from django.utils import timezone
from django.db.models.signals import post_save
import os


def get_leave_upload_path(instance, filename):
    username = instance.user.username.replace(".", "_")
    today = datetime.datetime.today().date()
    file_extension = filename.split(".")[-1]
    file_name = f"leave_{instance.id}-{today}.{file_extension}"
    return os.path.join("leaves", username, file_name)


def get_absence_upload_path(instance, filename):
    username = instance.user.username.replace(".", "_")
    today = datetime.datetime.today().date()
    file_extension = filename.split(".")[-1]
    file_name = f"absence_{instance.id}-{today}.{file_extension}"
    return os.path.join("leaves", username, file_name)


class AbsenceType(models.Model):
    description = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.description


class ApprovalTypes(models.TextChoices):
    WAITING = ("WAITING", _("Waiting"))
    REFUSED = ("REFUSED", _("Refused"))
    ACCEPTED = ("ACCEPTED", _("Accepted"))


class Absence(models.Model):
    # Foreign Keys
    absence_type = models.ForeignKey(
        AbsenceType, null=True, blank=True, on_delete=models.SET_NULL
    )
    approval_user = models.ForeignKey(
        "auth.User",
        related_name="absence_approval_user",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    user = models.ForeignKey("accounts.UserProxy", on_delete=models.CASCADE)
    reason = models.CharField(max_length=255, blank=True, null=True)
    observation = models.CharField(max_length=255, blank=True, null=True)
    date = models.DateField()
    approved = models.CharField(
        max_length=10, choices=ApprovalTypes.choices, default="WAITING"
    )
    approval_date = models.DateField(null=True, blank=True)
    attachement = models.FileField(
        blank=True, null=True, upload_to=get_absence_upload_path
    )
    attachement_upload_date = models.DateTimeField(null=True, blank=True)

    # Auto Added Fields
    added = models.DateField(default=timezone.now)

    class Meta:
        permissions = [
            (
                "approve_absence",
                "Can decide whether the absence is accepted or refused",
            ),
        ]

    def save(self, *args, **kwargs):
        if self.pk:
            db_instance = Absence.objects.get(id=self.id)
            if db_instance.approved != self.approved:
                self.approval_date = timezone.now()

            if not db_instance.attachement and self.attachement:
                self.attachement_upload_date = timezone.now()

        return super(Absence, self).save(*args, **kwargs)


class LeaveType(models.Model):
    description = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.description


from django.conf import settings

class Leave(models.Model):
    # Foreign Keys
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    author = models.ForeignKey(
        "auth.User", related_name="author", on_delete=models.CASCADE
    )
    approval_user = models.ForeignKey(
        "auth.User",
        related_name="approval_user",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    user = models.ForeignKey("accounts.UserProxy", on_delete=models.CASCADE)

    start_date = models.DateField()
    end_date = models.DateField()
    approved = models.CharField(
        max_length=10, choices=ApprovalTypes.choices, default="WAITING"
    )
    approval_date = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    observation = models.CharField(max_length=255, blank=True, null=True)
    attachement = models.FileField(
        blank=True, null=True, upload_to=get_leave_upload_path
    )

    # Auto Added Fields
    added = models.DateField(default=timezone.now)

    def save(self, *args, **kwargs):
        if self.pk:
            db_instance = Leave.objects.get(id=self.id)
            if db_instance.approved != self.approved:
                self.approval_date = timezone.now()

            if not db_instance.attachement and self.attachement:
                self.attachement_upload_date = timezone.now()

        return super(Leave, self).save(*args, **kwargs)


"""
        annuel, sans solde, autre
       ("maladie","maladie"), ("recuperation","recuperation"), ("marriage","marriage") ,
        ("naissance","naissance"), ("maternite","maternite"), ("deces","deces") , ("autre","autre") 
"""


@receiver(post_save, sender=Leave)
def delete_absences_on_create(sender, instance, created, **kwargs):
    if created:
        absences_within_leave_period = Absence.objects.filter(
            date__range=[instance.start_date, instance.end_date], user=instance.user
        )
        if absences_within_leave_period.exists():
            absences_within_leave_period.delete()
            print("Absence deleted")


from django.core.mail import send_mail  # Add this import


@receiver(post_save, sender=Leave)
def send_leave_request_email(sender, instance, created, **kwargs):
    if created:
        # Define the email subject and message
        subject = f"New Leave Request from {instance.user}"
        message = (
            f"A new leave request has been submitted by {instance.user}. \n\n"
            f"Leave Type: {instance.leave_type}\n"
            f"Start Date: {instance.start_date}\n"
            f"End Date: {instance.end_date}\n"
            f"Observation: {instance.observation}\n\n"
            "Please review and take necessary actions."
        )
        from_email = settings.DEFAULT_FROM_EMAIL  # Use your default sender email
        recipient_list = ['r.boutitaou@liliumpharma.com']
        
        # Send the email
        #send_mail(subject, message, from_email, recipient_list)




from django.db import models


def get_holiday_video_upload_path(instance, filename):
    return f"holidays/videos/{instance.name}/{filename}"


class Occasion(models.Model):
    OCCASION_TYPES = [
        ("RELIGIOUS", "Religious"),
        ("NATIONAL", "National"),
    ]

    name = models.CharField(max_length=255)
    name_arabe = models.CharField(max_length=255)
    occasion_type = models.CharField(max_length=10, choices=OCCASION_TYPES)
    date = models.DateField()
    video = models.FileField(
        upload_to=get_holiday_video_upload_path, blank=True, null=True
    )  # Champ pour associer une vidéo à l'occasion

    def __str__(self):
        return f"{self.name} ({self.get_occasion_type_display()})"

    class Meta:
        verbose_name = "Occasion"
        verbose_name_plural = "Occasions"

