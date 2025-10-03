from django.urls import path
from .views import *

urlpatterns = [
    path('front/', front_main, name='front_main'),
    path('addfront/', front_add, name='front_add'),
    path('proxy/', proxy_openrouteservice, name='proxy_openrouteservice'),
    path('deplacement/create/', create_deplacement, name='create_deplacement'),
    path('api/', get_deplacements, name='get_deplacements'),
    path('api/<int:deplacement_id>/update_status/', update_status, name='update_status'),



]


