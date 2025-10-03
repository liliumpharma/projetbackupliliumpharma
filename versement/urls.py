from django.urls import path,re_path,include
from .views import *
from .export_excel import *


urlpatterns = [
    path("/", versement_front, name="versement_front"),
    # path('api/create-versement/', CreateVersementAPI.as_view(), name='create_versement_api'),
    path('api/create-versement/', CreateVersementAPI.as_view(), name='create_versement_api'),
    path('paybook/user/list/', paybook_user_list, name='paybook_user_list'),
    path('api/creances/', CreanceAPI.as_view(), name='creance-api'),
    path('api/encaissement/', EncaissementAPI.as_view(), name='EncaissementAPI'),

    #EXCEL
    path("export_excel",AllExportExcel.as_view(), name="versementExportExcel" )

]
