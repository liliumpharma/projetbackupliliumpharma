from django.db import models

class Company(models.Model):
    name=models.CharField(max_length=255)
    activité=models.CharField(max_length=500, blank=True, null=True)
    adress=models.CharField(max_length=255)
    r_c=models.CharField(max_length=255)
    fiscal_id=models.CharField(max_length=255)
    a_i=models.CharField(max_length=255)
    n_i_s=models.CharField(max_length=255)
    mobile=models.CharField(max_length=255, blank=True, null=True)
    mobile_2=models.CharField(max_length=255, blank=True, null=True)
    mobile_3=models.CharField(max_length=255, blank=True, null=True)
    mobile_4=models.CharField(max_length=255, blank=True, null=True)
    phone=models.CharField(max_length=255, blank=True, null=True)
    phone_2=models.CharField(max_length=255, blank=True, null=True)
    phone_2=models.CharField(max_length=255,blank=True, null=True)
    bank_name=models.CharField(max_length=255)
    email=models.CharField(max_length=255,blank=True, null=True)
    r_i_b=models.CharField(max_length=255)
    i_b_a_n=models.CharField(max_length=255)
    swift=models.CharField(max_length=255,blank=True, null=True)
    file = models.FileField(upload_to="companys", max_length=255, null=True, blank=True, verbose_name="Réglement intérieur")
    logo = models.ImageField(upload_to="companys",null=True, blank=True)



    def __str__(self):
        return self.name
    

