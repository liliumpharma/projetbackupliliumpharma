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

class AllExportExcel(APIView):

    def get(self, request, format=None):
        # Getting Today's Date
        current_month = timezone.now().month
        current_year = timezone.now().year


        response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    
        workbook = xlsxwriter.Workbook(response, {'in_memory': True})
    
        worksheet = workbook.add_worksheet(f"Liste Bon de Versement {current_month}-{current_year}")
        border_format = workbook.add_format({'border': 1})


        title = f'Liste Encaissement | {current_month}-{current_year}'
        title_format = workbook.add_format({'bold': True, 'font_size': 20, 'align': 'center', 'valign': 'vcenter'})
        worksheet.merge_range('A1:C1', title, title_format)

        row = 2

        # Writing Headers
        worksheet.write(row, 0, 'ID')
        worksheet.write(row, 1, 'Délégué')
        worksheet.write(row, 2, 'N° de bon')
        worksheet.write(row, 3, 'Date d''ajout')
        worksheet.write(row, 4, 'Date document')
        worksheet.write(row, 5, 'Client')
        worksheet.write(row, 6, 'Montant')
        worksheet.write(row, 7, 'Mode')
        worksheet.write(row, 8, 'Attachement')

        versements = Versement.objects.all()

        response['Content-Disposition'] = f'attachment; filename=Bon de versement | {current_month}-{current_year}.xlsx'


        for versement in sorted(versements, key=lambda x: x.added):
            # Incrementing Row
            row += 1

            paybook_user = versement.paybook

            # Access the associated User object through the PaybookUser
            user = paybook_user.user

            # Get the username from the User object
            username = f"{user.first_name} {user.last_name}"

            date_value = versement.added
            formatted_date = date_value.strftime('%Y-%m-%d') 

            date_value_doc = versement.date_document
            formatted_date_doc = date_value_doc.strftime('%Y-%m-%d') 

            worksheet.write(row, 0, versement.id)
            worksheet.write(row, 1, username)
            worksheet.write(row, 2, versement.num_recu)
            worksheet.write(row, 3, formatted_date)
            worksheet.write(row, 4, formatted_date_doc)
            worksheet.write(row, 5, versement.recu)
            somme_value = float(versement.somme) if versement.somme else 0.0
            worksheet.write_number(row, 6, somme_value)
            worksheet.write(row, 7, versement.way_of_payment)
            worksheet.write(row, 8, versement.link)
        
        workbook.close()
        return response
