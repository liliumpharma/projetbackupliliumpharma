import os
import django
import subprocess 


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'liliumpharm.settings')
django.setup()


import calendar

from django.db.models import Q
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.contrib.auth.models import User
from rapports.models import Rapport
from leaves.models import Absence
from plans.models import * 
from datetime import date, timedelta
from django.template.loader import render_to_string 
from rest_framework.response import Response
from leaves.models import*





# ####   DATABASE BACKUP 



# os.system("./utils/dump_all.sh")

# os.system("bash -c  'zip -r data.zip utils/data' ")









# print("email sent")






# GENERATING RAPPORTS 
    

# for p in  Plan.objects.filter(user__userprofile__speciality_rolee in [""],plantask__isnull=False,day=datetime.datetime.today()):
#     try:
#         rapport_exist = Rapport.objects.filter(added=p.day, user=p.user).exists()

#         if not rapport_exist:
#             print("Created rapport for user"+ p.user)
#             Rapport.objects.create(user=p.user,added=p.day,image="rapports/rapport.jpeg")
#     except:
#         print("alreday exists ")
#         pass   

import datetime

# Récupérer la date d'hier
#previous_day = datetime.datetime.today() - datetime.timedelta(days=1)
previous_day = date.today() -timedelta(days=1)

# Filtrer les plans d'hier
for p in Plan.objects.filter(day=previous_day):
    try:
        if not p.isfree:
            # Vérifier si l'utilisateur a le rôle de superviseur national
            if p.user.userprofile.speciality_rolee in ["CountryManager","Admin"] or p.user.is_superuser:
                # Vérifier si les tâches ne sont pas vides
                if p.plantask_set.exists():
                    # Créer un rapport s'il n'existe pas encore pour cet utilisateur et cette date
                    rapport_exist = Rapport.objects.filter(added=p.day, user=p.user).exists()
                    if not rapport_exist:
                        absences_on_date = Absence.objects.filter(date=p.day, user=p.user)
                        if absences_on_date.exists():
                            print("There are absences on the same date as the report.")
                            break

                        leaves_on_date = Leave.objects.filter(start_date__lte=p.day, end_date__gte=p.day, user=p.user)
                        if leaves_on_date.exists():
                            print("There are leaves covering the same date as the report.")
                            break
                        print("Created rapport for user ", p.user)
                        Rapport.objects.create(user=p.user, added=p.day, image="rapports/rapport.jpeg")
                        #Absence.objects.create(user=p.user, reason=f'Rapport du {previous_day} Manquant', date=previous_day)
    except:
        print("Error occurred while processing user", p.user)

# Filtrer les plans des superviseur nationaux et commerciaux
supervisors = User.objects.filter(userprofile__speciality_rolee__in=["Superviseur_national", "Medico_commercial","Commercial","Superviseur_regional"])
for p in Plan.objects.filter(day=previous_day, user__in = supervisors):
    try:
        if not p.isfree:
            if p.user.userprofile.speciality_rolee in ["Medico_commercial","Commercial"]:
                if p.valid_tasks and p.valid_commune and p.valid_clients:
                    if p.plantask_set.exists():
                        rapport_exist = Rapport.objects.filter(added=p.day, user=p.user).exists()
                        if not rapport_exist:
                            absences_on_date = Absence.objects.filter(date=p.day, user=p.user)
                            if absences_on_date.exists():
                                print("There are absences on the same date as the report.")
                                break
                            
                            leaves_on_date = Leave.objects.filter(start_date__lte=p.day, end_date__gte=p.day, user=p.user)
                            if leaves_on_date.exists():
                                print("There are leaves covering the same date as the report.")
                                break
                            print("Created rapport for user ", p.user)
                            Rapport.objects.create(user=p.user, added=p.day, image="rapports/rapport.jpeg")
            else:
                if p.valid_tasks and p.valid_commune and p.valid_clients:
                    if p.plantask_set.exists():
                        # Créer un rapport s'il n'existe pas encore pour cet utilisateur et cette date
                        rapport_exist = Rapport.objects.filter(added=p.day, user=p.user).exists()
                        if not rapport_exist:
                            print("Created rapport for user ", p.user)
                            absences_on_date = Absence.objects.filter(date=p.day, user=p.user)
                            if absences_on_date.exists():
                                print("There are absences on the same date as the report.")
                                break
                            
                            leaves_on_date = Leave.objects.filter(start_date__lte=p.day, end_date__gte=p.day, user=p.user)
                            if leaves_on_date.exists():
                                print("There are leaves covering the same date as the report.")
                                break
                            Rapport.objects.create(user=p.user, added=p.day, image="rapports/rapport.jpeg")
    except:
        print("Error occurred while processing user", p.user)


# SENDING MAILS FOR MISSING RAPPORTS 

# yesturday = date.today() -timedelta(days=1)
yesturday = date.today() -timedelta(days=1)

 

