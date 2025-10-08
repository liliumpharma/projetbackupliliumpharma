from medecins.models import Medecin
from rapports.models import Visite, Rapport
from .serializers import MedecinSerializer
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import (
    SessionAuthentication,
    TokenAuthentication,
    BasicAuthentication,
)
from rest_framework.response import Response
from rest_framework import status
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.db.models import Count
from django.core.exceptions import ObjectDoesNotExist

import datetime
from medecins.get_medecins import get_medecins
from produits.get_produits_stock import get_stock

import json
from django.http import HttpResponse
from django.db.models.functions import TruncDate
from django.contrib.auth.models import User
from datetime import datetime, date, timedelta
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q
from accounts.models import UserProfile, Rolee
from django.shortcuts import get_object_or_404


class MedecinAPI(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, commune, name, format=None):
        print("MEEDECINS VIEW APIII")
        print(name)
        if name.isdigit():
            medecins = Medecin.objects.filter(
                id=name,
                users__in=[request.user, *request.user.userprofile.usersunder.all()],
            )
        else:
            if (
                request.user.userprofile.rolee != "CountryManager"
                and not request.user.is_superuser
            ):
                medecins = Medecin.objects.filter(
                    nom__icontains=name.lower(),
                    users__in=[
                        request.user,
                        *request.user.userprofile.usersunder.all(),
                    ],
                )
            else:

                if not request.user.is_superuser:
                    medecins = Medecin.objects.filter(
                        nom__icontains=name.lower(),
                        commune__wilaya__pays__id=request.user.userprofile.commune.wilaya.pays.id,
                    )
                else:
                    medecins = Medecin.objects.filter(nom__icontains=name.lower())

        serializer = MedecinSerializer(medecins, many=True)
        return Response(serializer.data, status=200)


