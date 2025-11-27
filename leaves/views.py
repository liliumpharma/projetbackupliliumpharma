from notifications.models import Notification
from .models import *
from .serializers import *
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.db.models import Q, Count


from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import authentication, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token

from django.shortcuts import render, redirect
from django.core.mail import EmailMessage


class LeaveAbsenceAPI(APIView):

    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        holidays = LeaveAbsence.objects.filter(user=request.user)
        serializer = LeaveAbsenceSerializer(holidays, many=True)
        return Response(serializer.data, status=200)

    def post(self, request, format=None):
        serializer = LeaveAbsenceSerializer(
            data=request.data, instance=LeaveAbsence(user=request.user), partial=True
        )
        if serializer.is_valid():
            instance = serializer.save()
            body = f"""
                {request.user.username} vient de demander une autorisation d'absence pour consulter cliquer sur le lien suivant  
                https://app.liliumpharma.com/admin/holidays/leaveabsence/{instance.id}/change/
                  
            """
            email = EmailMessage(
                "Autorisation d'absence " + request.user.username,
                body,
                "server.lilium@gmail.com",
                ["contact.liliumpharma@gmail.com", "boughezala.aimen@gmail.com"],
            )
            email.send()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from django.db.models import F


# class LeavesAPIView(APIView):

#     authentication_classes = [authentication.TokenAuthentication]
#     permission_classes = [permissions.IsAuthenticated]

#     def get(self, request):
#         # Getting query params
#         username = request.GET.get("username")
#         family = request.GET.get("family")
#         starting_date = request.GET.get("starting_date")
#         ending_date = request.GET.get("ending_date")

#         # Ensure starting_date and ending_date are provided
#         if not starting_date or not ending_date:
#             return Response(
#                 {"error": "Starting and ending dates are required."}, status=400
#             )

#         # Date range query for leaves
#         leaves_date_query = Q(start_date__lte=ending_date) & Q(
#             end_date__gte=starting_date
#         )
#         absences_date_query = Q(date__range=[starting_date, ending_date])

#         # Family filter for superusers or CountryManagers
#         if (
#             family
#             and family != "Tous"
#             and (
#                 request.user.is_superuser
#                 or request.user.userprofile.rolee in ["CountryManager"]
#             )
#         ):
#             leaves_date_query &= Q(user__userprofile__family=family)
#             absences_date_query &= Q(user__userprofile__family=family)

#             leaves = Leave.objects.filter(leaves_date_query)
#             absences = Absence.objects.filter(absences_date_query)
#             leaves_number = leaves.values_list("leave_type__description").annotate(
#                 type_count=Count("leave_type__id")
#             )

#             serializer = Serializer({"leaves": leaves, "absences": absences})
#             data = {**serializer.data, "leaves_stats": list(leaves_number)}
#             return Response(data, status=200)

#         # Handle user-based filtering
#         if username:
#             try:
#                 requester = User.objects.get(username=username)
#                 user_under = request.user.userprofile.usersunder.filter(
#                     username=username
#                 ).exists()

#                 if request.user.is_superuser or request.user.userprofile.rolee in [
#                     "CountryManager"
#                 ]:
#                     # Date filtering for the specified user
#                     leaves_date_query &= Q(user=requester)

#                 elif not user_under:
#                     return Response(status=403)

#                 else:
#                     leaves_date_query &= Q(user=requester)

#             except User.DoesNotExist:
#                 return Response({"error": "User not found"}, status=404)

#         else:
#             # If no username is provided, handle based on user roles
#             if (
#                 not request.user.is_superuser
#                 and request.user.userprofile.rolee not in ["CountryManager"]
#             ):
#                 if request.user.userprofile.speciality_rolee == "Superviseur_national":
#                     users_under_supervisor = list(
#                         request.user.userprofile.usersunder.all()
#                     ) + [request.user]
#                     leaves_date_query &= Q(user__in=users_under_supervisor)
#                     absences_date_query &= Q(user__in=users_under_supervisor)
#                 else:
#                     leaves_date_query &= Q(user=request.user)
#                     absences_date_query &= Q(user=request.user)
#             else:
#                 if request.user.userprofile.speciality_rolee in [
#                     "CountryManager",
#                     "Administration",
#                 ]:
#                     user_in_same_company = User.objects.filter(
#                         userprofile__company=request.user.userprofile.company,
#                         userprofile__is_human=True,
#                     )
#                     leaves_date_query &= Q(user__in=user_in_same_company)
#                     absences_date_query &= Q(user__in=user_in_same_company)

#         # Final query for leaves and absences
#         leaves = Leave.objects.filter(
#             leaves_date_query, user__userprofile__hidden=False,
#         ).order_by(F("start_date").desc(nulls_last=True))

#         absences = Absence.objects.filter(
#             absences_date_query, user__userprofile__hidden=False
#         ).order_by(F("date").desc(nulls_last=True))

#         leaves_number = leaves.values_list("leave_type__description").annotate(
#             type_count=Count("leave_type__id")
#         )
#         serializer = Serializer({"leaves": leaves, "absences": absences})

#         # Adding Data
#         data = {**serializer.data, "leaves_stats": list(leaves_number)}
#         return Response(data, status=200)