if calendar.day_name[yesturday.weekday()] not in ["Friday", "Saturday"]:

    # Preparing Query
    # query = Q(userprofile__recive_mail=True)

    query = ~Q(leave__approved='ACCEPTED', leave__start_date=yesturday, leave__end_date__gte=yesturday)
    excluded_profiles = ["Office", "Finance_et_comptabilité", "gestionnaire_de_stock", "Admin"]

    # for usr in User.objects.filter(query, userprofile__hidden=False, userprofile__is_human=True).exclude(userprofile__speciality_rolee__in=excluded_profiles):
    #for usr in User.objects.filter(query, is_active=True, userprofile__hidden=False, userprofile__is_human=True).exclude(userprofile__speciality_rolee__in=excluded_profiles):
    for usr in User.objects.filter(is_active=True, userprofile__hidden=False, userprofile__is_human=True).exclude(userprofile__speciality_rolee__in=excluded_profiles):
        try:
            r=Rapport.objects.get(user=usr,added=yesturday)
            print("user : "+str(usr))

            if len(r.visites_list) == 0 and len(PlanTask.objects.filter(plan__day=r.added,plan__user=usr)) == 0 :
                subject="Rapport Quotidien Lilium Pharma"
                body=render_to_string("rapports/empty_email.html",{"usr":usr,"yesturday":yesturday})
                #email = EmailMessage(subject, body, 'server.lilium@gmail.com', [usr.email,"contact.liliumpharma@gmail.com","rayanboukabous74@gmail.com","boughezala.aimen@gmail.com"])
                email = EmailMessage(subject, body, 'server.lilium@gmail.com', [usr.email,"contact.liliumpharma@gmail.com","ramoul.fatah.rf@gmail.com","r.boutitaou@liliumpharma.com"])
                email.content_subtype = 'html'
                email.send()
                print("email sent to ",usr)


        except Exception as e:
            # Create Absences
            leaves_on_date = Leave.objects.filter(start_date__lte=yesturday, end_date__gte=yesturday, user=usr).exclude(end_date=yesturday)
            if not leaves_on_date.exists():
                print("created absence for "+str(usr))
                Absence.objects.create(user=usr, reason=f'Rapport du {yesturday} Manquant', date=yesturday)




# import calendar
# from datetime import datetime, timedelta
# from django.utils import timezone
# from django.core.mail import EmailMessage
# from django.template.loader import render_to_string

# # Define the start date as March 1st, 2024
# start_date = datetime(2024, 3, 1).date()
# # Define the end date as today's date
# end_date = timezone.now().date()

# # Iterate over each day from March 1st until today
# current_date = start_date
# while current_date <= end_date:
#     yesturday = current_date - timedelta(days=1)

#     # Check if yesturday is not Friday or Saturday
#     if calendar.day_name[yesturday.weekday()] not in ["Friday", "Saturday"]:
#         query = ~Q(leave__approved='ACCEPTED', leave__start_date__lte=yesturday, leave__end_date__gte=yesturday)
#         excluded_profiles = ["Office", "Finance_et_comptabilité", "gestionnaire_de_stock", "Admin"]

#         for usr in User.objects.filter(query, userprofile__hidden=False, userprofile__is_human=True).exclude(userprofile__speciality_rolee__in=excluded_profiles):
#             try:
#                 r = Rapport.objects.get(user=usr, added=yesturday)

#                 if len(r.visites_list) == 0 and len(PlanTask.objects.filter(plan__day=r.added, plan__user=usr)) == 0:
#                     print(r.user, "has empty rapport", r.added)
#                     subject = "Rapport Quotidien Lilium Pharma"
#                     body = render_to_string("rapports/empty_email.html", {"usr": usr, "yesturday": yesturday})
#                     email = EmailMessage(subject, body, 'server.lilium@gmail.com', [usr.email, "contact.liliumpharma@gmail.com", "n.bouriah@gmail.com", "boughezala.aimen@gmail.com"])
#                     email.content_subtype = 'html'
#                     email.send()
#                     print("email sent to ", usr)
#                     Absence.objects.create(user=usr, reason=f'Rapport du {yesturday} Manquant', date=yesturday)
#             except Rapport.DoesNotExist:
#                 Absence.objects.create(user=usr, reason=f'Rapport du {yesturday} Manquant', date=yesturday)
#                 print("Absence created for"+str(usr))
#                 if usr.email:
#                     subject = "Rapport Quotidien LiliumPharma"
#                     body = render_to_string("rapports/email.html", {"usr": usr, "yesturday": yesturday})
#                     email = EmailMessage(subject, body, 'server.lilium@gmail.com', [usr.email, "contact.liliumpharma@gmail.com", "n.bouriah@gmail.com", "boughezala.aimen@gmail.com"])
#                     email.content_subtype = 'html'
#                     email.send()
#                     print("email sent to ", usr)
#             except Exception as e:
#                 print("An error occurred:", e)

#     current_date += timedelta(days=1)



