from .models import *

from io import StringIO
import xlsxwriter
from rest_framework.views import APIView
from rest_framework import authentication, permissions
from django.http import HttpResponse
from django.db.models import Q
from accounts.models import UserProxy as User

# class ExportExcel(APIView):

#     authentication_classes = [authentication.SessionAuthentication]
#     permission_classes = [permissions.IsAuthenticated]

#     def get(self, request, format=None):
#         # if not request.user.is_superuser: return HttpResponse("You are not allowed to download this file",status=403)

#         starting_date = request.GET.get('starting_date')
#         ending_date = request.GET.get('ending_date')

#         leaves_date_query = Q(start_date__range=[starting_date, ending_date]) | Q(end_date__range=[starting_date, ending_date])
#         absences_date_query = Q(date__range=[starting_date, ending_date])
        
#         # Querying
#         leaves = Leave.objects.filter(leaves_date_query)
#         absences = Absence.objects.filter(absences_date_query)

#         # Creating a Response
#         response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
#         response['Content-Disposition'] = f"attachment; filename=Congés_&_Absences_{starting_date}-{ending_date}.xlsx"
        
#         # Create a workbook.
#         workbook = xlsxwriter.Workbook(response, {'in_memory': True})
#         worksheet = workbook.add_worksheet()

#         # Preparing Formats
#         date_format = workbook.add_format({'num_format': 'mmmm d yyyy', 'border': 1})
#         # cells_format = workbook.add_format({
#         #     'border': 1,
#         # })

#         # # Writing Document Header
#         # worksheet.set_column('A:B', 15)
#         # worksheet.merge_range('A3:B3', '')
#         # worksheet.insert_image('A3', 'static/img/logo.png', {'x_scale': 0.5, 'y_scale': 0.5})


#         # merge_format = workbook.add_format({
#         #     'bold': 1,
#         #     'border': 1,
#         #     'align': 'center',
#         #     'valign': 'vcenter',
#         #     'text_wrap':'true'})
#         # worksheet.set_column('C:E', 30)

#         # document_header_title = '''
#         #     Nom et prénom du gérant : NAWAFLEH MOHAMED
#         #     Nom et prénom ou raison sociale : LILIUM PHARMA ALGERIE
#         #     Statut juridique : EURL
#         #     Capital social : 140 000,00 DA
#         # ''' 
        
#         # worksheet.merge_range('C3:E3', document_header_title, merge_format)
#         # worksheet.set_row(2, 90)

        
#         # document_title = f'''
#         #     RECAP Congés Et Absence DU {starting_date} AU {ending_date}
#         # ''' 

#         # worksheet.merge_range('C5:E6', document_title)
#         # worksheet.set_row(0, 30)


#         # Init Row Index
#         row = 1

#         header_format = workbook.add_format({
#             'bold': True,  # Make the text bold
#             'font_size': 14,  # Set the font size
#             'align': 'center',  # Align text to the center
#             'valign': 'vcenter',  # Vertically center text
#             'bg_color': 'green',  # Background color
#             'font_color': 'white',  # Font color
#             'border': 1  # Add a border
#         })
#         worksheet.merge_range('A1:J1', 'Récapitulatif Des Congés & absences', header_format)


  
#         # Writing Headers
#         worksheet.write(row, 0, 'Numéro')
#         worksheet.write(row, 1, 'Company')
#         worksheet.write(row, 2, 'Family')
#         worksheet.write(row, 3, 'Nom & Prénom')
#         worksheet.write(row, 4, 'Date de Recrutement')
#         worksheet.write(row, 5, 'Poste Occupé')
#         # worksheet.write(row, 5, 'Salaire', cells_format)
#         worksheet.write(row, 6, 'Actif')
#         worksheet.write(row, 7, 'Jours Pris')
#         worksheet.write(row, 8, 'Type')
#         worksheet.write(row, 9, 'Observation')

#         # Observation Width
#         max_width = 0
#         num = 0


#          # Get the current logged-in user
#         user_request = request.user
        
