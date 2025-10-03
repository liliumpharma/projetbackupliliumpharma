from .models import *
from django.db.models import Q

import xlsxwriter
from rest_framework.views import APIView
from rest_framework import authentication, permissions
from django.http import HttpResponse
from django.db.models import *
from django.contrib.auth.models import User
from accounts.models import UserProxy as User
from datetime import date
from liliumpharm.workbook import Workbook
from medecins.models import *
from django.utils import timezone
from rest_framework.authentication import TokenAuthentication,SessionAuthentication,BasicAuthentication
from rest_framework.permissions import IsAuthenticated



class AllExportExcel(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        # Getting Today's Date
        today = date.today()


        response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    
        workbook = xlsxwriter.Workbook(response, {'in_memory': True})
    
        worksheet = workbook.add_worksheet(f"Liste Du Personnel")
        border_format = workbook.add_format({'border': 1})

        # Set the title of the table
        title = 'Liste Des Utilisateurs | 2025'
        title_format = workbook.add_format({'bold': True, 'font_size': 20, 'align': 'center', 'valign': 'vcenter'})
        worksheet.write('A1', title, title_format)
        worksheet.merge_range('A1:C1', title, title_format)


        # Init Row Index
        row = 1

        indexx=10

        # Writing Headers
        worksheet.write(row, 0, 'ID')
        worksheet.write(row, 1, 'Nom')
        worksheet.write(row, 2, 'Prénom')
        worksheet.write(row, 3, 'Date de naissance')
        worksheet.write(row, 4, 'Sexe')
        worksheet.write(row, 5, 'E-mail')
        worksheet.write(row, 6, 'Adresse')
        worksheet.write(row, 7, 'Commune')
        worksheet.write(row, 8, 'Téléphone')
        worksheet.write(row, 9, 'Famille')
        worksheet.write(row, 10, 'Compte Bancaire')
        worksheet.write(row, 11, 'Banque')
        worksheet.write(row, 12, 'Poste')
        worksheet.write(row, 13, 'Date d''entrée')
        worksheet.write(row, 14, 'CNAS')
        worksheet.write(row, 15, 'Fonction')
        worksheet.write(row, 16, 'Nom d''utilisateur')
        worksheet.write(row, 17, 'Situation familiale')
        worksheet.write(row, 18, 'Secteur')
        worksheet.write(row, 19, 'CODE Section')
        worksheet.write(row, 20, 'CODE Contrat')
        worksheet.write(row, 21, 'LIB. CONTRAT')

        response['Content-Disposition'] = f'attachment; filename=Liste Du Personel.xlsx'

        users = UserProfile.objects.filter(is_human=True).exclude(Q(adresse__icontains="tunis"))



        # Looping through Orders
        sorted_users = sorted(users, key=lambda x: x.user.id)

        for user in sorted_users:
            # Incrementing Row
            row += 1

            date_of_birth_str = user.date_of_birth.strftime('%d-%m-%Y') if user.date_of_birth else ""
            date_entry_str = user.entry_date.strftime('%d-%m-%Y') if user.entry_date else ""

            worksheet.write(row, 0, user.user.id)
            worksheet.write(row, 1, user.user.first_name)
            worksheet.write(row, 2, user.user.last_name)
            worksheet.write(row, 3, date_of_birth_str)
            worksheet.write(row, 4, user.gender)
            worksheet.write(row, 5, user.user.email)
            worksheet.write(row, 6, user.adresse)
            worksheet.write(row, 7, user.commune.nom if user.commune else "")
            worksheet.write(row, 8, user.telephone)
            worksheet.write(row, 9, user.family)
            worksheet.write(row, 10, user.bank_account)
            worksheet.write(row, 11, user.bank_name)
            worksheet.write(row, 12, user.job_name)
            worksheet.write(row, 13, date_entry_str)
            worksheet.write(row, 14, user.CNAS)
            worksheet.write(row, 15, user.speciality_rolee)
            worksheet.write(row, 16, user.user.username)
            worksheet.write(row, 17, user.situation)
            worksheet.write(row, 19, user.code_section)
            worksheet.write(row, 20, user.code_contrat)

            if user.speciality_rolee == "Medico_commercial" :
                worksheet.write(row, 15, 'Délégué Médico-Commercial')

            if user.speciality_rolee == "Commercial" :
                worksheet.write(row, 15, 'Délégué Commercial')

            if user.speciality_rolee == "Superviseur_regional" :
                worksheet.write(row, 15, 'Superviseur Médical Régionale')

            if user.speciality_rolee == "Superviseur_national" :
                worksheet.write(row, 15, 'Superviseur Médical Nationale')

            if user.speciality_rolee == "Superviseur_national" :
                worksheet.write(row, 15, 'Superviseur Médical Nationale')

            if user.speciality_rolee == "Finance_et_comptabilité" :
                worksheet.write(row, 15, 'Responsable Finances et Comptabilité')

            if user.speciality_rolee == "chargé_de_communication" :
                worksheet.write(row, 15, 'Chargé de Communication')

            if user.speciality_rolee == "gestionnaire_de_stock" :
                worksheet.write(row, 15, 'Gestionnaire de stock')
            
            if user.code_contrat == "CDI" :
                worksheet.write(row, 21, 'Contrat à Durer Indéterminée')
            if user.code_contrat == "CDD" :
                worksheet.write(row, 21, 'Contrat à Durer Déterminée')

            sectors_list = user.sectors.all()
            sectors_names = ', '.join([sector.nom for sector in sectors_list])
            worksheet.write(row, 18, sectors_names)

        workbook.close()
        return response