from django.contrib import admin
from django.urls import path,re_path,include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.views.generic import TemplateView
from rest_framework.authtoken.views import obtain_auth_token
from .front import FrontView
from downloads.views import HomeDownloads,DownloadsAPI
from leaves.views import *
from leaves.views_excel import *
from monthly_evaluations.views import MonthlyEvaluationFront, MonthlyEvaluationMobile, monthly_evaluations_front_test
from meet.views import *
from visite_duo.views import visite_duo_front
from application_user_manual.views import ManualFront
from depenses.views import *


urlpatterns = [
    # re_path(r'^admin/', admin.site.urls),
    # i18n_patterns(r'^fr/admin/', include(admin.site.urls)),
    path('api-auth/', obtain_auth_token,name="obtain_auth_token"),
    re_path(r'^accounts/', include('accounts.urls')),
    re_path(r'^rapports/', include('rapports.urls')),
    re_path(r'^medecins/', include('medecins.urls')),
    # path('/', include('medecins.urls')),
    #re_path(r'^medecins/', include('medecins.urls')),
    re_path(r'^regions/', include('regions.urls')),
    re_path(r'^produits/', include('produits.urls')),
    re_path(r'^orders/', include('orders.urls')),
    re_path(r'^plans/', include('plans.urls')),
    re_path(r'^clients/', include('clients.urls')),
    re_path(r'^deals/', include('deals.urls')),
    re_path(r'^monthly_evaluation/', include('monthly_evaluations.urls')),
    re_path(r'^depenses/', include('depenses.urls')),
    re_path(r'^company/', include('company.urls')),
    re_path(r'^versement/', include('versement.urls')),
    re_path(r'^meet/', include('meet.urls')),
    re_path(r'^leaves/', include('leaves.urls')),
    re_path(r'^downloads/', include('downloads.urls')),
    re_path(r'^production/', include('production.urls')),
    re_path(r'^fournisseurs/', include('fournisseurs.urls')),
    re_path(r'^deplacement/', include('deplacement.urls')),

    # Leaves
    path("leaves/", LeavesAPIView.as_view(), name="Leaves"),
    path("leaves/export/excel/", ExportExcel.as_view(), name="Leaves"),

    path("leave/<int:pk>", LeaveAPIView.as_view(), name="Leave"),
    path("leaves/upload", LeaveFileUploadAPIView.as_view(), name="LeavesFileUpload"),
    path("leaves/types", LeaveTypesAPIView.as_view(), name="LeavesTypes"),
    path("leaves/front", leaves_frontend, name="LeavesFrontend"),

    # Absence
    path("absence/<int:pk>", AbsenceAPIView.as_view(), name="Absence"),
    path("absence/upload/<int:pk>", AbsenceFileUploadAPIView.as_view(), name="AbsenceFileUpload"),
    path("absence/types", AbsenceTypesAPIView.as_view(), name="AbsenceTypes"),

    # path("leaves/<int:id>", holidaysPDF, name="holidaysPDF"),

    re_path(r'^notifications/', include('notifications.urls')),
    re_path(r'^concurents/', include('concurents.urls')),
    path("downloads",HomeDownloads,name="HomeDownloads"),
    path("downloads/api",DownloadsAPI.as_view(),name="DownloadsAPI"),
    path('',FrontView.as_view(),name="Home"),

    #MonthlyEvaluations
    path("monthly_evaluations_front", MonthlyEvaluationFront.as_view(), name="MonthlyEvaluationsFrontEnd"),
    path("monthly_evaluations_front_test", monthly_evaluations_front_test, name="MonthlyEvaluationsFrontEndTest"),
    path('monthly_evaluations_front_mobile/', MonthlyEvaluationMobile.as_view(), name='monthly_evaluation_mobile'),

    #VisiteDuo
    path("visite_duo_front", visite_duo_front, name="VisiteDuoFrontEnd"),

    #ApplicationUserManual
    path("manual/", ManualFront, name="manual_front"),
    
    #Depenses
    # path("depenses/", depenses_front, name="depenses_front"),
    path('depenses_front_mobile/', depense_mobile, name='depense_mobile'),

    #Meet
    # path("meet_front", meet_front, name="meet_front"),
    #evaluations
    path('evaluations/', include('evaluations.urls')),



]+  static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    # If no prefix is given, use the default language
    prefix_default_language=False
)
urlpatterns += [
    re_path(r'(?P<path>.*)', FrontView.as_view(), name='home')
]

admin.site.site_header = 'administration'