#         # Filter users based on the company of the logged-in user
#         if user_request.userprofile.company == "lilium pharma":
#             users = User.objects.filter(userprofile__company="lilium pharma")
#         elif user_request.userprofile.company == "aniya pharma":
#             users = User.objects.filter(userprofile__company="aniya pharma")
#         elif user_request.userprofile.company == "orient bio":
#             users = User.objects.filter(userprofile__company="orient bio")
#         else:
#             # If the company of the logged-in user is not specified, retrieve all users
#             users = User.objects.all()



#         for user in users:

#             # Filtering User
#             user_leaves = leaves.filter(leaves_date_query, user=user)
#             user_absences = absences.filter(absences_date_query, user=user)

#             # Start from the first cell. Rows and columns are zero indexed.
#             nbr_absences_days = 0

#             observation = ''
#             type=''
#             id=''

#             # Iterate over Leaves and write it out row by row.
#             for leave in user_leaves:
#                 nbr_absences_days += (leave.end_date - leave.start_date).days
#                 observation += f'Congé du {leave.start_date} au {leave.end_date} | '
                
#             # Iterate over Absences and write it out row by row.
#             for absence in user_absences:
#                 nbr_absences_days += 1
#                 observation += f'Absence du {absence.date} | '

#             if user_leaves.exists():
#                 type += f'{leave.leave_type.description}'
                
#             # Iterate over Absences and write it out row by row.
#             if user_absences.exists():
#                 type += f'Absence'

#             # Incrementing Row
#             row += 1
#             num +=1
            

#             # Writing Rows
#             worksheet.write(row, 0, num)
#             worksheet.write(row, 1, user.userprofile.company)
#             worksheet.write(row, 2, user.userprofile.family)
#             worksheet.write(row, 3, f'{user.first_name} {user.last_name}' if user.first_name and user.last_name else user.username)
#             worksheet.write_datetime(row, 4, user.userprofile.entry_date, date_format)
#             worksheet.write(row, 5, user.userprofile.job_name)
#             # worksheet.write(row, 5, user.userprofile.salary,)
#             worksheet.write(row, 6, ('Oui' if user.is_active else 'Non'))
#             worksheet.write(row, 7, nbr_absences_days)
#             worksheet.write(row, 8, type)
#             worksheet.write(row, 9, observation)


#             observation_length = len(list(observation))
#             # Replace if an Observation is longer 
#             if max_width < observation_length:
#                 max_width = observation_length 


#         #  Setting Observation Column Wide
#         worksheet.set_column('J:J', max_width)
        
#         workbook.close()

#         return response


