from django.db import models
from medecins.models import Medecin
from accounts.models import User


class DealType(models.Model):
    description=models.CharField(max_length=255)
    
    def __str__(self):
        return self.description

    def __json__(self):
        return {
        "id":self.id,
        "description":self.description
        }

class DealStatus(models.Model):
    description=models.CharField(max_length=255)

    def __str__(self):
        return self.description


    def __json__(self):
        return {
            "id":self.id,
            "description":self.description
            }



class Deal(models.Model):
    added=models.DateField(auto_now_add=True)
    starting_date=models.DateField()
    ending_date=models.DateField()
    payment_date=models.DateField(blank=True,null=True)
    description=models.CharField(max_length=255)
    # cost=models.PositiveIntegerField()
    cost=models.CharField(max_length=255)
    status=models.ForeignKey(DealStatus,on_delete=models.CASCADE,null=True,blank=True)
    dtype=models.ForeignKey(DealType,on_delete=models.CASCADE,default=DealType.objects.first().id)
    user=models.ForeignKey("auth.user",on_delete=models.CASCADE)
    # medecin=models.ForeignKey("medecins.Medecin",on_delete=models.CASCADE)
    medecin=models.ManyToManyField(Medecin,related_name="medecin",blank=True)

    @property
    def prop1(self):
        return 'Im a property'

    def __str__(self):
        return self.description

    def __json__(self):
        return {
            "id":self.id,
            "added":self.added,
            "starting_date":self.starting_date,
            "ending_date":f"{self.ending_date} | Deal Nº{self.id} | ",
            "payment_date":self.payment_date,
            "description":self.description,
            "cost":self.cost,
            "dtype":self.dtype.__json__(),
            "status":self.status.__json__(),
            "user":self.user.username,
            "medecin":self.medecin.id,
            "items":[p.__json__() for p in self.dealproduct_set.all()],
            "comments":[c.__json__() for c in self.dealcomment_set.all()]
            }


class DealProduct(models.Model):
    deal=models.ForeignKey(Deal,on_delete=models.CASCADE)
    product=models.ForeignKey("produits.Produit",on_delete=models.CASCADE)
    qtt=models.PositiveIntegerField()

    def __json__(self):
        return {
            "id":self.id,
            "product":self.product.nom,
            "qtt":self.qtt,
            }



class DealComment(models.Model):
    added=models.DateTimeField(auto_now_add=True)
    deal=models.ForeignKey(Deal,on_delete=models.CASCADE)
    comment=models.TextField()


    def __str__(self):
        return self.comment

    def __json__(self):
        return {
            "id":self.id,
            "added":self.added,
            "deal":self.deal.id,
            }


class Delegue_Representant(models.Model):
    added = models.DateTimeField(auto_now_add=True)
    deal = models.ForeignKey('Deal', on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    date_debut_recuperation = models.DateField(null=True, blank=True)
    date_reprise_recuperation = models.DateField(null=True, blank=True)
    comment = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.comment if self.comment else "No comment"


