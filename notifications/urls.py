from django.urls import path,re_path,include
from .views import *

urlpatterns = [
    # path('api/<int:commune>/<str:name>',MedecinAPI.as_view(),name="MedecinAPI" ),
    path('api/',NotificationAPI.as_view(),name="NotificationAPI" ),
    path('get-unread-notifications/', get_unread_notifications, name='get-unread-notifications'),
    path('mark-notifications-read/', mark_notifications_read, name='mark-notifications-read'),
]
