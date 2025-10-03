from django.db import models
from django.contrib.auth.models import User


class Shape(models.Model):
    name=models.CharField(max_length=255)
    def __str__(self): return f"{self.name}"




class CProduct(models.Model):
    product=models.ForeignKey("produits.Produit",on_delete=models.CASCADE, verbose_name="lilium_product")
    name=models.CharField(null=True,max_length=255,verbose_name="المنتج المنافس")
    company=models.CharField(null=True,max_length=255,verbose_name=" اسم الشركة المنافسة ")
    country=models.CharField(null=True,max_length=255,verbose_name=" مكان الصنع ")
    price=models.CharField(null=True,max_length=255,verbose_name=" السعر ")
    shape=models.ForeignKey(Shape,on_delete=models.CASCADE,verbose_name=" الشكل الصيدلاني ")
    treatment_duration=models.CharField(max_length=255, verbose_name=" مدة العلاج ")
    marketing=models.CharField(max_length=255,choices=(("medical","medical"), ("commercial","commercial"), ("medicocommercial","medicocommercial")),verbose_name=" طريقة التسويق المعتمدة ")
    good=models.TextField(null=True,verbose_name=" نقاط القوة ")
    bad=models.TextField(null=True,verbose_name=" نقاط الضعف  ")
    observations=models.TextField(null=True,verbose_name=" ملاحظات ")
    image=models.ImageField(null=True,blank=True)
    image_2=models.ImageField(null=True,blank=True)
    image_3=models.ImageField(null=True,blank=True)
    brochure=models.ImageField(null=True,blank=True)


    user=models.ForeignKey(User,blank=True,null=True,on_delete=models.SET_NULL)
    valid=models.BooleanField(default=False)



    def __str__(self): return f"{self.company} {self.name}"



class Composition(models.Model):
    name=models.CharField(max_length=255)
    qtt=models.CharField(max_length=255)
    product=models.ForeignKey(CProduct,on_delete=models.CASCADE)
    


