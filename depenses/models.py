from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class SpendTypes(models.TextChoices):
    DEPLACEMENT = "Déplacement", "Déplacement"
    SEMI_DEPLACEMENT = "Semi-déplacement", "Semi-déplacement"
    OTHER = "Autre", "Autre"


class WayOfPaymentChoices(models.TextChoices):
    CHEQUE = "Chéque", "Chéque"
    VIREMENT_BANCAIRE = "Virement bancaire", "Virement bancaire"
    ESPECES = "Espèces", "Espèces"


class StatusTypesChoices(models.TextChoices):
    INITIAL = "INITIAL", "INITIAL"
    SUPERVISOR_VALIDATION = "SUP_VALIDATION", "SUP_VALIDATION"
    DIRECTION_VALIDATION = "DIR_VALIDATION", "DIR_VALIDATION"
    NON_CONFIRME = "Non confirmé", "Non confirmé"
    CONFIRME = "Confirmé", "Confirmé"


class Spend(models.Model):
    added = models.DateField(default=timezone.now(), null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    # log_number = models.PositiveIntegerField(null=True, default=0)
    reason = models.TextField(max_length=1000, null=True, blank=True)
    spender = models.TextField(max_length=1000, null=False)
    attachement = models.FileField(
        upload_to="spends", max_length=255, null=True, blank=True
    )
    price = models.PositiveIntegerField(null=False, blank=False)
    price_in_letters = models.TextField(null=True, blank=True)
    nature_depense = models.TextField(max_length=2000, null=True, blank=True)
    url = models.TextField(max_length=2000, null=True, blank=True)
    status = models.TextField(
        max_length=20,
        choices=StatusTypesChoices.choices,
        default=StatusTypesChoices.INITIAL,
    )
    administration_comment = models.TextField(
        max_length=1000, blank=True, null=True, default="-"
    )
    approved_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="approved_user", null=True, blank=True
    )
    approved_date = models.DateTimeField(null=True, blank=True)




class SpendComment(models.Model):
    added = models.DateField(default=timezone.now(), null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    spend = models.ForeignKey(to=Spend, on_delete=models.CASCADE)
    comment = models.TextField(max_length=2000, null=True, blank=True)
