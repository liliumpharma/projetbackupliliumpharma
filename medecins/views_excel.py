from .models import *

from io import StringIO
import xlsxwriter
from rest_framework.views import APIView
from rest_framework import authentication, permissions
from django.http import HttpResponse
from django.db.models import Q
from accounts.models import UserProxy as User
from datetime import date
from produits.models import Produit
import xlsxwriter
from medecins.models import MEDICAL, COMMERCIAL
from urllib.parse import unquote


# class AllExportExcel(APIView):

#     authentication_classes = [authentication.SessionAuthentication]
#     permission_classes = [permissions.IsAuthenticated]

#     def get(self, request, format=None):

#         # Getting Today's Date
#         today = date.today()

#         # Init Workbook
#         response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
#         workbook = xlsxwriter.Workbook(response, {'in_memory': True})
#         worksheet = workbook.add_worksheet(f"Porte feuille client {today}")
#         border_format = workbook.add_format({'border': 1})


#         title = f'Liste Medecins | {today}'
#         title_format = workbook.add_format({'bold': True, 'font_size': 20, 'align': 'center', 'valign': 'vcenter'})
#         worksheet.merge_range('A1:C1', title, title_format)

#         # Init Row Index
#         row = 1

#         indexx=10

#         # Writing Headers
#         worksheet.write(row, 0, 'ID')
#         worksheet.write(row, 1, 'Nom')
#         worksheet.write(row, 2, 'Specialité')
#         worksheet.write(row, 3, 'Has location')
#         worksheet.write(row, 4, 'Classification')
#         worksheet.write(row, 5, 'Telephone')
#         worksheet.write(row, 6, 'Email')
#         worksheet.write(row, 7, 'Wilaya')
#         worksheet.write(row, 8, 'Commune')
#         worksheet.write(row, 9, 'Adresse')
#         worksheet.write(row, 10, 'Délégués')

#         # Observation Width
#         max_width = 0

#         user = request.GET.get("user")
#         if user is None:
#             print("USER IS NONE")
#             liste_medecins = Medecin.objects.filter(commune__wilaya__pays__id=1)
#         else:
#             liste_medecins = Medecin.objects.filter(users__id__in=[user])
#             print("MEDS "+str(liste_medecins))


#         for medecin in liste_medecins:

#             last_visite=medecin.last_visite()
#             # Determine if the Medecin has coordinates
#             has_coordinates = bool(medecin.lat and medecin.lon)
#             # Incrementing Row
#             row += 1

#             # Writing Rows
#             worksheet.write(row, 0, medecin.id)
#             worksheet.write(row, 1, medecin.nom)
#             worksheet.write(row, 2, medecin.specialite)
#             worksheet.write(row, 3, str(has_coordinates))
#             worksheet.write(row, 4, medecin.classification)
#             worksheet.write(row, 5, medecin.telephone)
#             worksheet.write(row, 6, medecin.email)
#             worksheet.write(row, 7, medecin.commune.wilaya.nom)
#             worksheet.write(row, 8, medecin.commune.nom)
#             worksheet.write(row, 9, medecin.adresse)
#             worksheet.write(row, 10, ' | '.join([f'{user.first_name} {user.last_name}' for user in medecin.users.all()]))

#             indexx=10


#         #  Setting Observation Column Wide
#         # worksheet.set_column('I:I', max_width)

#         workbook.close()

#         return response

# class AllExportExcel(APIView):

#     authentication_classes = [authentication.SessionAuthentication]
#     permission_classes = [permissions.IsAuthenticated]

#     def get(self, request, format=None):
#         # Getting Today's Date
#         today = date.today()

#         # Init Workbook
#         response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
#         workbook = xlsxwriter.Workbook(response, {'in_memory': True})
#         worksheet = workbook.add_worksheet(f"Porte feuille client {today}")
#         border_format = workbook.add_format({'border': 1})

