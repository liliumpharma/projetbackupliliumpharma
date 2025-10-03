from .models import *
from regions.models import Wilaya

from io import StringIO
import xlsxwriter
from rest_framework.views import APIView
from rest_framework import authentication, permissions
from django.http import HttpResponse
from django.db.models import Q, Sum
from accounts.models import UserProxy as User
from produits.models import Produit
from django.contrib.auth.models import User


class TemplateExportExcel(APIView):

    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        # Creating a Response
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = f"attachment; filename=Template_Ventes.xlsx"

        # Create a workbook.
        workbook = xlsxwriter.Workbook(response, {"in_memory": True})

        # Worksheet 1
        worksheet = workbook.add_worksheet("Ventes")
        worksheet.write(0, 0, "Super Grossite")
        worksheet.write(0, 1, "Client")
        worksheet.write(0, 2, "Produit")
        worksheet.write(0, 3, "Quantité")

        # Worksheet 2
        worksheet = workbook.add_worksheet("Stock")
        worksheet.write(0, 0, "Super Grossite")
        worksheet.write(0, 1, "Nom du Produit")
        worksheet.write(0, 2, "Quantité")

        # Worksheet 3
        worksheet = workbook.add_worksheet("Super Grossites")
        worksheet.write(0, 0, "Nom")

        clients = Client.objects.filter(supergro=True)
        row = 0
        for client in clients:
            worksheet.write(row, 0, client.name)
            row += 1

        # Worksheet 4
        worksheet = workbook.add_worksheet("Grossites")
        worksheet.write(0, 0, "Nom")

        clients = Client.objects.filter(supergro=False)
        row = 0
        for client in clients:
            worksheet.write(row, 0, client.name)
            row += 1

        # Worksheet 5
        worksheet = workbook.add_worksheet("Wilayas")
        row = 0
        worksheet.write(row, 0, "Description")

        wilayas = Wilaya.objects.filter(pays__nom="algerie")
        row = 1
        for wilaya in wilayas:
            worksheet.write(row, 0, wilaya.nom.capitalize())
            row += 1

        # Worksheet 6
        worksheet = workbook.add_worksheet("Produits")
        row = 0
        worksheet.write(row, 0, "Nom")

        products = Produit.objects.all()
        for product in products:
            worksheet.write(row, 0, product.nom)
            row += 1

        workbook.close()

        return response


# class SalesExportExcel(APIView):

#     authentication_classes = [authentication.SessionAuthentication]
#     permission_classes = [permissions.IsAuthenticated]

#     def get(self, request, format=None):

#         # Getting GET Params
#         year = request.GET.get("year")

#         # Creating a Response
#         response = HttpResponse(
#             content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#         )
#         response["Content-Disposition"] = f"attachment; filename=Ventes_du_{year}.xlsx"

#         # Create a workbook.
#         workbook = xlsxwriter.Workbook(response, {"in_memory": True})

#         # Worksheet 1
#         worksheet = workbook.add_worksheet("Ventes")
#         worksheet.write(0, 0, "Super Grossite")
#         worksheet.write(0, 1, "Wilaya")
#         worksheet.write(0, 2, "Month")
#         worksheet.write(0, 3, "Type")

#         col = 3
#         produits = Produit.objects.all()

#         for product in produits:
#             worksheet.write(0, col, product.nom)
#             col += 1

#         worksheet.write(0, col, "Totaux")

#         # Init Row Index
#         row = 1
#         order_sources = OrderSource.objects.filter(date__year=year)
#         for order_source in order_sources:

#             # Writing Sales
#             worksheet.write(row, 0, order_source.source.name)
#             worksheet.write(row, 1, order_source.source.wilaya.nom)
#             worksheet.write(
#                 row, 2, f"{order_source.date.month}-{order_source.date.year}"
#             )
#             worksheet.write(row, 3, "Vente")

#             col = 3
#             total_quantities = 0
#             for product in produits:
#                 total = OrderProduct.objects.filter(
#                     order__source=order_source, produit=product
#                 ).aggregate(total=Sum("qtt"))["total"]
#                 worksheet.write(row, col, total if total else 0)
#                 col += 1
#                 total_quantities += total if total else 0

#             worksheet.write(row, col, total_quantities)

#             # Writing Remaining Stock
#             row += 1

#             worksheet.write(row, 0, order_source.source.name)
#             worksheet.write(row, 1, order_source.source.wilaya.nom)
#             worksheet.write(
#                 row, 2, f"{order_source.date.month}-{order_source.date.year}"
#             )
#             worksheet.write(row, 3, "Stock Restant")

#             col = 3
#             total_quantities = 0
#             for product in produits:
#                 total = OrderSourceProduct.objects.filter(
#                     produit=product, source=order_source
#                 )

#                 quantity = total.first().qtt if total.exists() else -1

#                 worksheet.write(row, col, quantity if quantity != -1 else "-")
#                 col += 1

#                 total_quantities += quantity if quantity != -1 else 0

#             worksheet.write(row, col, total_quantities)

#             row += 1

#         workbook.close()

#         return response


from django.utils import timezone
from django.db.models import Sum
from datetime import datetime, timedelta


