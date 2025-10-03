import os
import django
import sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'liliumpharm.settings')
django.setup()

from django.contrib.auth.models import User


for user in User.objects.all():
    profile=user.userprofile 
    profile.conge+=2.5
    profile.save()
