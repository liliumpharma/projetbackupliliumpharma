import os
import django
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.db.models import Q





os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'liliumpharm.settings')
django.setup()

from rapports.models import Visite
from monthly_evaluations.models import Monthly_Evaluation


from django.utils.timezone import now
import datetime
from django.utils import timezone



from accounts.models import *
from leaves.models import *
from django.db.models import F
from rapports.models import *

uu = "itedaldz"
usr = User.objects.filter(username=uu).first()
print(usr)
annee = 2025
mois = 12
start_of_month = datetime.datetime(annee, mois, 1)
print(f" start_of_month {start_of_month}")
if mois == 12:
    end_of_month = datetime.datetime(annee + 1, 1, 1)
else:
    end_of_month = datetime.datetime(annee, mois + 1, 1)

print(f"end_of_month {end_of_month}")

medecins_associes = Medecin.objects.filter(users=usr)
visites_specified_mois = Visite.objects.filter(
            rapport__added__gte=start_of_month,
            rapport__added__lt=end_of_month,
            rapport__user=usr,
            medecin__in=medecins_associes,
        )
print(f"visites_specified_mois {visites_specified_mois}")
visites_communes_counts = (
            visites_specified_mois.values("medecin__commune")
            .annotate(num_visites=Count("id"))
            .filter(num_visites__gt=1)
        )
print(f"visites_communes_counts {visites_communes_counts}")


communes_ids = [item["medecin__commune"] for item in visites_communes_counts]

print(f"communes_ids {communes_ids}")

communes_visitees = Commune.objects.filter(id__in=communes_ids).annotate(
    nombre_de_visites=Count(
        "medecin__visite",
        filter=Q(
            medecin__visite__rapport__added__gte=start_of_month,
            medecin__visite__rapport__added__lt=end_of_month,
            medecin__visite__rapport__user=usr,
        ),
    )
)
print(f"communes_visitees {communes_visitees}")
medecins_multiple_visites_table = []

for commune in communes_visitees:
    medecins_multiple_visites_table.append(
                {
                    "id": commune.id,
                    "nom": commune.nom,
                    "nombre_de_visites": commune.nombre_de_visites,
                }
            )

print(f"medecins_multiple_visites_table {medecins_multiple_visites_table}")

total_communes_visitees = len(medecins_multiple_visites_table)

        # Préparer les données de réponse
response_data = {
            "total_communes_visitees": total_communes_visitees,
            "communes": medecins_multiple_visites_table,
        }


print(f"response_data {response_data}")
#exit()
#visited_more_one = [
#            v["medecin__id"]
#            for v in visites
#            if v["total_visites"] == 2 and v["total_users"] == 2
#        ]
#print(visited_more_one)

