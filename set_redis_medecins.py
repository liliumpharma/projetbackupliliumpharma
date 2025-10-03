import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'liliumpharm.settings')
django.setup()

from accounts.models import UserProfile, UserProduct
from django.contrib.auth.models import User
from regions.models import Commune, Wilaya
from produits.models import Produit
from django.contrib.auth.models import Group
from medecins.models import Medecin
from clients.models import *
from django.contrib.auth.models import User
# from accounts.models import UserProfile
# from rapports.models import Rapport
# from django.db.models import Q,F,Max,Count,ExpressionWrapper

from plans.models import Plan
import datetime
from accounts.models import UserProxy
import json
from liliumpharm.redis_cli import RedisConnect

redis=RedisConnect()




for usr in UserProxy.objects.exclude(username__in=[
"liliumdz","ibtissemdz","BillalDZ","Medecin_Recycle_Bin","Pharmacie_Recycle_Bin","BillelDZ","AHMEDDZ","yasmindz","kenzadz","SihemDZ","MeriemDZ","sabrinadz","mohammed"]):

    print(usr,"**************************")
    if usr.is_superuser:
        users=UserProxy.objects.all()
    elif usr.userprofile.rolee =="CountryManager":
        users=UserProxy.objects.filter(userprofile__commune__wilaya__pays=usr.userprofile.commune.wilaya.pays)
    else:    
        users=[ *usr.userprofile.usersunder.all(), usr ]

    medecins_list=Medecin.objects.filter(users__in=users).distinct()


    ################### CREATING MEDECINS CACHING  #############################

    redis.set_key(f"{usr.username}_medecins",json.dumps([
        {
            "id":m.id,
            "nom":m.get_id_name_region(),
            "specialite":m.specialite,
            # "last_visite":m.get_last_visite()
            "last_visite":m.get_last_visite()

        } 
    for m in medecins_list]))


################### CREATING COMMERCIAL CACHING  #############################
    # medecins_list=Medecin.objects.filter(users__in=users,specialite__in=["Pharmacie","Grossiste","SuperGros"]).distinct()
    medecins_list=Medecin.objects.filter(specialite__in=["Pharmacie","Grossiste","SuperGros"]).distinct()

    redis.set_key(f"{usr.username}_commercials",json.dumps([
        {
            "id":m.id,
            "nom":m.get_id_name_region(),
            "specialite":m.specialite,
            "last_visite": m.get_last_visite2()
        } 
    for m in medecins_list]))


################### CREATING PHARMACY AND GROSSISTE CACHING  #############################
    for spc in ["Pharmacie","Grossiste"]:
        medecins_list=Medecin.objects.filter(users__in=users,specialite=spc).distinct()




        redis.set_key(f"{usr.username}_{spc.lower()}",json.dumps([
            {
                "id":m.id,
                "nom":m.get_id_name_region(),
                "specialite":m.specialite,
                "last_visite":m.get_last_visite()
            } 
        for m in medecins_list]))





# Iterate over each user
# for usr in UserProxy.objects.exclude(username__in=["liliumdz","ibtissemdz","BillalDZ","MedBin","BillelDZ","AHMEDDZ","yasmindz","kenzadz","SihemDZ","MeriemDZ","sabrinadz"]):
#     print(usr, "**************************")
#     if usr.is_superuser:
#         users = UserProxy.objects.all()
#     elif usr.userprofile.rolee == "CountryManager":
#         users = UserProxy.objects.filter(userprofile__commune__wilaya__pays=usr.userprofile.commune.wilaya.pays)
#     else:
#         users = [*usr.userprofile.usersunder.all(), usr]

#     # Gather all medecins once
#     medecins_list_all = Medecin.objects.filter(users__in=users).distinct()
    
#     # Filter medecins for commercials
#     medecins_list_commercials = medecins_list_all.filter(specialite__in=["Pharmacie", "Grossiste", "SuperGros"]).distinct()
    
#     # Caching for medecins
#     redis.set_key(f"{usr.username}_medecins", json.dumps([
#         {
#             "id": m.id,
#             "nom": m.get_id_name_region(),
#             "specialite": m.specialite,
#             "last_visite": m.get_last_visite(),
#         }
#         for m in medecins_list_all
#     ]))

#     # Caching for commercials
#     redis.set_key(f"{usr.username}_commercials", json.dumps([
#         {
#             "id": m.id,
#             "nom": m.get_id_name_region(),
#             "specialite": m.specialite,
#             "last_visite": m.get_last_visite2()
#         }
#         for m in medecins_list_commercials
#     ]))

#     # Caching for specific specialities
#     for spc in ["Pharmacie", "Grossiste"]:
#         medecins_list_specific = medecins_list_all.filter(specialite=spc).distinct()
#         redis.set_key(f"{usr.username}_{spc.lower()}", json.dumps([
#             {
#                 "id": m.id,
#                 "nom": m.get_id_name_region(),
#                 "specialite": m.specialite,
#                 "last_visite": m.get_last_visite()
#             }
#             for m in medecins_list_specific
#         ]))