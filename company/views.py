from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication,TokenAuthentication
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated



from .models import *

class companyPDF(APIView):
    authentication_classes = (TokenAuthentication, SessionAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, id):
        company = Company.objects.get(id=id)
        return render(request, 'pdf_template.html', {'company': company})

class RulesPDF(APIView):
    authentication_classes = (TokenAuthentication, SessionAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, id):
        company = Company.objects.get(id=id)
        return render(request, 'rules.html', {'company': company})
