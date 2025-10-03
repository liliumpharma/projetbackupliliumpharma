from datetime import date
from .models import *
from django.http import Http404 
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.db.models import Q, Count
from django.utils import timezone
from django.shortcuts import render,redirect
from django.core.mail import EmailMessage
from django.views.generic import TemplateView
from rest_framework.authtoken.models import Token
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.shortcuts import redirect
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response


@login_required
def meet_front(request):
    return render(request, "meet/index.html")

class MeetAPI(APIView):
    def get(self, request):
        today = date.today()
        us = request.user.username
        user = User.objects.filter(username=us)
        meets = Meet.objects.filter(user__in=user, date_meet=today)
        
        response = []
        for meet in meets:
            m = {
                'id': meet.id,
                'added': meet.added,
                'title': meet.title,
                'date_meet': meet.date_meet,
                'heure_debut': meet.heure_debut.strftime('%H:%M:%S'),
                'heure_fin': meet.heure_fin.strftime('%H:%M:%S'),
                'user_count': meet.user.count(),  # Nombre d'utilisateurs associés à cette réunion
                'note': meet.note,
                'link': meet.link,
            }
            response.append(m)
        return Response(response)