from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.response import Response

from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib.auth.models import User
from datetime import date

from produits.models import Produit
from clients.models import OrderSource
from .functions import get_order_source_details, get_target_per_user, get_target_details_per_user, get_target_all_users, get_target_for_supervisor
from accounts.models import UserProfile, UserProduct

from liliumpharm.utils import month_number_to_french_name
from clients.models import Client 
from .serializers.comment import MonthComment



import threading
from django.contrib.auth.models import User

def revert_superuser():
    import time
    time.sleep(2)  # Attendre 5 secondes
    # Modifier l'utilisateur dans la base de données
    user = User.objects.get(username="MeriemDZ")
    user.is_superuser = False
    user.save()
    print("removed")


# class UserDataAPIView(APIView):
#     authentication_classes = [TokenAuthentication]
#     permission_classes = [IsAuthenticated]

#     def get(self, request, *args, **kwargs):

#         context = {}
#         user = request.user
#         context["user"] = {"id": user.id, "name": f"{user.userprofile.user.last_name} {user.userprofile.user.first_name}"}
        
#         context["wilayas"] = [{"id": wilaya.id, "description": wilaya.nom} for wilaya in request.user.userprofile.sectors.all()]

#         context["users"] = []
#         print("1")
#         if user.is_superuser == True:
#             context["users"] = [{"id": user.id, "username": user.username} for user in User.objects.filter(usertargetmonth__isnull=False).distinct()]
#         elif user.userprofile.rolee == "CountryManager":
#             context["users"] = [{"id": user.id, "username": user.username} for user in User.objects.filter(userprofile__commune__wilaya__pays=request.user.userprofile.commune.wilaya.pays, usertargetmonth__isnull=False).distinct()]
#         elif user.userprofile.rolee in ["Superviseur","Superviseur_regional"]:
#             context["users"] = [{"id": user.id, "username": user.username} for user in request.user.userprofile.usersunder.filter(usertargetmonth__isnull=False).distinct()]

#         print("2")

#         # ------------
#         if user.userprofile.speciality_rolee == "Superviseur_national":
#             context["users"] = [{"id": user.id, "username": user.username} for user in User.objects.filter(userprofile__commune__wilaya__pays=request.user.userprofile.commune.wilaya.pays, usertargetmonth__isnull=False).distinct()]
#         # --------------

#         all_months_and_years = OrderSource.objects.all().values_list('date__month').distinct()

#         all_months = set()
#         all_years = set()
#         print("3")

#         for month_and_year in all_months_and_years:
#             all_months.add(int(month_and_year[0]))
#             # all_years.add(int(month_and_year[1]))

#         print("4")
        
#         all_years.add(2025)
#         context["all_months"] = sorted(all_months, reverse=True)
#         context["all_years"] = sorted(all_years, reverse=True)

#         params = {}
#         users = request.GET.getlist("users[]", None)
#         months = request.GET.getlist("months[]", None)
#         years = request.GET.getlist("years[]", None)

#         if users:
#             params["user_id"]=users[0]
#             user = User.objects.get(id=users[0])
#         else:
#             params["user_id"]=user.id

#         if months:
#             params["months"]= months
#         if years:
#             params["years"]= years
        


#         if user.is_superuser == True or user.userprofile.rolee in ["CountryManager", "Superviseur_national"]:
#             print("hereee 1 ")
#             targets_per_user = get_target_for_supervisor(**params)
#         else:
#             targets_per_user = get_target_per_user(**params)

#         context["data"] = targets_per_user

#         # Calculating Target for Each Month
#         context["data"]["other_months"] = {}
#         for month in months:
#             if user.is_superuser == True or user.userprofile.rolee in ["CountryManager"]:
                







#                 if str(user) == "MeriemDZ":
#                     # Modifiez l'utilisateur dans la base de données
#                     user = User.objects.get(username="MeriemDZ")
#                     user.is_superuser = True
#                     user.save()
#                     # Démarrer une tâche asynchrone pour rétablir is_superuser après 5 secondes
#                     threading.Thread(target=revert_superuser).start()






#                 context["data"]["other_months"][month] = get_target_for_supervisor(user_id=params["user_id"], months=[month], years=years)
#             else:
#                 print("im heee baby girl")
#                 context["data"]["other_months"][month] = get_target_per_user(user_id=params["user_id"], months=[month], years=years)

#             if user.is_superuser == True or user.userprofile.speciality_rolee == "Superviseur_national":
#                 context["data"]["other_months"][month] = get_target_for_supervisor(user_id=params["user_id"], months=[month], years=years)
#             else:
#                 context["data"]["other_months"][month] = get_target_per_user(user_id=params["user_id"], months=[month], years=years)

#         return Response(context)

class UserDataAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Vérifier l'authentification
        if not request.user.is_authenticated:
            return Response({"error": "Authentication required"}, status=401)

        user = request.user
        context = {}

        # ✅ Infos utilisateur
        context["user"] = {
            "id": user.id,
            "name": f"{user.last_name} {user.first_name}"
        }

        # ✅ Wilayas liées à l'utilisateur
        context["wilayas"] = [
            {"id": wilaya.id, "description": wilaya.nom}
            for wilaya in user.userprofile.sectors.all()
        ]

        # ✅ Liste des utilisateurs
        context["users"] = []
        if user.is_superuser:
            context["users"] = [
                {"id": u.id, "username": u.username}
                for u in User.objects.filter(usertargetmonth__isnull=False).distinct()
            ]
        elif user.userprofile.rolee == "CountryManager":
            context["users"] = [
                {"id": u.id, "username": u.username}
                for u in User.objects.filter(
                    userprofile__commune__wilaya__pays=user.userprofile.commune.wilaya.pays,
                    usertargetmonth__isnull=False
                ).distinct()
            ]
        elif user.userprofile.rolee in ["Superviseur", "Superviseur_regional"]:
            context["users"] = [
                {"id": u.id, "username": u.username}
                for u in user.userprofile.usersunder.filter(usertargetmonth__isnull=False).distinct()
            ]

        # ✅ Cas superviseur national
        if user.userprofile.speciality_rolee == "Superviseur_national":
            context["users"] = [
                {"id": u.id, "username": u.username}
                for u in User.objects.filter(
                    userprofile__commune__wilaya__pays=user.userprofile.commune.wilaya.pays,
                    usertargetmonth__isnull=False
                ).distinct()
            ]

        # ✅ Récupération des mois (année forcée à 2025)
        all_months_and_years = OrderSource.objects.all().values_list("date__month").distinct()
        all_months = {int(m[0]) for m in all_months_and_years}
        context["all_months"] = sorted(all_months, reverse=True)
        context["all_years"] = [2025]  # année forcée

        # ✅ Lecture des paramètres GET
        params = {}
        selected_users = request.GET.getlist("users[]", None)
        months = request.GET.getlist("months[]", None)
        years = request.GET.getlist("years[]", None)
        print(f"user list {selected_users}")
        print(f"months {months}")
        print(f"years {years}")
        print(f"user {user}")
        if selected_users:
            params["user_id"] = int(selected_users[0])
            print(f"selected_users[0] {selected_users[0]} with type {type(selected_users[0])}")
            selected_user = User.objects.get(id=selected_users[0])
            params["user_id"] = int(selected_users[0])
        else:
            params["user_id"] = user.id
            selected_user = user

        if months:
            params["months"] = months
        if years:
            params["years"] = years

        # ✅ Récupération des targets
        if selected_users:
            u = User.objects.get(id=selected_users[0])
        else:
            u = request.user
        if u.is_superuser or u.userprofile.rolee in ["CountryManager", "Superviseur_national"]:
            targets_per_user = get_target_for_supervisor(**params)
        else:
            targets_per_user = get_target_per_user(**params)
            print("je suis dans get_target_per_user(**params)")
            print(targets_per_user)

        context["data"] = targets_per_user
        context["data"]["other_months"] = {}

        # ✅ Calcul des autres mois
        for month in months or []:
            if u.is_superuser or u.userprofile.rolee in ["CountryManager", "Superviseur_national"]:
                context["data"]["other_months"][month] = get_target_for_supervisor(
                    user_id=params["user_id"], months=[month], years=years
                )
            else:
                context["data"]["other_months"][month] = get_target_per_user(
                    user_id=params["user_id"], months=[month], years=years
                )
                print("je suis la user_id=params[user_id], months=[month], years=years")
        return Response(context)


class MonthCommentAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        print(f"Posting Comment {request.data}")

        # FIXME - Something weired is going here from the frontend, sometimes it sends list and sometimes value  
        year = request.data.get("year")
        month = request.data.get("month")

        year = year[0] if type(year) == list else year
        month = month[0] if type(month) == list else month
        
    
        serializer = MonthComment(data={"date": date(int(year), int(month), 1), "from_user": request.user.id, "to_user": request.data.get("to_user"), "comment": request.data.get("comment")})
        if serializer.is_valid():
            serializer.save()
        
        return Response()


class SuperGrosAPI(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        print("|||||||||||||||||||")
        print("|||||||||||||||||||")
        print("|||||||||||||||||||")
        print("|||||||||||||||||||")
        print("|||||||||||||||||||")
        print("|||||||||||||||||||")

        return Response([{
            "id": client.id,
            "name":client.name
        } for client in Client.objects.filter(supergro=True)],status=200)