class LeavesAPIView(APIView):

    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Getting query params
        username = request.GET.get("username")
        family = ""
        starting_date = request.GET.get("starting_date")
        ending_date = request.GET.get("ending_date")
        # Ensure starting_date and ending_date are provided
        if not starting_date or not ending_date:
            return Response(
                {"error": "Starting and ending dates are required."}, status=400
            )
        # Date range query for leaves
        leaves_date_query = Q(start_date__lte=ending_date) & Q(
            end_date__gte=starting_date
        )
        absences_date_query = Q(date__range=[starting_date, ending_date])

        print("1 "+str(family))

        # Handle user-based filtering
        if username:
            print("2")
            try:
                requester = User.objects.get(username=username)
                user_under = request.user.userprofile.usersunder.filter(
                    username=username
                ).exists()
                if request.user.is_superuser or request.user.userprofile.rolee in [
                    "CountryManager"
                ]:
                    # Date filtering for the specified user
                    leaves_date_query &= Q(user=requester)
                    absences_date_query &= Q(
                        user=requester
                    )  # Apply user filter to absences
                elif not user_under:
                    return Response(status=403)
                else:
                    leaves_date_query &= Q(user=requester)
                    absences_date_query &= Q(
                        user=requester
                    )  # Apply user filter to absences
            except User.DoesNotExist:
                return Response({"error": "User not found"}, status=404)
        else:
            # If no username is provided, handle based on user roles
            if (
                not request.user.is_superuser
                and request.user.userprofile.rolee not in ["CountryManager"]
            ):
                if request.user.userprofile.speciality_rolee == "Superviseur_national":
                    users_under_supervisor = list(
                        request.user.userprofile.usersunder.all()
                    ) + [request.user]
                    leaves_date_query &= Q(user__in=users_under_supervisor)
                    absences_date_query &= Q(
                        user__in=users_under_supervisor
                    )  # Apply user filter to absences
                else:
                    leaves_date_query &= Q(user=request.user)
                    absences_date_query &= Q(
                        user=request.user
                    )  # Apply user filter to absences
            else:
                if request.user.userprofile.speciality_rolee in [
                    "CountryManager"
                    
                ]:
                    user_in_same_company = User.objects.filter(
                        userprofile__company=request.user.userprofile.company,
                        userprofile__is_human=True,
                    )
                    leaves_date_query &= Q(user__in=user_in_same_company)
                    absences_date_query &= Q(
                        user__in=user_in_same_company
                    )  # Apply user filter to absences
        # Final query for leaves and absences
        leaves = Leave.objects.filter(
            leaves_date_query,
            user__userprofile__hidden=False,
        ).order_by(F("start_date").desc(nulls_last=True))
        absences = Absence.objects.filter(
            absences_date_query, user__userprofile__hidden=False
        ).order_by(F("date").desc(nulls_last=True))
        leaves_number = leaves.values_list("leave_type__description").annotate(
            type_count=Count("leave_type__id")
        )
        serializer = Serializer({"leaves": leaves, "absences": absences})
        # Adding Data
        data = {**serializer.data, "leaves_stats": list(leaves_number)}
        return Response(data, status=200)


# class LeavesAPIView(APIView):

#     authentication_classes = [authentication.TokenAuthentication]
#     permission_classes = [permissions.IsAuthenticated]

#     def get(self, request):
#         # Getting User Param
#         username = request.GET.get("username")
#         family = request.GET.get("family")

#         print("------#######-----" + str(family))

#         starting_date = request.GET.get("starting_date")
#         ending_date = request.GET.get("ending_date")

#         leaves_date_query = Q(start_date__range=[starting_date, ending_date]) | Q(
#             end_date__range=[starting_date, ending_date]
#         )
#         absences_date_query = Q(date__range=[starting_date, ending_date])

#         if family and family != "Tous":
#             if request.user.is_superuser or request.user.userprofile.rolee in [
#                 "CountryManager"
#             ]:
#                 # Appliquez le filtre pour la famille
#                 leaves_date_query = (
#                     Q(user__userprofile__family=family) & leaves_date_query
#                 )
#                 absences_date_query = (
#                     Q(user__userprofile__family=family) & absences_date_query
#                 )
#                 print("-->" + str(family))
#                 print(str(leaves_date_query))

#                 leaves = Leave.objects.filter(leaves_date_query)
#                 absences = Absence.objects.filter(absences_date_query)

#                 leaves_number = leaves.values_list("leave_type__description").annotate(
#                     type_count=Count("leave_type__id")
#                 )

#                 serializer = Serializer({"leaves": leaves, "absences": absences})

#                 # Adding Data
#                 data = {**serializer.data, "leaves_stats": list(leaves_number)}
#                 return Response(data, status=200)
#         else:

#             if username:
#                 print(
#                     str("-----> hhh")
#                 )  # Impression de test pour vérifier si 'username' est défini
#                 requester = User.objects.get(username=username)
#                 print(f"Requester: {requester}")  # Impression pour voir le requester
#                 requester_company = requester.userprofile.company
#                 print(
#                     f"Requester company: {requester_company}"
#                 )  # Impression pour vérifier la société du requester
#                 user_under = request.user.userprofile.usersunder.filter(
#                     username=username
#                 )
#                 print(
#                     f"User under: {user_under}"
#                 )  # Impression pour vérifier si l'utilisateur est sous 'usersunder'

#                 # Return 403 if the user is not under
#                 # if not request.user.is_superuser or request.user.userprofile.rolee not in ["CountryManager"] and not user_under.exists():
#                 # if not request.user.is_superuser or request.user.userprofile.rolee not in ["CountryManager"]:
#                 #     print("here bb")
#                 #     return Response(status=403)

#                 user_under = get_object_or_404(User, username=username)
#                 print(
#                     f"User under after get_object_or_404: {user_under}"
#                 )  # Impression après récupération de l'utilisateur

#                 if request.user.is_superuser or request.user.userprofile.rolee in [
#                     "CountryManager"
#                 ]:
#                     # leaves_date_query &= Q(user__username=username)
#                     # absences_date_query &= Q(user__username=username)
#                     us = request.user
#                     print(f"Current user: {us}")  # Impression de l'utilisateur actuel
#                     us_comp = us.userprofile.company
#                     print(
#                         f"Current user's company: {us_comp}"
#                     )  # Impression de la société de l'utilisateur actuel
#                     user_in_same_company = User.objects.filter(
#                         userprofile__company=us_comp, userprofile__is_human=True
#                     )
#                     print(
#                         f"Users in same company: {user_in_same_company}"
#                     )  # Impression des utilisateurs dans la même société

#                     leaves_date_query = (
#                         Q(user__username=username)
#                         | Q(start_date__range=[starting_date, ending_date])
#                         | Q(end_date__range=[starting_date, ending_date])
#                     )
#                     absences_date_query = Q(user__username=username) | Q(
#                         date__range=[starting_date, ending_date]
#                     )

#                     # Si vous avez un modèle "Leave" ou similaire pour les absences, utilisez-le ici
#                     leaves = Leave.objects.filter(leaves_date_query)
#                     print(f"Leaves for {username}: {leaves}")

#                 else:
#                     leaves_date_query &= Q(user=user_under)
#                     absences_date_query &= Q(user=user_under)
#             else:
#                 print(str("----->  2"))

