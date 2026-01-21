from .models import *
from .serializers import *
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.db.models import Q, Count
from django.utils import timezone
from django.shortcuts import render, redirect
from django.core.mail import EmailMessage
from django.views.generic import TemplateView
from rest_framework.authtoken.models import Token
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.shortcuts import redirect


from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import authentication, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.authtoken.models import Token

from .forms import (
    Commercial_Monthly_EvaluationModelForm,
    MonthlyEvaluationModelForm,
    SupMonthlyEvaluationModelForm,
)

from rapports.models import *
from medecins.models import *

import json
from datetime import date


class CountMedecinsVisitesPerUser(APIView):
    authentication_classes = (
        TokenAuthentication,
        SessionAuthentication,
    )
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        users = User.objects.annotate(
            count_medecins_visites=Count("rapport__visite__medecin", distinct=True)
        ).filter(count_medecins_visites__gt=0)

        users_data = []
        for user in users:
            user_data = {
                "username": user.username,
                "count_medecins_visites": user.count_medecins_visites,
            }
            users_data.append(user_data)

        return Response(users_data)


class MonthlyEvaluationFront(APIView):
    authentication_classes = (
        TokenAuthentication,
        SessionAuthentication,
    )
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        if request.user.userprofile.speciality_rolee in ["Superviseur_national"]:
            print(request.GET.get("eve"))
            if request.GET.get("eve") is not None:
                usr = User.objects.filter(username=request.GET.get("user")).first()
                if usr.userprofile.speciality_rolee == "Medico_commercial":
                    return render(request, "monthly_evaluations/index copy.html")
                elif usr.userprofile.speciality_rolee == "Commercial":
                    return render(request, "monthly_evaluations/index_commercial.html")
            else:
                return render(request, "monthly_evaluations/index_supervisor.html")
        else:
            if request.user.userprofile.speciality_rolee in [
                "CountryManager",
                "Office",
                "Admin",
            ]:
                print(request.GET.get("eve"))
                if request.GET.get("eve") is not None:
                    usr = User.objects.filter(username=request.GET.get("user")).first()
                    if usr.userprofile.speciality_rolee == "Medico_commercial":
                        return render(request, "monthly_evaluations/index copy.html")
                    elif usr.userprofile.speciality_rolee == "Commercial":
                        return render(request, "monthly_evaluations/index_commercial.html")
                else:
                    return render(request, "monthly_evaluations/index_supervisor.html")
                    #return render(request, "monthly_evaluations/index_supervisor.html")
                    #return render(request, "monthly_evaluations/index_direction.html")
            else:
                if request.user.userprofile.speciality_rolee in [
                    "Medico_commercial",
                    "Superviseur_regional",
                ]:
                    return render(request, "monthly_evaluations/index copy.html")
                if request.user.userprofile.speciality_rolee in ["Commercial"]:
                    return render(request, "monthly_evaluations/index_commercial.html")

    def post(self, request):
        data = request.data.copy()
        us = request.GET.get("user")
        a = User.objects.filter(username=us).first()
        ME = Monthly_Evaluation.objects.filter(
            user=a, added__month=date.today().month
        )
        return render(request, "monthly_evaluations/index copy.html")


class MonthlyEvaluationFrontSupToDirection(APIView):
    authentication_classes = (
        TokenAuthentication,
        SessionAuthentication,
    )
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        print("called")
        if request.user.userprofile.speciality_rolee in ["Superviseur_national"]:
            print("hereee yes im sup")
            return render(
                request, "monthly_evaluations/index_supervisor_direction.html"
            )
        else:
            if request.user.userprofile.speciality_rolee in ["CountryManager"]:
                return render(
                    request, "monthly_evaluations/index_direction_supervisor.html"
                )

    def post(self, request):
        data = request.data.copy()
        ME = Monthly_Evaluation.objects.filter(
            user=request.user, added__month=date.today().month
        )
        return render(request, "monthly_evaluations/index copy.html")


