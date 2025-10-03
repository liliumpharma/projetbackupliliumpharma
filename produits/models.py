from django.db import models
from django.dispatch import receiver
from regions.models import Pays
from django.apps import apps

# Validators
from django.core.validators import MinValueValidator
from django.db.models import CheckConstraint, Q




class FileType(models.TextChoices):
    presentation = 'presentation'
    studies = 'studies'
    certification = 'certification'

class PackagingType(models.TextChoices):
    Blister = 'Blister'
    Stick = 'Stick'
    Sachet = 'Sachet'
    Ampoule = 'Ampoule'

class formType(models.TextChoices):
    Tablet = 'Tablet'
    Capsule = 'Capsule'
    coated_tablet = 'Coated Tablet'
    sublingual_tablet = 'Sublingual Tablet'
    Powder_for_oral_solution = 'Powder for oral solution'
    Oral_suspenssion_in_stick = 'Oral suspension in stick'

class PresentationType(models.TextChoices):
    Box_of_30_tablets = 'Box of 30 tablets'
    Box_of_30_sachets = 'Box of 30 sachets'
    Box_of_20_tablets = 'Box of 20 tablets'
    Box_of_20_sachets = 'Box of 20 sachets'
    Box_of_20_capsules = 'Box of 20 capsules'
    Box_of_15_sticks = 'Box of 15 sticks'

class UnitChoices(models.TextChoices):
    kg = 'kg'
    mg = 'mg'
    ml = 'ml'
    mcg = 'mcg'
    UI = 'UI'
    Billions_CFU = 'Billions CFU'

class ClassificationChoices(models.TextChoices):
    Food_supplement = 'Food supplement'

class DosageFormChoices(models.TextChoices):
    powder = 'powder'


class ProductFamily(models.TextChoices):
    lilium_Pharma = 'lilium pharma'
    orient_bio = 'orient bio'
    aniya_pharm = 'aniya pharma'

class ProducerFamily(models.TextChoices):
    lilium_Pharma = 'lilium pharma'
    Soprodum = 'Soprodum'
    cpcm = 'cpcm'

class ServingSizeChoices(models.TextChoices):
    one_tablet= '1 tablet'
    one_sachet = '1 sachet'
    one_capsule = '1 capsule'
    one_stick = '1 stick'



class Produit(models.Model):
    nom=models.CharField(max_length=255)
    pays=models.ManyToManyField(Pays)
    # Check in Form Only
    # family = models.CharField(max_length=100, choices = ProductFamily.choices, default=ProductFamily.lilium_Pharma, null=True)

    price=models.FloatField(default=0, validators=[MinValueValidator(0.0)])

    fname=models.CharField(max_length=255,blank=True,null=True)

    pdf = models.FileField(upload_to="products", max_length=255, null=True, blank=True)
    pdf_2 = models.FileField(upload_to="products", max_length=255, null=True, blank=True)
    image=models.ImageField(null=True,blank=True)


    
    class Meta:
        # Check in DB
        constraints = (
            CheckConstraint(
                check=Q(price__gte=0.0),
                name='price_positive'),
            )

    def __str__(self):
        return self.nom 

class ProductCompany(models.Model):
    product = models.ForeignKey(Produit, null=True,  on_delete=models.CASCADE)
    family = models.CharField(max_length=100, choices = ProductFamily.choices, default=ProductFamily.lilium_Pharma)

class ProductInformations(models.Model):
    product = models.ForeignKey(Produit, null=False,  on_delete=models.CASCADE)
    with_inactive_ingredient = models.BooleanField(default=False, verbose_name="With Inactive while printing")
    product_name = models.CharField(max_length=100, null=True, blank=True)
    price_bba=models.FloatField(default=0, validators=[MinValueValidator(0.0)])

    # -------
    product_identifier = models.CharField(max_length=500, null=True, blank=True)
    suggested_use = models.CharField(max_length=2000, null=True, blank=True)
    dosage_form = models.CharField(max_length=3000,null=True, blank=True)
    description = models.CharField(max_length=3000, null=True, blank=True)
    producer = models.CharField(max_length=100,  choices = ProducerFamily.choices, null=True, blank=True, default = ProducerFamily.lilium_Pharma)
    Tablet_size = models.CharField(max_length=3000, null=True, blank=True)
    Tablet_weight = models.CharField(max_length=3000, null=True, blank=True)
    # ---------
    code_reference = models.CharField(max_length=100, null=True, blank=True)
    galenic_form = models.CharField(max_length=100, choices = formType.choices, null=True, blank=True, default = formType.Tablet)
    product_classification = models.CharField(max_length=100,  choices = ClassificationChoices.choices, null=True, blank=True, default = ClassificationChoices.Food_supplement)
    presentation = models.CharField(max_length=100,  choices = PresentationType.choices, null=True, blank=True, default = PresentationType.Box_of_30_tablets)
    weight = models.CharField(max_length=50, null=True, blank=True)
    serving_size = models.CharField(max_length=100, choices=ServingSizeChoices.choices, null=True, default=ServingSizeChoices.one_tablet)   


class ProductNote(models.Model):
    produit=models.ForeignKey(Produit, on_delete=models.CASCADE)
    note=models.TextField(max_length=10000, null=True)

class ProductFile(models.Model):
    fil = models.FileField(upload_to="products", max_length=255, null=True, blank=True)
    produit=models.ForeignKey(Produit, on_delete=models.CASCADE)
    name=models.CharField(max_length=255)
    file_type=models.CharField(max_length=255,choices=FileType.choices,default=FileType.presentation)


