from django.shortcuts import render
from .models import *
from .serializers import *
from django.http import Http404 
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.db.models import Q, Count
from django.utils import timezone


from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import authentication, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from django.shortcuts import render,redirect
from django.core.mail import EmailMessage

from django.contrib.auth.decorators import login_required


from rapports.models import *
from medecins.models import *

from datetime import date

# Create your views here.
@login_required
def visite_duo_front(request):

    return render(request, "visite_duo/index.html")