#####################################################################################################################
# FOR MOBILE APP
class MonthlyEvaluationMobile(APIView):

    authentication_classes = (TokenAuthentication,)
    # permission_classes = (IsAuthenticated,)

    def get(self, request):

        if not request.user.is_authenticated:
            try:
                user = Token.objects.get(key=request.GET.get("token")).user
                print("the user is ", user)
                login(request, user)
                token = request.GET.get("token")
            except:
                return redirect("login")
        else:
            token = request.headers.get("Authorization").split()[-1]

        month = date.today().month
        if request.user.userprofile.speciality_rolee in [
            "CountryManager"
        ] or request.user.userprofile.rolee in ["CountryManager"]:
            print("hereee yes im cm")
            return render(
                request,
                "monthly_evaluations/index_direction_supervisor.html",
                context={"token": token, "month": month},
            )
        else:
            return render(
                request,
                "monthly_evaluations/mobile.html",
                context={"token": token, "month": month},
            )

    def post(self, request):
        data = request.data.copy()
        ME = Monthly_Evaluation.objects.filter(
            user=user, added__month=date.today().month
        )
        return render(request, "monthly_evaluations/mobile.html")


###############################################################################################################################


@login_required
def monthly_evaluations_front_test(request):
    if request.method == "POST":
        data = request.POST.copy()
        ME = Monthly_Evaluation.objects.filter(
            user=request.user, added__month=date.today().month
        )
    return render(request, "monthly_evaluations/index.html")


class AddCommercialeMonthlyEvaluation(APIView):

    authentication_classes = (
        TokenAuthentication,
        SessionAuthentication,
    )
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        data = request.data.copy()
        month_url = int(request.GET.get("month"))
        uu = request.GET.get("user")
        year = int(request.GET.get("year"))
        
        if uu:
            user = User.objects.filter(username=uu).first()
        else:
            user = request.user

        ME = Commercial_Monthly_Evaluation.objects.filter(
            user=user, added__year=year, added__month=month_url
        )

        if ME.exists():
            message = (
                "ATTENTION : Vous avez déjà un rapport mensuel pour le mois courant"
            )
            return Response({"message": message}, status=403)
        else:
            data.pop("csrfmiddlewaretoken")
            data["user"] = user
            if month_url in [1, 3, 5, 7, 8, 10, 12]:  # Mois avec 31 jours
                day_of_month = 31
            elif month_url in [4, 6, 9, 11]:  # Mois avec 30 jours
                day_of_month = 30
            else:
                is_leap_year = (
                    year % 4 == 0 and year % 100 != 0
                ) or year % 400 == 0
                day_of_month = 29 if is_leap_year else 28

            data["added"] = date(year, month_url, day_of_month)
            model_form = Commercial_Monthly_EvaluationModelForm(data)

            if model_form.is_valid():
                model_form.save()
            else:
                print(model_form.errors)
        return Response()


class AddMonthlyEvaluation(APIView):

    authentication_classes = (
        TokenAuthentication,
        SessionAuthentication,
    )
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        data = request.data.copy()
        #month_url = int(request.GET.get("month", date.today().month))
        month_url = int(request.GET.get("month"))
        uu = request.GET.get("user")
        if uu:
            user = User.objects.filter(username=uu).first()
        else:
            user = request.user
        print(f"month {month_url}  user  {user}")
        ME = Monthly_Evaluation.objects.filter(
            user=user, added__year=date.today().year, added__month=month_url
        )

        if ME.exists():
            message = (
                "ATTENTION : Vous avez déjà un rapport mensuel pour le mois courant"
            )
            return Response({"message": message}, status=403)
        else:
            data.pop("csrfmiddlewaretoken")
            data["user"] = user
            if month_url in [1, 3, 5, 7, 8, 10, 12]:  # Mois avec 31 jours
                day_of_month = 31
            elif month_url in [4, 6, 9, 11]:  # Mois avec 30 jours
                day_of_month = 30
            else:
                is_leap_year = (
                    date.today().year % 4 == 0 and date.today().year % 100 != 0
                ) or date.today().year % 400 == 0
                day_of_month = 29 if is_leap_year else 28

            data["added"] = date(date.today().year, month_url, day_of_month)
            model_form = MonthlyEvaluationModelForm(data)

            if model_form.is_valid():
                model_form.save()
            else:
                print(model_form.errors)
        return Response()


