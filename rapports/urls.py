from django.urls import path, re_path, include
from .views import *
from .api.api import RapportAPI
from .api.app_api import RapportAppAPI, CommentAppAPI, VisiteAppApi, SingleRapportAPI, CommentAPI

urlpatterns = [
    path("/home", HomeRapport.as_view(), name="HomeRapport"),
    path("addrapport", aaa.as_view(), name="addrapport"),
    path("showvisit/<int:id>/", vis.as_view(), name="showvisit"),
    path("test", ListRapport.as_view(), name="test"),
    path("new", AddRapport.as_view(), name="AddRapport"),
    path("<int:id>", UpdateRapport.as_view(), name="UpdateRapport"),
    # path("PDF/", RapportPDF.as_view(), name="RapportPDF"),
    path("PDF/<int:id>", RapportSinglePDF.as_view(), name="RapportSinglePDF"),
    path("SPDF/", RapportPDF.as_view(), name="RapportPDF"),
    path("IMAGE/", RapportPDF.as_view(), name="RapportIMAGE"),
    path("csv/<int:year>", export_rapport_csv.as_view(), name="export_rapport_csv"),
    path("comments/add/<int:id>", AddComment.as_view(), name="AddComment"),
    path("<int:id>/note/set/", AddNote, name="AddNote"),
    path('api/user/<int:user_id>/', get_user_by_id, name='get_user_by_id'),
    path(
        "RapportSummaryAPIView",
        RapportSummaryAPIView.as_view(),
        name="RapportSummaryAPIView",
    ),
    path("visite/update/<int:id>", UpdateVisite.as_view(), name="UpdateVisite"),
    path("visite/delete/<int:id>", DeleteVisite.as_view(), name="DeleteVisite"),
    path("visite/new", AddVisite.as_view(), name="AddVisite"),
    path("visite/new/<int:id>", AddVisite.as_view(), name="AddVisiteId"),
    path("visites/PDF/", VisitesPDF.as_view(), name="VisitesPDF"),
    path("visites/csv/<int:id>", export_visite_csv, name="export_visite_csv"),
    # FOR EMAIL INTERFACE TO AVOID CREATING NEW APP JUST FOR AN HTML TEMPLATE
    # path("email",email.as_view(),name="email"),
    path(
        "rapports-utilisateur/",
        obtenir_rapports_utilisateur,
        name="rapports_utilisateur",
    ),
    path("api", RapportAPI.as_view(), name="RapportAPI"),
    path("app/api", RapportAppAPI.as_view(), name="RapportAppAPI"),
    path("app/api/<int:id>", RapportAppAPI.as_view(), name="RapportAppPostAPI"),
    path(
        "app/api/single/<int:id>", SingleRapportAPI.as_view(), name="SingleRapportAPI"
    ),
    path("app/comment/api", CommentAppAPI.as_view(), name="CommentAppAPI"),
    path("comment/api", CommentAPI.as_view(), name="CommentAPI"),
    path(
        "SupprimerDoublonsRapportsView",
        SupprimerDoublonsParDateView.as_view(),
        name="SupprimerDoublonsRapportsView",
    ),
    path("visites/app/api/<int:id>", VisiteAppApi.as_view(), name="VisiteAppApi"),
    path("visites/app/api/", VisiteAppApi.as_view(), name="VisiteAppApi"),
    path(
        "api/communes_non_visitees/",
        NonVisitedCommunesAPIView.as_view(),
        name="commune_non_visitees",
    ),
    path(
        "api/visites_communes_multiple/",
        MultipleVisitedCommunesAPIView.as_view(),
        name="visites_communes_multiple",
    ),
    path(
        "api/visites_clients_multiple/",
        MultipleVisitedMedecinsAPIView.as_view(),
        name="visites_clients_multiple",
    ),
    path(
        "api/client_non_visites/",
        MedecinsNonVisitesAPIView.as_view(),
        name="client_non_visites",
    ),
    path("griffes-passages", griffePassageFront.as_view(), name="griffePassageFront"),
    path(
        "griffes-passages-pharmacies",
        griffePassagePharmacieFront.as_view(),
        name="griffePassagePharmacieFront",
    ),
    path("generate-pages/", generate_pages, name="generate_pages_medical"),
    path("generate-pages_test/", generate_pages_task, name="generate_pages_medical_test"),
    path(
        "generate_pages_commercial/",
        generate_pages_pharmacie,
        name="generate_pages_commercial",
    ),
    path(
        "generate_pages_commercial_test/",
        generate_pages_pharmacie_task,
        name="generate_pages_commercial_test",
    ),
    path("", reports_front, name="rapport_front_test"),
    # path("generate-pdf/", generate_pdf_view, name="generate_pdf"),
    path('admin/anomalies/print/', anomalies_print_view, name='anomalies-print'),


    # path('send-notification/', SendNotificationView.as_view(), name='send_notification'),

]
