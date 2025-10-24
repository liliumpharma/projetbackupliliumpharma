from accounts.models import UserProfile
from accounts.models import UserProxy as User
from .serializers import *
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import (
    SessionAuthentication,
    BasicAuthentication,
    TokenAuthentication,
)
from django.core.paginator import Paginator
from django.db.models import Q
from rapports.models import Rapport
from datetime import datetime

from liliumpharm.utils import month_number_to_french_name
from medecins.models import MedecinSpecialite
from accounts.api.serializers import MedecinSpecialiteSerializer
from plans.models import Plan
from clients.models import UserTargetMonth


class UserProfileApi(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def pagination_response(self, users, serializer, users_length):
        response = {
            "pages": users.paginator.num_pages,
            "result": serializer.data,
            "length": users_length,
        }
        try:
            response["previous"] = users.previous_page_number()
        except:
            pass
        try:
            response["next"] = users.next_page_number()
        except:
            pass
        return response

    def get(self, request, format=None):
        page = request.GET.get("page")
        filters = {}
        q = Q()

        if request.GET.get("pays") and request.GET.get("pays") != "0":
            filters["commune__wilaya__pays__id"] = request.GET.get("pays")

        if request.GET.get("wilaya") and request.GET.get("wilaya") != "0":
            filters["commune__wilaya__id"] = request.GET.get("wilaya")

        if request.GET.get("commune") and request.GET.get("commune") != "0":
            filters["commune__id"] = request.GET.get("commune")

        if request.GET.get("spec"):
            filters["specialite"] = request.GET.get("spec")

        if request.GET.get("commercial") and request.GET.get("commercial") != "":
            q |= Q(user__first_name__icontains=request.GET.get("commercial"))
            q |= Q(user__last_name__icontains=request.GET.get("commercial"))

        # users_list=UserProfile.objects.filter(**filters).order_by("-user__first_name")

        # if q:
        #     users_list=users_list.filter(q)

        # paginator = Paginator(users_list, 1)
        # users=paginator.get_page(page)

        user = request.user
        user_company = user.userprofile.company
        poste_a_exlure = [
            "Office",
            "Finance_et_comptabilité",
            "chargé_de_communication",
            "gestionnaire_de_stock",
        ]
        medecin_recycle_bin = User.objects.filter(username="Medecin_Recycle_Bin")
        pharmacie_recycle_bin = User.objects.filter(username="Pharmacie_Recycle_Bin")
        if user.is_superuser:
            users = User.objects.filter(userprofile__is_human=True)
        elif user.userprofile.rolee == "CountryManager":
            users = User.objects.filter(
                userprofile__commune__wilaya__pays=user.userprofile.commune.wilaya.pays,
                userprofile__is_human=True,
                #userprofile__company=user_company,
            ).exclude(userprofile__speciality_rolee__in=poste_a_exlure)
        elif user.userprofile.speciality_rolee == "Superviseur_national" or user.userprofile.speciality_rolee == "Superviseur_regional":
            users = user.userprofile.usersunder.all()
            users = users | User.objects.filter(id=request.user.id)
            #users = list(user.userprofile.usersunder.all())
            #if request.user not in users:
            #    users.insert(0, request.user)
            #users = users.exclude(username=request.user.username)

        else:
            # users=request.user
            print(user.id)
            users = User.objects.filter(id=user.id)

        print("getting user *********")

        serializer = UserSerializer(
            #     # User.objects.filter(id__in=request.user.userprofile.usersunder.all().values("id") if not request.user.is_superuser else User.objects.all()),
            # users.order_by("username"),many=True)
            users.order_by("username"),
            many=True,
        )

        return Response(serializer.data, status=200)


class UserProfileAdminApi(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        page = request.GET.get("page")
        filters = {}
        q = Q()
        user = request.user
        user_company = user.userprofile.company
        poste_a_exlure = [
            "Office",
            "Finance_et_comptabilité",
            "chargé_de_communication",
            "gestionnaire_de_stock",
        ]
        medecin_recycle_bin = User.objects.filter(username="Medecin_Recycle_Bin")
        pharmacie_recycle_bin = User.objects.filter(username="Pharmacie_Recycle_Bin")
        if user.is_superuser:
            users = User.objects.filter(userprofile__is_human=True)
            users |= medecin_recycle_bin
            users |= pharmacie_recycle_bin
        elif user.userprofile.rolee == "CountryManager":
            users = User.objects.filter(
                userprofile__commune__wilaya__pays=user.userprofile.commune.wilaya.pays,
                userprofile__is_human=True,
                userprofile__company=user_company,
            ).exclude(userprofile__speciality_rolee__in=poste_a_exlure)
            users |= medecin_recycle_bin
            users |= pharmacie_recycle_bin
        elif user.userprofile.speciality_rolee == "Superviseur_national":
            users = user.userprofile.usersunder.all()
            users = users.exclude(username=request.user.username)
            users |= medecin_recycle_bin
            users |= pharmacie_recycle_bin
        else:
            users = User.objects.filter(id=user.id)
            users |= medecin_recycle_bin
            users |= pharmacie_recycle_bin

        serializer = UserSerializer(
            #     # User.objects.filter(id__in=request.user.userprofile.usersunder.all().values("id") if not request.user.is_superuser else User.objects.all()),
            # users.order_by("username"),many=True)
            users.order_by("username"),
            many=True,
        )

        return Response(serializer.data, status=200)


class SpecialiteApi(APIView):
    def get(self, request, format=None):
        # data = [{'id': ms.id, 'nom': ms.description, 'medical': ms.ismedical} for ms in MedecinSpecialite.objects.all()]
        data = [
            {"id": ms.id, "nom": ms.description, "medical": True}
            for ms in MedecinSpecialite.objects.all()
        ]
        print(data)
        return Response(data)


class ClassificationsApi(APIView):
    def get(self, request, format=None):
        content = [
            {"id": 1, "nom": "a"},
            {"id": 2, "nom": "b"},
            {"id": 3, "nom": "c"},
            {"id": 4, "nom": "d"},
            {"id": 5, "nom": "e"},
            {"id": 6, "nom": "f"},
            {"id": 7, "nom": "g"},
            {"id": 8, "nom": "p"},
        ]
        return Response(content)


class AccountApi(APIView):
    def get(self, request, format=None):
        request.session['user_id'] = request.user.id
        print(f"dans account/api initialisation des user_id dans session {request.user.id}")
        # return Response({'id':request.user.id,'nom':request.user.username})
        return Response({"id": request.user.id, "nom": request.user.username})


class AccountAppApi(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):

        if request.user.is_superuser:
            users = User.objects.filter(userprofile__is_human=True).exclude(
                id=request.user.id
            )
        elif request.user.userprofile.rolee == "CountryManager":
            if request.user.username == "MeriemDZ":
                users = User.objects.filter(
                    userprofile__commune__wilaya__pays=request.user.userprofile.commune.wilaya.pays,
                    userprofile__is_human=True,
                    userprofile__company="lilium pharma",
                ).exclude(
                    userprofile__speciality_rolee="Office",
                )
            else:
                company = request.user.userprofile.company
                users = User.objects.filter(
                    userprofile__commune__wilaya__pays=request.user.userprofile.commune.wilaya.pays,
                    userprofile__company=company,
                )
        else:
            users = request.user.userprofile.usersunder.all().order_by("username")

        rapport = Rapport.objects.filter(added=datetime.today(), user=request.user)
        plan = Plan.objects.filter(
            day=datetime.today(),
            valid_commune=True,
            valid_clients=True,
            user=request.user,
        )

        if len(rapport) != 0:
            message = "votre rapport d'aujourdhui a été ajouter vous ne pouvez pas ajouter un rapport"
        else:
            if len(plan) != 1:
                message = "Vous devez ajouter votre planning pour aujourdhui et qu'il soit validé par votre superieur"
            else:
                message = ""

        # Targets
        target = {
            "year": datetime.today().year,
            "month": month_number_to_french_name(datetime.today().month),
            "products": [],
        }
        monthly_target = UserTargetMonth.objects.filter(
            date__year=datetime.today().year,
            date__month=datetime.today().month,
            user=request.user,
        )
        if monthly_target.exists():
            monthly_target = monthly_target.first()
            target["products"] = [
                {
                    "product": product_target.product.nom,
                    "quantity": product_target.quantity,
                }
                for product_target in monthly_target.usertargetmonthproduct_set.all()
            ]

        return Response(
            {
                "id": request.user.id,
                "username": request.user.username,
                "first_name": request.user.first_name,
                "last_name": request.user.last_name,
                "email": request.user.email,
                "telephone": request.user.userprofile.telephone,
                "adresse": request.user.userprofile.adresse,
                "commune": request.user.userprofile.commune.id,
                "activate": request.user.userprofile.activate,
                "can_send_receive_tasks": request.user.userprofile.can_send_receive_tasks,
                "rolee": request.user.userprofile.rolee,
                # "usersunder":request.user.userprofile.usersunder,
                "can_view_visites": request.user.userprofile.can_view_visites,
                "notification_token": request.user.userprofile.notification_token,
                "recive_mail": request.user.userprofile.recive_mail,
                "gender": request.user.userprofile.gender,
                "sectors": [
                    {"id": s.id, "nom": s.nom}
                    for s in request.user.userprofile.sectors.all()
                ],
                "CNAS": request.user.userprofile.CNAS,
                "entry_date": request.user.userprofile.entry_date,
                "conge": request.user.userprofile.conge,
                "bank_account": request.user.userprofile.bank_account,
                "bank_name": request.user.userprofile.bank_name,
                "situation": request.user.userprofile.situation,
                "job_name": request.user.userprofile.job_name,
                "salary": request.user.userprofile.salary,
                "date_of_birth": request.user.userprofile.date_of_birth,
                "country": request.user.userprofile.commune.wilaya.pays.id,
                # "can_add_rapport": len(rapport)==0 and len(plan) ==1 ,
                "can_add_rapport": True,
                "message": message,
                "is_supervisor": request.user.is_superuser
                or request.user.userprofile.rolee == "Superviseur"
                or request.user.userprofile.rolee == "CountryManager",
                "users_under": [
                    {"id": usr.id, "username": usr.username} for usr in users
                ],
                "is_superuser": request.user.is_superuser,
                "is_country_manager": request.user.userprofile.rolee
                == "CountryManager",
                "can_add_medecin": request.user.userprofile.can_add_medecin,
                "can_update_medecin": request.user.userprofile.can_update_medecin,
                "can_add_client": request.user.userprofile.can_add_client,
                "monthly_target": target,
                "groups": [g.name for g in request.user.groups.all()],
                "permissions": [
                    permission.codename
                    for permission in request.user.user_permissions.all()
                ],
            }
        )

    def post(self, request):
        if request.data.get("ios_notification_token"):
            UserProfile.objects.filter(user__id=request.user.id).update(
                ios_notification_token=request.data["ios_notification_token"]
            )
        else:
            UserProfile.objects.filter(user__id=request.user.id).update(
                notification_token=request.data["notification_token"]
            )

        return Response({"response": "hello"}, status=200)


class AllUsersApi(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        return Response(
            [
                {"id": usr.id, "username": usr.username}
                for usr in User.objects.filter(userprofile__work_as_commercial=True)
            ],
            status=200,
        )


class TransferTaskUsersApi(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        # Créer une liste de dictionnaires pour chaque utilisateur
        users_data = [
            {"id": usr.id, "username": usr.username}
            for usr in User.objects.filter(userprofile__can_send_receive_tasks=True)
        ]

        # Afficher la liste des utilisateurs
        print(str(users_data))

        # Vous pouvez également retourner les données sous forme de réponse JSON
        return Response(users_data, status=200)


class EditProfileApi(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        # serializer=EditProfileSerializer(request.user.userprofile)
        serializer = EditProfileSerializer(UserProfile.objects.get(id=1))
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = EditProfileSerializer(request.user.userprofile, data=request.data)
        # serializer = EditProfileSerializer(UserProfile.objects.get(id=1), data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EditUserApi(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        serializer = UserSerializer(request.user, data=request.data)
        # serializer=UserSerializer(User.objects.get(id=1), data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
