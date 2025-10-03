from django.db import models

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from fournisseurs.models import *
from produits.models import *


class Entree(models.Model):
    TYPE_CHOICES = [
        ('Premix', 'Premix'),
        ('Matiere premiere', 'Matiere premiere'),
        ('Primary packaging', 'Primary packaging'),
        ('Secondary packaging', 'Secondary packaging'),
    ]

    SUBTYPE_CHOICES = [
        ('Premix powder', 'Premix powder'),
        ('Premix liquide', 'Premix liquide'),
        ('Coating', 'Coating'),
        ('Excipient', 'Excipient'),
        ('Active ingredient', 'Active ingredient'),
        ('PVC', 'PVC'),
        ('Aluminium', 'Aluminium'),
        ('Aluminium Formage', 'Aluminium Formage'),
        ('PVDC', 'PVDC'),
        ('Triplex', 'Triplex'),
        ('Box', 'Box'),
        ('Carton', 'Carton'),
    ]

    DEVISE_CHOICES = [
        ('EUR', 'Euro'),
        ('DZD', 'Dinar Algérien'),
        ('USD', 'Dollar Américain'),
    ]

    UNITE_CHOICES = [
        ('kg', 'Kilogrammes'),
        ('g', 'Grammes'),
        ('mg', 'Milligrammes'),
        ('l', 'Litres'),
        ('ml', 'Millilitres'),
        ('pcs', 'Pièces'),
        ('box', 'Boîtes'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE,null=False)
    added = models.DateTimeField(default=timezone.now)
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.CASCADE,null=False)
    number = models.PositiveIntegerField(null=False)
    lot = models.PositiveIntegerField(null=False)
    manifacture_date = models.DateField(default=timezone.now, null=False)
    expiry_date = models.DateField(default=timezone.now, null=False)
    e_type = models.CharField(max_length=20, choices=TYPE_CHOICES,null=False)
    subtype = models.CharField(max_length=20, choices=SUBTYPE_CHOICES,null=False)
    ingredient_name = models.CharField(max_length=200,null=True)
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE,null=False)
    quantity = models.PositiveIntegerField(null=False)
    main_quantity = models.PositiveIntegerField(null=True)
    unite = models.CharField(max_length=10, choices=UNITE_CHOICES,null=False)
    price = models.DecimalField(max_digits=10, decimal_places=2,null=False)
    devise = models.CharField(max_length=3, choices=DEVISE_CHOICES,null=False)
    qc_approval = models.BooleanField(default=False)
    attachement = models.FileField(upload_to='production/', blank=True, null=True)

    def __str__(self):
        return f"Entree {self.number} - {self.produit.nom}"

    def save(self, *args, **kwargs):
        # Si c'est une nouvelle instance (pas encore sauvegardée en base)
        if not self.id:  # Cela signifie que c'est une nouvelle instance (pas encore sauvegardée)
            self.main_quantity = self.quantity  # Copie de quantity dans main_quantity

        super(Entree, self).save(*args, **kwargs)


