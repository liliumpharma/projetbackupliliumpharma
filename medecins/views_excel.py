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
