import os
import django

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'liliumpharm.settings')
# django.setup()

from accounts.models import UserProfile, UserProduct
from django.contrib.auth.models import User
from regions.models import Commune, Wilaya, Pays
from produits.models import Produit
from django.contrib.auth.models import Group
from medecins.models import Medecin
from clients.models import *
# from django.contrib.auth.models import User
# from accounts.models import UserProfile
# from rapports.models import Rapport
# from django.db.models import Q,F,Max,Count,ExpressionWrapper

from plans.models import Plan
import datetime
from accounts.models import UserProxy
import json
from liliumpharm.redis_cli import RedisConnect

# import pandas as pd
# xlsx = pd.ExcelFile('wilayas.xlsx')
# sheet1 = pd.read_excel(xlsx)

# for wi in sheet1.iterrows():
#     data=wi[1]
#     country = Pays.objects.get(id=1)
#     wil = Wilaya.objects.filter(nom__icontains=data[1])
#     if not wil.exists():
#         print(f'Creating {wi[1]}')
#         Wilaya.objects.create(nom=data[1], code_name=data[0], pays=country)
    # else:
    #     print(f'Updating {wi[1]}')
    #     wil = wil.first()
    #     wil.code_name = data[0]
    #     wil.save(update_fields=['code_name'])


country = Pays.objects.get(id=1)

for wilaya in Wilaya.objects.filter(pays=country):
    clients = Client.objects.filter(name__icontains=wilaya.nom, wilaya=wilaya, supergro=False)
    if not clients.exists():
        # print(f'Creating Client {wilaya.nom}')
        Client.objects.create(wilaya=wilaya, name=wilaya.nom)

# redis=RedisConnect()


# for usr in UserProxy.objects.exclude(username__in=[
# "liliumdz",
# ]):

#     print(usr,"**************************")
#     if usr.is_superuser:
#         users=UserProxy.objects.all()
#     elif usr.userprofile.rolee =="CountryManager":
#         users=UserProxy.objects.filter(pays=usr.userprofile.commune.wilaya.pays)
#     else:    
#         users=[ *usr.userprofile.usersunder.all(), usr ]

#     medecins_list=Medecin.objects.filter(users__in=users).distinct()




#     redis.set_key(f"{usr.username}_medecins",json.dumps([
#         {
#             "id":m.id,
#             "nom":m.nom,
#             "specialite":m.specialite,
#             "last_visite":f'{m.get_last_visite()}'
#         } 
#     for m in medecins_list]))



# print(User.objects.filter(userprofile__isnull=True))
# from medecins.models import MedecinSpecialite



# for client in Client.objects.filter(supergro=True):
#     med=Medecin.objects.create(
#         nom="supergros "+client.name,
#         commune=client.wilaya.commune_set.first(),
#         specialite="SuperGros",
#         telephone="0655342974",
#         adresse="adress"
#         )
#     med.users.set(User.objects.all())

# for ms in MedecinSpecialite.objects.all():
#     print(ms.description)
#     ms.description = ms.description.replace('�', 'e')
#     ms.save(update_fields=['description'])


# Generate Plans
# for u in User.objects.all():
#     for day in range(1,31):
#         if not Plan.objects.filter(day=datetime.datetime(2022,12,day).date(),user=u,updatable=True).exists():
#             Plan.objects.create(
#                 day=datetime.datetime(2022,12,day).date(),
#                 user=u,
#                 updatable=True
#                 )


# for u in User.objects.all():
#     grupo = Group.objects.get(id=6)
#     grupo.user_set.add(u)


# from regions.models import Wilaya

# from produits.models import Produit



# products = Produit.objects.all()
# ordersource = OrderSource.objects.get(id=24)

# data = []

# for order in ordersource.order_set.all():
#     products_list = []
#     for product in products:
#         order_product = OrderProduct.objects.filter(order=order, produit=product)
#         if order_product.exists():
#             order_product = order_product.first()
#             products_list.append(order_product.qtt)
#             continue
#         products_list.append(0)
    






















# wilayas = Wilaya.objects.all().values_list("id", flat=True)

# userprofile = UserProfile.objects.filter(sectors__id__in=wilayas)

# print(userprofile)

# from clients.models import *
# from clients.functions import get_targets_by_order_source

# os = OrderSource.objects.get(id=19)
# print(get_targets_by_order_source(os))

# data = []

# products = Produit.objects.all()

# for wilaya in Wilaya.objects.all():

#     users = UserProfile.objects.filter(sectors=wilaya)

#     users_data = []

#     for user_profile in users:
#         targets = []
#         prices = []
#         quantities = []
#         total_targets = []
#         total_achievements = []

#         for product in products:
#             # Appending Price
#             prices.append(product.price)

#             order_product = OrderProduct.objects.filter(produit=product, 
#                                                         order__client__wilaya=wilaya, 
#                                                         order__source__date__month=7, 
#                                                         order__source__date__year=2022).values("produit__nom").annotate(total=Sum("qtt"))
#             total = 0
#             if order_product.exists():
#                 total = order_product[0].get("total")
            
#             total_common_target = round(total / users.count(), 2)

#             # Appending Quantity
#             quantities.append(total_common_target)
#             total_achievements.append(round(total_common_target * product.price, 2))

#             user = user_profile.user
#             user_product = UserProduct.objects.filter(user=user, product=product)
            