class ProductActiveIngerients(models.Model):
    produit=models.ForeignKey(Produit, on_delete=models.CASCADE)
    ingredient = models.CharField(max_length=300, blank=True, null=True)
    unit = models.CharField(max_length=100, choices = UnitChoices.choices, null=True, blank=True, default = UnitChoices.mg)
    quantity = models.FloatField(default=0, null=True, verbose_name="Label Quantity")
    convert = models.FloatField(default=0, null=True)
    quantity_mg = models.FloatField(default=0, null=True)

class ProductInactiveIngredients(models.Model):
    produit=models.ForeignKey(Produit, on_delete=models.CASCADE)
    ingredient = models.CharField(max_length=100, blank=True, null=True)
    unit = models.CharField(max_length=100, choices = UnitChoices.choices, null=True, blank=True, default = UnitChoices.mg)
    quantity = models.FloatField(default=0, null=True)
    e_num = models.CharField(max_length=100, blank=True, null=True, verbose_name="E-NUM")
    coating_material=models.BooleanField(default=False)

class ProductProductionInfos(models.Model):
    packaging_form=models.CharField(max_length=255,choices=PackagingType.choices,default=PackagingType.Blister)
    produit=models.ForeignKey(Produit, on_delete=models.CASCADE)
    tablet_weight = models.CharField(max_length=300, blank=True, null=True, verbose_name="tablet weight in mg")
    tablet_per_blister = models.CharField(max_length=300, blank=True, null=True)
    blister_per_box = models.CharField(max_length=300, blank=True, null=True)
    batch_size = models.CharField(max_length=20, blank=True, null=True)
    unit = models.CharField(max_length=100, choices = UnitChoices.choices, null=True, blank=True, default = UnitChoices.mg)




class ProduitVisite(models.Model):
    visite = models.ForeignKey("rapports.Visite", on_delete=models.CASCADE)
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    prescription=models.BooleanField(default=False)
    qtt=models.IntegerField()
    medecin=models.ForeignKey("medecins.Medecin",on_delete=models.CASCADE,null=True,blank=True)


from django.db.models.signals import pre_save,post_delete


@receiver(pre_save, sender=ProduitVisite)   # if kwargs['instance'].visite.rapport == Rapport.objects.filter(user=kwargs['instance'].visite.rapport.user,visite__medecin=kwargs['instance'].visite.medecin).order_by('-added')[0]:
def new_ProduitVisite(sender, **kwargs):
    Rapport=apps.get_model(app_label='rapports', model_name='Rapport')
    visite=kwargs['instance'].visite
    medecin=kwargs['instance'].visite.medecin
    # print(f"from visite ************* {visite.id}")
    if medecin.last_visite() == visite:
       ProduitVisite.objects.filter(medecin=medecin).exclude(visite=visite).update(medecin=None)
       kwargs['instance'].medecin= medecin
       


class ProductionStepChoices(models.TextChoices):
    MIXING_POWDER = 'MIXING_POWDER', 'MIXING_POWDER'
    MIXING_LIQUIDE = 'MIXING_LIQUIDE', 'MIXING_LIQUIDE'

    TABLETTE = 'tablette', 'Tablette'
    COATING = 'coating', 'Coating'
    BLISTER = 'blister', 'Blister'

    CAPSULE = 'CAPSULE', 'CAPSULE'
    SACHET = 'SACHET', 'SACHET'
    STICK = 'STICK', 'STICK'

    SECONDARY_PACKAGING = 'SECONDARY_PACKAGING', 'SECONDARY_PACKAGING'
    STORE_FINISH_PRODUCT = 'STORE_FINISH_PRODUCT', 'STORE_FINISH_PRODUCT'


class ProductProductionPremixStep(models.Model):
    produit = models.ForeignKey(Produit, related_name='production_steps', on_delete=models.CASCADE)
    step_number = models.PositiveIntegerField()  # Le numéro de l'étape
    step_name = models.CharField(max_length=50, choices=ProductionStepChoices.choices)  # Étape de production
    description = models.CharField(max_length=2000, null=True, blank=True)  # Étape de production

    class Meta:
        ordering = ['step_number']  # Pour ordonner les étapes par numéro

    def __str__(self):
        return f"Étape {self.step_number} - {self.get_step_name_display()}"


class ProductionStepFullProcessChoices(models.TextChoices):
    MIXING_POWDER = 'MIXING_POWDER', 'MIXING_POWDER'
    MIXING_LIQUIDE = 'MIXING_LIQUIDE', 'MIXING_LIQUIDE'

    TABLETTE = 'tablette', 'Tablette'
    COATING = 'coating', 'Coating'
    BLISTER = 'blister', 'Blister'

    CAPSULE = 'CAPSULE', 'CAPSULE'
    SACHET = 'SACHET', 'SACHET'
    STICK = 'STICK', 'STICK'

    SECONDARY_PACKAGING = 'SECONDARY_PACKAGING', 'SECONDARY_PACKAGING'
    STORE_FINISH_PRODUCT = 'STORE_FINISH_PRODUCT', 'STORE_FINISH_PRODUCT'

class ProductProductionFullProcessStep(models.Model):
    produit = models.ForeignKey(Produit, related_name='production_full_process_steps', on_delete=models.CASCADE)
    step_number = models.PositiveIntegerField()  # Le numéro de l'étape
    step_name = models.CharField(max_length=50, choices=ProductionStepFullProcessChoices.choices)  # Étape de production
    description = models.CharField(max_length=2000, null=True, blank=True)  # Étape de production

    class Meta:
        ordering = ['step_number']  # Pour ordonner les étapes par numéro

    def __str__(self):
        return f"Étape {self.step_number} - {self.get_step_name_display()}"

