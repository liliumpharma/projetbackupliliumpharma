from requests import Response
from .models import *

from io import StringIO
import xlsxwriter
from rest_framework.views import APIView
from rest_framework import authentication, permissions
from django.http import HttpResponse
from django.db.models import *
from django.contrib.auth.models import User
from accounts.models import UserProxy as User
from datetime import date
from produits.models import Produit
from liliumpharm.workbook import Workbook
from medecins.models import *
from rapports.models import Visite
from django.utils import timezone


class EtatStockClientExcel(APIView):
    def get(self, request, format=None):
        current_month = timezone.now().month
        current_year = timezone.now().year

        response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        workbook = xlsxwriter.Workbook(response, {'in_memory': True})
        worksheet = workbook.add_worksheet(f"Etat stocks clients")
        border_format = workbook.add_format({'border': 1})

        title = f'Etat de stock | {current_year}'
        title_format = workbook.add_format({'bold': True, 'font_size': 20, 'align': 'center', 'valign': 'vcenter'})
        worksheet.merge_range('A1:C1', title, title_format)

        row = 2
        worksheet.write(row, 0, 'Date')
        worksheet.write(row, 1, 'User')
        worksheet.write(row, 2, 'Medecin')
        worksheet.merge_range(row, 3, row, 4, 'Produits/Qtt')
        # worksheet.write(row, 4, 'Quantité')

        response['Content-Disposition'] = f'attachment; filename=Etat de stock client.xlsx'

        latest_visits = Visite.objects.filter(
            medecin=OuterRef('medecin'),
            rapport__added__month=current_month,
            rapport__added__year=current_year,
        ).order_by('-rapport__added').values('id')[:1]

        latest_visites_queryset = Visite.objects.filter(
            id=Subquery(latest_visits)
        )

        medecin_products = {}

        for latest_visite in latest_visites_queryset:
            medecin_name = latest_visite.medecin.nom
            observation = latest_visite.observation
            produits = latest_visite.produits.all()
            for produit in produits:
                qtt = produit.produitvisite_set.filter(visite=latest_visite).first().qtt
                if qtt > 0:
                    visite_date = latest_visite.rapport.added
                    formatted_date = visite_date.strftime('%Y-%m-%d') 
                    rapport_user = latest_visite.rapport.user.username
    
                    if medecin_name not in medecin_products:
                        medecin_products[medecin_name] = {'formatted_date': formatted_date, 'rapport_user': rapport_user, 'products': {}}
    
                    if produit.nom not in medecin_products[medecin_name]['products']:
                        medecin_products[medecin_name]['products'][produit.nom] = qtt
                    else:
                        medecin_products[medecin_name]['products'][produit.nom] += qtt

        for medecin_name, data in medecin_products.items():
            row += 1
            worksheet.write(row, 0, data['formatted_date'])
            worksheet.write(row, 1, data['rapport_user'])
            worksheet.write(row, 2, medecin_name)

            products_cell = ""
            for product_name, product_quantity in data['products'].items():
                products_cell += f" {product_name}:{product_quantity} Boite(s)   |   \n----------------\n"

            worksheet.set_row(row, None, None, {'valign': 'top'})

            worksheet.write(row, 3, products_cell.strip())  # Utilisez strip() pour supprimer le dernier saut de ligne
            row += 1
            
        workbook.close()
        return response