class ExportExcel(APIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        # Récupérer la plage de dates depuis la requête
        starting_date = request.GET.get('starting_date')
        ending_date = request.GET.get('ending_date')

        # Filtrer les absences et congés selon la plage de dates
        leaves_date_query = Q(start_date__range=[starting_date, ending_date]) | Q(end_date__range=[starting_date, ending_date])
        absences_date_query = Q(date__range=[starting_date, ending_date])

        # Obtenir les types de congés
        leave_types = LeaveType.objects.all()

        # Création de la réponse
        response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response['Content-Disposition'] = f"attachment; filename=Congés_&_Absences_{starting_date}-{ending_date}.xlsx"

        # Création du classeur
        workbook = xlsxwriter.Workbook(response, {'in_memory': True})
        worksheet = workbook.add_worksheet()

        # Format pour l'entête (plus petit et non en gras)
        header_format = workbook.add_format({
            'bold': False,
            'font_size': 10,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1
        })

        # Ajouter la date d'export et les informations de l'utilisateur
        current_date_time = "now().strftime('%d-%m-%Y %H:%M:%S')"
        user_full_name = f"{request.user.first_name} {request.user.last_name}" if request.user.first_name and request.user.last_name else request.user.username

        # Insérer le logo
        logo_path = "static/img/logo-22.png"  # Chemin vers le logo
        if os.path.exists(logo_path):
            worksheet.insert_image('A1', logo_path, {'x_scale': 0.3, 'y_scale': 0.3})  # Redimensionner le logo

        # Ajouter le titre d'export et les informations à côté du logo
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 12,
            'align': 'left',
            'valign': 'vcenter'
        })

        # Fusionner les colonnes pour le titre d'export
        worksheet.merge_range('B1:D1', f'Congé & Absence | Exporté le : {current_date_time}', title_format)
        worksheet.merge_range('B2:D2', f'Par : {user_full_name}', title_format)

        # Ajouter une ligne vide après le logo pour un espacement
        worksheet.set_row(3, 20)

        # Écrire les entêtes de données (commencer à la ligne 5)
        worksheet.write(4, 0, 'ID', header_format)  # Nouvelle colonne pour l'ID séquentiel
        worksheet.write(4, 1, 'PC Paie ID', header_format)  # Nouvelle colonne pour l'ID PC Paie
        worksheet.write(4, 2, 'User', header_format)
        worksheet.write(4, 3, 'Company', header_format)  # Nouvelle colonne pour la société (Company)

        # Ajouter l'entête pour Absence et Congés
        col_idx = 4
        worksheet.write(4, col_idx, 'Absence', header_format)
        col_idx += 1

        # Ajouter les entêtes pour les types de congés valides
        valid_leave_types = []
        for leave_type in leave_types:
            leave_count_for_type = Leave.objects.filter(leave_type=leave_type).filter(leaves_date_query).count()
            if leave_count_for_type > 0:
                valid_leave_types.append(leave_type)
                worksheet.write(4, col_idx, leave_type.description, header_format)
                col_idx += 1

        # Ajouter la colonne "Total" à la fin des entêtes
        worksheet.write(4, col_idx, 'Total', header_format)

        # Filtrer les utilisateurs avec is_human=True et leur compagnie
        users = User.objects.filter(
            userprofile__is_human=True, 
            userprofile__hidden__in=[True, False]
        ).filter(
            Q(userprofile__company='lilium pharma') | Q(userprofile__company='production')
        )

        # Initialiser le compteur de ligne pour les données
        row = 5
        cell_format = workbook.add_format({'border': 1})
        small_text_format = workbook.add_format({'font_size': 8, 'border': 1})

        # Itérer à travers chaque utilisateur et leurs absences/congés
        for idx, user in enumerate(users, 1):
            worksheet.write(row, 0, idx, cell_format)
            worksheet.write(row, 1, user.userprofile.pc_paie_id, cell_format)
            worksheet.write(row, 2, f"{user.first_name} {user.last_name}", cell_format)
            worksheet.write(row, 3, user.userprofile.company, cell_format)

            # Gérer les absences
            absences = Absence.objects.filter(user=user).filter(absences_date_query)
            absence_count = absences.count()
            total_leaves = absence_count
            col_idx = 4

            if absence_count > 0:
                absence_dates = " - ".join([f"(le: {absence.date})" for absence in absences])
                worksheet.write(row, col_idx, f"{absence_count}\n{absence_dates}", small_text_format)
            else:
                worksheet.write(row, col_idx, 0, cell_format)
            col_idx += 1

            # Gérer les congés pour chaque type de congé valide
            for leave_type in valid_leave_types:
                leaves = Leave.objects.filter(user=user, leave_type=leave_type).filter(leaves_date_query)
                leave_count = leaves.count()
                total_leaves += leave_count

                if leave_count > 0:
                    leave_dates = " - ".join([f"(du: {leave.start_date} - au: {leave.end_date})" for leave in leaves])
                    worksheet.write(row, col_idx, f"{leave_count}\n{leave_dates}", small_text_format)
                else:
                    worksheet.write(row, col_idx, leave_count, cell_format)

                col_idx += 1

            # Écrire le total des congés et absences dans la dernière colonne
            worksheet.write(row, col_idx, total_leaves, cell_format)

            row += 1

        # Sauvegarder et fermer le classeur
        workbook.close()

        return response
