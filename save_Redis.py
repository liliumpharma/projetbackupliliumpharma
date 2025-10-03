
import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "liliumpharm.settings")  # adapte 'server' au nom de ton projet
django.setup()

import threading
from medecins.models import Medecin
from clients.models import Client
from django.contrib.auth.models import User
from liliumpharm.redis_cli import RedisConnect
import json 


class SaveRedisThread(threading.Thread):
    def __init__(self, thread_name,user):
        threading.Thread.__init__(self)
        self.thread_name = thread_name
        # self.thread_ID = thread_ID
        self.user=user


    def run(self):
        print(str(self.thread_name))
        self.save_in_redis()
        print("done generating")


    def save_in_redis(self):
        
        print("saving for user ", self.user)

        redis=RedisConnect()

        if self.user.is_superuser:
            users=User.objects.all()
        elif self.user.userprofile.rolee =="CountryManager":
            # users=User.objects.filter(pays=self.user.userprofile.commune.wilaya.pays)
            users = User.objects.filter(
                userprofile__commune__wilaya__pays=self.user.userprofile.commune.wilaya.pays
            )

        else:    
            users=[ *self.user.userprofile.usersunder.all(), self.user ]


        medecins_list=Medecin.objects.filter(users__in=users).distinct()


        ################### CREATING MEDECINS CACHING  #############################

        redis.set_key(f"{self.user.username}_medecins",json.dumps([
            {
                "id":m.id,
                "nom":m.nom,
                "specialite":m.specialite,
                "last_visite":f'{m.get_last_visite()}'
            } 
        for m in medecins_list]))

        # print(medecins_list)
        print("saved  medecins for user ", self.user)

    ################### CREATING COMMERCIAL CACHING  #############################
        medecins_list=Medecin.objects.filter(users__in=users,specialite__in=["Pharmacie","Grossiste"]).distinct()

        redis.set_key(f"{self.user.username}_commercials",json.dumps([
            {
                "id":m.id,
                "nom":m.nom,
                "specialite":m.specialite,
                "last_visite":f'{m.get_last_visite()}'
            } 
        for m in medecins_list]))

        # print(medecins_list)
        print("saved  commercials for user ", self.user)


    ################### CREATING PHARMACY AND GROSSISTE CACHING  #############################
        for spc in ["Pharmacie","Grossiste"]:
            medecins_list=Medecin.objects.filter(users__in=users,specialite=spc).distinct()
            redis.set_key(f"{self.user.username}_{spc.lower()}",json.dumps([
                {
                    "id":m.id,
                    "nom":m.nom,
                    "specialite":m.specialite,
                    "last_visite":f'{m.get_last_visite()}'
                } 
            for m in medecins_list]))   
            # print(medecins_list)
            print(f"saved  {self.user.username}_{spc.lower()} for user ", self.user) 
        
    ################### CREATING SUPERGROS CACHING  #############################
        for spc in ["SuperGros"]:
            # Sauvegarde globale des SuperGros
            
            supergros_list = Client.objects.filter(supergro=True)
            redis.set_key("supergros", json.dumps(list(supergros_list.values())))

            # Sauvegarde formatée
            data_to_save = [
                {"id": m.id, "name": m.name}
                for m in medecins_list
            ]
            print("📦 Données sauvegardées dans Redis:", data_to_save)

            redis.set_key(f"{spc.lower()}", json.dumps(data_to_save))
            print(f"✅ saved {self.user.username}_{spc.lower()} for user {self.user}")

            
# ---------- EXÉCUTION DIRECTE ----------
if __name__ == "__main__":
    user = User.objects.first()  # Choisir un utilisateur
    t = SaveRedisThread("test_thread", user)
    t.start()
