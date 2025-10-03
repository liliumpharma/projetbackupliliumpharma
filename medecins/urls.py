from django.urls import path, re_path, include
from .api.api import *
#from .api.app_api import MedecinAppAPI, NewMedecinList, PlanMedecinAPI
from medecins.api.app_api import MedecinAppAPI, NewMedecinList, PlanMedecinAPI, SaveRedisThread
from medecins.save_to_redis import SaveRedisThread

from .views import *
from .views_excel import *
APPEND_SLASH = True

urlpatterns = [
    path("api/<int:commune>/<str:name>", MedecinAPI.as_view(), name="MedecinAPI"),
    path("api/", MedecinFrontAPI.as_view(), name="MedecinFrontAPI"),
    path("add/", AddMedecin.as_view(), name="AddMedecin"),
    path('ajax/communes/', get_communes, name='get_communes'),
    path("update/<int:id>", UpdateMedecin.as_view(), name="UpdateMedecin"),
    path("list/", HomeMedecin.as_view(), name="HomeMedecin"),
    path("visites/PDF/<int:id>/", VisitesMedecin.as_view(), name="VisitesMedecin"),
    path("list/show/", MedecinListPDF.as_view(), name="MedecinListPDF"),
    path("<int:id>/flag", ChangeFlag, name="ChangeFlag"),
    path("update-Medecins/", updateredis, name="update-Medecins"),
    path("last/six/<int:id>", medecin_last_six_months, name="medecin_last_six_months"),
    path("users", ChangeUser, name="ChangeUser"),
    path("app/api/<int:id>", MedecinAppAPI.as_view(), name="MedecinAppAPI"),
    path("app/api/", MedecinAppAPI.as_view(), name="MedecinAppAPI"),
    path("app/api/new/search", NewMedecinList.as_view(), name="NewMedecinList"),
    path("api/v2/search", MedecinAPIV2.as_view(), name="MedecinAPIV2"),
    #path("api/save/", SaveRedisThread.as_view(), name="SaveRedisThread"),
    #path("app/api/new/search", lambda request: redirect("MedecinAppAPI", permanent=True)),
    path(
        "api/v2/versement_search",
        VersementMedecinAPIV2.as_view(),
        name="VersementMedecinAPIV2",
    ),
    path("api/v2/visite_duo", MedecinVisiteDuo.as_view(), name="MedecinVisiteDuo"),
    path(
        "api/v2/medecin_visited_duo_Per_user",
        MedecinVisiteDuoPerUser.as_view(),
        name="MedecinVisiteDuoPerUser",
    ),
    path(
        "api/v2/medecin_visite_duo_per_user_with_qtt_products",
        MedecinVisiteDuoPerUserWithQttProducts.as_view(),
        name="MedecinVisiteDuoPerUserWithQttProducts",
    ),
    path(
        "api/v2/current_month_medecin_visite_duo_per_user_with_qtt_products",
        CurrentMonthMedecinVisiteDuoPerUserWithQttProducts.as_view(),
        name="CurrentMonthMedecinVisiteDuoPerUserWithQttProducts",
    ),
    path("api/medecin_per_user", medecinPerUser.as_view(), name="MedecinPerUser"),
    path(
        "api/visitedMedecinPerUser",
        visitedMedecinPerUser.as_view(),
        name="visitedMedecinPerUser",
    ),
    path("api/MedecinPerUser", MedecinPerUser.as_view(), name="MedecinPerUser"),
    path(
        "api/ListMedecinPerUser",
        ListMedecinPerUser.as_view(),
        name="ListMedecinPerUser",
    ),
    path("api/VisitsPerUser", VisitsPerUser.as_view(), name="VisitsPerUser"),
    path(
        "api/VisitsMoreThanOneTimeForMedecinPerUserPerYear",
        VisitsMoreThanOneTimeForMedecinPerUserPerYear.as_view(),
        name="VisitsMoreThanOneTimeForMedecinPerUserPerYear",
    ),
    path(
        "api/VisitsMoreThanOneTimeForMedecinPerUser",
        VisitsMoreThanOneTimeForMedecinPerUser.as_view(),
        name="VisitsMoreThanOneTimeForMedecinPerUser",
    ),
    path(
        "api/MedecinsNonVisites",
        MedecinsNonVisites.as_view(),
        name="MedecinsNonVisites",
    ),
    path(
        "api/SupervisedUsersView",
        SupervisedUsersView.as_view(),
        name="SupervisedUsersView",
    ),
    path(
        "api/PharmaciesGrossitesVisitsPerUser",
        PharmaciesGrossitesVisitsPerUser.as_view(),
        name="PharmaciesGrossitesVisitsPerUser",
    ),
    path(
        "api/SuperGrossitesVisitsPerUser",
        SuperGrossitesVisitsPerUser.as_view(),
        name="SuperGrossitesVisitsPerUser",
    ),
    path(
        "api/StatisticMedecinsPerUser",
        StatisticMedecinsPerUser.as_view(),
        name="StatisticMedecinsPerUser",
    ),
    path("api/AllMedecinsApi", AllMedecinsApi.as_view(), name="AllMedecinsApi"),
    path(
        "pdf/StatisticMedecinsPerUser",
        PdfStatisticMedecinsPerUser,
        name="PdfStatisticMedecinsPerUser",
    ),
    path("MedecinInfo/", MedecinInfo.as_view(), name="MedecinInfo"),
    path("change_medecin/", ChangeMedecin, name="ChangeMedecin"),
    # HELP
    path("update_wilaya/", update_wilaya, name="update_wilaya"),
    path("delete_medecin/", DeleteMedecinView.as_view(), name="delete_medecin"),
    path("app/plan/api/", MedecinAppAPI.as_view(), name="PlanMedecinAPI"),
    # Excel
    path("export/excel", AllExportExcel.as_view(), name="AllMedecinExportExcel"),
    path(
        "export/listeMedecin",
        ListMedecinPerUserExcel.as_view(),
        name="ListMedecinPerUserExcel",
    ),
    path("upload_excel/", upload_excel, name="upload_excel"),
    path("excel-loading/", excel_loading_view, name="excel_loading"),
    path('delete-medecins/', DeleteMedecinsView.as_view(), name='delete_medecins'),

]