class AllExportExcel(APIView):

    def get(self, request, format=None):
        # Getting Today's Date
        today = date.today()


        response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    
        workbook = xlsxwriter.Workbook(response, {'in_memory': True})
    
        worksheet = workbook.add_worksheet(f"Liste Bon de commandes")
        border_format = workbook.add_format({'border': 1})

        # Set the title of the table
        title = 'Liste Bons de commandes | 2023'
        title_format = workbook.add_format({'bold': True, 'font_size': 20, 'align': 'center', 'valign': 'vcenter'})
        worksheet.write('A1', title, title_format)
        worksheet.merge_range('A1:C1', title, title_format)


        # Init Row Index
        row = 1

        indexx=10

        # Writing Headers
        worksheet.write(row, 0, 'ID')
        worksheet.write(row, 1, 'Date')
        worksheet.write(row, 2, 'User')
        worksheet.write(row, 3, 'Pharmacies')
        worksheet.write(row, 4, 'Grossistes')
        worksheet.write(row, 5, 'Super Grossistes')
        worksheet.write(row, 6, 'Status')
        worksheet.write(row, 7, 'From Office')
        worksheet.write(row, 8, 'FF')
        worksheet.write(row, 9, 'FM')
        worksheet.write(row, 10, 'IRON')
        worksheet.write(row, 11, 'YES CAL')
        worksheet.write(row, 12, 'YES VIT')
        worksheet.write(row, 13, 'ADVAGEN')
        worksheet.write(row, 14, 'DHEA 75mg')
        worksheet.write(row, 15, 'HAIRVOL')
        worksheet.write(row, 16, 'SUB12')
        worksheet.write(row, 17, 'MENOLIB')
        worksheet.write(row, 18, 'THYROLIB')
        worksheet.write(row, 19, 'HEPALIB')
        worksheet.write(row, 20, 'SOPK FREE')
        worksheet.write(row, 21, 'DIGEST PLUS')
        worksheet.write(row, 22, 'ANAFLAM')
        worksheet.write(row, 23, 'URICITRIL')
        worksheet.write(row, 24, 'URISOFT')
        worksheet.write(row, 25, 'BESTFER')


        # Define product columns and headers
        product_columns = {
            'FF': 8,
            'FM': 9,
            'IRON': 10,
            'YES CAL': 11,
            'YES VIT': 12,
            'ADVAGEN': 13,
            'DHEA 75mg': 14,
            'HAIRVOL': 15,
            'SUB12': 16,
            'MENOLIB': 17,
            'THYROLIB': 18,
            'HEPALIB': 19,
            'SOPK FREE': 20,
            'DIGEST PLUS': 21,
            'ANAFLAM': 22,
            'URICITRIL':23,
            'URISOFT':24,
            'BESTFER':25,
        }

        year = request.GET.get("added__year")
        month = request.GET.get("added__month")
        print(year)
        print(month)
        from_office = request.GET.get("from_company__exact")
        print(from_office)
        print(str(from_office))

        if (month):
            try:
                if (from_office == '1'):
                    print("ici 1")
                    orders = Order.objects.filter(added__year = year, added__month=month, from_company=True)
                else:
                    print("ici 2")

                    orders = Order.objects.filter(added__year = year, added__month=month)
                response['Content-Disposition'] = f'attachment; filename=Bon de commande - date extraction mois {month}-{year}.xlsx'
            except User.DoesNotExist:
                print("no user")
                return Response({"message": "order not found."}, status=400)
        else:
            orders = Order.objects.filter(added__year = date.today().year)
            print("le fichier va generer et telecharger")
            response['Content-Disposition'] = f'attachment; filename=Bon de commande - date extraction année {year}.xlsx'


        for order in sorted(orders, key=lambda x: x.added):
            # Incrementing Row
            row += 1

            date_value = order.added.date()
            formatted_date = date_value.strftime('%Y-%m-%d') 

            worksheet.write(row, 0, order.id)
            worksheet.write(row, 1, formatted_date)
            worksheet.write(row, 2, order.user.username)
            worksheet.write(row, 3, order.pharmacy.nom if order.pharmacy else "")
            worksheet.write(row, 4, order.gros.nom if order.gros else "")
            worksheet.write(row, 5, order.super_gros.name if order.super_gros else "")
            worksheet.write(row, 6, order.status)
            worksheet.write(row, 7, order.from_company)

            order_items = OrderItem.objects.filter(order=order)

            for product_name, col in product_columns.items():
                print(f"produittttttttt {product_name}")
                order_item = next((item for item in order_items if item.produit.nom == product_name), None)
                
                if order_item and order_item.qtt > 0:
                    print("ifffffff")
                    print(f"order item {order_item} et order item qtt {order_item.qtt}")
                    worksheet.write(row, col, order_item.qtt)
                else:
                    print("elseeee")
                    worksheet.write(row, col, "")



        print("le fichier excel va t'il exporter")
        workbook.close()
        return response

