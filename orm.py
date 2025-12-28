import os
import django
from django.db.models import Count
from django.db.models.functions import TruncDate




os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'liliumpharm.settings')
django.setup()

from rapports.models import Visite
from monthly_evaluations.models import Monthly_Evaluation


from django.utils.timezone import now
from datetime import datetime, date, timedelta

aujourdhui = now()
plus_une_heure = now() + timedelta(hours=1)

aujourdhui = now() + timedelta(hours=1)
aujourdhui = aujourdhui.date()


from accounts.models import *
from leaves.models import *
from django.db.models import F
from rapports.models import *

uu = "HANIADZ"
user_by_reg = User.objects.filter(username=uu).first()
print(user_by_reg)
date_start = "2025-11-01"
date_end = "2025-11-30"
yesturday = "2025-11-06"
if user_by_reg.userprofile.speciality_rolee in ["Superviseur_regional","Superviseur_national"]:
    user_under = user_by_reg.userprofile.usersunder.exclude(id=user_by_reg.id)
elif user_by_reg.userprofile.speciality_rolee in ["Medico_commercial","Commercial"]:
    sup_user = User.objects.filter(userprofile_usersunder=user_by_reg)


visites = (Visite.objects.filter(
    rapport__added__gte=date_start, rapport__added__lte= date_end, rapport__user=user_by_reg
)#.annotate(jour=TruncDate("rapport__added"))  # 👈 regroupe par jour
  #          .values("medecin__id", "jour")               # 👈 groupement par médecin et par jour
   #         .annotate(
    #            total_visites=Count("id", distinct=True),
     #           total_users=Count("rapport__user", distinct=True),
      #      )
      )

print(f"les visites de {user_by_reg} sont {visites}")
#exit()
#visited_more_one = [
#            v["medecin__id"]
#            for v in visites
#            if v["total_visites"] == 2 and v["total_users"] == 2
#        ]
#print(visited_more_one)


for v in visites:
    if user_by_reg.userprofile.speciality_rolee in ["Superviseur_regional","Superviseur_national"]:
        visites_under = Visite.objects.filter(rapport__added=v.rapport.added, rapport__user__in=user_under,medecin=v.medecin)
        print(f"le superviseur a un visite dou le {v.rapport.added} est {visites_under}")
    elif user_by_reg.userprofile.speciality_rolee in ["Medico_commercial","Commercial"]:
        visites_super = Visite.objects.filter(rapport__added=v.rapport.added, rapport__user__in=sup_user,medecin=v.medecin)
        print(f"le delegue a un visite dou le {v.rapport.added} est {visites_under}")

exit()

leaves = Leave.objects.filter(
                            user__in=user_by_reg,
                            start_date__lte=date_end,  # Leave starts before or on the end date of the filter
                            end_date__gte=date_start,
                            ).order_by(F("start_date").asc(nulls_last=True))

#leaves_on_date = Leave.objects.filter(start_date__lte=yesturday, end_date__gte=yesturday, user=user_by_reg)
planss = Plan.objects.filter(
                day__month=date_start.month, day__year=date_start.year, user="tawfikdz"
                )

print(planss)
#print(leaves_on_date)

exit()
ME = Monthly_Evaluation.objects.filter(
            user=user, added__year=date.today().year, added__month=int('9')
        )


print(ME)