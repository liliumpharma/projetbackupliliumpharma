from django.urls import path

from .views import *

urlpatterns = [
    # API
    path('api/users_data', UserDataAPIView.as_view(), name="users_data"), 
    path('api/super/gros/', SuperGrosAPI.as_view(), name="super_gros_list"), 
    path('api/month_comment', MonthCommentAPIView.as_view(), name="month_comment"), 
]
