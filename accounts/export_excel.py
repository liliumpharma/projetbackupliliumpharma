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

from django.shortcuts import render
from datetime import datetime

class ExportDepSemiExcel(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        def build_data(category_name, is_dep=False):
            details = UserSectorDetail.objects.filter(category=category_name).select_related("user_profile", "user_profile__user").prefetch_related("wilayas", "communes", "communes__wilaya").order_by("user_profile__region", "user_profile__user__username")
            
            from collections import defaultdict
            grouped = defaultdict(list)
            for d in details:
                grouped[d.user_profile].append(d)

            data_list = []
            for profile, user_details in grouped.items():
                username = profile.user.username if profile.user else ""
                region = profile.get_region_display() if profile.region else ""
                speciality = profile.speciality_rolee
                
                objectif = ""
                if profile.rolee == "Superviseur":
                    has_medico = False
                    for u in profile.usersunder.all():
                        if hasattr(u, "userprofile") and u.userprofile.speciality_rolee == "Medico_commercial":
                            has_medico = True
                            break
                    if has_medico:
                        objectif = "12 Medical + 4 Commercial"
                    else:
                        objectif = "14 Commercial"
                elif speciality == "Medico_commercial":
                    objectif = "12 Medical + 4 Commercial"
                elif speciality == "Commercial":
                    objectif = "14 Commercial"

                sectors_list = []
                for d in user_details:
                    sector_wilayas = d.wilayas.all()
                    sector_communes = d.communes.all()

                    if sector_communes:
                        # Show wilaya / commune for each commune
                        sector_name = ", ".join(
                            f"{c.wilaya.nom} / {c.nom}" for c in sector_communes
                        )
                    else:
                        sector_name = ", ".join(w.nom for w in sector_wilayas) or ""

                    month_freq = d.month_frequency if d.month_frequency in ("ODD", "EVEN") else ""

                    portfolio_qs = list(Medecin.objects.filter(users=profile.user, wilaya__in=sector_wilayas).values('specialite').annotate(count=Count('id')))
                    commercial_count = sum(item['count'] for item in portfolio_qs if item['specialite'] in ["Pharmacie", "Grossiste", "SuperGros"])
                    medical_count = sum(item['count'] for item in portfolio_qs if item['specialite'] not in ["Pharmacie", "Grossiste", "SuperGros"])
                    
                    portfolio_detail = ", ".join(f"{item['count']} {item['specialite']}" for item in portfolio_qs)

                    times = d.times or 0
                    base_val = float(d.value or 0)

                    sector_info = {
                        "name": sector_name,
                        "month_freq": month_freq,
                        "portfolio_medical": medical_count,
                        "portfolio_commercial": commercial_count,
                        "portfolio_detail": portfolio_detail,
                        "times": times,
                        "prime": base_val,
                        "note": d.note or "",
                    }

                    if is_dep:
                        days = d.days or 0
                        nights = d.nights or 0
                        hotel_cost = float(d.hotel_cost or 0)
                        total_dep = base_val + hotel_cost
                        total_mensuel = total_dep * float(times)
                        
                        sector_info.update({
                            "days": days,
                            "nights": nights,
                            "hotel_cost": hotel_cost,
                            "total_dep": total_dep,
                            "total_mensuel": total_mensuel
                        })
                    else:
                        total_dep = base_val
                        total_mensuel = total_dep * float(times)
                        
                        sector_info.update({
                            "total_dep": total_dep,
                            "total_mensuel": total_mensuel
                        })
                    
                    sectors_list.append(sector_info)

                data_list.append({
                    "rowspan": len(user_details),
                    "username": username,
                    "region": region,
                    "speciality": speciality,
                    "family": profile.family,
                    "objectif": objectif,
                    "sectors": sectors_list
                })
            return data_list

        def group_by_region(data_list):
            from itertools import groupby as _groupby
            regions = []
            grand_total = 0.0
            user_counter = 0
            for region_name, users_iter in _groupby(data_list, key=lambda x: x["region"]):
                users = list(users_iter)
                region_rowspan = sum(u["rowspan"] for u in users)
                region_total = sum(
                    sector["total_mensuel"] for u in users for sector in u["sectors"]
                )
                grand_total += region_total
                for u in users:
                    user_counter += 1
                    u["user_num"] = user_counter
                regions.append({
                    "name": region_name,
                    "total": region_total,
                    "rowspan": region_rowspan,
                    "users": users,
                })
            return {"regions": regions, "grand_total": grand_total}

        # ── 1. ADD THIS NEW FUNCTION HERE ──
        def build_high_cost_data():
            current_month = datetime.now().month
            is_even_month = (current_month % 2 == 0)

            high_cost_users = []
            
            # Fetch users and prefetch to avoid N+1 query performance issues
            users = UserProfile.objects.prefetch_related(
                'user', 
                'sector_details', 
                'sector_details__wilayas', 
                'sector_details__communes'
            ).all()

            for profile in users:
                semi_sectors = []
                dep_sectors = []
                total_semi = 0.0
                total_dep = 0.0

                for sector in profile.sector_details.all():
                    # Format wilayas and communes
                    wilayas_list = [w.nom for w in sector.wilayas.all()]
                    wilaya_str = ", ".join(wilayas_list) if wilayas_list else "-"

                    communes_list = [c.nom for c in sector.communes.all()]
                    commune_str = ", ".join(communes_list) if communes_list else "-"

                    # Safely fetch numeric values
                    times = float(sector.times or 0)
                    prime = float(sector.value or 0)
                    hotel_cost = float(sector.hotel_cost or 0)
                    days = sector.days or '-'
                    nights = sector.nights or '-'

                    if sector.category == "DEP":
                        freq = sector.month_frequency
                        sector_total = (prime + hotel_cost) * times
                        
                        # Zero out if frequency doesn't match the current month
                        if (freq == "EVEN" and not is_even_month) or (freq == "ODD" and is_even_month):
                            sector_total = 0.0

                        dep_sectors.append({
                            'wilaya': wilaya_str,
                            'commune': commune_str,
                            'times': int(times),
                            'days': days,
                            'nights': nights,
                            'hotel_cost': hotel_cost,
                            'prime': prime,
                            'total_mensuel': sector_total,
                            'freq': freq
                        })
                        total_dep += sector_total

                    elif sector.category == "SEMI":
                        sector_total = prime * times
                        semi_sectors.append({
                            'wilaya': wilaya_str,
                            'commune': commune_str,
                            'times': int(times),
                            'days': '-',
                            'nights': '-',
                            'hotel_cost': '-',
                            'prime': prime,
                            'total_mensuel': sector_total,
                        })
                        total_semi += sector_total

                grand_total = total_semi + total_dep

                # ── 2. FILTER: ONLY KEEP IF > 50,000 DA ──
                if grand_total > 50000.0:
                    # Add empty rows to keep the HTML rowspan formatting intact if a user has one type but not the other
                    if not semi_sectors:
                        semi_sectors.append({'is_empty': True})
                    if not dep_sectors:
                        dep_sectors.append({'is_empty': True})
                        
                    semi_count = len(semi_sectors)
                    dep_count = len(dep_sectors)
                    total_rows = semi_count + dep_count

                    high_cost_users.append({
                        'username': profile.user.username if profile.user else "",
                        'region': profile.get_region_display() if profile.region else "",
                        'semi_sectors': semi_sectors,
                        'dep_sectors': dep_sectors,
                        'total_semi': total_semi,
                        'total_dep': total_dep,
                        'grand_total': grand_total,
                        'total_rows': total_rows,
                        'semi_count': semi_count,
                        'dep_count': dep_count
                    })

            return high_cost_users

        # ── 3. CALL YOUR FUNCTIONS ──
        semi_data = group_by_region(build_data("SEMI", is_dep=False))
        dep_data = group_by_region(build_data("DEP", is_dep=True))
        high_cost_data = build_high_cost_data() # Call the new function

        # ── 4. UPDATE THE CONTEXT DICTIONARY ──
        context = {
            "semi_data": semi_data,
            "dep_data": dep_data,
            "high_cost_users": high_cost_data, # Pass it to the template here
            "title": "Visualisation DEP/SEMI"
        }
        return render(request, "admin/accounts/userprofile/view_dep_semi.html", context)