#                 # Getting all Users if supervisor
#                 if (
#                     not request.user.is_superuser
#                     and request.user.userprofile.rolee not in ["CountryManager"]
#                 ):
#                     if (
#                         request.user.userprofile.speciality_rolee
#                         == "Superviseur_national"
#                     ):
#                         user_under_supervisor = (
#                             request.user.userprofile.usersunder.all()
#                         )
#                         user_under_supervisor = list(user_under_supervisor)
#                         user_under_supervisor.append(request.user)
#                         leaves_date_query &= Q(user__in=user_under_supervisor)
#                         absences_date_query &= Q(user__in=user_under_supervisor)

#                     else:
#                         leaves_date_query &= Q(user=request.user)
#                         absences_date_query &= Q(user=request.user)
#                 else:
#                     print("im here 99")
#                     print(str(request.user.userprofile.speciality_rolee))
#                     if request.user.userprofile.speciality_rolee in [
#                         "CountryManager",
#                         "Administration",
#                     ]:
#                         us = request.user
#                         us_comp = us.userprofile.company
#                         print(str(us_comp))
#                         user_in_same_company = User.objects.filter(
#                             userprofile__company=us_comp, userprofile__is_human=True
#                         )
#                         print(str(user_in_same_company))
#                         leaves_date_query &= Q(user__in=user_in_same_company)
#                         absences_date_query &= Q(user__in=user_in_same_company)

#             # Querying
#             leaves = Leave.objects.filter(
#                 leaves_date_query, user__userprofile__hidden=False
#             ).order_by(F("start_date").desc(nulls_last=True))

#             absences = Absence.objects.filter(
#                 absences_date_query, user__userprofile__hidden=False
#             ).order_by(F("date").desc(nulls_last=True))

#             leaves_number = leaves.values_list("leave_type__description").annotate(
#                 type_count=Count("leave_type__id")
#             )
#             serializer = Serializer({"leaves": leaves, "absences": absences})

#             # Adding Data
#             data = {**serializer.data, "leaves_stats": list(leaves_number)}
#             return Response(data, status=200)


class LeaveAPIView(APIView):

    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        instance = get_object_or_404(Leave, ~Q(approved="WAITING"), pk=pk)
        if (
            request.user.is_superuser
            or request.user.userprofile.rolee in ["CountryManager"]
            or request.user.has_perm("approve_absence")
            or request.user == instance.user
        ):
            data = LeaveSerializer(instance=instance).data

            return Response(data=data)

        return Response(status=403)

    def put(self, request, pk):
        instance = get_object_or_404(Leave, pk=pk, approved="WAITING")

        if (
            request.user.is_superuser
            or request.user.userprofile.rolee in ["CountryManager"]
            or request.user.userprofile.speciality_rolee in ["Superviseur_national"]
            or request.user.has_perm("approve_absence")
        ):
            if request.user != instance.user:
                for key, value in request.data.items():
                    setattr(instance, key, value)

                instance.approval_user = request.user
                instance.save()

                return Response(status=204)
            else:
                return HttpResponseForbidden(
                    "Vous ne pouvez pas valider votre propre demande de congé."
                )

        return Response(status=403)


class LeaveTypesAPIView(APIView):
    def get(self, request):
        print("username ------- 4444")
        instances = LeaveType.objects.all()
        data = LeaveTypeSerializer(instance=instances, many=True).data
        return Response(data)


from django.utils import timezone
from rest_framework.exceptions import ValidationError


class LeaveFileUploadAPIView(APIView):

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    def put(self, request):
        request.data._mutable = True
        leave_type = get_object_or_404(LeaveType, pk=request.data.pop("leave_type")[0])
        user = get_object_or_404(User, username=request.data.get("username"))

        end_date_str = request.data.get("end_date")

        if end_date_str:
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        else:
            end_date = None

        today = timezone.now().date()

        start_date_str = request.data.get("start_date")

        if start_date_str:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        else:
            start_date = None

        if start_date < today or end_date < today:
            return Response({"message": "Date antérieure impossible."}, status=430)

        if start_date > end_date:
            return Response({"message": "Start date superior to end date."}, status=440)

        if start_date == end_date:
            return Response(
                {"message": "Impossible d'ajouter un congé le même jour."}, status=400
            )
        else:

            absences = Absence.objects.filter(
                user=user, date__range=[start_date, end_date]
            )
            leave = Leave.objects.filter(
                user=user, start_date=start_date, end_date=end_date
            )
            if absences.exists():
                return Response({"message": "Absence existe deja."}, status=410)
            if leave.exists():
                return Response({"message": "Congé existe deja."}, status=420)
            else:
                instance = Leave.objects.create(
                    user=user,
                    author=request.user,
                    leave_type=leave_type,
                    start_date=start_date,
                    end_date=end_date,
                    address=request.data.get("address"),
                    attachement=request.data.get("attachement"),
                    observation=request.data.get("observation"),
                )

                notification = Notification.objects.create(
                    title=f"Nouvelle demande de congé !",
                    description=f"{instance.user.username} vient d'ajouter une demande de congé",
                    data={
                        "name": "Congé & Absence",
                        "title": "Congé & Absence",
                        "message": f"Nouvelle demande de congé par {instance.user.username}",
                        "confirm_text": "voir",
                        "cancel_text": "plus tard",
                        "StackName": "Versement",
                        "url": f"https://app.liliumpharma.com/leaves/front?user={instance.user}&starting_date={instance.start_date}&ending_date={instance.end_date}",
                    },
                )

                users_with_permissions = list(
                    User.objects.filter(
                        userprofile__speciality_rolee="Finance_et_comptabilité"
                    )
                )
                users_office = list(User.objects.filter(username="mohammed"))
                other_users_to_notify = list(
                    [usr for usr in instance.user.userprofile.get_users_to_notify()]
                )

                all_users_to_notify = (
                    users_with_permissions + users_office + other_users_to_notify
                )

                # Définir les utilisateurs pour la notification
                notification.users.set(all_users_to_notify)
                # notification.send()

                return Response(status=204)


