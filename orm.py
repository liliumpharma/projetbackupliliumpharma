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

user = User.objects.filter(username='itedaldz').first()
print(user)

ME = Monthly_Evaluation.objects.filter(
            user=user, added__year=date.today().year, added__month=int('9')
        )


print(ME)