class AllExitOrdersExportExcel(APIView):

    def get(self, request, format=None):
        
        # Getting Today's Date
        today = date.today()


        response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response['Content-Disposition'] = f'attachment; filename=Bon de sortie - date extraction {today}.xlsx'
    
        workbook = xlsxwriter.Workbook(response, {'in_memory': True})
    
        worksheet = workbook.add_worksheet(f"Liste Bons de sortie")
        border_format = workbook.add_format({'border': 1})

        # Set the title of the table
        title = 'Liste Bons de sortie | 2023'
        title_format = workbook.add_format({'bold': True, 'font_size': 20, 'align': 'center', 'valign': 'vcenter'})
        worksheet.write('A1', title, title_format)
        worksheet.merge_range('A1:C1', title, title_format)


        # Init Row Index
        row = 1

        indexx=10

        # Writing Headers
        worksheet.write(row, 0, 'ID')
        worksheet.write(row, 1, 'Date')
        worksheet.write(row, 2, 'User')
        worksheet.write(row, 3, 'Status')
        worksheet.write(row, 4, 'Brochure')
        worksheet.write(row, 5, 'Depôt')
        worksheet.write(row, 6, 'Confirmed by')
        worksheet.write(row, 7, 'FF')
        worksheet.write(row, 8, 'FM')
        worksheet.write(row, 9, 'IRON')
        worksheet.write(row, 10, 'YES CAL')
        worksheet.write(row, 11, 'YES VIT')
        worksheet.write(row, 12, 'ADVAGEN')
        worksheet.write(row, 13, 'DHEA 75mg')
        worksheet.write(row, 14, 'HAIRVOL')
        worksheet.write(row, 15, 'SUB12')
        worksheet.write(row, 16, 'MENOLIB')
        worksheet.write(row, 17, 'THYROLIB')
        worksheet.write(row, 18, 'HEBALIB')
        worksheet.write(row, 19, 'SOPK FREE')
        worksheet.write(row, 20, 'DIGEST PLUS')
        worksheet.write(row,21, 'ANAFLAM')


        # Define product columns and headers
        product_columns = {
            'FF': 7,
            'FM':8,
            'IRON': 9,
            'YES CAL': 10,
            'YES VIT': 11,
            'ADVAGEN': 12,
            'DHEA 75mg': 13,
            'HAIRVOL': 14,
            'SUB12': 15,
            'MENOLIB': 16,
            'THYROLIB': 17,
            'HEBALIB': 18,
            'SOPK FREE': 19,
            'DIGEST PLUS': 20,
            'ANAFLAM': 21,
        }


        year = request.GET.get("added__year")
        month = request.GET.get("added__month")
        ye = str(year)
        if (month):
            try:
                orders = ExitOrder.objects.filter(added__year = year, added__month=month)
                response['Content-Disposition'] = f'attachment; filename=Bon de sortie - date extraction mois {month}-{ye}.xlsx'
            except:
                return Response({"message": "order not found."}, status=400)
        else:
            orders = ExitOrder.objects.filter(added__year = date.today().year)
            response['Content-Disposition'] = f'attachment; filename=Bon de sortie - date extraction année {ye}.xlsx'

        # Looping through ExitOrders
        for order in orders:
            # Incrementing Row
            row += 1

            date_value = order.added.date()
            formatted_date = date_value.strftime('%Y-%m-%d') 

            worksheet.write(row, 0, order.id)
            worksheet.write(row, 1, formatted_date)
            worksheet.write(row, 2, order.user.username)
            worksheet.write(row, 3, order.status)
            if order.brochure:
                worksheet.write(row, 4, "Oui")
            else:
                worksheet.write(row, 4, "Non")
            worksheet.write(row, 5, order.depot)
            worksheet.write(row, 6, order.user_confirmed.username if order.user_confirmed else "-")

            order_items = ExitOrderItem.objects.filter(order=order)

            for product_name, col in product_columns.items():
                order_item = next((item for item in order_items if item.produit.nom == product_name), None)

                if order_item and order_item.qtt > 0:
                    worksheet.write(row, col, order_item.qtt)
                else:
                    worksheet.write(row, col, "-")

        
        workbook.close()
        return response