#         title = f'Liste Medecins | {today}'
#         title_format = workbook.add_format({'bold': True, 'font_size': 20, 'align': 'center', 'valign': 'vcenter'})
#         worksheet.merge_range('A1:C1', title, title_format)

#         # Init Row Index
#         row = 1

#         indexx = 10

#         # Writing Headers
#         worksheet.write(row, 0, 'ID')
#         worksheet.write(row, 1, 'Nom')
#         worksheet.write(row, 2, 'Specialité')
#         worksheet.write(row, 3, 'Has location')
#         worksheet.write(row, 4, 'Classification')
#         worksheet.write(row, 5, 'Telephone')
#         worksheet.write(row, 6, 'Email')
#         worksheet.write(row, 7, 'Wilaya')
#         worksheet.write(row, 8, 'Commune')
#         worksheet.write(row, 9, 'Adresse')
#         worksheet.write(row, 10, 'Délégués')
#         worksheet.write(row, 11, 'Uploaded from excel')

#         # Applying Filters
#         queryset = Medecin.objects.all()

#         user = request.GET.get("users__id__exact")
#         specialite = request.GET.get("specialite")
#         flag = request.GET.get("flag__exact")
#         updatable = request.GET.get("updatable__exact")
#         commune = request.GET.get("commune__id__exact")
#         uploaded_from_excel = request.GET.get("uploaded_from_excel__exact")
#         visited = request.GET.get("visited")
#         uid = request.GET.get("uid")

#         # Applying filters based on GET parameters
#         for key, value in request.GET.items():
#             if key == 'visited':
#                 if value == 'yes':
#                     queryset = queryset.filter(visite__isnull=False).distinct()
#                 else :
#                     queryset = queryset.filter(visite__isnull=True)
#             elif flag!="null" and key == 'flag':
#                 queryset = queryset.filter(flag=value)
#             elif updatable!="null" and key == 'updatable':
#                 queryset = queryset.filter(updatable=value)
#             elif  key == 'wilaya':
#                 queryset = queryset.filter(wilaya=value)
#             elif key == 'commune':
#                 queryset = queryset.filter(commune=value)
#             elif key == 'blocked':
#                 queryset = queryset.filter(blocked=value)
#             elif key == 'classification':
#                 queryset = queryset.filter(classification=value)
#             elif uploaded_from_excel!="null" and key == 'uploaded_from_excel':
#                 uploaded_from_excel = request.GET.get("uploaded_from_excel__exact")
#                 filter_uploaded_from_excel = uploaded_from_excel == '1'
#                 print(f"Applying filter: uploaded_from_excel={uploaded_from_excel}")
#                 queryset = queryset.filter(uploaded_from_excel=filter_uploaded_from_excel)
#                 print(f"Filtered queryset for uploaded_from_excel={uploaded_from_excel}: {queryset.query}")
#             elif key == 'user':
#                 queryset = queryset.filter(users__id__in=user)

#         print(str(queryset))

#         # Writing Rows for each Medecin in the queryset
#         # for medecin in queryset:
#         #     has_coordinates = bool(medecin.lat and medecin.lon)
#         #     row += 1

#         #     worksheet.write(row, 0, medecin.id)
#         #     worksheet.write(row, 1, medecin.nom)
#         #     worksheet.write(row, 2, medecin.specialite)
#         #     worksheet.write(row, 3, str(has_coordinates))
#         #     worksheet.write(row, 4, medecin.classification)
#         #     worksheet.write(row, 5, medecin.telephone)
#         #     worksheet.write(row, 6, medecin.email)
#         #     worksheet.write(row, 7, medecin.commune.wilaya.nom)
#         #     worksheet.write(row, 8, medecin.commune.nom)
#         #     worksheet.write(row, 9, medecin.adresse)
#         #     worksheet.write(row, 10, ' | '.join([f'{user.first_name} {user.last_name}' for user in medecin.users.all()]))
#         #     worksheet.write(row, 11, medecin.uploaded_from_excel)