# class MonthlyEvaluationView(APIView):
#     def get(self, request):
#         # user = request.user
#         user = User.objects.get(username='aimen')
#         current_month = date.today().month

#         monthly_evaluations = Monthly_Evaluation.objects.filter(
#             user=user,
#             added__month=current_month
#         )

#         evaluations_data = []

#         for evaluation in monthly_evaluations:
#             evaluation_data = {
#                 'q1': evaluation.q1,
#                 'q2': evaluation.q2,
#                 'q3': evaluation.q3,
#                 'q4': evaluation.q4,
#                 'q5': evaluation.q5,
#                 'q6': evaluation.q6,
#                 'q7': evaluation.q7,
#                 'q8': evaluation.q8,
#                 'q9': evaluation.q9,
#                 'q10': evaluation.q10,
#             }
#             evaluations_data.append(evaluation_data)

#         context = {'evaluation': evaluations_data}
#         print(evaluations_data)
#         return render(request, 'monthly_evaluations/pdf.html', context)

from django.http import JsonResponse
from django.core.serializers import serialize


class MonthlyEvaluationView(APIView):
    def get(self, request):
        user = request.GET.get("user")
        print(f"le user est {user}")
        id_username = User.objects.get(username=user)
        month = request.GET.get("month")
        current_year = int(request.GET.get("year"))
        #current_year = datetime.now().year

        monthly_evaluations = Monthly_Evaluation.objects.filter(
            user=id_username,
            added__month=month,
            added__year=current_year,
        )

        # Get the primary keys of filtered Monthly_Evaluation instances
        monthly_evaluation_pks = list(monthly_evaluations.values_list("pk", flat=True))

        # Serialize the list of primary keys to JSON
        data = json.dumps(monthly_evaluation_pks)

        # Return a JSON response with the serialized data
        return JsonResponse(data, safe=False)


# VIEW FOR PRINT BUTTON ADMINISTRATION
class MEPDF(APIView):
    # authentication_classes = (TokenAuthentication, SessionAuthentication,)
    # permission_classes = (IsAuthenticated,)
    def get(self, request, id):

        monthly_evaluation = Monthly_Evaluation.objects.get(id=id)
        user = monthly_evaluation.user
        month = monthly_evaluation.added.month
        year = monthly_evaluation.added.year

        if monthly_evaluation.user.userprofile.speciality_rolee == "Commercial":
            try:
                sup_monthly_evaluation = SupEvaluation.objects.get(
                    added__month=month, added__year=year, user=user
                )
            except SupEvaluation.DoesNotExist:
                sup_monthly_evaluation = None

            try:
                direction_to_delegate_evaluation = (
                    DirectionToDelegateEvaluation.objects.get(
                        added__month=month, added__year=year, user=user
                    )
                )
            except DirectionToDelegateEvaluation.DoesNotExist:
                direction_to_delegate_evaluation = None

            return render(
                request,
                "monthly_evaluations/pdf_commerciale.html",
                {
                    "evaluation": monthly_evaluation,
                    "sup_evaluation": sup_monthly_evaluation,
                    "direction_eval": direction_to_delegate_evaluation,
                },
            )

        else:

            try:
                sup_monthly_evaluation = SupEvaluation.objects.get(
                    added__month=month, added__year=year, user=user
                )
            except SupEvaluation.DoesNotExist:
                sup_monthly_evaluation = None

            try:
                direction_to_delegate_evaluation = (
                    DirectionToDelegateEvaluation.objects.get(
                        added__month=month, added__year=year, user=user
                    )
                )
            except DirectionToDelegateEvaluation.DoesNotExist:
                direction_to_delegate_evaluation = None

            return render(
                request,
                "monthly_evaluations/pdf.html",
                {
                    "evaluation": monthly_evaluation,
                    "sup_evaluation": sup_monthly_evaluation,
                    "direction_eval": direction_to_delegate_evaluation,
                },
            )


# VIEW FOR PRINT BUTTON INTERFACE
from datetime import datetime


