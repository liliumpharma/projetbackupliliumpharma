from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.dispatch import receiver
from notifications.models  import Notification
from django.db.models.deletion import CASCADE


class Meet(models.Model):
    added=models.DateField(default=timezone.now,blank=True,db_index=True, verbose_name="Date De création")
    date_meet=models.DateField(default=timezone.now,blank=True,db_index=True, verbose_name="Date De La Réunion")
    title=models.CharField(max_length=500, blank=True, null=True, verbose_name="Titre")
    heure_debut=models.TimeField(default=timezone.now,blank=True,db_index=True, verbose_name="Heure De Début De La Réunion")
    heure_fin=models.TimeField(default=timezone.now,blank=True,db_index=True, verbose_name="Heure De Fin De La Réunion")
    # owner = models.ForeignKey(User, on_delete=CASCADE, verbose_name="User")
    
    link=models.CharField(max_length=500, blank=True, null=True, verbose_name="Lien")
    user=models.ManyToManyField(User, verbose_name="Participants")
    note=models.CharField(max_length=500, blank=True, null=True, verbose_name="Note")