class AbsenceAPIView(APIView):

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        instance = get_object_or_404(Absence, pk=pk, approved="WAITING")

        if (
            request.user.is_superuser
            or request.user.userprofile.rolee in ["CountryManager"]
            or request.user.has_perm("approve_absence")
        ):
            for key, value in request.data.items():
                setattr(instance, key, value)

            instance.approval_user = request.user
            instance.save()

            return Response(status=204)

        return Response(status=403)


class AbsenceFileUploadAPIView(APIView):

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    def put(self, request, pk):
        instance = get_object_or_404(Absence, pk=pk, approved="WAITING")

        if request.user == instance.user:
            absence_type = get_object_or_404(
                AbsenceType, pk=request.data.pop("absence_type")[0]
            )
            instance.absence_type = absence_type
            for key, value in request.data.items():
                setattr(instance, key, value)
            instance.save()
            return Response(status=204)

        return Response(status=403)


class AbsenceTypesAPIView(APIView):
    def get(self, request):
        print("username ------- 555")
        instances = AbsenceType.objects.all()
        data = AbsenceTypeSerializer(instance=instances, many=True).data
        return Response(data)


from datetime import datetime
from datetime import timedelta

from collections import defaultdict
import json


from django.http import JsonResponse


# class ReportView(APIView):
#     def get(self, request):
#         requester = request.user
#         requester_company = requester.userprofile.company

#         # Retrieve starting_date and ending_date from the URL query parameters
#         starting_date_param = request.GET.get("starting_date")
#         ending_date_param = request.GET.get("ending_date")

#         # Convert starting_date and ending_date parameters to datetime objects
#         starting_date = datetime.strptime(starting_date_param, "%Y-%m-%d")
#         ending_date = datetime.strptime(ending_date_param, "%Y-%m-%d")

#         # Filter leaves and absences based on starting_date and ending_date
#         if requester.userprofile.speciality_rolee == "Superviseur_national":
#             requester_family = requester.userprofile.family
#             leaves = Leave.objects.filter(
#                 start_date__range=[starting_date, ending_date],
#                 user__userprofile__hidden=False,
#                 user__userprofile__family=requester_family,
#             )
#             absences = Absence.objects.filter(
#                 date__range=[starting_date, ending_date],
#                 user__userprofile__hidden=False,
#                 user__userprofile__family=requester_family,
#             )
#         else:
#             if (
#                 requester.userprofile.speciality_rolee == "CountryManager"
#                 or requester.is_superuser
#             ):
#                 leaves = Leave.objects.filter(
#                     start_date__range=[starting_date, ending_date],
#                     user__userprofile__hidden=False,
#                     user__userprofile__company=requester_company,
#                 )
#                 absences = Absence.objects.filter(
#                     date__range=[starting_date, ending_date],
#                     user__userprofile__hidden=False,
#                     user__userprofile__company=requester_company,
#                 )
#             else:
#                 leaves = Leave.objects.filter(
#                     start_date__range=[starting_date, ending_date],
#                     user__username=requester,
#                 )
#                 absences = Absence.objects.filter(
#                     date__range=[starting_date, ending_date], user__username=requester
#                 )

#         leave_response = []
#         absence_response = []
#         leave_counts = defaultdict(int)
#         leave_days_taken = defaultdict(
#             int
#         )  # To store the total days taken for each leave type

#         # Calculate leave-related data
#         if leaves.exists():
#             for leave in leaves:
#                 difference_in_days = (leave.end_date - leave.start_date).days

#                 # Calculer le nombre de jours pris
#                 if leave.start_date.month == leave.end_date.month:
#                     # Si les dates de début et de fin sont dans le même mois
#                     nombre_jours_pris = (leave.end_date - leave.start_date).days
#                 else:
#                     jours_du_mois_debut = (
#                         leave.start_date.replace(day=1) + timedelta(days=32)
#                     ).replace(day=1) - leave.start_date
#                     jours_pris_dans_mois_debut = min(
#                         jours_du_mois_debut.days,
#                         (
#                             leave.start_date + timedelta(days=jours_du_mois_debut.days)
#                         ).day
#                         - leave.start_date.day,
#                     )
#                     jours_pris_dans_mois_fin = leave.end_date.day
#                     nombre_jours_pris = (
#                         jours_pris_dans_mois_debut + jours_pris_dans_mois_fin
#                     )

#                 if nombre_jours_pris == 0:
#                     nombre_jours_pris = 1

#                 if nombre_jours_pris < 0:
#                     nombre_jours_pris = (leave.end_date - leave.start_date).days + 1

#                 difference_in_days = (leave.end_date - leave.start_date).days

#                 leave_response.append(
#                     {
#                         "id": leave.id,
#                         "user": f"{leave.user.first_name} {leave.user.last_name}",
#                         "family": leave.user.userprofile.family,
#                         "type": leave.leave_type.description,
#                         "starting_date": leave.start_date,
#                         "ending_date": leave.end_date,
#                         "actif": "oui" if leave.user.is_active else "non",
#                         "nombre_jours_pris": difference_in_days,  # Include the difference in days
#                         "status": leave.approved,
#                     }
#                 )

#                 leave_counts[leave.leave_type.description] += 1
#                 leave_days_taken[leave.leave_type.description] += difference_in_days

#         absence_count_per_user = defaultdict(int)
#         if absences.exists():
#             for absence in absences:
#                 user_name = f"{absence.user.first_name} {absence.user.last_name}"
#                 absence_response.append(
#                     {
#                         "id": absence.id,
#                         "user": user_name,
#                         "family": absence.user.userprofile.family,
#                         "reason": absence.reason,
#                         "starting_date": absence.date,
#                         "ending_date": absence.date,
#                         "status": absence.approved,
#                     }
#                 )
#                 absence_count_per_user[user_name] += 1

#         absence_count_per_user_list = [
#             {"user": user, "absence_count": count}
#             for user, count in absence_count_per_user.items()
#         ]

#         leave_counts_json = json.dumps(leave_counts)
#         leave_days_taken_json = json.dumps(leave_days_taken)

#         return render(
#             request,
#             "holidays/report.html",
#             {
#                 "leaves": leave_response,
#                 "absences": absence_response,
#                 "starting_date": starting_date,
#                 "ending_date": ending_date,
#                 "leave_counts": leave_counts_json,
#                 "leave_days_taken_json": leave_days_taken_json,
#                 "absence_count_per_user": absence_count_per_user_list,
#             },
#         )


