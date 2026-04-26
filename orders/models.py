from django.db import models
from django.contrib.auth.models import User 
import json
from .generate_jpg import thread
import requests

class Order(models.Model):
    added=models.DateTimeField(auto_now_add=True)
    pharmacy=models.ForeignKey("medecins.Medecin",on_delete=models.CASCADE,null=True,blank=True,related_name="from_pharmacy")
    gros=models.ForeignKey("medecins.Medecin",on_delete=models.CASCADE,null=True,blank=True,related_name="from_grossite")
    super_gros=models.ForeignKey("clients.Client",on_delete=models.CASCADE,related_name="from_sgros",null=True,blank=True)
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    observation=models.TextField(blank=True)
    status=models.CharField(max_length=20,choices=(("initial","initial"),("confirme","confirme"),("en cours","en cours"),("traite","traite") ), default="initial")
    flag=models.BooleanField(default=False, verbose_name="Flag  |   طلبية معلقة")
    cause=models.TextField(max_length=500,null=True,blank=True,verbose_name="Cause Flag  |   سبب التعليق")

    validation_date=models.DateField(null=True,blank=True)
    done_date=models.DateField(null=True,blank=True)

    infos=models.CharField(max_length=255,choices=(("yalidine", "yalidine"), ('livreur',"livreur"), ("bureau", "bureau"), ("delegue", "delegue")),null=True,blank=True)
    tracking = models.JSONField(default=dict,blank=True)
    bl=models.CharField(max_length=255,null=True,blank=True)


    touser=models.ForeignKey(User,on_delete=models.CASCADE,related_name="share_to_user",null=True,blank=True)
    transfer_date=models.DateField(null=True,blank=True)

    image=models.ImageField(upload_to="order_photo/", blank=True,null=True)
    from_company=models.BooleanField(default=False)
    attente=models.BooleanField(default=False, verbose_name="En attente")

    class Meta:
        verbose_name="Bon de commande"


    def items_admin(self):
        return '<br/> '.join([f'{item}' for item in OrderItem.objects.filter(order=self)])  
    
    @property
    def valeur_net(self):
        """Calcule la somme de (prix unitaire x quantité) pour tous les articles."""
        return sum(item.produit.price * item.qtt for item in self.orderitem_set.all())

    @property
    def valeur_brute(self):
        return sum(item.line_total_ttc for item in self.orderitem_set.all())
    # ---------------------------

    def save(self, *args, **kwargs):
        if  not  ( self.super_gros and self.super_gros.id == 149 or (not self.pharmacy and  not self.gros and self.super_gros ) ):
            if not self.status:
                self.status = "traite"
        else:
            self.from_company=True    
        super(Order, self).save(*args, **kwargs)





