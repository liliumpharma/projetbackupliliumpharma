# urls.py
from django.urls import path
from .views import *


urlpatterns = [
    path('report/', ReportView.as_view(), name='ReportView'),
]