# class ReportView(APIView):
#     def get(self, request):
#         requester = request.user
#         requester_company = requester.userprofile.company

#         # Retrieve starting_date, ending_date, and user from the URL query parameters
#         starting_date_param = request.GET.get("starting_date")
#         ending_date_param = request.GET.get("ending_date")
#         selected_user_param = request.GET.get("user")  # Get user parameter

#         # Convert starting_date and ending_date parameters to datetime objects
#         starting_date = datetime.strptime(starting_date_param, "%Y-%m-%d")
#         ending_date = datetime.strptime(ending_date_param, "%Y-%m-%d")

#         # Get the selected user object if user is specified
#         selected_user = None
#         if selected_user_param:
#             try:
#                 selected_user = User.objects.get(username=selected_user_param)
#             except User.DoesNotExist:
#                 selected_user = None

#         # Filter leaves and absences based on starting_date, ending_date, and optionally the user
#         if requester.userprofile.speciality_rolee == "Superviseur_national":
#             requester_family = requester.userprofile.family
#             leaves = Leave.objects.filter(
#                 start_date__range=[starting_date, ending_date],
#                 user__userprofile__hidden=False,
#                 user__userprofile__family=requester_family,
#             )
#             absences = Absence.objects.filter(
#                 date__range=[starting_date, ending_date],
#                 user__userprofile__hidden=False,
#                 user__userprofile__family=requester_family,
#             )
#         else:
#             if (
#                 requester.userprofile.speciality_rolee == "CountryManager"
#                 or requester.is_superuser
#             ):
#                 leaves = Leave.objects.filter(
#                     start_date__range=[starting_date, ending_date],
#                     user__userprofile__hidden=False,
#                     user__userprofile__company=requester_company,
#                 )
#                 absences = Absence.objects.filter(
#                     date__range=[starting_date, ending_date],
#                     user__userprofile__hidden=False,
#                     user__userprofile__company=requester_company,
#                 )
#             else:
#                 leaves = Leave.objects.filter(
#                     start_date__range=[starting_date, ending_date],
#                     user__username=requester,
#                 )
#                 absences = Absence.objects.filter(
#                     date__range=[starting_date, ending_date], user__username=requester
#                 )

#         # If a specific user is provided, filter results for that user only
#         if selected_user:
#             leaves = leaves.filter(user=selected_user)
#             absences = absences.filter(user=selected_user)

#         leave_response = []
#         absence_response = []
#         leave_counts = defaultdict(int)
#         leave_days_taken = defaultdict(
#             int
#         )  # To store the total days taken for each leave type

#         # Calculate leave-related data
#         if leaves.exists():
#             for leave in leaves:
#                 difference_in_days = (leave.end_date - leave.start_date).days

#                 # Calculer le nombre de jours pris
#                 if leave.start_date.month == leave.end_date.month:
#                     # Si les dates de début et de fin sont dans le même mois
#                     nombre_jours_pris = (leave.end_date - leave.start_date).days
#                 else:
#                     jours_du_mois_debut = (
#                         leave.start_date.replace(day=1) + timedelta(days=32)
#                     ).replace(day=1) - leave.start_date
#                     jours_pris_dans_mois_debut = min(
#                         jours_du_mois_debut.days,
#                         (
#                             leave.start_date + timedelta(days=jours_du_mois_debut.days)
#                         ).day
#                         - leave.start_date.day,
#                     )
#                     jours_pris_dans_mois_fin = leave.end_date.day
#                     nombre_jours_pris = (
#                         jours_pris_dans_mois_debut + jours_pris_dans_mois_fin
#                     )

#                 if nombre_jours_pris == 0:
#                     nombre_jours_pris = 1

#                 if nombre_jours_pris < 0:
#                     nombre_jours_pris = (leave.end_date - leave.start_date).days + 1

#                 difference_in_days = (leave.end_date - leave.start_date).days

#                 leave_response.append(
#                     {
#                         "id": leave.id,
#                         "user": f"{leave.user.first_name} {leave.user.last_name}",
#                         "family": leave.user.userprofile.family,
#                         "type": leave.leave_type.description,
#                         "starting_date": leave.start_date,
#                         "ending_date": leave.end_date,
#                         "actif": "oui" if leave.user.is_active else "non",
#                         "nombre_jours_pris": difference_in_days,  # Include the difference in days
#                         "status": leave.approved,
#                     }
#                 )

#                 leave_counts[leave.leave_type.description] += 1
#                 leave_days_taken[leave.leave_type.description] += difference_in_days

#         absence_count_per_user = defaultdict(int)
#         if absences.exists():
#             for absence in absences:
#                 user_name = f"{absence.user.first_name} {absence.user.last_name}"
#                 absence_response.append(
#                     {
#                         "id": absence.id,
#                         "user": user_name,
#                         "family": absence.user.userprofile.family,
#                         "reason": absence.reason,
#                         "starting_date": absence.date,
#                         "ending_date": absence.date,
#                         "status": absence.approved,
#                     }
#                 )
#                 absence_count_per_user[user_name] += 1

#         absence_count_per_user_list = [
#             {"user": user, "absence_count": count}
#             for user, count in absence_count_per_user.items()
#         ]

#         leave_counts_json = json.dumps(leave_counts)
#         leave_days_taken_json = json.dumps(leave_days_taken)

#         return render(
#             request,
#             "holidays/report.html",
#             {
#                 "leaves": leave_response,
#                 "absences": absence_response,
#                 "starting_date": starting_date,
#                 "ending_date": ending_date,
#                 "leave_counts": leave_counts_json,
#                 "leave_days_taken_json": leave_days_taken_json,
#                 "absence_count_per_user": absence_count_per_user_list,
#             },
#         )

from collections import defaultdict
from datetime import datetime, timedelta
from rest_framework.views import APIView
from django.shortcuts import render
from .models import Leave, Absence
from django.contrib.auth.models import User
import json


# class ReportView(APIView):
#     def get(self, request):
#         requester = request.user
#         requester_company = requester.userprofile.company