class SalesExportExcel(APIView):
    authentication_classes = [authentication.SessionAuthentication]
    #permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        # Get current date and calculate last month
        today = timezone.now()
        first_day_last_month = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
        last_day_last_month = today.replace(day=1) - timedelta(days=1)

        # Creating a Response
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = (
            f"attachment; filename=Ventes_du_{first_day_last_month.month}_{first_day_last_month.year}.xlsx"
        )

        # Create a workbook.
        workbook = xlsxwriter.Workbook(response, {"in_memory": True})

        # Worksheet 1
        worksheet = workbook.add_worksheet("Ventes")
        worksheet.write(0, 0, "Super Grossite")
        worksheet.write(0, 1, "Wilaya")
        worksheet.write(0, 2, "Month")
        worksheet.write(0, 3, "Type")

        col = 3
        produits = Produit.objects.all()

        for product in produits:
            worksheet.write(0, col, product.nom)
            col += 1

        worksheet.write(0, col, "Totaux")

        # Init Row Index
        row = 1
        order_sources = OrderSource.objects.filter(
            date__range=[first_day_last_month, last_day_last_month]
        )
        for order_source in order_sources:
            # Writing Sales
            worksheet.write(row, 0, order_source.source.name)
            worksheet.write(row, 1, order_source.source.wilaya.nom)
            worksheet.write(
                row, 2, f"{order_source.date.month}-{order_source.date.year}"
            )
            worksheet.write(row, 3, "Vente")

            col = 3
            total_quantities = 0
            for product in produits:
                total = OrderProduct.objects.filter(
                    order__source=order_source, produit=product
                ).aggregate(total=Sum("qtt"))["total"]
                worksheet.write(row, col, total if total else 0)
                col += 1
                total_quantities += total if total else 0

            worksheet.write(row, col, total_quantities)

            # Writing Remaining Stock
            row += 1

            worksheet.write(row, 0, order_source.source.name)
            worksheet.write(row, 1, order_source.source.wilaya.nom)
            worksheet.write(
                row, 2, f"{order_source.date.month}-{order_source.date.year}"
            )
            worksheet.write(row, 3, "Stock Restant")

            col = 3
            total_quantities = 0
            for product in produits:
                total = OrderSourceProduct.objects.filter(
                    produit=product, source=order_source
                )

                quantity = total.first().qtt if total.exists() else -1

                worksheet.write(row, col, quantity if quantity != -1 else "-")
                col += 1

                total_quantities += quantity if quantity != -1 else 0

            worksheet.write(row, col, total_quantities)

            row += 1

        workbook.close()

        return response


class UserTargetMonthExcel(APIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):

        # Getting GET Params
        year = request.GET.get("date__year")

        # Creating a Response
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = (
            f"attachment; filename=Objectifs_du_{year}.xlsx"
        )

        # Create a workbook.
        workbook = xlsxwriter.Workbook(response, {"in_memory": True})

        # Worksheet 1
        worksheet = workbook.add_worksheet("Ventes")
        worksheet.write(0, 0, "Delegué")
        worksheet.write(0, 1, "Family")
        worksheet.write(0, 2, "Mois")

        col = 3
        products = Produit.objects.all()

        for product in products:
            worksheet.write(0, col, product.nom)
            col += 1

        user_target_months = UserTargetMonth.objects.filter(date__year=year).order_by(
            "date__month"
        )

        # Init
        row = 1

        for user_target_month in user_target_months:

            worksheet.write(row, 0, user_target_month.user.username)
            worksheet.write(row, 1, user_target_month.user.userprofile.family)
            worksheet.write(
                row, 2, f"{user_target_month.date.month}-{user_target_month.date.year}"
            )

            products_targets = user_target_month.usertargetmonthproduct_set.all()

            for index, product in enumerate(list(products)):
                product_target = products_targets.filter(product=product)

                if product_target.exists():
                    worksheet.write(row, index + 3, product_target.first().quantity)
                else:
                    worksheet.write(row, index + 3, 0)

            row += 1

        workbook.close()

        return response


class OrdersExportExcel(APIView):

    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):

        # Getting GET Params
        year = request.GET.get("year")

        # Creating a Response
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = f"attachment; filename=Ventes_du_{year}.xlsx"

        # Create a workbook.
        workbook = xlsxwriter.Workbook(response, {"in_memory": True})

        # Worksheet 1
        worksheet = workbook.add_worksheet("Ventes")
        worksheet.write(0, 0, "Wilaya")
        worksheet.write(0, 1, "Month")

        col = 2
        produits = Produit.objects.all()

        for product in produits:
            worksheet.write(0, col, product.nom)
            col += 1

        # Init Row Index
        row = 1
        orders = (
            Order.objects.filter(source__date__year=year)
            .values("client__wilaya__nom", "source__date__year", "source__date__month")
            .order_by("source__date__month", "source__date__year")
            .distinct()
        )

        for order in orders:

            # Writing Sales
            worksheet.write(row, 0, order.get("client__wilaya__nom"))
            worksheet.write(
                row,
                1,
                f'{order.get("source__date__month")}-{order.get("source__date__year")}',
            )

            col = 2
            total_quantities = 0
            for product in produits:
                total = OrderProduct.objects.filter(
                    order__client__wilaya__nom=order.get("client__wilaya__nom"),
                    order__source__date__month=order.get("source__date__month"),
                    order__source__date__year=order.get("source__date__year"),
                    produit=product,
                ).aggregate(total=Sum("qtt"))["total"]
                worksheet.write(row, col, total if total else 0)
                col += 1
                total_quantities += total if total else 0

            worksheet.write(row, col, total_quantities)

            row += 1

        workbook.close()

        return response
