from django.db import models
from django.dispatch import receiver
from django.contrib.auth.models import User
from medecins.models import Medecin
from django.utils import timezone
from django.core.exceptions import ValidationError
from notifications.models  import Notification
from django.db.models.deletion import CASCADE
from django.db.models.signals import post_save
from django.dispatch import receiver

import datetime
import json


class WayOfPayment(models.TextChoices):
    annule = 'annulé'
    cheque = 'Chéque'
    virement = 'Virement Bancaire'
    espece = 'Espéce'
    espèce = 'Espèce'

class PaybookUser(models.Model):
    date = models.DateField(default=timezone.now, verbose_name="Date")
    number = models.CharField(max_length=200, null=True, blank=True, verbose_name="Numéro du Carnet")

    page_debut = models.PositiveIntegerField(null=True, blank=True, verbose_name="Numéro de la Première Page")
    page_fin = models.PositiveIntegerField(null=True, blank=True, verbose_name="Numéro de la Dérnière Page")
    page_actuelle = models.PositiveIntegerField(null=True, blank=True, verbose_name="Page Actuelle (NE PAS REMPLIR")

    user = models.ForeignKey(User, on_delete=CASCADE, verbose_name="User")
    still_using = models.BooleanField(default=True, verbose_name="Still Using")

    def __str__(self):
        return f"{self.date} - {self.user.username}"
    
    class Meta:
        verbose_name_plural = "Carnets De Versement"

@receiver(post_save, sender=PaybookUser)
def initialiser_page_actuelle(sender, instance, created, **kwargs):
    if created and instance.page_debut is not None:
        instance.page_actuelle = instance.page_debut
        instance.save()

class Versement(models.Model):
    done= models.BooleanField(default=False)
    added = models.DateField(default=timezone.now, verbose_name="Date d'ajout Versement")
    date_document = models.DateField(null=True,blank=True ,verbose_name="Date Document")
    num_recu = models.CharField(max_length=200, null=True, blank=True, verbose_name="Numéro de Reçu")
    paybook = models.ForeignKey(to=PaybookUser, on_delete=CASCADE, null=False, verbose_name="Carnet")
    recu = models.CharField(max_length=200, null=False, blank=False, verbose_name="Client")
    somme = models.CharField(max_length=200, null=False, blank=False, verbose_name="Somme")
    way_of_payment = models.CharField(max_length=35, choices=WayOfPayment.choices, default=WayOfPayment.cheque, verbose_name="Type de paiement")
    numero_de_cheque = models.CharField(max_length=100,null=True, blank=True ,verbose_name="Numéro de chéque")
    link = models.CharField(max_length=1000,null=True, blank=True ,verbose_name="Cloudinary links")
    attachement = models.FileField(upload_to="versements", max_length=255, null=True, blank=True,verbose_name="Piéce jointe")
    updatable= models.BooleanField(default=False)



    class Meta:
        verbose_name_plural = "Bons De Versements"



@receiver(post_save, sender=Versement)
def increment_page_actuelle(sender, instance, created, **kwargs):
    if created:
        # Récupérer l'instance PaybookUser liée au versement
        paybook_user = instance.paybook
        if paybook_user:
            # Vérifier si page_actuelle est défini
            if paybook_user.page_actuelle is not None:
                # Incrémenter page_actuelle de 1
                paybook_user.page_actuelle += 1
            # Sauvegarder l'instance de PaybookUser mise à jour
            paybook_user.save()

@receiver(post_save, sender=Versement)
def notifiate_on_create(sender, **kwargs):
    instance=kwargs['instance']
    notification=Notification.objects.create(
                title=f"Nouvel Encaissement !",
                description=f"{instance.paybook.user.username} vient d'ajouter un bon de versement",
                data={
                        "name":"Encaissement",
                        "title":"Encaissement",
                        "message":f"Nouvel Encaissement par {instance.paybook.user.username}",
                        "confirm_text":"voir le versement",
                        "cancel_text":"plus tard",
                        "StackName":"Versement",
                        "url":f"https://app.liliumpharma.com/admin/versement/versement/{instance.id}/change/",

                    },

            )

    users_with_permissions = list(User.objects.filter(userprofile__speciality_rolee="Finance_et_comptabilité"))
    users_office = list(User.objects.filter(username='mohammed'))

    all_users_to_notify = users_with_permissions + users_office

    # Définir les utilisateurs pour la notification
    notification.users.set(all_users_to_notify)
    # notification.send()

class Creance(models.Model):
    date = models.DateField(default=timezone.now, verbose_name="Date")
    date_echeance = models.DateField(default=timezone.now, verbose_name="Date écheance")
    user = models.ForeignKey(User, on_delete=CASCADE, verbose_name="User")
    attachement = models.FileField(upload_to="versements", max_length=255, null=True, blank=True,verbose_name="Piéce jointe")

class CreanceClient(models.Model):
    date = models.DateField(default=timezone.now, verbose_name="Date")
    user = models.ForeignKey(User, on_delete=CASCADE, verbose_name="User")
    client = models.ForeignKey(Medecin, on_delete=CASCADE, verbose_name="Client")
    attachement = models.FileField(upload_to="versements", max_length=255, null=True, blank=True,verbose_name="Piéce jointe")
