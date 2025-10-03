import os
import django
import subprocess 


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'liliumpharm.settings')
django.setup()

from django.contrib.auth.models import User
from medecins.models import Medecin


medecins_sans_user = Medecin.objects.filter(users__isnull=True)
medecins_sans_user.delete()