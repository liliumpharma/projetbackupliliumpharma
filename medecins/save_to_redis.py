import threading
from medecins.models import Medecin
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
            users=User.objects.filter(pays=self.user.userprofile.commune.wilaya.pays)
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
        medecins_list=Medecin.objects.filter(users__in=users,specialite__in=["Pharmacie","Grossiste","SuperGros"]).distinct()

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