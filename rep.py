import os
import django
import subprocess 


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'liliumpharm.settings')
django.setup()

from rapports.models import Rapport

all = Rapport.objects.filter(can_update=True).update(can_update=False)