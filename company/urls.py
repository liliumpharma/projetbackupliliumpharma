# urls.py
from django.urls import path
from .views import *

urlpatterns = [
    path('companyPDF/<int:id>/', companyPDF.as_view(), name='companyPDF'),
    path('RulesPDF/<int:id>/', RulesPDF.as_view(), name='RulesPDF'),
]