#         #     indexx = 10

#         # workbook.close()

#         return response


# class AllExportExcel(APIView):

#     authentication_classes = [authentication.SessionAuthentication]
#     permission_classes = [permissions.IsAuthenticated]

#     def get(self, request, format=None):
#         # Getting Today's Date
#         today = date.today()

#         # Init Workbook
#         response = HttpResponse(
#             content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#         )
#         workbook = xlsxwriter.Workbook(response, {"in_memory": True})
#         worksheet = workbook.add_worksheet(f"Porte feuille client {today}")
#         border_format = workbook.add_format({"border": 1})

#         title = f"Liste Medecins | {today}"
#         title_format = workbook.add_format(
#             {"bold": True, "font_size": 20, "align": "center", "valign": "vcenter"}
#         )
#         worksheet.merge_range("A1:C1", title, title_format)

#         # Init Row Index
#         row = 1

#         # Writing Headers
#         worksheet.write(row, 1, "Délégués")
#         worksheet.write(row, 2, "Wilaya")
#         worksheet.write(row, 3, "Commune")
#         worksheet.write(row, 4, "Nom")
#         worksheet.write(row, 5, "Adresse")
#         worksheet.write(row, 6, "Telephone")
#         worksheet.write(row, 7, "Email")
#         worksheet.write(row, 8, "ID")
#         worksheet.write(row, 9, "Specialité")
#         worksheet.write(row, 10, "Has location")
#         worksheet.write(row, 11, "Classification")
#         worksheet.write(row, 12, "Uploaded from excel")

#         # Getting parameters from GET request
#         print(str(request))
#         user = request.GET.get("user")
#         print("user id " + str(user))
#         specialite = request.GET.get("specialite")
#         flag = request.GET.get("flag")
#         updatable = request.GET.get("updatable")
#         commune = request.GET.get("commune")
#         wilaya = request.GET.get("wilaya")
#         uploaded_from_excel = request.GET.get("uploaded_from_excel")
#         visited = request.GET.get("visited")
#         classification = request.GET.get("classification")
#         blocked = request.GET.get("blocked")
#         uid = request.GET.get("uid")

#         queryset = Medecin.objects.all()

#         # Applying filters based on GET parameters
#         if visited is not None:
#             print("called 1 ")
#             if visited.lower() == "true":
#                 print("visited is true")
#                 queryset = queryset.filter(visite__isnull=False)
#             elif visited.lower() == "false":
#                 print("visited is true")
#                 queryset = queryset.filter(visite__isnull=True)

#         if uploaded_from_excel is not None:
#             print("called 2 ")
#             print("uploaded_from_excel is " + str(uploaded_from_excel))
#             queryset = queryset.filter(
#                 uploaded_from_excel=(uploaded_from_excel.lower() == "true")
#             )

#         if flag is not None:
#             print("called 3 ")
#             queryset = queryset.filter(flag=(flag.lower() == "true"))

#         if updatable is not None:
#             print("called 4 ")
#             queryset = queryset.filter(updatable=(updatable.lower() == "true"))

#         if commune is not None:
#             queryset = queryset.filter(commune__id=commune)

#         if wilaya is not None:
#             queryset = queryset.filter(commune__wilaya__id=wilaya)

#         if user is not None:
#             print("user filter applied for user " + str(user))
#             queryset = queryset.filter(users__id=user)

#         print("specialite " + str(specialite))
#         if specialite is not None:
#             # specialite = unquote(specialite)
#             # if specialite == 'Pharmacie,Grossiste,SuperGros':
#             #     print("---> true getted here")
#             #     queryset = queryset.filter(specialite__in=['Pharmacie', 'Grossiste', 'SuperGros'])
#             # elif specialite == 'Orthopedie,Nutritionist,Dermatologue,Généraliste,Diabetologue,Neurologue,Psychologue,Gynécologue,Rumathologue,Allergologue,Phtisio,Cardiologue,Urologue,Hematologue,Interniste,Gastrologue,Endocrinologue,Dentiste,ORL':
#             #     queryset = queryset.exclude(specialite__in=['Pharmacie', 'Grossiste', 'SuperGros'])
#             # else:
#             #     print("---> getted here")
#             queryset = queryset.filter(specialite=specialite)

