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


user_by_reg = User.objects.filter(username="aminadz")
print(user_by_reg)
date_start = "2025-11-06"
date_end = "2025-11-06"
yesturday = "2025-11-06"


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