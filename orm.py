import os
import django
from django.db.models import Count
from django.db.models.functions import TruncDate




os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'liliumpharm.settings')
django.setup()

from rapports.models import Visite

all = (
    Visite.objects
    .annotate(jour=TruncDate('rapport__added'))  # le champ de date dans Rapport
    .values('medecin', 'jour')                   # group by medecin + jour
    .annotate(total=Count('id'))                 # count des visites
    .order_by('medecin', 'jour')
)

#(
#    Visite.objects
#    .annotate(jour=TruncDate('rapport__added'))  # champ de date dans Rapport
#    .values('medecin', 'jour')                   # group by medecin + jour
#    .annotate(total=Count('id'))                 # compter les visites
#    .filter(total__gte=2)                        # seulement 2 ou plus
#    .order_by('medecin', 'jour')
#)
#.filter(total=2)

for item in all:
    if item['total'] == 2:
        pass
        #print(item)
        #print(item['rapport'].user)


from django.utils.timezone import now
from datetime import datetime, date, timedelta

aujourdhui = now()
plus_une_heure = now() + timedelta(hours=1)

aujourdhui = now() + timedelta(hours=1)
aujourdhui = aujourdhui.date()

print("Avant :", aujourdhui)
print("Après :", plus_une_heure.date())

print(datetime.today().date())

from django.utils import timezone
import calendar

today = timezone.now()
first_day_last_month = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
last_day_last_month = today.replace(day=1) - timedelta(days=1)

print(first_day_last_month)
print(last_day_last_month)

y=2025
m=9
from accounts.models import *
a= User.objects.filter(userprofile__speciality_rolee__in=["Medico_commercial", "Commercial"], userprofile__region="Sud")
print(a)
exit()
first_day_last_month = datetime(y, m, 1)
last_day_last_month = last_day = datetime(y, m, calendar.monthrange(y, m)[1])

print(first_day_last_month)
print(last_day_last_month)

print(first_day_last_month.month)