class print_evaluation(APIView):
    authentication_classes = (
        TokenAuthentication,
        SessionAuthentication,
    )
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        u = request.GET.get("user")
        if u:
            user = User.objects.filter(username=u).first()
        else:
            user = request.user
        default_month = str(int(datetime.now().month) - 1)
        current_year = int(request.GET.get("year"))
        #current_year = datetime.now().year
        month_from_request = request.GET.get("month")

        if month_from_request == "null":
            month = default_month
        else:
            month = month_from_request

        monthly_evaluation = get_object_or_404(
            Monthly_Evaluation, added__month=month, added__year=current_year, user=user
        )
        if monthly_evaluation:
            url = (
                "https://app.liliumpharma.com/monthly_evaluation/monthly_evaluations/"
                + str(monthly_evaluation.id)
                + "/"
            )
            response = {"url": url}
            return Response(response)


# --------SUPERVISOR EVALUATIONS TO DELEGATE-------
from .models import SupEvaluation


class AddMonthlyEvaluationSup(APIView):
    authentication_classes = (
        TokenAuthentication,
        SessionAuthentication,
    )
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        data = request.data.copy()
        own_perc = data.get("own_perc")
        print(request.GET.get("user"))  # Use request.GET, not request.Get
        month_url = int(request.GET.get("month", date.today().month))
        userURL = request.GET.get("user")  # Use request.GET, not request.Get

        user = User.objects.filter(username=userURL).first()
        print(user)
        SE = SupEvaluation.objects.filter(
            user__username=userURL, added__month=month_url
        ).first()
        if SE is not None:
            message = (
                "ATTENTION : Vous avez déjà un rapport mensuel pour le mois courant"
            )
            return Response({"message": message}, status=403)
        else:
            data.pop("csrfmiddlewaretoken")
            data["user"] = user
            if month_url in [1, 3, 5, 7, 8, 10, 12]:  # Mois avec 31 jours
                day_of_month = 31
            elif month_url in [4, 6, 9, 11]:  # Mois avec 30 jours
                day_of_month = 30
            else:
                is_leap_year = (
                    date.today().year % 4 == 0 and date.today().year % 100 != 0
                ) or date.today().year % 400 == 0
                day_of_month = 29 if is_leap_year else 28
            data["added"] = date(date.today().year, month_url, day_of_month)
            model_form = SupMonthlyEvaluationModelForm(data)
            if model_form.is_valid():
                monthly_evaluation = Monthly_Evaluation.objects.filter(
                    user=user, added__year=timezone.now().year, added__month=month_url
                ).first()

                monthly_evaluation.sup_evaluation = True
                monthly_evaluation.save()

                model_form.save()

            else:
                print(model_form.errors)

            return Response()


# --------SUPERVISOR EVALUATIONS TO DIRECTION-------
from .forms import SupMonthlyEvaluationToDirectionModelForm


class AddMonthlyEvaluationSupToDirection(APIView):
    authentication_classes = (
        TokenAuthentication,
        SessionAuthentication,
    )
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        data = request.data.copy()
        month_url = int(request.GET.get("month", date.today().month))
        requester = request.user
        print(requester)

        user = User.objects.filter(username=requester).first()
        SE = SupEvaluationToDirection.objects.filter(
            user__username=requester, added__month=month_url
        ).first()

        if SE is not None:
            message = (
                "ATTENTION : Vous avez déjà un rapport mensuel pour le mois courant"
            )
            return Response({"message": message}, status=403)
        else:
            data.pop("csrfmiddlewaretoken")
            data["user"] = user
            if month_url in [1, 3, 5, 7, 8, 10, 12]:  # Mois avec 31 jours
                day_of_month = 31
            elif month_url in [4, 6, 9, 11]:  # Mois avec 30 jours
                day_of_month = 30
            else:
                is_leap_year = (
                    date.today().year % 4 == 0 and date.today().year % 100 != 0
                ) or date.today().year % 400 == 0
                day_of_month = 29 if is_leap_year else 28

            data["added"] = date(date.today().year, month_url, day_of_month)
            data["user"] = requester

            model_form = SupMonthlyEvaluationToDirectionModelForm(data)

            if model_form.is_valid():
                model_form.save()

            else:
                print(model_form.errors)

            return Response()