#         # Retrieve starting_date, ending_date, and user from the URL query parameters
#         starting_date_param = request.GET.get("starting_date")
#         ending_date_param = request.GET.get("ending_date")
#         selected_user_param = request.GET.get("user")  # Get user parameter

#         # Convert starting_date and ending_date parameters to datetime objects
#         starting_date = datetime.strptime(starting_date_param, "%Y-%m-%d")
#         ending_date = datetime.strptime(ending_date_param, "%Y-%m-%d")

#         # Get the selected user object if user is specified
#         selected_user = None
#         if selected_user_param:
#             try:
#                 selected_user = User.objects.get(username=selected_user_param)
#             except User.DoesNotExist:
#                 selected_user = None

#         # Filter leaves and absences based on starting_date, ending_date, and optionally the user
#         if requester.userprofile.speciality_rolee == "Superviseur_national":
#             requester_family = requester.userprofile.family
#             leaves = Leave.objects.filter(
#                 start_date__range=[starting_date, ending_date],
#                 end_date__range=[starting_date, ending_date],
#                 user__userprofile__hidden=False,
#                 user__userprofile__family=requester_family,
#             )
#             absences = Absence.objects.filter(
#                 date__range=[starting_date, ending_date],
#                 user__userprofile__hidden=False,
#                 user__userprofile__family=requester_family,
#             )
#         else:
#             if (
#                 requester.userprofile.speciality_rolee == "CountryManager"
#                 or requester.is_superuser
#             ):
#                 leaves = Leave.objects.filter(
#                     start_date__range=[starting_date, ending_date],
#                     user__userprofile__hidden=False,
#                     user__userprofile__company=requester_company,
#                 )
#                 absences = Absence.objects.filter(
#                     date__range=[starting_date, ending_date],
#                     user__userprofile__hidden=False,
#                     user__userprofile__company=requester_company,
#                 )
#             else:
#                 leaves = Leave.objects.filter(
#                     start_date__range=[starting_date, ending_date],
#                     end_date__range=[starting_date, ending_date],
#                     user=requester,
#                 )
#                 absences = Absence.objects.filter(
#                     date__range=[starting_date, ending_date], user=requester
#                 )

#         # If a specific user is provided, filter results for that user only
#         if selected_user:
#             leaves = leaves.filter(user=selected_user)
#             absences = absences.filter(user=selected_user)

#         leave_response = []
#         absence_response = []
#         leave_counts = defaultdict(int)
#         leave_days_taken = defaultdict(int)

#         # Calculate leave-related data
#         for leave in leaves:
#             difference_in_days = (
#                 leave.end_date - leave.start_date
#             ).days + 1  # Include both start and end days
#             leave_response.append(
#                 {
#                     "id": leave.id,
#                     "user": f"{leave.user.first_name} {leave.user.last_name}",
#                     "family": leave.user.userprofile.family,
#                     "type": leave.leave_type.description,
#                     "starting_date": leave.start_date,
#                     "ending_date": leave.end_date,
#                     "actif": "oui" if leave.user.is_active else "non",
#                     "nombre_jours_pris": difference_in_days,
#                     "status": leave.approved,
#                 }
#             )
#             leave_counts[leave.leave_type.description] += 1
#             leave_days_taken[leave.leave_type.description] += difference_in_days

#         # Calculate absence-related data
#         absence_count_per_user = defaultdict(int)
#         for absence in absences:
#             user_name = f"{absence.user.first_name} {absence.user.last_name}"
#             absence_response.append(
#                 {
#                     "id": absence.id,
#                     "user": user_name,
#                     "family": absence.user.userprofile.family,
#                     "reason": absence.reason,
#                     "starting_date": absence.date,
#                     "ending_date": absence.date,  # Absences typically last one day
#                     "status": absence.approved,
#                 }
#             )
#             absence_count_per_user[user_name] += 1

#         absence_count_per_user_list = [
#             {"user": user, "absence_count": count}
#             for user, count in absence_count_per_user.items()
#         ]

#         leave_counts_json = json.dumps(leave_counts)
#         leave_days_taken_json = json.dumps(leave_days_taken)

#         return render(
#             request,
#             "holidays/report.html",
#             {
#                 "leaves": leave_response,
#                 "absences": absence_response,
#                 "starting_date": starting_date,
#                 "ending_date": ending_date,
#                 "leave_counts": leave_counts_json,
#                 "leave_days_taken_json": leave_days_taken_json,
#                 "absence_count_per_user": absence_count_per_user_list,
#             },
#         )


from django.db.models import Q

from datetime import timedelta

# Function to check if a date is a Friday or Saturday
def is_weekend(date):
    return date.weekday() in [4, 5] 

from collections import defaultdict
from datetime import datetime, timedelta
from django.shortcuts import render
from django.db.models import Q
from rest_framework.views import APIView
import json
from django.shortcuts import render
from django.db.models import Count, F, Sum
from django.contrib.auth.models import User
from .models import Leave
from datetime import datetime, timedelta

# Fonction pour exclure les vendredis et samedis d'une période donnée
def get_working_days(start_date, end_date):
    total_days = (end_date - start_date).days + 1
    working_days = 0
    current_day = start_date
    while current_day < end_date:
        # Exclure vendredi (weekday() == 4) et samedi (weekday() == 5)
        if current_day.weekday() not in [4, 5]:
            working_days += 1
        current_day += timedelta(days=1)
    return working_days

def get_working_days_with_wend(start_date, end_date):
    total_days = (end_date - start_date).days + 1
    working_days = 0
    current_day = start_date
    while current_day < end_date:
        # Exclure vendredi (weekday() == 4) et samedi (weekday() == 5)
        working_days += 1
        current_day += timedelta(days=1)
    return working_days

from django.db.models import Prefetch
from django.utils.timezone import make_aware
from rapports.models import *

