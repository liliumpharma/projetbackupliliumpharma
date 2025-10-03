from datetime import datetime
from django.db import models

from django.contrib.auth.models import User
import datetime
from django.utils import timezone

# from django.core.validators import minValueValidator, maxValueValidator

from regions.models import Commune
import calendar


# class MonthlyPlan(models.Model):
#     user=models.ForeignKey(User,on_delete=models.CASCADE)
#     month=models.IntegerField(validators=[minValueValidator,maxValueValidator])
#     year=models.IntegerField(min=1,max=12)
#     valid=models.BooleanField(default=False)

#     def __str__(self):
#         return f"{self.user} {self.month}-{self.year}"
#     class Meta:
#         unique_together=(user, day)


class Plan(models.Model):
    day = models.DateField()
    # monthly_plan=models.ForeignKey(MonthlyPlan)
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    clients = models.ManyToManyField("medecins.Medecin", blank=True)
    communes = models.ManyToManyField(Commune, blank=True)

    valid_commune = models.BooleanField(default=False)
    commune_validation_date = models.DateTimeField(null=True, blank=True)
    commune_validation_user = models.ForeignKey(
        "auth.User",
        related_name="commune_validated_user",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    commune_request_date = models.DateTimeField(null=True, blank=True)

    valid_clients = models.BooleanField(default=False)
    client_validation_date = models.DateTimeField(null=True, blank=True)
    client_validation_user = models.ForeignKey(
        "auth.User",
        related_name="client_validated_user",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    client_request_date = models.DateTimeField(null=True, blank=True)

    valid_tasks = models.BooleanField(default=False)
    tasks_validation_date = models.DateTimeField(null=True, blank=True)
    tasks_validation_user = models.ForeignKey(
        "auth.User",
        related_name="tasks_validated_user",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    tasks_request_date = models.DateTimeField(null=True, blank=True)

    updatable = models.BooleanField(default=False)
    isfree = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username + " " + str(self.day)

    @property
    def free_day(self):
        # plan_date=datetime.datetime(
        # year=self.day.year,
        # month=self.day.month,
        # day=self.day.day,
        # )
        # return datetime.datetime(self.day.year, self.day.month, self.day.day, 0, 0, 0, 0).datestrftime("%A") in ["Friday", "Saturday"]
        print("**********", self.day.isoweekday())
        print("**************************************************")
        print(calendar.day_name[self.day.weekday()])
        return calendar.day_name[self.day.weekday()] in ["Friday", "Saturday"]

    # def get_date(self):
    #     return f"{calendar.day_name[self.day.weekday()]} {self.day}"

    def get_date(self):
        days_mapping = {
            "Monday": "Lundi   الاثنين",
            "Tuesday": "Mardi   الثلاثاء",
            "Wednesday": "Mercredi   الأربعاء",
            "Thursday": "Jeudi   الخميس",
            "Friday": "Vendredi   الجمعة",
            "Saturday": "Samedi   السبت",
            "Sunday": "Dimanche   الأحد",
        }

        return f"{days_mapping[calendar.day_name[self.day.weekday()]]} {self.day}"

    class Meta:
        ordering = ["day"]
        unique_together = ("day", "user")


class PlanTask(models.Model):
    added = models.DateTimeField(default=datetime.datetime.now)
    task = models.TextField()
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(null=True, blank=True)
    completed = models.BooleanField(default=False)

    transferred_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL
    )
    transferred_at = models.DateTimeField(default=timezone.now, null=True, blank=True)
    is_transferred = models.BooleanField(default=False)

    class Meta:
        unique_together = ["plan", "order"]
        ordering = ["order"]

    def __str__(self):
        return f"{self.order} - {self.task} added on {self.added}"

    def save(self, *args, **kwargs):
        if not self.id:
            max_order = PlanTask.objects.filter(plan=self.plan).aggregate(
                models.Max("order")
            )
            if max_order["order__max"]:
                self.order = max_order["order__max"] + 1
            else:
                self.order = 1

        return super(PlanTask, self).save(*args, **kwargs)

    def delete(self):
        superior_tasks = PlanTask.objects.filter(order__gt=self.order, plan=self.plan)
        super(PlanTask, self).delete()

        for task in superior_tasks:
            task.order -= 1
            task.save(update_fields=["order"])

        return

    # This allows us to permute two Tasks based on their Orders
    def permute(self, plan_task):
        # Getting Current Order
        current_order = self.order
        self.order = plan_task.order

        # Setting Second Task Order to Last Order Plus One, it will otherwise raise an exception because of the unique together rule
        plan_task.order = PlanTask.objects.filter(plan=self.plan).last().order + 1
        plan_task.save(update_fields=["order"])

        # Saving Current Task
        self.save(update_fields=["order"])

        # Putting Order Back to the Second Task
        plan_task.order = current_order
        plan_task.save(update_fields=["order"])


class PlanComment(models.Model):
    added = models.DateTimeField(default=datetime.datetime.now)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)


from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from notifications.utils import sendPush


@receiver(pre_save, sender=Plan)
def update_dates(sender, **kwargs):
    # Getting Instance
    instance = kwargs["instance"]

    # Update date of commune validation
    if instance.valid_commune:
        if not instance.commune_validation_date:
            instance.commune_validation_date = datetime.datetime.today()
    else:
        instance.commune_validation_date = None

    # Update date of Clients validation
    if instance.valid_clients:
        if not instance.client_validation_date:
            instance.client_validation_date = datetime.datetime.today()
    else:
        instance.client_validation_date = None

    # Update date of Tasks validation
    if instance.valid_tasks:
        if not instance.tasks_validation_date:
            instance.tasks_validation_date = datetime.datetime.today()
    else:
        instance.tasks_validation_date = None


# @receiver(post_save, sender=Plan)
def my_handler(sender, **kwargs):
    from .serializers import PlanSerializer
    import json

    if kwargs["created"]:

        tokens = []

        for user in User.objects.filter(
            userprofile__usersunder=kwargs["instance"].user
        ):
            (
                tokens.append(user.userprofile.notification_token)
                if user.userprofile.notification_token
                else None
            )

        for user in User.objects.filter(
            userprofile__usersunder=kwargs["instance"].user
        ):
            (
                tokens.append(user.userprofile.ios_notification_token)
                if user.userprofile.ios_notification_token
                else None
            )

        sendPush(
            "Nouveau Plan",
            "plan " + kwargs["instance"].user.username,
            tokens,
            {
                "name": "Plans",
                "title": "Plan",
                "message": f"Nouveau Plan de {kwargs['instance'].user.username}",
                "confirm_text": "voir le plan",
                "cancel_text": "plus tard",
                "navigate_to": json.dumps(
                    {
                        "screen": "PlanList",
                        "params": {
                            "plan": f"{PlanSerializer(kwargs['instance']).data}"
                        },
                    }
                ),
            },
        )