class OrderItem(models.Model):
    order=models.ForeignKey(Order,on_delete=models.CASCADE)
    produit = models.ForeignKey("produits.Produit", on_delete=models.CASCADE)
    qtt=models.IntegerField()
    


    def __str__(self):
        return f"{self.produit.nom}--{self.qtt}"
        
    @property
    def prix_unitaire(self):
        import decimal
        base_price = float(self.produit.price)
        
        def normal_round(n):
            return float(decimal.Decimal(str(n)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
            
        # 1. Si une Pharmacie est sélectionnée
        if self.order.pharmacy:
            return normal_round(base_price * 1.19) * 1.15 * 1.1
        # 2. Si un Super Grossiste ET un Grossiste sont sélectionnés
        elif self.order.super_gros and self.order.gros:
            return normal_round(base_price * 1.19) * 1.15
        # 3. Si uniquement un Super Grossiste est sélectionné
        elif self.order.super_gros:
            return normal_round(base_price * 1.19)
        return base_price

    @property
    def line_total_net(self):
        return self.produit.price * self.qtt
        
    @property
    def line_total_ttc(self):
        return self.prix_unitaire * self.qtt


class ExitOrder(models.Model):
    added=models.DateTimeField(auto_now_add=True)
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    observation=models.TextField(blank=True)
    status=models.CharField(max_length=20,choices=(("initial","initial"),("traite","traite") ), default="initial")
    brochure=models.BooleanField(default=False)
    validation_date=models.DateField(null=True,blank=True)
    done_date=models.DateField(null=True,blank=True)
    depot=models.CharField(max_length=20,choices=(("delegue","delegue"),("principale","principale") ), default="principale")
    user_confirmed=models.ForeignKey(User,on_delete=models.SET_NULL,blank=True,null=True,related_name="confirmed_by")

    class Meta:
        verbose_name="Bon de sortie"
    def items_admin(self):
        return '<br/> '.join([f'{item}' for item in ExitOrderItem.objects.filter(order=self)])  




class ExitOrderItem(models.Model):
    order=models.ForeignKey(ExitOrder,on_delete=models.CASCADE)
    produit = models.ForeignKey("produits.Produit", on_delete=models.CASCADE)
    qtt=models.IntegerField()


    def __str__(self):
        return f"{self.produit.nom}--{self.qtt}"




from datetime import datetime
from datetime import timedelta
from django.db.models.signals import pre_save,post_save
from django.dispatch import receiver
# from notifications.utils import sendPush
from notifications.models import Notification 




@receiver(post_save, sender=ExitOrder)
def my_handler(sender, **kwargs):
    from .serializers import ExitOrderSerializer

    tokens=[]
   
    for user in User.objects.filter(userprofile__usersunder=kwargs['instance'].user):
        tokens.append(user.userprofile.notification_token) if user.userprofile.notification_token else None


    for user in User.objects.filter(is_superuser=True):
        tokens.append(user.userprofile.notification_token) if user.userprofile.notification_token else None
    
    for user in User.objects.filter(username__in=["liliumdz","ibtissemdz"]):
        tokens.append(user.userprofile.notification_token) if user.userprofile.notification_token else None    


    for user in User.objects.filter(userprofile__rolee="CountryManager"):
        tokens.append(user.userprofile.notification_token) if user.userprofile.notification_token else None    


    instance=kwargs['instance']

    updated_datetime = instance.added + timedelta(hours=1)

    date_format = "%Y-%m-%d à %H:%M"
    date_formatee = updated_datetime.strftime(date_format)

    # notification=Notification.objects.create(
    #         title=f"Nouveau bon de sortie",
    #         description=f"Délégué:{kwargs['instance'].user.username}\nDate:{date_formatee}",
    #         data={
    #                 "name":"ExitOrders",
    #                 "title":"Bon de sortie",
    #                 "message":f"Nouveau Bon de sortie de {instance.user.username}",
    #                 "confirm_text":"voir le bon",
    #                 "cancel_text":"plus tard",
    #                 "StackName":"ExitOrders",
    #                 "url":f"https://app.liliumpharma.com/orders/front/exits/?user={instance.user.username}&date={instance.added.date()}",
    #                 "navigate_to":
    #                 json.dumps({
    #                         "screen":"List",
    #                         "params":{
    #                                 "user":instance.user.username,
    #                                 "date":str(instance.added.date())
    #                         }

    #                     },ensure_ascii=False)
    #             },
    #     )
    # notification.users.set([usr for usr in instance.user.userprofile.get_users_to_notify()])
    # notification.send()

    # users_to_notify = [usr for usr in instance.user.userprofile.get_users_to_notify()]
    # users_office = list(User.objects.filter(userprofile__speciality_rolee='Office', userprofile__is_human = True))
    # # Combiner les deux listes
    # all_users_to_notify = users_to_notify + users_office

    # # Mettre à jour les utilisateurs de la notification
    # print ("Users to notifiate -------> " + str(all_users_to_notify))
    # notification.users.set(all_users_to_notify)

    # shot = WebShot()
    # create_jpg = thread(
    #     "generating_jpg_for_exit_order"+str(instance.id),
    #      instance.id+1000,
    #      'http://localhost:8001/orders/exit_orders/'+str(instance.id),
    #      '/app/static/share/exit_orders/'+str(instance.id)+'.jpg'
    #      )

    # create_jpg.start()


@receiver(post_save, sender=Order)
def my_handler(sender, **kwargs):
    from .serializers import OrderSerializer

    tokens=[]
   
    for user in User.objects.filter(userprofile__usersunder=kwargs['instance'].user):
        tokens.append(user.userprofile.notification_token) if user.userprofile.notification_token else None


    for user in User.objects.filter(is_superuser=True):
        tokens.append(user.userprofile.notification_token) if user.userprofile.notification_token else None
    
    for user in User.objects.filter(username__in=["liliumdz","ibtissemdz"]):
        tokens.append(user.userprofile.notification_token) if user.userprofile.notification_token else None    


    for user in User.objects.filter(userprofile__rolee="CountryManager"):
        tokens.append(user.userprofile.notification_token) if user.userprofile.notification_token else None    


    instance=kwargs['instance']



    # notification=Notification.objects.create(
    #         title=f"Nouveau Bon de commande  {kwargs['instance'].user.username}",
    #         description=f"{str(instance.added)}",
    #         data={
    #                 "name":"Orders",
    #                 "title":"Bon de commande",
    #                 "message":f"Nouveau Bon de commande de {instance.user.username}",
    #                 "confirm_text":"voir le bon",
    #                 "cancel_text":"plus tard",
    #                 "StackName":"Orders",
    #                 "url":f"https://app.liliumpharma.com/orders/front/?user={instance.user.username}&date={instance.added.date()}",
    #                 "navigate_to":
    #                 json.dumps({
    #                         "screen":"List",
    #                         "params":{
    #                                 "user":instance.user.username,
    #                                 "date":str(instance.added.date())
    #                         }

    #                     },ensure_ascii=False)
    #             },
    #     )
    # users_to_notify = [usr for usr in instance.user.userprofile.get_users_to_notify()]
    # users_office = list(User.objects.filter(userprofile__speciality_rolee='Office', userprofile__is_human = True))
    # # Combiner les deux listes
    # all_users_to_notify = users_to_notify + users_office

    # # Mettre à jour les utilisateurs de la notification
    # print ("Users to notifiate -------> " + str(all_users_to_notify))
    # notification.users.set(all_users_to_notify)

    # notification.send()
    # shot = WebShot()
    # create_jpg = thread(
    #     "generating_jpg_for_order"+str(instance.id),
    #      instance.id+1000,
    #      'http://localhost:8001/orders/'+str(instance.id),
    #      '/app/static/share/orders/'+str(instance.id)+'.jpg'
    #      )

    # create_jpg.start()
    # import imgkit
    # imgkit.from_url('http://localhost:8001/orders/'+str(instance.id),'/app/static/share/orders/'+str(instance.id)+'.jpg')

    # img_filepath ='/app/static/share/orders/'+str(instance.id)+'.jpg'
    # resp = requests.get('https://app.liliumpharma.com/orders/'+str(instance.id))
    # html_source=resp.text
    # html = wsp.HTML(string=html_source)
    # html.write_png(img_filepath)