from django.utils.timezone import make_aware
from datetime import datetime, timedelta
class ReportView(APIView):
    def get(self, request):
        # Récupérer les types de congés existants
        leave_types = LeaveType.objects.values_list('description', flat=True)

        # Récupérer les dates fournies dans les paramètres GET
        starting_date_param = request.GET.get("starting_date")
        ending_date_param = request.GET.get("ending_date")

        # Convertir les paramètres en objets datetime, avec gestion du fuseau horaire
        if starting_date_param:
            starting_date = datetime.strptime(starting_date_param, "%Y-%m-%d")
            starting_date = make_aware(starting_date) if not isinstance(starting_date, datetime) else starting_date
        else:
            starting_date = None

        if ending_date_param:
            ending_date = datetime.strptime(ending_date_param, "%Y-%m-%d")
            ending_date = make_aware(ending_date) if not isinstance(ending_date, datetime) else ending_date
        else:
            ending_date = None

        # Récupérer les utilisateurs avec des congés et des absences
        users_with_leaves = User.objects.filter(userprofile__company__in=["lilium pharma", "production"], userprofile__is_human = True)

        # Initialiser un dictionnaire global pour le total des jours pris par type de congé et absences
        total_by_leave_type = {leave_type: 0 for leave_type in leave_types}
        total_absence_days = 0  # Total global pour les absences

        # Préparer les données pour le template
        user_data = []
        num_id = 1
        globale_total_days = 0

        for user in users_with_leaves:
            # Filtrer les leaves en fonction des dates et du statut 'approved=ACCEPTED'
            leaves = Leave.objects.filter(user=user, approved='ACCEPTED')

            if starting_date and ending_date:
                # Filtrer les leaves en fonction des dates fournies
                leaves = leaves.filter(start_date__lte=ending_date, end_date__gte=starting_date)

            # Initialiser un dictionnaire pour les types de congé avec 0 jours pour cet utilisateur
            leaves_by_type = {leave_type: 0 for leave_type in leave_types}
            absence_days = 0
            total_days = 0
            total_days_with_wend = 0

            for leave in leaves:
                # Convertir les dates des congés en `datetime` si elles sont stockées comme `date`
                leave_start = leave.start_date
                leave_end = leave.end_date

                if isinstance(leave_start, datetime):
                    leave_start = leave_start.date()

                if isinstance(leave_end, datetime):
                    leave_end = leave_end.date()

                # Calcul des jours effectivement pris dans la période de filtrage
                actual_start_date = max(leave_start, starting_date.date()) if starting_date else leave_start
                actual_end_date = min(leave_end, ending_date.date()) if ending_date else leave_end

                # Calculer les jours pris en excluant les vendredis et samedis
                days_taken = get_working_days(actual_start_date, actual_end_date)
                total_days_with_wend_a = get_working_days_with_wend(leave_start, leave_end)

                # Grouper par type de congé
                if leave.leave_type.description in leaves_by_type:
                    leaves_by_type[leave.leave_type.description] += days_taken
                    # Ajouter au total global pour ce type de congé
                    total_by_leave_type[leave.leave_type.description] += days_taken

                total_days += days_taken
                total_days_with_wend = total_days_with_wend + total_days_with_wend_a

            # Récupérer les absences de l'utilisateur
            absences = Absence.objects.filter(user=user)

            if starting_date and ending_date:
                # Filtrer les absences en fonction des dates fournies
                absences = absences.filter(date__lte=ending_date, date__gte=starting_date)
            if starting_date and ending_date:
                rapports = Rapport.objects.filter(
                    user=user, added__range=[starting_date, ending_date]
                )
            elif starting_date:
                rapports = Rapport.objects.filter(user=user, added__gte=starting_date)
            elif ending_date:
                rapports = Rapport.objects.filter(user=user, added__lte=ending_date)
            else:
                rapports = Rapport.objects.filter(user=user)
            # Étape 2 : Annoter le nombre de visites
            rapports = rapports.annotate(nb_visites=Count('visite', distinct=True))

            # Étape 3 : Garder seulement ceux ayant moins de 6 visites
            rapports = rapports.filter(nb_visites__lt=6).order_by('added')
            
            rapport_vide_count = rapports.count()
            
            #if user.userprofile.speciality_rolee in ["Superviseur_regional", "Superviseur_national", "CountryManager", "Commercial", "Medico_commercial"]:
            if 1:
                for t in rapports:
                    plan = Plan.objects.filter(user=user, day=t.added).first()
                    if plan and plan.plantask_set.exists():
                        rapport_vide_count -= 1
            
            
            for absence in absences:
                # Calculer les jours d'absence pris (1 jour par absence)
                absence_days += 1
                total_absence_days += 1  # Ajouter un jour au total global des absences
                total_days += 1  # Ajouter un jour au total global pour cet utilisateur

            # Ajouter les informations de chaque utilisateur dans la liste user_data
            user_data.append({
                'num_id': num_id,
                'username': user.username,
                'company': user.userprofile.speciality_rolee,
                'pc_paie_id': user.userprofile.pc_paie_id,
                'absence_days': absence_days,
                'leaves_by_type': leaves_by_type,
                'total_days': total_days,
                'rapport_vide': rapport_vide_count,
                'total_days_with_wend':total_days_with_wend
            })
            num_id += 1
            globale_total_days += total_days

        # Ne pas exclure de leave_types, garder tous les types
        # Exclure les types de congés ayant un total de 0 dans `total_by_leave_type`
        total_by_leave_type = {leave_type: total for leave_type, total in total_by_leave_type.items() if total > 0}

        # Filtrer leave_types pour exclure ceux qui ont un total de 0
        filtered_leave_types = [leave_type for leave_type in leave_types if total_by_leave_type.get(leave_type, 0) > 0]


        # Trier les utilisateurs d'abord par entreprise (company) puis par total de jours (total_days)
        #user_data = sorted(user_data, key=lambda x: (x['company'], x['total_days']), reverse=True)
        user_data = sorted(user_data, key=lambda x: x['total_days_with_wend'], reverse=True)


        # Créer l'objet date_infos
        date_infos = {
            'starting_date': starting_date_param,
            'ending_date': ending_date_param
        }

        # Rendu de la page avec les données, incluant total_by_leave_type et total_absence_days
        return render(request, 'holidays/index2.html', {
            'users': user_data,
            'leave_types': filtered_leave_types,  # Ne pas exclure les leave_types, même ceux avec total 0
            'total_by_leave_type': total_by_leave_type,  # Total global par type de congé
            'total_absence_days': total_absence_days,    # Total global pour les absences
            'date_infos': date_infos, # Ajout de date_infos
            'globale_total_days': globale_total_days
        })