from datetime import datetime, timedelta
from django.utils import timezone


class MonthlyEvaluationSupToDirectionView(APIView):
    authentication_classes = (
        TokenAuthentication,
        SessionAuthentication,
    )
    permission_classes = (IsAuthenticated,)

    def get(self, request):

        user = request.user
        response = []
        current_datetime = timezone.now()

        if (
            user.userprofile.speciality_rolee in ["admin", "CountryManager"]
            or user.is_superuser
        ):

            users = User.objects.filter(
                userprofile__speciality_rolee__in=["Superviseur_national"]
            )

            for u in users:

                username = str(u)
                id_username = User.objects.get(username=u)
                month = request.GET.get("month")

                if month == "null":
                    if current_datetime.month == 1:  # If the current month is January
                        month = 12
                    else:
                        month = current_datetime.month - 1

                EvaluationSupToDirection = SupEvaluationToDirection.objects.filter(
                    user=id_username, added__month=month
                )

                DirectionEvaluationToSu = DirectionEvaluationToSup.objects.filter(
                    user=id_username, added__month=month
                )
                DIE = DirectionEvaluationToSu.first()

                id = ""
                if DirectionEvaluationToSu.exists():
                    updatable = DIE.updatable
                    id = DIE.id

                else:
                    updatable = False

                if EvaluationSupToDirection.exists():
                    for eval in EvaluationSupToDirection:
                        response.append(
                            {
                                "id": eval.id,
                                "user": username,
                                "sup_evaluate_direction": eval.sup_evaluate_direction,
                                "direction_evaluate_sup": eval.direction_evaluate_sup,
                                "EvaluationSupToDirectionUpdatable": updatable,
                                "DirectionEvaluationToSupId": id,
                                "Date": eval.added.strftime("%Y-%m-%d"),
                                "exists": True,
                                "updatable": eval.updatable,
                            }
                        )
        else:

            id_username = User.objects.get(username=user)
            month = request.GET.get("month")
            username = str(user)

            if month == "null":
                if current_datetime.month == 1:  # If the current month is January
                    month = 12
                else:
                    month = current_datetime.month - 1

            EvaluationSupToDirection = SupEvaluationToDirection.objects.filter(
                user=id_username, added__month=month
            )

            DirectionEvaluationToSu = DirectionEvaluationToSup.objects.filter(
                user=id_username, added__month=month
            ).first()

            DirectionEvaluationToSu = DirectionEvaluationToSup.objects.filter(
                user=id_username, added__month=month
            )
            id = ""
            DIE = DirectionEvaluationToSu.first()
            print(str(DIE))
            if DirectionEvaluationToSu.exists():
                updatable = DIE.updatable
                id = DIE.id
            else:
                updatable = False

            if EvaluationSupToDirection.exists():
                for eval in EvaluationSupToDirection:
                    response.append(
                        {
                            "id": eval.id,
                            "user": username,
                            "sup_evaluate_direction": eval.sup_evaluate_direction,
                            "direction_evaluate_sup": eval.direction_evaluate_sup,
                            "EvaluationSupToDirectionUpdatable": updatable,
                            "DirectionEvaluationToSupId": id,
                            "Date": eval.added.strftime("%Y-%m-%d"),
                            "exists": True,
                            "updatable": eval.updatable,
                        }
                    )
            else:
                response.append({"exists": False})

        return Response(response)


class MonthlyEvaluationSupToDirection(APIView):
    # authentication_classes = (TokenAuthentication, SessionAuthentication,)
    # permission_classes = (IsAuthenticated,)
    def get(self, request, id):
        sup_eval_to_direction = SupEvaluationToDirection.objects.get(id=id)
        return render(
            request,
            "monthly_evaluations/pdf_supervisor_to_direction.html",
            {"SupEvaluationToDirection": sup_eval_to_direction},
        )


# --------DIRECTION EVALUATIONS TO SUP-------
from .forms import DirectionEvaluationToSupModelForm


