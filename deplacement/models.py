from django.db import models
from django.contrib.auth.models import User

class Deplacement(models.Model):

    STATUS_CHOICES = [
        ('waiting', 'En attente'),
        ('validated_by_supervisor', 'Validé par le superviseur'),
        ('validated_by_direction', 'Validé par la direction'),
        ('Traité', 'Traité'),
    ]

    start_date = models.DateField(verbose_name="Date de début de déplacement")
    end_date = models.DateField(verbose_name="Date de fin de déplacement")
    nb_jours = models.PositiveIntegerField(verbose_name="Nombre de jours")
    nb_nuits = models.PositiveIntegerField(verbose_name="Nombre de nuits")
    wilaya1 = models.CharField(max_length=100, verbose_name="Wilaya 1 (point de départ)")
    wilaya2 = models.CharField(max_length=100, verbose_name="Wilaya 2 (destination)")
    distance = models.FloatField(verbose_name="Distance calculée (km)")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Utilisateur")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='waiting',
        verbose_name="Statut"
    )
    supervisor_validated_at = models.DateTimeField(null=True, blank=True, verbose_name="Date validation superviseur")
    supervisor_validated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="supervisor_validations",
        verbose_name="Validé par le superviseur"
    )
    direction_validated_at = models.DateTimeField(null=True, blank=True, verbose_name="Date validation direction")
    direction_validated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="direction_validations",
        verbose_name="Validé par la direction"
    )
    fully_validated_at = models.DateTimeField(null=True, blank=True, verbose_name="Date validation complète")
    fully_validated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="full_validations",
        verbose_name="Validé complètement par"
    )

    class Meta:
        verbose_name = "Déplacement"
        verbose_name_plural = "Déplacements"

    def __str__(self):
        return f"Déplacement de {self.user.username} du {self.start_date} au {self.end_date}"

class NuitDetail(models.Model):
    deplacement = models.ForeignKey(Deplacement, related_name='nuits_details', on_delete=models.CASCADE)
    nuit = models.PositiveIntegerField(verbose_name="Nuit numéro")
    start_date = models.DateField(verbose_name="Date de début")
    end_date = models.DateField(verbose_name="Date de fin")

    class Meta:
        verbose_name = "Détail de nuitée"
        verbose_name_plural = "Détails des nuitées"

    def __str__(self):
        return f"Nuit {self.nuit} ({self.start_date} - {self.end_date}) pour {self.deplacement}"