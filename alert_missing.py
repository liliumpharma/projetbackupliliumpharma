import os
import django
import subprocess 


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'liliumpharm.settings')
django.setup()



import calendar
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.contrib.auth.models import User
from rapports.models import Rapport
from plans.models import * 
from leaves.models import *
from datetime import date, timedelta
from leaves.models import Absence




# SENDING MAILS FOR MISSING RAPPORTS 

yesterday = date.today() - timedelta(days=1)
print("Heure système datetime :", datetime.now())
print("yesterday :", yesterday)
print("date.today :", date.today())

 

if calendar.day_name[yesterday.weekday()] not in ["Friday", "Saturday"]:

    for usr in User.objects.filter(userprofile__speciality_rolee__in=["Medico_commercial","Commercial"]):
        try:
            r=Rapport.objects.get(user=usr,added=yesterday)
            
        except:
            if usr.email and not Leave.objects.filter(user=usr, start_date__lte=yesterday, end_date__gte=yesterday).exists() and not Absence.objects.filter(user=usr,date=yesterday).exists():
                subject="Absence de rapport"
                body=" Manque Rapport de"
                body+=f" {usr.username} "
                #ody=" E-MAIL BODY"
                email = EmailMessage(subject, body, 'server.lilium@gmail.com', [usr.email,"contact.liliumpharma@gmail.com","ramoul.fatah.rf@gmail.com","r.boutitaou@liliumpharma.com"])
                email.send()
                Absence.objects.create(user=usr, reason=f'Rapport du {yesterday} Manquant', date=yesterday)