#         if classification is not None:
#             queryset = queryset.filter(classification=classification)

#         # if blocked is not None:
#         #     queryset = queryset.filter(blocked=(blocked.lower() == 'true'))

#         # if uid is not None:
#         #     queryset = queryset.filter(uid=uid)

#         # Writing Rows for each Medecin in the queryset
#         queryset = queryset.distinct()
#         print("-------------------" + str(queryset))
#         for medecin in queryset:
#             print("medeecin -->" + str(medecin.nom))
#             has_coordinates = bool(medecin.lat and medecin.lon)
#             row += 1

#             worksheet.write(
#                 row,
#                 1,
#                 " | ".join(
#                     [
#                         f"{user.first_name} {user.last_name}"
#                         for user in medecin.users.all()
#                     ]
#                 ),
#             )
#             worksheet.write(row, 2, medecin.commune.wilaya.nom)
#             worksheet.write(row, 3, medecin.commune.nom)
#             worksheet.write(row, 4, medecin.nom)
#             worksheet.write(row, 5, medecin.adresse)
#             worksheet.write(row, 6, medecin.telephone)
#             worksheet.write(row, 7, medecin.email)
#             worksheet.write(row, 8, medecin.id)
#             worksheet.write(row, 9, medecin.specialite)
#             worksheet.write(row, 10, str(has_coordinates))
#             worksheet.write(row, 11, medecin.classification)
#             worksheet.write(row, 12, str(medecin.uploaded_from_excel))

#         workbook.close()

#         return response


from datetime import date
from rest_framework.views import APIView
from rest_framework import authentication, permissions
from django.http import HttpResponse
import xlsxwriter


