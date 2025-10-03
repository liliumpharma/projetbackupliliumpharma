from django.contrib import admin
from django.urls import path,re_path,include

from .views import *


urlpatterns = [
    path("shapes/api/", ShapeAPI.as_view(), name="ShapeAPI"),
    path("products/api/<int:id>", CProductsList.as_view(), name="CProductsAPI"),
    path("CProductsExportExcel/", CProductsExportExcel.as_view(), name="CProductsExportExcel"),
    path("api/", DetailCProduct.as_view(), name="DetailCProduct"),
    path("api/<int:pk>", DetailCProduct.as_view(), name="DetailCProduct"),
    # path("api/status/", DealStatusAPI.as_view(), name="DealStatusAPI"),
    # path("print/<int:id>/", DealPDF.as_view(), name="DealPDF"),
    # path("medecin/<int:medecin_id>", DealMedecin.as_view(), name="DealMedecin"),
    path('mServices/competors/',MsCocurrents,name="MsMonthlyPlanning" ),
]