class Sortie(models.Model):
    TYPE_CHOICES = [
        ('Premix', 'Premix'),
        ('Matiere premiere', 'Matiere premiere'),
        ('Primary packaging', 'Primary packaging'),
        ('Secondary packaging', 'Secondary packaging'),
    ]

    SUBTYPE_CHOICES = [
        ('Premix powder', 'Premix powder'),
        ('Premix liquide', 'Premix liquide'),
        ('Coating', 'Coating'),
        ('Excipient', 'Excipient'),
        ('Active ingredient', 'Active ingredient'),
        ('PVC', 'PVC'),
        ('Aluminium', 'Aluminium'),
        ('Aluminium Formage', 'Aluminium Formage'),
        ('PVDC', 'PVDC'),
        ('Triplex', 'Triplex'),
        ('Box', 'Box'),
        ('Carton', 'Carton'),
    ]

    DEVISE_CHOICES = [
        ('EUR', 'Euro'),
        ('DZD', 'Dinar Algérien'),
        ('USD', 'Dollar Américain'),
    ]

    UNITE_CHOICES = [
        ('kg', 'Kilogrammes'),
        ('g', 'Grammes'),
        ('mg', 'Milligrammes'),
        ('l', 'Litres'),
        ('ml', 'Millilitres'),
        ('pcs', 'Pièces'),
        ('box', 'Boîtes'),
    ]

    entree = models.ForeignKey(Entree, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    added = models.DateTimeField(default=timezone.now)
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.CASCADE)
    number = models.PositiveIntegerField()
    e_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    subtype = models.CharField(max_length=20, choices=SUBTYPE_CHOICES)
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unite = models.CharField(max_length=10, choices=UNITE_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    devise = models.CharField(max_length=3, choices=DEVISE_CHOICES)
    qc_approval = models.BooleanField(default=False)
    attachement = models.FileField(upload_to='production/', blank=True, null=True)

    def __str__(self):
        return f"Sortie {self.number} - {self.produit.nom}"



class Retour(models.Model):
    TYPE_CHOICES = [
        ('Premix', 'Premix'),
        ('Matiere premiere', 'Matiere premiere'),
        ('Primary packaging', 'Primary packaging'),
        ('Secondary packaging', 'Secondary packaging'),
    ]

    SUBTYPE_CHOICES = [
        ('Premix powder', 'Premix powder'),
        ('Premix liquide', 'Premix liquide'),
        ('Coating', 'Coating'),
        ('Excipient', 'Excipient'),
        ('Active ingredient', 'Active ingredient'),
        ('PVC', 'PVC'),
        ('Aluminium', 'Aluminium'),
        ('Aluminium Formage', 'Aluminium Formage'),
        ('PVDC', 'PVDC'),
        ('Triplex', 'Triplex'),
        ('Box', 'Box'),
        ('Carton', 'Carton'),
    ]

    DEVISE_CHOICES = [
        ('EUR', 'Euro'),
        ('DZD', 'Dinar Algérien'),
        ('USD', 'Dollar Américain'),
    ]

    UNITE_CHOICES = [
        ('kg', 'Kilogrammes'),
        ('g', 'Grammes'),
        ('mg', 'Milligrammes'),
        ('l', 'Litres'),
        ('ml', 'Millilitres'),
        ('pcs', 'Pièces'),
        ('box', 'Boîtes'),
    ]

    entree = models.ForeignKey(Entree, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    added = models.DateTimeField(default=timezone.now)
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.CASCADE)
    number = models.PositiveIntegerField()
    e_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    subtype = models.CharField(max_length=20, choices=SUBTYPE_CHOICES)
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unite = models.CharField(max_length=10, choices=UNITE_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    devise = models.CharField(max_length=3, choices=DEVISE_CHOICES)
    qc_approval = models.BooleanField(default=False)
    attachement = models.FileField(upload_to='production/', blank=True, null=True)

    def __str__(self):
        return f"Retour {self.number} - {self.produit.nom}"




class OrderProduction(models.Model):
    PROCESS_CHOICES = [
        ('full_process', 'Full Process'),
        ('premix', 'Premix'),
    ]

    LOCATION_CHOICES = [
        ('waiting', 'Waiting'),
        ('stock_mp', 'Stock MP'),
        ('pesee', 'Pesee'),
        ('Tablette', 'Tablette'),
        ('mp_pesee', 'MP Pesee'),
        ('in_process', 'IN PROCESS'),
    ]

    STATUS_CHOICES = [
        ('waiting', 'Waiting'),
        ('received', 'received'),
        ('transfered', 'transfered'),
        ('traite', 'traite'),
        ('in_process', 'in_process'),
    ]



    added = models.DateTimeField(auto_now_add=True)  # Date et heure automatiques lors de la création
    code = models.CharField(max_length=40,null=True, blank=True)  # Nouveau champ location
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Clé étrangère vers le modèle User
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)  # Clé étrangère vers le modèle Produit
    batch_number = models.IntegerField()  # Numéro du lot
    process_type = models.CharField(max_length=50, choices=PROCESS_CHOICES) 
    location = models.CharField(max_length=20, choices=LOCATION_CHOICES, default='waiting')  # Nouveau champ location
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waiting')  # Nouveau champ location
    transfered_from_stock = models.BooleanField(default=False) 
    returned_from_weight = models.BooleanField(default=False) 

    

    def __str__(self):
        return f"OrderProduction {self.batch_number} - {self.produit.nom} ({self.process_type})"


class ItemOrderProduction(models.Model):
    LOCATION_CHOICES = [
        ('waiting', 'Waiting'),
        ('stock_mp', 'Stock MP'),
        ('pesee', 'Pesee'),
        ('Tablette', 'Tablette'),
        ('mp_pesee', 'MP Pesee'),
        ('in_process_tablet', 'IN PROCESS SALLE TABLET'),
    ]

    UNITE_CHOICES = [
        ('kg', 'Kilogrammes'),
        ('g', 'Grammes'),
        ('mg', 'Milligrammes'),
        ('l', 'Litres'),
        ('ml', 'Millilitres'),
        ('pcs', 'Pièces'),
        ('box', 'Boîtes'),
    ]

    order_production = models.ForeignKey(OrderProduction, on_delete=models.CASCADE, related_name='items')  # Clé étrangère vers OrderProduction
    item = models.CharField(max_length=255)  # Nom de l'article
    entree = models.ForeignKey(Entree, on_delete=models.CASCADE, null=True)  # Clé étrangère vers Entree
    qtt = models.DecimalField(max_digits=10, decimal_places=2)  # Quantité en kilogrammes
    qtt_from_stock_to_weight = models.DecimalField(max_digits=10, decimal_places=2,null=True)  # Quantité en kilogrammes
    qtt_from_weight_to_stock = models.DecimalField(max_digits=10, decimal_places=2,null=True)  # Quantité en kilogrammes
    unite = models.CharField(max_length=10, choices=UNITE_CHOICES,  default='g')
    location = models.CharField(max_length=20, choices=LOCATION_CHOICES, default='waiting')  # Nouveau champ location



    def __str__(self):
        return f"Item: {self.item} - {self.qtt} kg"


class ItemOrderProductionTransfered(models.Model):
    LOCATION_CHOICES = [
        ('waiting', 'Waiting'),
        ('stock_mp', 'Stock MP'),
        ('pesee', 'Pesee'),
        ('Tablette', 'Tablette'),
        ('mp_pesee', 'MP Pesee'),
        ('in_process_tablet', 'IN PROCESS SALLE TABLET'),

    ]

    UNITE_CHOICES = [
        ('kg', 'Kilogrammes'),
        ('g', 'Grammes'),
        ('mg', 'Milligrammes'),
        ('l', 'Litres'),
        ('ml', 'Millilitres'),
        ('pcs', 'Pièces'),
        ('box', 'Boîtes'),
    ]
    added = models.DateTimeField(auto_now_add=True)  # Date et heure automatiques lors de la création
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True, blank=True)  # Clé étrangère vers le modèle User
    item = models.ForeignKey(ItemOrderProduction, on_delete=models.CASCADE, related_name='items')  # Clé étrangère vers OrderProduction
    qtt = models.DecimalField(max_digits=10, decimal_places=2)  # Quantité en kilogrammes
    location = models.CharField(max_length=20, choices=LOCATION_CHOICES, default='waiting')  # Nouveau champ location
    unite = models.CharField(max_length=10, choices=UNITE_CHOICES,  default='g')


    def __str__(self):
        return f"Item: {self.item} - {self.qtt} kg"





class ItemOrderProductionBash(models.Model):

    LOCATION_CHOICES = [
        ('waiting', 'Waiting'),
        ('stock_mp', 'Stock MP'),
        ('pesee', 'Pesee'),
        ('Tablette', 'Tablette'),
        ('mp_pesee', 'MP Pesee'),
        ('in_process_tablet', 'IN PROCESS SALLE TABLET'),

    ]


    item_order_production = models.ForeignKey(ItemOrderProduction, on_delete=models.CASCADE, related_name='bash_items')  # Clé étrangère vers ItemOrderProduction
    qtt = models.DecimalField(max_digits=10, decimal_places=2)  # Quantité en kilogrammes
    location = models.CharField(max_length=20, choices=LOCATION_CHOICES, default='mp_pesee')  # Champ location
    ref = models.CharField(max_length=50)  # Champ location
    added = models.DateTimeField(auto_now_add=True)  # Champ added qui se remplit automatiquement à la création de l'instance

    def __str__(self):
        return f"Item Bash: {self.item_order_production.item} - {self.qtt} {self.item_order_production.unite}"