class AllExportExcel(APIView):
    #authentication_classes = [authentication.SessionAuthentication]
    #permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        # Initialisation du Workbook
        today = date.today()
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        workbook = xlsxwriter.Workbook(response, {"in_memory": True})
        worksheet = workbook.add_worksheet(f"Porte feuille client {today}")

        # Formattage
        title_format = workbook.add_format(
            {"bold": True, "font_size": 20, "align": "center", "valign": "vcenter"}
        )
        worksheet.merge_range("A1:C1", f"Liste Medecins | {today}", title_format)

        # Écriture des en-têtes
        headers = [
            "Délégués",
            "Wilaya",
            "Commune",
            "Nom",
            "Adresse",
            "Telephone",
            "Email",
            "ID",
            "Specialité",
            "Has location",
            "Classification",
            "Uploaded from excel",
        ]
        for col_num, header in enumerate(headers, start=1):
            worksheet.write(1, col_num, header)

        # Récupération des paramètres GET
        filters = {
            "visited": request.GET.get("visited"),
            "uploaded_from_excel": request.GET.get("uploaded_from_excel"),
            "flag": request.GET.get("flag"),
            "updatable": request.GET.get("updatable"),
            "commune": request.GET.get("commune"),
            "wilaya": request.GET.get("wilaya"),
            "user": request.GET.get("user"),
            "specialite": request.GET.get("specialite"),
            "classification": request.GET.get("classification"),
        }
        print(request.GET.get("user"))
        queryset = (
            Medecin.objects.exclude(users__username__in="Medecin_Recycle_Bin")
            .exclude(users__username__in="Pharmacie_Recycle_Bin")
            .distinct()
        )
        print('test fatah 0000')
        print(queryset)
        # Application des filtres
        if filters["visited"] is not None:
            queryset = queryset.filter(
                visite__isnull=(filters["visited"].lower() == "false")
            )

        if filters["uploaded_from_excel"] is not None:
            queryset = queryset.filter(
                uploaded_from_excel=(filters["uploaded_from_excel"].lower() == "true")
            )

        if filters["flag"] is not None:
            queryset = queryset.filter(flag=(filters["flag"].lower() == "true"))

        if filters["updatable"] is not None:
            queryset = queryset.filter(
                updatable=(filters["updatable"].lower() == "true")
            )

        if filters["commune"] is not None:
            queryset = queryset.filter(commune__id=filters["commune"])

        if filters["wilaya"] is not None:
            queryset = queryset.filter(commune__wilaya__id=filters["wilaya"])

        if filters["user"] is not None:
            queryset = queryset.filter(users__id=filters["user"])
        print('test fatah 0001')
        print(queryset)
        
        if filters["specialite"] is not None:
            queryset = queryset.filter(specialite__in=filters["specialite"].split(","))
        print('test fatah 0002')
        print(queryset)
        
        if filters["classification"] is not None:
            queryset = queryset.filter(classification=filters["classification"])

        # Écriture des lignes pour chaque Médecin
        print("testttt fatah")
        print(queryset)
        row = 1
        for medecin in queryset:
            has_coordinates = bool(medecin.lat and medecin.lon)
            row += 1

            worksheet.write(
                row,
                1,
                " | ".join(
                    f"{user.first_name} {user.last_name}"
                    for user in medecin.users.all()
                ),
            )
            worksheet.write(row, 2, medecin.commune.wilaya.nom)
            worksheet.write(row, 3, medecin.commune.nom)
            worksheet.write(row, 4, medecin.nom)
            worksheet.write(row, 5, medecin.adresse)
            worksheet.write(row, 6, medecin.telephone)
            worksheet.write(row, 7, medecin.email)
            worksheet.write(row, 8, medecin.id)
            worksheet.write(row, 9, medecin.specialite)
            worksheet.write(row, 10, str(has_coordinates))
            worksheet.write(row, 11, medecin.classification)
            worksheet.write(row, 12, str(medecin.uploaded_from_excel))

        workbook.close()

        print(str(response))
        print("finished proceess babe")

        return response


class ListMedecinPerUserExcel(APIView):

    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):

        today = date.today()

        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        workbook = xlsxwriter.Workbook(response, {"in_memory": True})

        worksheet = workbook.add_worksheet(f"Porte feuille client {today}")
        border_format = workbook.add_format({"border": 1})

        title = f"Liste Medecins | {today}"
        title_format = workbook.add_format(
            {"bold": True, "font_size": 20, "align": "center", "valign": "vcenter"}
        )
        worksheet.merge_range("A1:C1", title, title_format)

        row = 2
        user = request.user.id

        userr = User.objects.get(id=user)

        # Extract first name and last name
        first_name = userr.first_name
        last_name = userr.last_name

        # Writing Headers
        worksheet.write(row, 0, "ID")
        worksheet.write(row, 1, "Nom")
        worksheet.write(row, 2, "Specialité")
        worksheet.write(row, 3, "Classification")
        worksheet.write(row, 4, "Telephone")
        worksheet.write(row, 5, "Email")
        worksheet.write(row, 6, "Wilaya")
        worksheet.write(row, 7, "Commune")
        worksheet.write(row, 8, "Adresse")
        worksheet.write(row, 9, "Délégués")

        med = Medecin.objects.filter(commune__wilaya__pays__id=1, users=user)
        print(med)

        for medecin in med:
            row += 1
            worksheet.write(row, 0, medecin.id)
            worksheet.write(row, 1, medecin.nom)
            worksheet.write(row, 2, medecin.specialite)
            worksheet.write(row, 3, medecin.classification)
            worksheet.write(row, 4, medecin.telephone)
            worksheet.write(row, 5, medecin.email)
            worksheet.write(row, 6, medecin.commune.wilaya.nom)
            worksheet.write(row, 7, medecin.commune.nom)
            worksheet.write(row, 8, medecin.adresse)
            # worksheet.write(row, 9, ' | '.join([f'{user.first_name} {user.last_name}' for user in medecin.users.all()]))
            worksheet.write(row, 9, f"{first_name} {last_name}")

        workbook.close()

        return response



