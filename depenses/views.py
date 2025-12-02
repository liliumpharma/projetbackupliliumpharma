from django.shortcuts import render
from .models import *
from .serializers import *
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.db.models import Q, Count
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from .models import *

from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import authentication, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.authentication import (
    SessionAuthentication,
    TokenAuthentication,
    BasicAuthentication,
)

from rest_framework.authtoken.models import Token
from django.shortcuts import render, redirect
from django.core.mail import EmailMessage

from django.contrib.auth.decorators import login_required

from datetime import date

from .forms import *


from .models import Spend


class get_spends(APIView):
    authentication_classes = (
        TokenAuthentication,
        SessionAuthentication,
    )
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        if user.userprofile.rolee in ["CountryManager"] or user.is_superuser:
            spends = Spend.objects.all()
        else:
            spends = Spend.objects.filter(user=request.user)
        response = []
        if spends.exists():
            for spend in spends:
                attachement = spend.attachement.url if spend.attachement else "null"
                response.append(
                    {
                        "id": spend.id,
                        "user": spend.user.username,
                        "added": spend.added.strftime("%Y-%m-%d"),
                        "reason": spend.reason,
                        "spender": spend.spender,
                        "url": spend.url,
                        "price": spend.price,
                        "price_in_letters": spend.price_in_letters,
                        "nature_depense": spend.nature_depense,
                        "status": spend.status,
                        "administration_comment": spend.administration_comment,
                    }
                )
            response.append({"total": spends.count()})
        return Response(response)


