from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from produits.models import Produit


class famille(models.TextChoices):
    DETAILLANT = "detaillant", "detaillant"
    GROSSISTE = "grossistes", "Grossistes"
    SUPER_GROSSISTE = "Super grossistes", "Super grossistes"


class mode_paiement(models.TextChoices):
    VIREMENT_BANCAIRE = "virement_bancaire", "virement_bancaire"
    CHEQUE = "chéque", "chéque"
    ESPECES = "espece", "espece"


class pays(models.TextChoices):
    ALGERIE = "Algerie", "Algerie"
    TUNISIE = "Tunisie", "Tunisie"
    JORDANIE = "Jordanie", "Jordanie"
    USA = "Usa", "Usa"


class typeFamily(models.TextChoices):
    matiere_premiere = " matiere_premiere"
    semi_finish_product = " semi finish product"
    primary_packaging = " primary packaging"
    secondary_packaging = " secondary packaging"


class UnitOfMeasure(models.TextChoices):
    KG = "kg", "Kilogram"
    G = "g", "Gram"
    L = "l", "Liter"
    ML = "ml", "Milliliter"
    UNIT = "unit", "Unit"


class destinationFamily(models.TextChoices):
    autre_usine = ("autre_usine",)
    endomage = ("endomage",)
    destination = "destination"


class Fournisseur(models.Model):
    added = models.DateField(default=timezone.now(), null=False)
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    societe = models.CharField(max_length=100, null=False)
    activite = models.CharField(max_length=100, null=False)
    famille = models.TextField(
        max_length=40, choices=famille.choices, default=famille.DETAILLANT
    )
    representant = models.CharField(max_length=100, null=True)
    adresse = models.CharField(max_length=100, null=False)
    code_postal = models.CharField(max_length=50, null=True)
    numero_de_telephone = models.CharField(max_length=15, null=True)
    email = models.CharField(max_length=100, null=True)
    mode_de_reglement = models.TextField(
        max_length=40, choices=mode_paiement.choices, null=False
    )
    pays = models.TextField(max_length=20, choices=pays.choices, default=pays.ALGERIE)


class Information(models.Model):
    fournisseur = models.ForeignKey(
        to=Fournisseur, null=False, on_delete=models.CASCADE
    )
    rc = models.CharField(max_length=100, null=False)
    id_fiscal = models.CharField(max_length=100, null=False)
    compte_bancaire = models.CharField(max_length=100, null=False)
    compte_comptable = models.CharField(max_length=100, null=False)
    nis = models.CharField(max_length=100, null=False)
    rib = models.CharField(max_length=100, null=False)
    nif = models.CharField(max_length=100, null=False)
    banque = models.CharField(max_length=100, null=False)


class Item(models.Model):
    fournisseur = models.ForeignKey(
        to=Fournisseur, null=False, on_delete=models.CASCADE
    )
    type = models.CharField(
        max_length=1000, choices=typeFamily.choices, null=True, blank=True
    )
    product = models.ManyToManyField(to=Produit, null=False, blank=True)
    description = models.CharField(max_length=1000, null=False)

    def __str__(self):
        return self.description


class Achat(models.Model):
    item = models.ForeignKey(to=Item, null=False, on_delete=models.CASCADE)
    Quantity = models.PositiveIntegerField(null=False, blank=False)
    unit = models.CharField(
        max_length=10,
        choices=UnitOfMeasure.choices,
        default=UnitOfMeasure.UNIT,
        null=False,
        blank=False,
    )

    def __str__(self):
        return f"{self.Quantity} {self.get_unit_display()} of {self.item}"


class Sortie(models.Model):
    item = models.ForeignKey(to=Item, null=False, on_delete=models.CASCADE)
    Quantity = models.PositiveIntegerField(null=False, blank=False)
    unit = models.CharField(
        max_length=10,
        choices=UnitOfMeasure.choices,
        default=UnitOfMeasure.UNIT,
        null=False,
        blank=False,
    )
    destination = models.CharField(
        max_length=100,
        choices=destinationFamily.choices,
        default=destinationFamily.destination,
        null=False,
        blank=False,
    )

    def __str__(self):
        return f"{self.Quantity} {self.get_unit_display()} of {self.item}"
