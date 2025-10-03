from django.urls import path,include,re_path
from .api.api import PaysApi

urlpatterns = [
        #------------------API ROUTES-----------------------------------#
        path('pays/api', PaysApi.as_view(),name='PaysApi'),
]