class ConfirmSpend(APIView):
    authentication_classes = (
        TokenAuthentication,
        SessionAuthentication,
    )
    permission_classes = (IsAuthenticated,)

    def get(self, request, spend_id):
        try:
            user = request.user
            if user.userprofile.rolee in ["CountryManager"] or user.is_superuser:
                spend = Spend.objects.get(id=spend_id)
                if spend.status.lower() == "initial":
                    spend.status = (
                        StatusTypesChoices.CONFIRME
                    )  # Mettez à jour le statut en utilisant la valeur de choix
                    spend.approved_user = user
                    spend.approved_date = timezone.now()
                    spend.save()
                    return Response(
                        {"message": "Statut de la dépense mis à jour avec succès."},
                        status=status.HTTP_200_OK,
                    )
                else:
                    return Response(
                        {
                            "message": "Impossible de mettre à jour le statut de la dépense."
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            else:
                print("False")

        except Spend.DoesNotExist:
            return Response(
                {"message": "La dépense n'existe pas."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Si aucune condition n'est satisfaite, renvoyez une réponse 404 par défaut
        return Response(
            {"message": "Une erreur inattendue s'est produite."},
            status=status.HTTP_404_NOT_FOUND,
        )


class AddSpend(APIView):

    # authentication_classes = (TokenAuthentication, SessionAuthentication,)
    # permission_classes = (IsAuthenticated,)

    def post(self, request):
        print(request.data)
        data = request.data.copy()
        data.pop("csrfmiddlewaretoken")
        data["user"] = request.user
        data["added"] = date.today()
        model_form = SpendModelForm(data)
        if model_form.is_valid():
            model_form.save()
        else:
            print(model_form.errors)
        return Response()


# VIEW FOR PRINT BUTTON ADMINISTRATION
class SpendPDF(APIView):
    authentication_classes = (
        TokenAuthentication,
        SessionAuthentication,
    )
    permission_classes = (IsAuthenticated,)

    def get(self, request, id):
        spend = Spend.objects.get(id=id)
        return render(request, "depenses/pdf.html", {"spend": spend})


# VIEW FOR PRINT BUTTON INTERFACE
class print_spend(APIView):
    authentication_classes = (
        TokenAuthentication,
        SessionAuthentication,
    )
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        id = request.GET.get("id")
        spend = get_object_or_404(Spend, id=id)
        if spend:
            url = (
                "https://app.liliumpharma.com/depenses/printSpend/"
                + str(spend.id)
                + "/"
            )
            response = {"url": url}
            return Response(response)


class AddSpendComment(APIView):

    # authentication_classes = (TokenAuthentication, SessionAuthentication,)
    # permission_classes = (IsAuthenticated,)

    def post(self, request):
        data = request.data.copy()
        data.pop("csrfmiddlewaretoken")
        data["user"] = request.user
        data["added"] = date.today()
        model_form = SpendCommentModelForm(data)
        if model_form.is_valid():
            model_form.save()
        else:
            print(model_form.errors)
        return Response()


class GetSpendComment(APIView):
    def get(self, request):
        id = request.GET.get("id")
        print("----|||----- called here baby ")
        SpendComments = SpendComment.objects.filter(spend=id)
        response = []
        if SpendComments.exists():
            for spend in SpendComments:
                response.append(
                    {
                        "comment": spend.comment,
                        "date": spend.added,
                        "user": spend.user.username,
                    }
                )
        return Response(response)


class getting_users_under(APIView):
    def get(self, request):
        user = request.user
        print("Getting users from " + str(user))
        response = []
        if (
            user.userprofile.speciality_rolee in ["admin", "CountryManager","Office"]
            or user.is_superuser
        ):
            users = users = User.objects.filter(userprofile__speciality_rolee__in=["Medico_commercial", "Commercial", "Superviseur_regional", "Superviseur_national"])
            for u in users:
                response.append({"user": f"{u.first_name} {u.last_name}"})
        else:
            if user.userprofile.speciality_rolee == "Superviseur_national":
                users_under_supervisor = user.userprofile.usersunder.all()
                for u in users_under_supervisor:
                    response.append(
                        {response.append({"user": f"{u.first_name} {u.last_name}"})}
                    )
            else:
                response.append({"user": f"{user.first_name} {user.last_name}"})
        return Response(response)


@login_required
def depenses_front(request):
    return render(request, "depenses/index.html")


#####################################################################################################################


# FOR MOBILE APP
@login_required(login_url="login")
def depense_mobile(request):
    return render(request, "depenses/mobile.html")


###############################################################################################################################

# EXPORT EXCEL

from io import StringIO
import xlsxwriter
from liliumpharm.workbook import Workbook


class AllExportExcel(APIView):

    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):

        # Getting Today's Date
        today = date.today()

        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = (
            f"attachment; filename=Liste des dépense - date {today}.xlsx"
        )

        workbook = xlsxwriter.Workbook(response, {"in_memory": True})
        worksheet = workbook.add_worksheet(f"Liste des dépenses")

        # Getting Today's Date
        today = date.today()

        # Init Workbook

        # Set the title of the table
        title = "Liste des dépenses | 2023"
        title_format = workbook.add_format(
            {"bold": True, "font_size": 20, "align": "center", "valign": "vcenter"}
        )
        worksheet.write("A1", title, title_format)
        worksheet.merge_range("A1:C1", title, title_format)

        # Init Row Index
        row = 1

        indexx = 10

        # Writing Headers
        worksheet.write(row, 0, "ID")
        worksheet.write(row, 1, "User")
        worksheet.write(row, 2, "N° logiciel")
        worksheet.write(row, 3, "Date d" "ajout")
        worksheet.write(row, 4, "Type de dépense")
        worksheet.write(row, 5, "Wilaya de départ")
        worksheet.write(row, 6, "Wilaya d" "arrivé")
        worksheet.write(row, 7, "Distance")
        worksheet.write(row, 8, "Autre raison")
        worksheet.write(row, 9, "Beneficiaire")
        worksheet.write(row, 10, "Tarif dépensé")
        worksheet.write(row, 11, "Tarif en lettres")
        worksheet.write(row, 12, "Méthode de paiement")
        worksheet.write(row, 13, "Nature de la dépense")

        user_id = request.GET.get("user")

        if user_id:
            try:
                user = User.objects.get(id=user_id)
                spends = Spend.objects.filter(user=user)
            except User.DoesNotExist:
                return Response({"message": "User not found."}, status=400)
        else:
            spends = Spend.objects.all()
        for spend in spends:

            date_value = spend.added
            formatted_date = date_value.strftime("%Y-%m-%d")

            # Incrementing Row
            row += 1

            # Writing Rows
            worksheet.write(row, 0, spend.id)
            worksheet.write(row, 1, spend.user.username)
            worksheet.write(row, 2, spend.log_number)
            worksheet.write(row, 3, formatted_date)
            worksheet.write(row, 4, spend.spend_type)
            worksheet.write(row, 5, spend.departure if spend.departure else "-")
            worksheet.write(row, 6, spend.arrival if spend.arrival else "-")
            worksheet.write(row, 7, spend.distance)
            worksheet.write(
                row, 8, spend.other_spend_reason if spend.other_spend_reason else "-"
            )
            worksheet.write(row, 9, spend.spender)
            worksheet.write(row, 10, spend.price)
            worksheet.write(row, 11, spend.price_in_letters)
            worksheet.write(row, 12, spend.way_of_payment)
            worksheet.write(row, 13, spend.nature_depense)

        workbook.close()
        return response