#             if user_product:
#                 user_product = user_product.first()
#                 # Appending Quantity
#                 targets.append(user_product.quantity)
#                 total_targets.append(round(user_product.quantity * product.price, 2))
#             else:
#                 # Appending Quantity
#                 targets.append("NTD")
#                 total_targets.append("NTD")

#         total_target = round(sum([total for total in total_targets if type(total) != str]), 2)
#         total_reached = round(sum([total for total in total_achievements if type(total) != str]), 2)
#         percentage_reached = round(total_reached * 100 / total_target, 2)

#         users_data.append({"user": user.username, 
#                             "targets": targets, 
#                             "prices": prices, 
#                             "quantities": quantities, 
#                             "total_targets": total_targets,
#                             "total_achievements": total_achievements,
#                             "total_target": total_target,
#                             "total_reached": total_reached,
#                             "percentage_reached": percentage_reached})


#     data.append({"wilaya": wilaya, "users": users_data})
    






# from django.db.models import Count
# from rapports.models import Visite
# from medecins.models import *


# DONE = []

# for visite in Visite.objects.all():
#     if not list(filter(lambda a: list(a.keys())[0]==visite.medecin and list(a.values())[0]==visite.rapport, DONE)):
#         redundancy = Visite.objects.exclude(id=visite.id).filter(medecin=visite.medecin, rapport=visite.rapport)
#         if redundancy:
#             # REPLACE THIS LOOP WITH > 
#             redundancy.delete()
#             print(f'Deleting Visites')
#             # --------------------------------------------
#             # print('\n')
#             # for r in redundancy:
#             #     print(f'Deleting Visite {r.id} \t\t Medecin {r.medecin.id} \t\t Rapport {r.rapport.id} {r.rapport.added} {r.rapport.user.username}')
#             # print(f'Redundancy {len(redundancy)} Time(s)')
#             # print('\n===============================')
#             # --------------------------------------------
#         else:
#             print("no redendency")
#         DONE.append({visite.medecin: visite.rapport})




# from accounts.models import UserProfile


# for m in Medecin.objects.all():
#     for usr in m.users.all():
#         try:
#             for up in UserProfile.objects.filter(usersunder=usr):
#                 m.users.add(up.user)
#         except:
#             print(usr)    

# import json
  
# Opening JSON file
# f = open('utils/data/medecins.json')
  
# returns JSON object as 
# a dictionary
# data = json.load(f)
  
# Iterating through the json
# list
# for dt in data:
#     # print(dt["fields"]["users"])
#     medecin=Medecin.objects.get(id=dt["pk"])
#     medecin.users.clear()
#     for usr in dt["fields"]["users"]:
#         print(usr[0])
#         try: 
#             medecin.users.add(User.objects.get(username=usr[0]))
#         except:
#             print("faild")    
#         # medecin.users.add(User.objects.get(username=usr))

  
# # Closing file
# f.close()

# for profile in UserProfile.objects.all():
#     profile.can_add_medecin=False
#     profile.can_add_client=True
#     profile.save()




# print('PLEASE CALL 0561-38-15-32 FOR TEL3ABLI BIH SHUIY VERY QUICKLY\t'*50)

# from plans.models import Plan
# import datetime
# from django.contrib.auth.models import User


# from medecins.models import Medecin 


# print(Medecin.objects.filter(specialite="G�n�raliste").update(specialite="Généraliste"))




# Generate Plans
# for u in User.objects.all():
#     for day in range(1,31):
#         if not Plan.objects.filter(day=datetime.datetime(2022,10,day).date(),user=u,updatable=True).exists():
#             Plan.objects.create(
#                 day=datetime.datetime(2022,10,day).date(),
#                 user=u,
#                 updatable=True
#                 )

# Plan.objects.filter(user__username="Lydiadz").update(valid_commune=True,valid_clients=True)

# for plan in Plan.objects.all():
#     if plan.free_day:
#         plan.isfree=True
#         plan.save()

# from rapports.models import Rapport 
# from plans.models import * 




# for p in Plan.objects.filter(plantask__isnull=False):
    



# for p in  Plan.objects.filter(plantask__isnull=False,day__lt=datetime.datetime.today()):
#     Rapport.objects.create(user=p.user,added=p.day,image="rapports/rapport.jpeg")


# Medecin.objects.filter(note="").update(note=None)
# print(len(med))
# for m in med:
#     print(m.id, m.note) 

# for m in Medecin.objects.all():
#     try:
#         m.specialite_fk=MedecinSpecialite.objects.get(description=m.specialite)
#         m.save(update_fields=["specialite_fk"])
#     except:
#         print(m.specialite," not found ")    





# import calendar
# from django.core.mail import send_mail
# from django.core.mail import EmailMessage
# from django.contrib.auth.models import User
# from rapports.models import Rapport
# from plans.models import * 
# from datetime import date, timedelta




# SENDING MAILS FOR MISSING RAPPORTS 

# yesterday = date.today() - timedelta(days=1)

 

# if calendar.day_name[yesterday.weekday()] not in ["Friday", "Saturday"]:

#     for usr in User.objects.all():
#         try:
#             r=Rapport.objects.get(user=usr,added=yesterday)
#         except:
#             if usr.email:
#                 # subject="Some Subject"
#                 # body=" E-MAIL BODY"
#                 # email = EmailMessage(subject, body, 'server.lilium@gmail.com', [usr.email,"contact.liliumpharma@gmail.com","boughezala.aimen@gmail.com"])
#                 # email.send()
#                 print(usr)


