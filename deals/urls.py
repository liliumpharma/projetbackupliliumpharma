from django.contrib import admin
from django.urls import path,re_path,include

from .views import *


urlpatterns = [
    path("api/", DealsAPI.as_view(), name="Deals"),
    path("api/types/", DealTypesAPI.as_view(), name="DealTypesAPI"),
    path("api/status/", DealStatusAPI.as_view(), name="DealStatusAPI"),
    path("print/<int:id>/", DealPDF.as_view(), name="DealPDF"),
    path("medecin/<int:medecin_id>", DealMedecin.as_view(), name="DealMedecin"),
    path("DealExportExcel/", DealExportExcel.as_view(), name="DealExportExcel"),
]