from rest_framework.views import APIView
from rest_framework import authentication, permissions
from django.http import HttpResponse
from datetime import date
import xlsxwriter

from .models import Medecin

from django.db.models import Count, OuterRef, Subquery
from django.utils import timezone
from rapports.models import Visite
from medecins.get_medecins import get_medecinsss
from django.db.models import Count, OuterRef, Subquery
from django.utils import timezone
from rapports.models import Visite
from medecins.get_medecins import get_medecinsss
from medecins.models import COMMERCIAL  

from rest_framework.views import APIView
from rest_framework import authentication, permissions
from django.http import HttpResponse
from datetime import date
import xlsxwriter

from django.db.models import Count
from django.db.models.functions import TruncMonth
from rapports.models import Visite
from medecins.get_medecins import get_medecinsss

from rest_framework.views import APIView
from rest_framework import authentication, permissions
from django.http import HttpResponse
from datetime import date
import xlsxwriter

from django.db.models import Count
from django.db.models.functions import TruncMonth
from rapports.models import Visite
from medecins.get_medecins import get_medecinsss


class HomeMedecinExportExcel(APIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        from datetime import date as date_cls

        today = date.today()

        # SAME queryset as the list page (same filters + same role scoping)
        base_qs = get_medecinsss(request)

        # Keep compatibility with your existing "cat" behavior (if used in UI)
        cat = (request.GET.get("cat") or "").strip()
        if cat == "0":
            base_qs = base_qs.filter(visite__isnull=True)
        elif cat == "1":
            base_qs = base_qs.filter(visite__isnull=False)

        base_qs = (
            base_qs.distinct()
            .select_related("commune__wilaya")
            .prefetch_related("users")
        )

        medecin_ids = list(base_qs.values_list("id", flat=True))
        total_results = len(medecin_ids)

        # -------- Build visit filters (align with list filters when present) --------
        visite_filters = {}

        mindate = (request.GET.get("mindate") or "").strip()
        maxdate = (request.GET.get("maxdate") or "").strip()
        produit = (request.GET.get("produit") or "").strip()

        if mindate:
            visite_filters["rapport__added__gte"] = mindate
        if maxdate:
            visite_filters["rapport__added__lte"] = maxdate
        if produit:
            visite_filters["produits__id"] = produit

        commercial_raw = (request.GET.get("commercial") or "").strip()
        commercial_username = commercial_raw.split(" - ")[0].strip() if commercial_raw else ""
        if commercial_username and commercial_username.lower() not in ["tous"]:
            visite_filters["rapport__user__username__icontains"] = commercial_username

        # Rolling 12 months (start = first day of month 11 months ago)
        def first_day_month_n_months_ago(ref_date: date_cls, n_months: int) -> date_cls:
            y, m = ref_date.year, ref_date.month
            m = m - n_months
            while m <= 0:
                m += 12
                y -= 1
            return date_cls(y, m, 1)

        start_12m = first_day_month_n_months_ago(today, 11)

        month_lbl = {
            1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
            7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec",
        }

        # -------- Aggregate visits (no N+1) --------
        monthly_by_med = {}  # medecin_id -> list[(month_date, label, count)]
        ytd_by_med = {}      # medecin_id -> count

        if medecin_ids:
            monthly_qs = (
                Visite.objects
                .filter(medecin_id__in=medecin_ids, **visite_filters)
                .filter(rapport__added__gte=start_12m)
                .annotate(m=TruncMonth("rapport__added"))
                .values("medecin_id", "m")
                .annotate(c=Count("id"))
                .order_by("m")
            )

            for row in monthly_qs:
                mval = row.get("m")
                if mval is None:
                    key_date = date_cls.min
                    label = "Sans date"
                else:
                    key_date = mval.date() if hasattr(mval, "date") else mval
                    mm = getattr(mval, "month", None)
                    label = month_lbl.get(mm, str(mm) if mm else "Mois")
                monthly_by_med.setdefault(row["medecin_id"], []).append(
                    (key_date, label, int(row["c"] or 0))
                )

            ytd_qs = (
                Visite.objects
                .filter(medecin_id__in=medecin_ids, **visite_filters)
                .filter(rapport__added__year=today.year)
                .values("medecin_id")
                .annotate(c=Count("id"))
            )
            ytd_by_med = {r["medecin_id"]: int(r["c"] or 0) for r in ytd_qs}

        def fmt_months(items):
            if not items:
                return ""
            items = sorted(items, key=lambda t: t[0])
            return ", ".join([f"{lbl}: {cnt}" for _, lbl, cnt in items])

        # -------- Filters block at top (only active filters) --------
        def _is_default_for_key(key: str, v: str) -> bool:
            """
            Generic default detection:
              - empty is default
              - 'Tous'/'tous' are default
              - '0' is often default, BUT for some keys (like 'visites') it's a valid value.
            """
            v = (v or "").strip()
            if v in ["", "Tous", "tous", "all", "ALL"]:
                return True
            if v == "0" and key != "visites":
                return True
            return False

        def _map_visites_value(raw: str) -> str:
            """
            Convert visits filter values:
              0 -> Non visité
              1 -> Visité
              2 -> Visite multiple
              3 -> Visite duo
            """
            raw = (raw or "").strip()
            mapping = {
                "0": "Non visité",
                "1": "Visité",
                "2": "Visite multiple",
                "3": "Visite duo",
            }
            return mapping.get(raw, raw)

        applied_filters_kv = []  # list of tuples (label, value)

        for key, label in [
            ("pays", "Pays"),
            ("wilaya", "Wilaya"),
            ("commune", "Commune"),
            ("medecin", "Médecin"),
            ("commercial", "Commercial"),
            ("specialite", "Spécialité"),
            ("classification", "Classification"),
            ("visites", "Visites"),
            ("produit", "Produit"),
            ("priority", "Priorité"),
            ("shared", "Partagé"),
            ("stock", "Stock"),
            ("note", "Note"),
            ("deal", "Deal"),
            ("cat", "Catégorie"),
        ]:
            val = (request.GET.get(key) or "").strip()
            if not _is_default_for_key(key, val):
                if key == "commercial":
                    val = commercial_raw
                if key == "visites":
                    val = _map_visites_value(val)
                applied_filters_kv.append((label, val))

        if mindate or maxdate:
            applied_filters_kv.append(("Période", f"{mindate or '…'} → {maxdate or '…'}"))

        # -------- Excel generation --------
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = f'attachment; filename="medecins_{today}.xlsx"'

        workbook = xlsxwriter.Workbook(response, {"in_memory": True})
        ws = workbook.add_worksheet("Medecins")

        # Formats (GREEN THEME)
        title_fmt = workbook.add_format({
            "bold": True, "font_size": 18, "align": "center", "valign": "vcenter",
            "bg_color": "#1B5E20", "font_color": "white"
        })
        sub_title_fmt = workbook.add_format({
            "bold": True, "font_size": 11, "align": "left", "valign": "vcenter",
            "bg_color": "#E8F5E9", "border": 1
        })
        meta_fmt = workbook.add_format({
            "italic": True, "font_size": 10, "align": "left", "valign": "vcenter"
        })
        header_fallback_fmt = workbook.add_format({
            "bold": True, "align": "center", "valign": "vcenter",
            "border": 1, "bg_color": "#2E7D32", "font_color": "white"
        })
        wrap_top_border = workbook.add_format({"text_wrap": True, "valign": "top", "border": 1})

        # Filters formats
        filter_name_bold_fmt = workbook.add_format({"bold": True, "border": 1, "bg_color": "#F1F8E9"})
        filter_val_fmt = workbook.add_format({"border": 1, "text_wrap": True})

        headers = ["délégué", "nom", "wilaya", "commune", "specialite", "telephone", "adresse", "visites"]
        last_col = len(headers) - 1

        ws.merge_range(0, 0, 0, last_col, f"Export Médecins — {today:%Y-%m-%d}", title_fmt)
        ws.write(1, 0, f"Exporté par: {getattr(request.user, 'username', '—')} | Résultats: {total_results}", meta_fmt)
        ws.merge_range(2, 0, 2, last_col, "Filtres appliqués", sub_title_fmt)

        filters_start_row = 3
        if not applied_filters_kv:
            ws.merge_range(filters_start_row, 0, filters_start_row, last_col, "Aucun filtre appliqué (Tous).", filter_val_fmt)
            filters_end_row = filters_start_row
        else:
            r = filters_start_row
            for (fname, fval) in applied_filters_kv:
                ws.write(r, 0, fname, filter_name_bold_fmt)
                ws.merge_range(r, 1, r, last_col, fval, filter_val_fmt)
                r += 1
            filters_end_row = r - 1

        table_start_row = filters_end_row + 2
        data_start_row = table_start_row + 1

        row = data_start_row
        for m in base_qs:
            delegues = " - ".join(
                (f"{u.first_name} {u.last_name}".strip() or u.username)
                for u in m.users.all()
            )

            nom_val = f"{m.id} {getattr(m, 'nom', '')}".strip()

            wilaya = ""
            commune = ""
            try:
                commune = m.commune.nom if getattr(m, "commune", None) else ""
                wilaya = (
                    m.commune.wilaya.nom
                    if (getattr(m, "commune", None) and getattr(m.commune, "wilaya", None))
                    else ""
                )
            except Exception:
                pass

            spec = (getattr(m, "specialite", "") or "").strip()
            cls = (getattr(m, "classification", "") or "").strip()
            spec_val = f"{spec} {cls}".strip()

            tel = getattr(m, "telephone", "") or "/"
            adr = getattr(m, "adresse", "") or "-"

            months_str = fmt_months(monthly_by_med.get(m.id, []))
            ytd = int(ytd_by_med.get(m.id, 0) or 0)
            visites_val = (months_str + ("\n" if months_str else "")) + f"{ytd} cette année"

            ws.write(row, 0, delegues, wrap_top_border)
            ws.write(row, 1, nom_val, wrap_top_border)
            ws.write(row, 2, wilaya, wrap_top_border)
            ws.write(row, 3, commune, wrap_top_border)
            ws.write(row, 4, spec_val, wrap_top_border)
            ws.write(row, 5, tel, wrap_top_border)
            ws.write(row, 6, adr, wrap_top_border)
            ws.write(row, 7, visites_val, wrap_top_border)

            row += 1

        last_data_row = row - 1

        if last_data_row >= data_start_row:
            ws.add_table(
                table_start_row, 0, last_data_row, last_col,
                {
                    "style": "Table Style Medium 21",
                    "columns": [{"header": h} for h in headers],
                    "autofilter": True,
                    "banded_rows": True,
                }
            )
        else:
            for c, h in enumerate(headers):
                ws.write(table_start_row, c, h, header_fallback_fmt)

        ws.freeze_panes(data_start_row, 0)

        ws.set_column(0, 0, 42)
        ws.set_column(1, 1, 40)
        ws.set_column(2, 2, 20)
        ws.set_column(3, 3, 22)
        ws.set_column(4, 4, 22)
        ws.set_column(5, 5, 18)
        ws.set_column(6, 6, 40)
        ws.set_column(7, 7, 42)

        ws.set_row(0, 28)
        ws.set_zoom(110)

        workbook.close()
        return response
