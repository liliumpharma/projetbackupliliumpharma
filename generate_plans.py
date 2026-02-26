import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'liliumpharm.settings')
django.setup()
from django.contrib.auth.models import User

from plans.models import Plan
from accounts.models import UserProfile
from rapports.views import generate_pages_pharmacie_task, generate_pages_task
from datetime import date
from calendar import monthrange
from django.http import HttpResponse
from django.shortcuts import render


today = date.today()

# month = today.month
month = 3
year = 2026

for u in User.objects.all():
    for day in range(1, monthrange(year, month)[1] + 1):
        current_date = date(year, month, day)
        if not Plan.objects.filter(day=current_date, user=u, updatable=True).exists():
            try:
                Plan.objects.create(day=current_date, user=u, updatable=True)
                print("Plan generated for "+str(u))
                #if u.id ==131:
                #generate_pages_pharmacie_task(u.id)
            except:
                pass
comp= 0

for u in User.objects.all():
    user_profile = UserProfile.objects.filter(user=u).first()
    
    if not user_profile:
        continue  # Ignorer les utilisateurs sans profil

    if user_profile.speciality_rolee == "Medico_commercial" or user_profile.speciality_rolee == "Superviseur_regional":
        print(u.id)
        print(u.username)
        print("IS Medico_commercial")
        generate_pages_task(u.id)
        generate_pages_pharmacie_task(u.id)
        comp = comp + 1

    elif user_profile.speciality_rolee == "Commercial" and u.username != "Pharmacie_Recycle_Bin":
        print(u.id)
        print(u.username)
        print("IS Commercial")
        generate_pages_pharmacie_task(u.id)
        comp = comp + 1
    
    
    print(f"On'a traite {comp} User")