# class ReportView(APIView):
#     def get(self, request):
#         requester = request.user
#         requester_company = requester.userprofile.company

#         # Retrieve starting_date, ending_date, and user from the URL query parameters
#         starting_date_param = request.GET.get("starting_date")
#         ending_date_param = request.GET.get("ending_date")
#         selected_user_param = request.GET.get("user")  # Get user parameter

#         # Convert starting_date and ending_date parameters to datetime objects
#         starting_date = datetime.strptime(starting_date_param, "%Y-%m-%d")
#         ending_date = datetime.strptime(ending_date_param, "%Y-%m-%d")

#         # Get the selected user object if user is specified
#         selected_user = None
#         if selected_user_param:
#             try:
#                 selected_user = User.objects.get(username=selected_user_param)
#             except User.DoesNotExist:
#                 selected_user = None

#         # Define the query for leaves that overlap with the filter range
#         leave_query = Q(
#             start_date__lte=ending_date,  # Leave starts before or on the end date of the filter
#             end_date__gte=starting_date,  # Leave ends after or on the start date of the filter
#         )

#         # Filter leaves and absences based on starting_date, ending_date, and optionally the user
#         if requester.userprofile.speciality_rolee == "Superviseur_national":
#             requester_family = requester.userprofile.family
#             leaves = Leave.objects.filter(
#                 leave_query,
#                 user__userprofile__hidden=False,
#                 user__userprofile__family=requester_family,
#             )
#             absences = Absence.objects.filter(
#                 date__range=[starting_date, ending_date],
#                 user__userprofile__hidden=False,
#                 user__userprofile__family=requester_family,
#             )
#         else:
#             if requester.userprofile.speciality_rolee == "CountryManager" or requester.is_superuser:
#                 leaves = Leave.objects.filter(
#                     leave_query,
#                     user__userprofile__hidden=False,
#                     user__userprofile__company=requester_company,
#                 )
#                 absences = Absence.objects.filter(
#                     date__range=[starting_date, ending_date],
#                     user__userprofile__hidden=False,
#                     user__userprofile__company=requester_company,
#                 )
#             else:
#                 leaves = Leave.objects.filter(
#                     leave_query,
#                     user=requester,
#                 )
#                 absences = Absence.objects.filter(
#                     date__range=[starting_date, ending_date],
#                     user=requester
#                 )

#         # If a specific user is provided, filter results for that user only
#         if selected_user:
#             leaves = leaves.filter(user=selected_user)
#             absences = absences.filter(user=selected_user)

#         # The rest of your leave and absence calculation logic remains the same

#         leave_response = []
#         absence_response = []
#         leave_counts = defaultdict(int)
#         leave_days_taken = defaultdict(int)

#         # Calculate leave-related data
#         leaves = leaves.order_by('leave_type__description')

#         for leave in leaves:
#             effective_start = max(leave.start_date, starting_date.date())
#             effective_end = min(leave.end_date, ending_date.date())
        
#             total_days = 0
        
#             # Loop through the dates in the range
#             current_date = effective_start
#             while current_date <= effective_end:
#                 if not is_weekend(current_date):  # Exclude Friday and Saturday
#                     total_days += 1
#                 current_date += timedelta(days=1)
        
#             # Subtract 1 day to avoid counting the first day (if necessary)
#             if total_days > 0:
#                 total_days -= 1

#             # Calculate the difference in days
#             difference_in_days = (effective_end - effective_start).days + 1
        
#             leave_response.append(
#                 {
#                     "id": leave.id,
#                     "user": f"{leave.user.first_name} {leave.user.last_name}",
#                     "family": leave.user.userprofile.family,
#                     "attachement": leave.attachement,
#                     "type": leave.leave_type.description,
#                     "starting_date": leave.start_date,
#                     "ending_date": leave.end_date,
#                     "actif": "oui" if leave.user.is_active else "non",
#                     "nombre_jours_pris": total_days,  # Only days within the filter range excluding weekends
#                     "status": leave.approved,
#                 }
#             )

#             leave_counts[leave.leave_type.description] += 1
#             leave_days_taken[leave.leave_type.description] += difference_in_days

#         # Calculate absence-related data
#         absence_count_per_user = defaultdict(int)
#         for absence in absences:
#             user_name = f"{absence.user.first_name} {absence.user.last_name}"
#             absence_response.append(
#                 {
#                     "id": absence.id,
#                     "user": user_name,
#                     "family": absence.user.userprofile.family,
#                     "reason": absence.reason,
#                     "starting_date": absence.date,
#                     "ending_date": absence.date,  # Absences typically last one day
#                     "status": absence.approved,
#                 }
#             )
#             absence_count_per_user[user_name] += 1

#         absence_count_per_user_list = [
#             {"user": user, "absence_count": count}
#             for user, count in absence_count_per_user.items()
#         ]

#         leave_counts_json = json.dumps(leave_counts)
#         leave_days_taken_json = json.dumps(leave_days_taken)

#         return render(
#             request,
#             "holidays/report.html",
#             {
#                 "leaves": leave_response,
#                 "absences": absence_response,
#                 "starting_date": starting_date,
#                 "ending_date": ending_date,
#                 "leave_counts": leave_counts_json,
#                 "leave_days_taken_json": leave_days_taken_json,
#                 "absence_count_per_user": absence_count_per_user_list,
#             },
#         )


def leaves_frontend(request):
    if request.user.is_authenticated:
        token = Token.objects.filter(user=request.user)

        if token.exists():
            token = token.first().key
        else:
            token = Token.objects.create(user=request.user).key

    return render(
        request,
        "micro_frontends/leaves/index.html",
        {"token": token if request.user.is_authenticated else ""},
    )


def holidaysPDF(request, id):
    return render(request, "holidays/pdf.html", {"holiday": Holiday.objects.get(id=id)})


def MsAbsences(request):

    if request.user.is_authenticated:
        token = Token.objects.filter(user=request.user)

        if token.exists():
            token = token.first().key
        else:
            Token.objects.create(user=request.user)
            token = Token.objects.filter(user=request.user)
            token = token.first().key

    return render(
        request,
        "micro_frontends/absences/index.html",
        {"token": token if request.user.is_authenticated else ""},
    )