class AddMonthlyEvaluationDirectionToSup(APIView):
    authentication_classes = (
        TokenAuthentication,
        SessionAuthentication,
    )
    permission_classes = (IsAuthenticated,)

    def post(self, request):

        data = request.data.copy()

        month_url = int(request.GET.get("month", date.today().month))
        requester = request.GET.get("user")

        DE = DirectionEvaluationToSup.objects.filter(
            user__username=requester, added__month=month_url
        ).first()
        print(DE)
        if DE is not None:
            message = (
                "ATTENTION : Vous avez déjà un rapport mensuel pour le mois courant"
            )
            return Response({"message": message}, status=403)
        else:
            user = User.objects.filter(username=requester).first()

            data.pop("csrfmiddlewaretoken")
            data["user"] = user
            if month_url in [1, 3, 5, 7, 8, 10, 12]:  # Mois avec 31 jours
                day_of_month = 31
            elif month_url in [4, 6, 9, 11]:  # Mois avec 30 jours
                day_of_month = 30
            else:
                is_leap_year = (
                    date.today().year % 4 == 0 and date.today().year % 100 != 0
                ) or date.today().year % 400 == 0
                day_of_month = 29 if is_leap_year else 28

            data["added"] = date(date.today().year, month_url, day_of_month)
            data["user"] = user
            model_form = DirectionEvaluationToSupModelForm(data)

            if model_form.is_valid():
                model_form.save()
                SE = SupEvaluationToDirection.objects.filter(
                    user__username=requester, added__month=month_url
                ).first()
                if SE is not None:
                    SE.direction_evaluate_sup = True
                    SE.save()
            else:
                print(model_form.errors)
            return Response()


class DirectionToSup(APIView):
    def get(self, request):
        # Get user and month from request query parameters
        user_param = request.GET.get("user")
        month_param = request.GET.get("month", date.today().month)

        # Filter DirectionEvaluationToSup instances based on user and month
        direction_evaluations = DirectionEvaluationToSup.objects.filter(
            user__id=user_param, added__month=month_param
        )

        response = []
        # Extract q1 values
        if direction_evaluations.exists():
            direction_evaluations = direction_evaluations.first()
            response.append({"q1": direction_evaluations.q1})

        # Return JSON response with q1 values
        return Response(response)


# --------DIRECTION EVALUATIONS TO DELEGATE-------

from .forms import DirectionToDelegateEvaluationModelForm


class AddMonthlyEvaluationDir(APIView):
    authentication_classes = (
        TokenAuthentication,
        SessionAuthentication,
    )
    permission_classes = (IsAuthenticated,)

    def post(self, request):

        data = request.data.copy()
        print(request.GET.get("user"))  # Use request.GET, not request.Get
        month_url = int(request.GET.get("month", date.today().month))
        userURL = request.GET.get("user")  # Use request.GET, not request.Get

        user = User.objects.filter(username=userURL).first()
        print(user)
        SE = DirectionToDelegateEvaluation.objects.filter(
            user__username=userURL, added__month=month_url
        ).first()
        if SE is not None:
            message = (
                "ATTENTION : Vous avez déjà un rapport mensuel pour le mois courant"
            )
            return Response({"message": message}, status=403)
        else:
            data.pop("csrfmiddlewaretoken")
            data["user"] = user
            if month_url in [1, 3, 5, 7, 8, 10, 12]:  # Mois avec 31 jours
                day_of_month = 31
            elif month_url in [4, 6, 9, 11]:  # Mois avec 30 jours
                day_of_month = 30
            else:
                is_leap_year = (
                    date.today().year % 4 == 0 and date.today().year % 100 != 0
                ) or date.today().year % 400 == 0
                day_of_month = 29 if is_leap_year else 28
            data["added"] = date(date.today().year, month_url, day_of_month)
            model_form = DirectionToDelegateEvaluationModelForm(data)
            if model_form.is_valid():
                monthly_evaluation = Monthly_Evaluation.objects.filter(
                    user=user, added__year=timezone.now().year, added__month=month_url
                ).first()

                monthly_evaluation.user_direction_evaluation = True
                monthly_evaluation.save()

                model_form.save()

            else:
                print(model_form.errors)

            return Response()

