from django.shortcuts import render
from django.http import Http404 
from django.http import HttpResponse



from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import authentication, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from rest_framework.authtoken.models import Token
from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required



from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def ManualFront(request):  
    return render(request, "manual/index.html")        
