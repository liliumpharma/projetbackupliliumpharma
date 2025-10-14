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
        print(item)
        #print(item['rapport'].user)