class MedecinFrontAPI(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def pagination_response(self, medecins, serializer, medecins_length, other):
        print(str(self))
        response = {
            "pages": medecins.paginator.num_pages,
            "result": serializer.data,
            "length": medecins_length,
            "other": other,
        }
        try:
            response["previous"] = medecins.previous_page_number()
        except:
            pass
        try:
            response["next"] = medecins.next_page_number()
        except:
            pass
        return response

    # def get(self, request, format=None):

    #     page = request.GET.get("page")
    #     medecins_list = get_medecins(request)

    #     print("############ cc bonjour")

    #     medecin_nbr = len(medecins_list) - len(
    #         medecins_list.filter(specialite__in=["Pharmacie", "Grossiste", "SuperGros"])
    #     )

    #     details = (
    #         Medecin.objects.filter(id__in=medecins_list.values("id"))
    #         .values("specialite")
    #         .annotate(dcount=Count("specialite"))
    #     )
    #     other_details = f" <b>({medecin_nbr})</b> Medecins "
    #     # other_details+=" ".join([f'<b>({detail["dcount"]})</b> {detail["specialite"]}' for detail in details])
    #     # other_details += " ".join([f'<b>({detail["dcount"]})</b> {detail["specialite"]}' for detail in sorted(details, key=lambda x: x["dcount"], reverse=True)])
    #     other_details += " ".join(
    #         [
    #             f'({detail["dcount"]}) {detail["specialite"]}'
    #             for detail in sorted(details, key=lambda x: x["dcount"], reverse=True)
    #             if detail["specialite"] not in ["Pharmacie", "Grossiste", "SuperGros"]
    #         ]
    #     )

    #     # Récupérez les détails pour "Pharmacie", "Grossiste" et "SuperGros"
    #     special_details = [
    #         f'({detail["dcount"]}) {detail["specialite"]}'
    #         for detail in sorted(details, key=lambda x: x["dcount"], reverse=True)
    #         if detail["specialite"] in ["Pharmacie", "Grossiste", "SuperGros"]
    #     ]

    #     # Ajoutez les détails spécifiques à la fin
    #     other_details += " ".join(special_details)

    #     other_details += "<br/><br/>"

    #     produitsvisites = get_stock(request)

    #     other_details += " ".join(
    #         [
    #             f'<small><b style="color:#2da231">({pv["total"]})</b> {pv["produit__nom"]}</small>'
    #             for pv in produitsvisites
    #         ]
    #     )

    #     paginator = Paginator(medecins_list, 15)
    #     medecins = paginator.get_page(page)

    #     serializer = MedecinSerializer(medecins, many=True)

    #     return Response(
    #         self.pagination_response(
    #             medecins, serializer, len(medecins_list), other_details
    #         ),
    #         status=200,
    #     )

    def get(self, request, format=None):
        print("kkkkkkkkkkk")
        commercial_input = request.GET.get("commercial")
        medecin = request.GET.get("medecin")
        print("111111111111")
        print(medecin)
        print("comcomcomcom")
        print(f" Nous somme la {commercial_input} la fin")
        #if commercial_input or (medecin and len(medecin) > 4):
        #if commercial_input or medecin:
        if 1:
            print("33333333")
            medecins_list = get_medecins(request)
            print(request)# Récupère le queryset de médecins
            print("222222222")
            # Calculez le nombre de médecins qui ne sont pas des spécialités "Pharmacie", "Grossiste", "SuperGros"
            medecin_nbr = medecins_list.exclude(
                specialite__in=["Pharmacie", "Grossiste", "SuperGros"]
            ).count()

            # Récupérez les détails des spécialités
            details = (
                Medecin.objects.filter(id__in=medecins_list.values("id"))
                .values("specialite")
                .annotate(dcount=Count("specialite"))
                .order_by("-dcount")
            )

            # Construction de la chaîne de caractères pour les détails
            other_details = f" <b>({medecin_nbr})</b> Médecins "

            other_details += " ".join(
                [
                    f'({detail["dcount"]}) {detail["specialite"]}'
                    for detail in details
                    if detail["specialite"]
                    not in ["Pharmacie", "Grossiste", "SuperGros"]
                ]
            )

            # Détails spécifiques à "Pharmacie", "Grossiste" et "SuperGros"
            special_details = [
                f'({detail["dcount"]}) {detail["specialite"]}'
                for detail in details
                if detail["specialite"] in ["Pharmacie", "Grossiste", "SuperGros"]
            ]
            other_details += " ".join(special_details)

            other_details += "<br/><br/>"

            # Récupérez les produits visités
            produitsvisites = get_stock(request)
            other_details += " ".join(
                [
                    f'<small><b style="color:#2da231">({pv["total"]})</b> {pv["produit__nom"]}</small>'
                    for pv in produitsvisites
                ]
            )
            other_details += """
            <style>
                .navbar-nav.ml-auto {
                    display: none !important;
                }
            </style>
            """
            # Pagination
            paginator = Paginator(medecins_list, 15)
            page = request.GET.get("page", 1)
            medecins = paginator.get_page(page)

            serializer = MedecinSerializer(medecins, many=True)

            return Response(
                self.pagination_response(
                    medecins, serializer, medecins_list.count(), other_details
                ),
                status=200,
            )
        serializer = MedecinSerializer(medecins, many=True)
        medecins = Medecin.objects.all()
        return Response(
                self.pagination_response(
                    medecins, serializer, medecins.count(), other_details
                ),
                status=200,
            )
    def post(self, request, format=None):
        print("kkkkkkkkkkk from post")
        commercial_input = request.GET.get("commercial")
        medecin = request.GET.get("medecin")
        print("111111111111 from post")
        print(medecin)
        print("comcomcomcom from post")
        print(f" Nous somme la {commercial_input} la fin from post")
        #if commercial_input or (medecin and len(medecin) > 4):
        #if commercial_input or medecin:
        if 1:
            print("33333333 from post")
            medecins_list = get_medecins(request)
            print(request)# Récupère le queryset de médecins
            print("222222222 from post")
            # Calculez le nombre de médecins qui ne sont pas des spécialités "Pharmacie", "Grossiste", "SuperGros"
            medecin_nbr = medecins_list.exclude(
                specialite__in=["Pharmacie", "Grossiste", "SuperGros"]
            ).count()

            # Récupérez les détails des spécialités
            details = (
                Medecin.objects.filter(id__in=medecins_list.values("id"))
                .values("specialite")
                .annotate(dcount=Count("specialite"))
                .order_by("-dcount")
            )

            # Construction de la chaîne de caractères pour les détails
            other_details = f" <b>({medecin_nbr})</b> Médecins "

            other_details += " ".join(
                [
                    f'({detail["dcount"]}) {detail["specialite"]}'
                    for detail in details
                    if detail["specialite"]
                    not in ["Pharmacie", "Grossiste", "SuperGros"]
                ]
            )

            # Détails spécifiques à "Pharmacie", "Grossiste" et "SuperGros"
            special_details = [
                f'({detail["dcount"]}) {detail["specialite"]}'
                for detail in details
                if detail["specialite"] in ["Pharmacie", "Grossiste", "SuperGros"]
            ]
            other_details += " ".join(special_details)

            other_details += "<br/><br/>"

            # Récupérez les produits visités
            produitsvisites = get_stock(request)
            other_details += " ".join(
                [
                    f'<small><b style="color:#2da231">({pv["total"]})</b> {pv["produit__nom"]}</small>'
                    for pv in produitsvisites
                ]
            )
            other_details += """
            <style>
                .navbar-nav.ml-auto {
                    display: none !important;
                }
            </style>
            """
            # Pagination
            paginator = Paginator(medecins_list, 15)
            page = request.GET.get("page", 1)
            medecins = paginator.get_page(page)

            serializer = MedecinSerializer(medecins, many=True)

            return Response(
                self.pagination_response(
                    medecins, serializer, medecins_list.count(), other_details
                ),
                status=200,
            )
        serializer = MedecinSerializer(medecins, many=True)
        medecins = Medecin.objects.all()
        return Response(
                self.pagination_response(
                    medecins, serializer, medecins.count(), other_details
                ),
                status=200,
            )
   
    # def get(self, request, format=None):
    #     # Vérifiez si des filtres sont fournis et récupérez la liste de médecins

    #     commercial_input = request.GET.get("commercial")
    #     medecin = request.GET.get("medecin")

    #     if commercial_input or (medecin and len(medecin) > 4):
    #         medecins_list = get_medecins(request)

    #         # Calculez le nombre de médecins qui ne sont pas des spécialités "Pharmacie", "Grossiste", "SuperGros"
    #         medecin_nbr = medecins_list.exclude(
    #             specialite__in=["Pharmacie", "Grossiste", "SuperGros"]
    #         ).count()

    #         # Récupérez les détails des spécialités
    #         details = (
    #             Medecin.objects.filter(id__in=medecins_list.values("id"))
    #             .values("specialite")
    #             .annotate(dcount=Count("specialite"))
    #             .order_by("-dcount")
    #         )

    #         # Construction de la chaîne de caractères pour les détails
    #         other_details = f" <b>({medecin_nbr})</b> Médecins "

    #         other_details += " ".join(
    #             [
    #                 f'({detail["dcount"]}) {detail["specialite"]}'
    #                 for detail in details
    #                 if detail["specialite"]
    #                 not in ["Pharmacie", "Grossiste", "SuperGros"]
    #             ]
    #         )

    #         # Détails spécifiques à "Pharmacie", "Grossiste" et "SuperGros"
    #         special_details = [
    #             f'({detail["dcount"]}) {detail["specialite"]}'
    #             for detail in details
    #             if detail["specialite"] in ["Pharmacie", "Grossiste", "SuperGros"]
    #         ]
    #         other_details += " ".join(special_details)

    #         other_details += "<br/><br/>"

    #         # Récupérez les produits visités
    #         produitsvisites = get_stock(request)
    #         other_details += " ".join(
    #             [
    #                 f'<small><b style="color:#2da231">({pv["total"]})</b> {pv["produit__nom"]}</small>'
    #                 for pv in produitsvisites
    #             ]
    #         )

    #         # Pagination
    #         paginator = Paginator(medecins_list, 15)
    #         page = request.GET.get("page", 1)
    #         medecins = paginator.get_page(page)

    #         serializer = MedecinSerializer(medecins, many=True)

    #         return Response(
    #             self.pagination_response(
    #                 medecins, serializer, medecins_list.count(), other_details
    #             ),
    #             status=200,
    #         )


class MedecinAPIV2(APIView):
    authentication_classes = (
        TokenAuthentication,
        SessionAuthentication,
    )
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        medecins_list = []
        user = request.user
        start = request.GET.get("name")
        if request.user.userprofile.speciality_rolee == "Commercial":
            medecins = Medecin.objects.filter(
                Q(nom__icontains=start) | Q(id__startswith=start), users=user
            )
            for medecin in medecins:
                medecins_list.append(
                    {
                        "nom": str(medecin.id)
                        + " "
                        + medecin.nom
                        + " / "
                        + medecin.specialite,
                    }
                )
        else:
            specialites_a_exclure = ["Pharmacie", "Grossiste", "SuperGros"]
            medecins = Medecin.objects.filter(
                Q(nom__icontains=start) | Q(id__startswith=start), users=user
            )
            medecins = medecins.exclude(specialite__in=specialites_a_exclure)

            for medecin in medecins:
                medecins_list.append(
                    {
                        "nom": str(medecin.id)
                        + " "
                        + medecin.nom
                        + " / "
                        + medecin.specialite,
                    }
                )
        return HttpResponse(json.dumps(medecins_list), content_type="application/json")


class VersementMedecinAPIV2(APIView):
    authentication_classes = (
        TokenAuthentication,
        SessionAuthentication,
    )
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        print(str(request.user))
        medecins_list = []
        start = request.GET.get("name")
        specialites_a_inclure = ["Pharmacie", "Grossiste", "SuperGros"]

        # Filter medecins by name or id
        medecins = Medecin.objects.filter(
            specialite__in=specialites_a_inclure, users=request.user
        )
        medecins = medecins.filter(Q(nom__startswith=start) | Q(id__startswith=start))

        # Filter medecins by specialite and associated with request.user

        for medecin in medecins:
            medecins_list.append(
                {
                    "nom": str(medecin.id) + " " + medecin.nom,
                }
            )

        print(str(medecins_list))

        return HttpResponse(json.dumps(medecins_list), content_type="application/json")


class MedecinVisiteDuo(APIView):
    authentication_classes = (
        TokenAuthentication,
        SessionAuthentication,
    )
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        year = request.GET.get("year")

        medecins_visites = (
            Visite.objects.filter(rapport__added__year=year)
            .values("medecin", "rapport__added")
            .annotate(nombre_visites=Count("medecin"))
            .filter(nombre_visites=2)
        )

        medecins_visites = medecins_visites.annotate(
            num_users=Count("rapport__user", distinct=True)
        ).filter(num_users=2)

        medecins = []
        for visite in medecins_visites:
            medecin_id = visite["medecin"]
            medecin = Medecin.objects.get(id=medecin_id)

            # Récupérer les utilisateurs associés à la visite
            utilisateurs = User.objects.filter(
                rapport__visite__medecin_id=medecin_id,
                rapport__added=visite["rapport__added"],
            ).distinct()

            medecins.append(
                {
                    "id": medecin.id,
                    "nom": medecin.nom,
                    "date_visite": visite["rapport__added"],
                    "utilisateurs": [
                        utilisateur.username for utilisateur in utilisateurs
                    ],
                }
            )

        return Response(medecins)


class MedecinVisiteDuoPerUser(APIView):
    authentication_classes = (
        TokenAuthentication,
        SessionAuthentication,
    )
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        year = request.GET.get("year")
        user = request.GET.get("user")
        date_min = request.GET.get("date_min")  # Date minimale au format 'YYYY-MM-DD'
        date_max = request.GET.get("date_max")  # Date maximale au format 'YYYY-MM-DD'

        # Convertir les dates en objets datetime
        date_min = datetime.strptime(date_min, "%Y-%m-%d").date() if date_min else None
        date_max = datetime.strptime(date_max, "%Y-%m-%d").date() if date_max else None

        medecins_visites = (
            Visite.objects.filter(rapport__added__year=year)
            .values("medecin", "rapport__added")
            .annotate(nombre_visites=Count("medecin"))
            .filter(nombre_visites=2)
        )

        medecins_visites = medecins_visites.annotate(
            num_users=Count("rapport__user", distinct=True)
        ).filter(num_users=2)

        medecins = []
        for visite in medecins_visites:
            medecin_id = visite["medecin"]
            medecin = Medecin.objects.get(id=medecin_id)

            # Récupérer les utilisateurs associés à la visite
            utilisateurs = User.objects.filter(
                rapport__visite__medecin_id=medecin_id,
                rapport__added=visite["rapport__added"],
            ).distinct()

            # Filtrer par date minimale et maximale
            visites_filtered = Visite.objects.filter(
                rapport__added__gte=date_min,
                rapport__added__lte=date_max,
                rapport__visite__medecin_id=medecin_id,
                rapport__added=visite["rapport__added"],
            )

            if visites_filtered.exists() and user in utilisateurs.values_list(
                "username", flat=True
            ):
                medecins.append(
                    {
                        "id": medecin.id,
                        "nom": medecin.nom,
                        "date_visite": visite["rapport__added"],
                        "utilisateurs": [
                            utilisateur.username for utilisateur in utilisateurs
                        ],
                    }
                )

        return Response(medecins)


class MedecinVisiteDuoPerUserWithQttProducts(APIView):
    authentication_classes = (
        TokenAuthentication,
        SessionAuthentication,
    )
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        year = datetime.today().year
        user = str(request.user)
        date_min = request.GET.get("date_min")
        print(str(date_min))
        default_date = date(2025, 1, 1)
        date_min = (
            datetime.strptime(date_min, "%Y-%m-%d").date() if date_min else default_date
        )
        date_max = date.today()

        medecins_visites = (
            Visite.objects.filter(rapport__added__year=year)
            .values("medecin", "rapport__added")
            .annotate(nombre_visites=Count("medecin"))
            .filter(nombre_visites__gte=2)
        )
        supervisor_users = UserProfile.objects.filter(
            usersunder=request.user, rolee=Rolee.superviseur
        ).values("user_id")

        # medecins_visites = medecins_visites.exclude(
        #     Q(medecin__rolee=Rolee.commercial) &
        #     Q(medecin__user_id__in=supervisor_users)
        # )

        medecins_visites = medecins_visites.annotate(
            num_users=Count("rapport__user", distinct=True)
        ).filter(num_users=2)

        medecins = []
        for visite in medecins_visites:
            medecin_id = visite["medecin"]
            medecin = Medecin.objects.get(id=medecin_id)

            utilisateurs = User.objects.filter(
                rapport__visite__medecin_id=medecin_id,
                rapport__added=visite["rapport__added"],
            ).distinct()

            visites_filtered = Visite.objects.filter(
                rapport__added__gte=date_min,
                rapport__added__lte=date_max,
                rapport__visite__medecin_id=medecin_id,
                rapport__added=visite["rapport__added"],
            )

            if visites_filtered.exists() and user in utilisateurs.values_list(
                "username", flat=True
            ):
                visite_data = {
                    "id": medecin.id,
                    "nom": medecin.nom,
                    "date_visite": visite["rapport__added"],
                    "utilisateurs": [
                        utilisateur.username for utilisateur in utilisateurs
                    ],
                    "produits": [],
                    "observations": [],
                }

                produits = visites_filtered.first().produits.all()
                for produit in produits:
                    visite_data["produits"].append(
                        {
                            "id": produit.id,
                            "nom": produit.nom,
                            "qtt": produit.produitvisite_set.get(
                                visite=visites_filtered.first()
                            ).qtt,
                            "prescription": produit.produitvisite_set.get(
                                visite=visites_filtered.first()
                            ).prescription,
                        }
                    )

                print(visite_data)

                observations = visites_filtered.values_list("observation", flat=True)
                visite_data["observations"] = list(observations)

                medecins.append(visite_data)

        return Response(medecins)


# class CurrentMonthMedecinVisiteDuoPerUserWithQttProducts(APIView):
#     authentication_classes = (TokenAuthentication, SessionAuthentication,)
#     permission_classes = (IsAuthenticated, )

#     def get(self, request):
#         year = datetime.today().year
#         user = str(request.user)

#         month_param = request.GET.get('month')
#         try:
#             month = int(month_param)
#             if 1 <= month <= 12:
#                 current_month = month
#             else:
#                 current_month = date.today().month
#         except (ValueError, TypeError):
#             current_month = date.today().month

#         medecins_visites = (
#             Visite.objects
#             .filter(rapport__added__year=year)
#             .filter(rapport__added__month=current_month)
#             .values('medecin', 'rapport__added')
#             .annotate(nombre_visites=Count('medecin'))
#             .filter(nombre_visites=2)
#         )

#         supervisor_users = UserProfile.objects.filter(usersunder=request.user, speciality_rolee="Superviseur_national").values('user_id')

#         medecins_visites = medecins_visites.filter(
#             Q(rapport__user__in=supervisor_users)         )

#         specialites_a_exclure = ["Pharmacie", "Grossiste", "SuperGros"]
#         medecins_visites = medecins_visites.exclude(
#             medecin__specialite__in=specialites_a_exclure
#         )


#         medecins_visites = medecins_visites.annotate(num_users=Count('rapport__user', distinct=True)).filter(num_users=2)

#         medecins = []
#         visites=[]

#         for visite in medecins_visites:
#             medecin_id = visite['medecin']
#             medecin = Medecin.objects.get(id=medecin_id)

#             utilisateurs = User.objects.filter(rapport__visite__medecin_id=medecin_id, rapport__added=visite['rapport__added']).distinct()

#             visites_filtered = Visite.objects.filter(rapport__added__month=current_month, rapport__added__year=year, rapport__visite__medecin_id=medecin_id, rapport__added=visite['rapport__added'])

#             if visites_filtered.exists() and user in utilisateurs.values_list('username', flat=True):
#                 visites.append({
#                     'id': medecin.id,
#                     'nom': medecin.nom,
#                     'date_visite': visite['rapport__added'],
#                     'utilisateurs': [utilisateur.username for utilisateur in utilisateurs],
#                     'produits': [],
#                     'observations': []
#                 })

#         nombre_medecins_visites_en_duo = len(visites)

#         data = {
#             'nombre_medecins_visites_en_duo': nombre_medecins_visites_en_duo,
#             'datas': visites,
#         }
#         return Response(data)
from datetime import datetime, date
from django.db.models import Count, Q
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView


class CurrentMonthMedecinVisiteDuoPerUserWithQttProducts(APIView):
    authentication_classes = (
        TokenAuthentication,
        SessionAuthentication,
    )
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        year = datetime.today().year
        user = request.user

        month_param = request.GET.get("month")
        try:
            month = int(month_param)
            if 1 <= month <= 12:
                current_month = month
            else:
                current_month = date.today().month
        except (ValueError, TypeError):
            current_month = date.today().month

        # Obtenir les utilisateurs superviseurs nationaux
        supervisor_users = UserProfile.objects.filter(
            usersunder=user, speciality_rolee="Superviseur_national"
        ).values_list("user_id", flat=True)

        # Filtrer les visites de médecins pour le mois courant et l'année en cours
        medecins_visites = (
            Visite.objects.filter(
                rapport__added__year=year, rapport__added__month=current_month
            )
            .values("medecin", "rapport__added")
            .annotate(
                nombre_visites=Count("medecin"),
                num_users=Count("rapport__user", distinct=True),
            )
            .filter(nombre_visites=2, num_users=2)
        )

        visites_duo = []
        specialites_a_exclure = ["Pharmacie", "Grossiste", "SuperGros"]

        for visite in medecins_visites:
            medecin_id = visite["medecin"]
            rapport_date = visite["rapport__added"]

            utilisateurs = User.objects.filter(
                rapport__visite__medecin_id=medecin_id, rapport__added=rapport_date
            ).distinct()

            # Vérifier les conditions de spécialité et utilisateurs
            if any(user.id in supervisor_users for user in utilisateurs):
                if any(u.id == user.id for u in utilisateurs):
                    medecin = Medecin.objects.get(id=medecin_id)
                    if medecin.specialite not in specialites_a_exclure:
                        visites_duo.append(
                            {
                                "id": medecin.id,
                                "nom": medecin.nom,
                                "date_visite": rapport_date,
                                "utilisateurs": [
                                    utilisateur.username for utilisateur in utilisateurs
                                ],
                                "produits": [],
                                "observations": [],
                            }
                        )

        nombre_medecins_visites_en_duo = len(visites_duo)
        print("datataaa" + str(visites_duo))

        data = {
            "nombre_medecins_visites_en_duo": nombre_medecins_visites_en_duo,
            "datas": visites_duo,
        }
        return Response(data)


class medecinPerUser(APIView):
    def get(self, request):
        user_medecins = Medecin.objects.filter(users=request.user)
        num_medecins = user_medecins.count()

        return Response()


class visitedMedecinPerUser(APIView):
    authentication_classes = (
        TokenAuthentication,
        SessionAuthentication,
    )
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        visited_medecins = (
            Visite.objects.filter(rapport__user=request.user)
            .values("medecin")
            .distinct()
        )
        num_visited_medecins = visited_medecins.count()
        return Response()


class MedecinPerUser(APIView):
    authentication_classes = (
        TokenAuthentication,
        SessionAuthentication,
    )
    permission_classes = (IsAuthenticated,)

    def get(self, request):

        user = request.user

        medecins = Medecin.objects.filter(users=user)

        nombre_medecins = medecins.count()

        return Response()


class ListMedecinPerUser(APIView):

    def get(self, request):
        user = request.user

        medecins = Medecin.objects.filter(users=user)

        medecins_json = []
        for medecin in medecins:
            medecin_json = {
                "id": medecin.id,
                "nom": medecin.nom,
            }
            medecins_json.append(medecin_json)

        return Response(medecins_json)


class VisitsPerUser(APIView):
    authentication_classes = (
        TokenAuthentication,
        SessionAuthentication,
    )
    permission_classes = (IsAuthenticated,)

    def get(self, request):

        user = request.user
        current_year = datetime.now().year

        # Récupérer le paramètre 'month' de l'URL
        month_param = request.GET.get("month")
        try:
            # Convertir la valeur du mois en entier
            month = int(month_param)
            # Vérifier si le mois est entre 1 et 12
            if 1 <= month <= 12:
                # Définir la date de début du mois spécifié dans l'URL
                date_debut_mois = datetime(
                    datetime.now().year,
                    month,
                    1,
                    0,
                    0,
                    0,
                    0,
                    tzinfo=datetime.now().tzinfo,
                )
                # Définir la date de fin du mois spécifié dans l'URL
                if month == 12:
                    date_fin_mois = datetime(
                        datetime.now().year + 1,
                        1,
                        1,
                        0,
                        0,
                        0,
                        0,
                        tzinfo=datetime.now().tzinfo,
                    )
                else:
                    date_fin_mois = datetime(
                        datetime.now().year,
                        month + 1,
                        1,
                        0,
                        0,
                        0,
                        0,
                        tzinfo=datetime.now().tzinfo,
                    )
            else:
                # Si le mois n'est pas valide, renvoyer une erreur
                return Response(
                    {"error": "Mois invalide. Utilisez une valeur entre 1 et 12."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except (ValueError, TypeError):
            # Si la valeur du mois n'est pas un entier valide ou n'est pas fournie, renvoyer une erreur
            return Response(
                {
                    "error": "Mois invalide. Utilisez une valeur numérique entre 1 et 12."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Filtrer les visites pour le mois spécifié dans l'URL
        date_fin_mois = date_fin_mois - timedelta(
            days=1
        )  # Adjust the end date to the last day of the specified month
        visites = Visite.objects.filter(
            rapport__added__range=(date_debut_mois, date_fin_mois),
            rapport__added__year=current_year,
            rapport__user=user,
        )

        specialites_a_exclure = ["Pharmacie", "Grossiste", "SuperGros"]

        # Filtrer les medecins visités pour le mois spécifié
        medecins_visites = (
            Medecin.objects.filter(
                visite__rapport__added__range=(date_debut_mois, date_fin_mois),
                visite__rapport__added__year=current_year,
                visite__rapport__user=user,
            )
            .exclude(specialite__in=specialites_a_exclure)
            .values("id", "nom")
            .distinct()
        )

        nombre_medecins_visites = medecins_visites.count()
        noms_medecins_visites = " | ".join(
            [f"{medecin['id']} {medecin['nom']}" for medecin in medecins_visites]
        )

        data = {
            "nombre_visites": nombre_medecins_visites,
            "noms_medecins_visites": noms_medecins_visites,
        }

        return Response(data)


class VisitsMoreThanOneTimeForMedecinPerUser(APIView):
    authentication_classes = (
        TokenAuthentication,
        SessionAuthentication,
    )
    permission_classes = (IsAuthenticated,)

    def get(self, request):

        user = request.user
        year = date.today().year

        # Récupérer le paramètre 'month' de l'URL
        month_param = request.GET.get("month")
        try:
            # Convertir la valeur du mois en entier
            month = int(month_param)
            # Vérifier si le mois est entre 1 et 12
            if 1 <= month <= 12:
                # Définir la date de début du mois spécifié dans l'URL
                date_debut_mois = datetime(
                    datetime.now().year,
                    month,
                    1,
                    0,
                    0,
                    0,
                    0,
                    tzinfo=datetime.now().tzinfo,
                )
                # Définir la date de fin du mois spécifié dans l'URL en excluant le 1er jour du mois suivant
                if month == 12:
                    date_fin_mois = datetime(
                        datetime.now().year + 1,
                        1,
                        1,
                        0,
                        0,
                        0,
                        0,
                        tzinfo=datetime.now().tzinfo,
                    )
                else:
                    date_fin_mois = datetime(
                        datetime.now().year,
                        month + 1,
                        1,
                        0,
                        0,
                        0,
                        0,
                        tzinfo=datetime.now().tzinfo,
                    )
            else:
                # Si le mois n'est pas valide, renvoyer une erreur
                return Response(
                    {"error": "Mois invalide. Utilisez une valeur entre 1 et 12."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except (ValueError, TypeError):
            # Si la valeur du mois n'est pas un entier valide ou n'est pas fournie, renvoyer une erreur
            return Response(
                {
                    "error": "Mois invalide. Utilisez une valeur numérique entre 1 et 12."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        medecins_visites = (
            Visite.objects.filter(
                rapport__added__gte=date_debut_mois,  # Utilisation de 'gte' pour inclure la date de début
                rapport__added__lt=date_fin_mois,
                rapport__added__year=year,
                rapport__user=user,
            )
            .values("medecin")
            .annotate(total_visites=Count("medecin"))
            .filter(total_visites__gt=1)
        )

        specialites_a_exclure = ["Pharmacie", "Grossiste", "SuperGros"]
        medecins_visites = medecins_visites.exclude(
            medecin__specialite__in=specialites_a_exclure
        )

        nombre_medecins_visites = len(medecins_visites)
        noms_medecins_visites = []
        for medecin_data in medecins_visites:
            medecin_id = medecin_data["medecin"]
            total_visites = medecin_data["total_visites"]
            # Assuming 'Medecin' is the related model containing the doctor's information.
            try:
                medecin_obj = Medecin.objects.get(id=medecin_id)
                medecin_nom = medecin_obj.nom
                medecin_specialite = medecin_obj.specialite
                medecin_classification = medecin_obj.classification
                nom_medecin = f"{medecin_id} {medecin_nom}"
            except ObjectDoesNotExist:
                # Handle the case if the related 'Medecin' object does not exist for this 'medecin_id'.
                medecin_nom = "Unknown"  # Replace with an appropriate default value.
                medecin_classification = ""
                medecin_specialite = ""
                nom_medecin = f"{medecin_id} {medecin_nom}"

            noms_medecins_visites.append(
                {
                    "nom": nom_medecin,
                    "total_visites": total_visites,
                    "specialite": medecin_specialite,
                    "classification": medecin_classification,
                }
            )

        data = {
            "nombre_medecins_visites": nombre_medecins_visites,
            "noms_medecins_visites": noms_medecins_visites,
        }

        return Response(data)


class VisitsMoreThanOneTimeForMedecinPerUserPerYear(APIView):
    authentication_classes = (
        TokenAuthentication,
        SessionAuthentication,
    )
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user1 = 16
        # Assuming you have a way to get the second user, let's call it 'user2'
        user2 = 8

        year = date.today().year

        # Retrieve visits for user1 in the current year
        user1_visits = (
            Visite.objects.filter(
                rapport__added__year=year,
                rapport__user=user1,
            )
            .values("medecin")
            .annotate(total_visites_user1=Count("medecin"))
        )

        # Retrieve visits for user2 in the current year
        user2_visits = (
            Visite.objects.filter(
                rapport__added__year=year,
                rapport__user=user2,
            )
            .values("medecin")
            .annotate(total_visites_user2=Count("medecin"))
        )

        # Combine the visits for each doctor from both users
        combined_visits = {}
        for visit_data in user1_visits:
            medecin_id = visit_data["medecin"]
            total_visites_user1 = visit_data["total_visites_user1"]
            combined_visits[medecin_id] = {"total_visites_user1": total_visites_user1}

        for visit_data in user2_visits:
            medecin_id = visit_data["medecin"]
            total_visites_user2 = visit_data["total_visites_user2"]
            if medecin_id in combined_visits:
                combined_visits[medecin_id]["total_visites_user2"] = total_visites_user2
            else:
                combined_visits[medecin_id] = {
                    "total_visites_user2": total_visites_user2
                }

        # Filter out the doctors who do not have at least one visit from both users
        combined_visits = {
            medecin_id: data
            for medecin_id, data in combined_visits.items()
            if "total_visites_user1" in data and "total_visites_user2" in data
        }

        # Assuming you have the 'specialite' field on the 'Medecin' model
        specialites_a_exclure = ["Pharmacie", "Grossiste", "SuperGros"]
        combined_visits = {
            medecin_id: data
            for medecin_id, data in combined_visits.items()
            if not Medecin.objects.filter(
                id=medecin_id, specialite__in=specialites_a_exclure
            ).exists()
        }

        # Prepare the response data
        noms_medecins_visites = []
        for medecin_id, data in combined_visits.items():
            total_visites_user1 = data["total_visites_user1"]
            total_visites_user2 = data["total_visites_user2"]
            total_visites = total_visites_user1 + total_visites_user2

            try:
                medecin_obj = Medecin.objects.get(id=medecin_id)
                medecin_nom = medecin_obj.nom
                nom_medecin = f"{medecin_id} {medecin_nom}"
            except ObjectDoesNotExist:
                medecin_nom = "Unknown"  # Replace with an appropriate default value.
                nom_medecin = f"{medecin_id} {medecin_nom}"

            noms_medecins_visites.append(
                {
                    "nom": nom_medecin,
                    "total_visites_user1": total_visites_user1,
                    "total_visites_user2": total_visites_user2,
                }
            )

        print(noms_medecins_visites)
        data = {
            "nombre_medecins_visites": len(noms_medecins_visites),
            "noms_medecins_visites": noms_medecins_visites,
        }

        return Response(data)


class MedecinsNonVisites(APIView):
    authentication_classes = (
        TokenAuthentication,
        SessionAuthentication,
    )
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        month_param = request.GET.get("month")
        current_year = datetime.now().year

        try:
            month = int(month_param)
            if 1 <= month <= 12:
                date_debut_mois = datetime(
                    datetime.now().year,
                    month,
                    1,
                    0,
                    0,
                    0,
                    0,
                    tzinfo=datetime.now().tzinfo,
                )
                if month == 12:
                    date_fin_mois = datetime(
                        datetime.now().year + 1,
                        1,
                        1,
                        0,
                        0,
                        0,
                        0,
                        tzinfo=datetime.now().tzinfo,
                    )
                else:
                    date_fin_mois = datetime(
                        datetime.now().year,
                        month + 1,
                        1,
                        0,
                        0,
                        0,
                        0,
                        tzinfo=datetime.now().tzinfo,
                    )
            else:
                return Response(
                    {"error": "Mois invalide. Utilisez une valeur entre 1 et 12."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except (ValueError, TypeError):
            return Response(
                {
                    "error": "Mois invalide. Utilisez une valeur numérique entre 1 et 12."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        medecins_users = Medecin.objects.filter(users=user)

        specialites_a_exclure = ["Pharmacie", "Grossiste", "SuperGros"]
        medecins_users = medecins_users.exclude(specialite__in=specialites_a_exclure)

        medecins_non_visites_data = []

        for medecin_user in medecins_users:
            est_visite = Visite.objects.filter(
                rapport__added__range=(date_debut_mois, date_fin_mois),
                rapport__added__year=current_year,
                rapport__user=user,
                medecin=medecin_user,
            ).exists()

            if not est_visite:
                derniere_visite = (
                    Visite.objects.filter(rapport__user=user, medecin=medecin_user)
                    .order_by("-rapport__added")
                    .first()
                )

                date_derniere_visite = (
                    derniere_visite.rapport.added.strftime("%Y-%m-%d")
                    if derniere_visite
                    else None
                )
                medecins_non_visites_data.append(
                    {
                        "id": medecin_user.pk,
                        "nom": medecin_user.nom,
                        "date_derniere_visite": date_derniere_visite,
                    }
                )

        nombre_medecins_non_visites = len(medecins_non_visites_data)

        data = {
            "nombre_medecins_non_visites": nombre_medecins_non_visites,
            "medecins_non_visites": medecins_non_visites_data,
        }
        return Response(data)


class SupervisedUsersView(APIView):
    authentication_classes = (
        TokenAuthentication,
        SessionAuthentication,
    )
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            supervised_users = user_profile.usersunder.all()
            supervised_usernames = [user.username for user in supervised_users]

            supervised_usernames.insert(0, str(request.user))

            return Response({"supervised_users": supervised_usernames})
        except UserProfile.DoesNotExist:
            return Response(
                {"error": "User profile not found for the current user."}, status=404
            )


class PharmaciesGrossitesVisitsPerUser(APIView):
    authentication_classes = (
        TokenAuthentication,
        SessionAuthentication,
    )
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        print(str(request))
        user_param = request.GET.get("user")
        current_year = datetime.now().year

        if user_param:
            user = user_param
        else:
            user = request.user
        # user=user_param

        # Récupérer le paramètre 'month' de l'URL
        month_param = request.GET.get("month")
        try:
            # Convertir la valeur du mois en entier
            month = int(month_param)
            # Vérifier si le mois est entre 1 et 12
            if 1 <= month <= 12:
                # Définir la date de début du mois spécifié dans l'URL
                date_debut_mois = datetime(
                    datetime.now().year,
                    month,
                    1,
                    0,
                    0,
                    0,
                    0,
                    tzinfo=datetime.now().tzinfo,
                )
                # Définir la date de fin du mois spécifié dans l'URL
                if month == 12:
                    date_fin_mois = datetime(
                        datetime.now().year + 1,
                        1,
                        1,
                        0,
                        0,
                        0,
                        0,
                        tzinfo=datetime.now().tzinfo,
                    )
                else:
                    date_fin_mois = datetime(
                        datetime.now().year,
                        month + 1,
                        1,
                        0,
                        0,
                        0,
                        0,
                        tzinfo=datetime.now().tzinfo,
                    )
            else:
                # Si le mois n'est pas valide, renvoyer une erreur
                return Response(
                    {"error": "Mois invalide. Utilisez une valeur entre 1 et 12."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except (ValueError, TypeError):
            # Si la valeur du mois n'est pas un entier valide ou n'est pas fournie, renvoyer une erreur
            return Response(
                {
                    "error": "Mois invalide. Utilisez une valeur numérique entre 1 et 12."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Filtrer les visites pour le mois spécifié dans l'URL et les spécialités "Pharmacie" et "Grossiste"
        date_fin_mois = date_fin_mois - timedelta(
            days=1
        )  # Adjust the end date to the last day of the specified month
        specialites_a_inclure = ["Pharmacie", "Grossiste"]
        visites = Visite.objects.filter(
            rapport__added__range=(date_debut_mois, date_fin_mois),
            rapport__added__year=current_year,
            rapport__user=user,
            medecin__specialite__in=specialites_a_inclure,
        )

        # Filtrer les medecins visités pour le mois spécifié et les spécialités "Pharmacie" et "Grossiste"
        medecins_visites = (
            Medecin.objects.filter(
                visite__rapport__added__range=(date_debut_mois, date_fin_mois),
                visite__rapport__user=user,
                visite__rapport__added__year=current_year,
                specialite__in=specialites_a_inclure,
            )
            .values("id", "nom", "specialite")
            .distinct()
        )

        nombre_medecins_visites = medecins_visites.count()
        noms_medecins_visites = " | ".join(
            [f"{medecin['id']} {medecin['nom']}" for medecin in medecins_visites]
        )

        # Compter le nombre total de pharmacies et de grossistes visités par l'utilisateur
        total_pharmacies_visitees = medecins_visites.filter(
            specialite="Pharmacie"
        ).count()
        total_grossistes_visites = medecins_visites.filter(
            specialite="Grossiste"
        ).count()

        data = {
            "nombre_visites": nombre_medecins_visites,
            "noms_medecins_visites": noms_medecins_visites,
            "total_pharmacies_visitees": total_pharmacies_visitees,
            "total_grossistes_visites": total_grossistes_visites,
        }

        return Response(data)


class SuperGrossitesVisitsPerUser(APIView):
    authentication_classes = (
        TokenAuthentication,
        SessionAuthentication,
    )
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        current_year = datetime.now().year
        month_param = request.GET.get("month")

        try:
            month = int(month_param)
            if 1 <= month <= 12:
                date_debut_mois = datetime(
                    datetime.now().year,
                    month,
                    1,
                    0,
                    0,
                    0,
                    0,
                    tzinfo=datetime.now().tzinfo,
                )
                if month == 12:
                    date_fin_mois = datetime(
                        datetime.now().year + 1,
                        1,
                        1,
                        0,
                        0,
                        0,
                        0,
                        tzinfo=datetime.now().tzinfo,
                    )
                else:
                    date_fin_mois = datetime(
                        datetime.now().year,
                        month + 1,
                        1,
                        0,
                        0,
                        0,
                        0,
                        tzinfo=datetime.now().tzinfo,
                    )
            else:
                return Response(
                    {"error": "Mois invalide. Utilisez une valeur entre 1 et 12."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except (ValueError, TypeError):
            return Response(
                {
                    "error": "Mois invalide. Utilisez une valeur numérique entre 1 et 12."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        date_fin_mois = date_fin_mois - timedelta(days=1)
        specialite_a_inclure = ["SuperGros"]
        visites = Visite.objects.filter(
            rapport__added__range=(date_debut_mois, date_fin_mois),
            rapport__added__year=current_year,
            rapport__user=user,
            medecin__specialite__in=specialite_a_inclure,
        )

        medecins_visites = (
            Medecin.objects.filter(
                visite__rapport__added__range=(date_debut_mois, date_fin_mois),
                visite__rapport__added__year=current_year,
                visite__rapport__user=user,
                specialite__in=specialite_a_inclure,
            )
            .annotate(num_visites=Count("visite"))
            .values("id", "nom", "num_visites")
            .distinct()
        )

        data = {
            "total_des_visites": visites.values("medecin").distinct().count(),
            "medecins": [],
        }

        for medecin in medecins_visites:
            last_non_empty_visit = (
                visites.filter(medecin_id=medecin["id"], produits__isnull=False)
                .order_by("-rapport__added")
                .first()
            )
            last_visit = (
                visites.filter(medecin_id=medecin["id"])
                .order_by("-rapport__added")
                .first()
            )

            if last_non_empty_visit:
                produits_info = last_non_empty_visit.products_to_admin()
                date_du_stock = last_non_empty_visit.rapport.added
            else:
                produits_info = ""
                date_du_stock = None

            if last_visit:
                date_derniere_visite = last_visit.rapport.added
            else:
                date_derniere_visite = None

            if date_du_stock is None and last_non_empty_visit:
                date_du_stock = last_non_empty_visit.rapport.added

            medecin_data = {
                "id": medecin["id"],
                "nom": medecin["nom"],
                "produits_visite": produits_info,
                "date_du_stock": date_du_stock,
                "nombre_visites": medecin["num_visites"],
                "date_derniere_visite": date_derniere_visite,
            }

            data["medecins"].append(medecin_data)
        return Response(data)


from django.db.models import Count


class StatisticMedecinsPerUser(APIView):
    def get(self, request, *args, **kwargs):
        user_id = request.GET.get("user")
        user = get_object_or_404(User, id=user_id)

        username = user.username
        # Initialize the response dictionary
        response_data = {
            "username": username,
            "role": user.userprofile.speciality_rolee,
            "total": user.medecin_set.count(),
            "specialite_per_wilaya": {},
            "specialite_per_commune": [],
        }

        medecins = user.medecin_set.all()

        # Compter les médecins par wilaya et spécialité
        wilaya_counts = medecins.values("commune__wilaya__nom").annotate(
            count=Count("id")
        )

        for wilaya_count in wilaya_counts:
            wilaya_name = wilaya_count["commune__wilaya__nom"]

            response_data["specialite_per_wilaya"].setdefault(wilaya_name, [])

            specialite_counts = (
                medecins.filter(commune__wilaya__nom=wilaya_name)
                .values("specialite")
                .annotate(count=Count("specialite"))
            )

            for specialite_count in specialite_counts:
                specialite_name = specialite_count["specialite"]
                count_for_specialite = Medecin.objects.filter(
                    commune__wilaya__nom=wilaya_name, specialite=specialite_name
                ).count()

                response_data["specialite_per_wilaya"][wilaya_name].append(
                    {
                        "specialite": specialite_name,
                        "count": specialite_count["count"],
                        "all_count": count_for_specialite,
                    }
                )

        # Compter les médecins par commune et spécialité
        commune_counts = medecins.values(
            "commune__wilaya__nom", "commune__nom"
        ).annotate(count=Count("id"))

        for commune_count in commune_counts:
            wilaya_name = commune_count["commune__wilaya__nom"]
            commune_name = commune_count["commune__nom"]

            response_data["specialite_per_commune"].append(
                {"wilaya": wilaya_name, "commune": commune_name, "specialites": []}
            )

            specialite_counts = (
                medecins.filter(commune__nom=commune_name)
                .values("specialite")
                .annotate(count=Count("specialite"))
            )

            for specialite_count in specialite_counts:
                specialite_name = specialite_count["specialite"]
                count_for_specialite = Medecin.objects.filter(
                    commune__nom=commune_name, specialite=specialite_name
                ).count()

                response_data["specialite_per_commune"][-1]["specialites"].append(
                    {
                        "specialite": specialite_name,
                        "count": specialite_count["count"],
                        "all_count": count_for_specialite,
                    }
                )
                # Count total doctors by specialty for the user
        user_specialite_counts = medecins.values("specialite").annotate(
            count=Count("specialite")
        )
        user_specialite_data = []

        for user_specialite_count in user_specialite_counts:
            specialite_name = user_specialite_count["specialite"]
            count_for_specialite = Medecin.objects.filter(
                specialite=specialite_name
            ).count()

            user_specialite_data.append(
                {
                    "specialite": specialite_name,
                    "count": user_specialite_count["count"],
                    "user_count": count_for_specialite,
                }
            )

        response_data["all_specialite_count"] = user_specialite_data

        print(str(response_data))
        return Response(response_data)


class AllMedecinsApi(APIView):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        # excluded_specialites = ['Pharmacie', 'Grossiste', 'SuperGro']
        # queryset = Medecin.objects.exclude(specialite__in=excluded_specialites)
        queryset = Medecin.objects.all()
        return Response(
            [{"id": medecin.id, "medecin": medecin.nom} for medecin in queryset],
            status=200,
        )
