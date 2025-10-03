from django.urls import path,re_path,include
from .views import *

urlpatterns = [
    path("/", meet_front, name="meet_front"),
    path('api/meet/', MeetAPI.as_view(), name='meet-api'),

]

