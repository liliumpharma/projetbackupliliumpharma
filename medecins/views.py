from django.shortcuts import render, redirect
from requests import Response
from .models import Medecin, MedecinModificationHistory
from .forms import MedecinForm
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
import datetime
from rapports.models import Visite
from produits.models import Produit
from django.db.models import Count
from django.contrib.auth.models import User
from .get_medecins import get_medecins

from django.http import HttpResponse
from dateutil import relativedelta
from django.template.loader import render_to_string
from weasyprint import HTML


MEDICAL = [
    "Généraliste",
    "Diabetologue",
    "Neurologue",
    "Psychologue",
    "Gynécologue",
    "Rumathologue",
    "Allergologue",
    "Phtisio",
    "Cardiologue",
    "Urologue",
    "Hematologue",
    "Orthopedie",
    "Nutritionist",
    "Dermatologue",
    "Interniste",
    "Gastrologue",
]
COMMERCIAL = ["Pharmacie", "Grossiste", "SuperGros"]

def updateredis(request):
    import subprocess
    if request.user.is_superuser:
        subprocess.run(['redis-cli', 'FLUSHALL'])
        return HttpResponse("SUCCES.")
    else:
        return HttpResponse("Non autorisé", status=403)

def get_communes(request):
    wilaya_id = request.GET.get('wilaya')
    if wilaya_id != None:
        wilaya_id = int(wilaya_id)
    communes = Commune.objects.filter(wilaya_id=wilaya_id).order_by('nom')
    data = [{'id': c.id, 'nom': c.nom} for c in communes]
    print(f"Les wilayas sont {data}")
    return JsonResponse(data, safe=False)

class AddMedecin(LoginRequiredMixin, TemplateView):
    def get(self, request):
        if (
            request.user.userprofile.can_add_medecin
            or request.user.userprofile.can_add_client
        ):
            return render(
                request,
                "medecins/add.html",
                {
                    "form": MedecinForm(),
                    "page_title": "ajouter un medecin",
                    "MEDICAL": MEDICAL,
                    "COMMERCIAL": COMMERCIAL,
                },
            )
        else:
            return redirect("HomeMedecin")

    def post(self, request):
        if (
            request.user.userprofile.can_add_medecin
            or request.user.userprofile.can_add_client
        ):
            form = MedecinForm(request.POST)
            if form.is_valid():
                medecin = form.save()
                medecin.users.add(request.user)
                medecin.save()
                return redirect("HomeMedecin")
            return render(
                request,
                "medecins/add.html",
                {"form": form, "page_title": "ajouter un medecin"},
            )
        else:
            return redirect("HomeMedecin")


class UpdateMedecin(LoginRequiredMixin, TemplateView):
    def get(self, request, id):
        medecin = Medecin.objects.get(id=id)
        if medecin.updatable:
            form = MedecinForm(instance=medecin)
            return render(
                request,
                "medecins/update.html",
                {"form": form, "page_title": "ajouter un medecin"},
            )
        else:
            return redirect("HomeMedecin")

    def post(self, request, id):
        medecin = Medecin.objects.get(id=id)
        if medecin.updatable:
            form = MedecinForm(request.POST, instance=medecin)
            if form.is_valid():
                medecin = form.save()
                medecin.users.add(request.user)
                medecin.save()
                return redirect("HomeMedecin")
            return render(
                request,
                "medecins/add.html",
                {"form": form, "page_title": "ajouter un medecin"},
            )
        else:
            return redirect("HomeMedecin")


# class MedecinListPDF(LoginRequiredMixin, TemplateView):
#     def get(self, request):
#         medecins_list = get_medecins(request)

#         medecin_nbr = len(medecins_list) - len(
#             medecins_list.filter(specialite__in=["Pharmacie", "Grossiste"])
#         )

#         details = (
#             Medecin.objects.filter(id__in=medecins_list.values("id"))
#             .values("specialite")
#             .annotate(dcount=Count("specialite"))
#         )
#         other_details = f" <b>({medecin_nbr})</b> medecins "
#         other_details += " ".join(
#             [
#                 f'<b>({detail["dcount"]})</b> {detail["specialite"]}'
#                 for detail in details
#             ]
#         )
#         rendered = render_to_string(
#             "medecins/PDF.html",
#             {
#                 "medecins": medecins_list,
#                 "details": other_details,
#                 "nbr_clients": len(medecins_list),
#             },
#             request=request,
#         )
#         # rendered = "teest"
#         # htmldoc = HTML(string=rendered, base_url="http://app.liliumpharma.com")
#         return HttpResponse(rendered)
#         # return HttpResponse(htmldoc.write_pdf(), content_type='application/pdf')

#         # return render(request,'medecins/PDF.html',{"medecins":medecins_list,'details':other_details,'nbr_clients':len(medecins_list)})


from django.db.models import Count
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from collections import defaultdict

from collections import defaultdict
from django.db.models import Count
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class MedecinListPDF(LoginRequiredMixin, TemplateView):
    # def get(self, request):
    #     # Récupération de la clé commerciale et extraction de l'utilisateur
    #     commercial_key = request.GET.get("commercial")
    #     specialite = request.GET.get("specialite")
    #     commune = request.GET.get("commune")
    #     user = None

    #     if commercial_key:
    #         username = commercial_key.split(" - ")[-1]  # Extraire le nom d'utilisateur
    #         user = User.objects.filter(username=username).first()

    #     # Obtenir la liste des médecins pour l'utilisateur
    #     if commune == "0":  # Si la commune n'est pas vide
    #         medecins_list = Medecin.objects.filter(users=user).order_by("commune")
    #     else:  # Si la commune est vide
    #         medecins_list = Medecin.objects.filter(
    #             users=user, commune=commune
    #         ).order_by("commune")

    #     medecin_nbr = medecins_list.count()

    #     # Détails par wilaya et commune
    #     wilaya_details = medecins_list.values("wilaya__nom", "commune__nom").annotate(
    #         nbr_clients=Count("id")
    #     )

    #     # Regroupement des communes par wilaya
    #     communes_by_wilaya = defaultdict(list)
    #     for detail in wilaya_details:
    #         wilaya = detail["wilaya__nom"]
    #         commune = detail["commune__nom"]
    #         count = detail["nbr_clients"]
    #         communes_by_wilaya[wilaya].append(f"{commune} ({count})")

    #     details_str = "; ".join(
    #         f"<b>{wilaya}</b>: {', '.join(communes)}"
    #         for wilaya, communes in communes_by_wilaya.items()
    #     )

    #     # Détails par spécialité, commune et wilaya
    #     specialite_details = medecins_list.values(
    #         "wilaya__nom", "commune__nom", "specialite"
    #     ).annotate(nbr_clients=Count("id"))

    #     # Regroupement des spécialités par wilaya et commune
    #     specialities_by_wilaya_commune = defaultdict(lambda: defaultdict(list))
    #     for detail in specialite_details:
    #         wilaya = detail["wilaya__nom"]
    #         commune = detail["commune__nom"]
    #         specialite = detail["specialite"]
    #         count = detail["nbr_clients"]
    #         specialities_by_wilaya_commune[wilaya][commune].append(
    #             f"{specialite} ({count})"
    #         )

    #     if user.userprofile.speciality_rolee == "Commercial":

    #         include_specialties = ["Pharmacie", "Grossiste", "SuperGros"]
    #         count_specialitys = []
    #         count_per_specialitys = []

    #         medecin_nbr_commercial = Medecin.objects.filter(
    #             id__in=medecins_list.values("id"), specialite__in=include_specialties
    #         ).count()

    #         # Récapitulatif avant la liste des spécialités médicales
    #         recap_specialities_commercial = f'<span style="font-weight: 900;">({medecin_nbr_commercial}) Commerciale </span>'

    #         count_per_specialitys_commercial = " ".join(
    #             f'<b>({detail["dcount"]})<b> {detail["specialite"]}'
    #             for detail in (
    #                 Medecin.objects.filter(
    #                     id__in=medecins_list.values("id"),
    #                     specialite__in=include_specialties,
    #                 )
    #                 .values("specialite")
    #                 .annotate(dcount=Count("specialite"))
    #             )
    #         )

    #         count_specialitys_commercial = (
    #             f"{recap_specialities_commercial} : {count_per_specialitys_commercial}"
    #         )

    #     else:

    #         print("herreeeeeeeee")
    #         exclude_specialties = ["Pharmacie", "Grossiste", "SuperGros"]

    #         medecin_nbr = (
    #             Medecin.objects.filter(id__in=medecins_list.values("id"))
    #             .exclude(specialite__in=exclude_specialties)
    #             .count()
    #         )

    #         # Récapitulatif avant la liste des spécialités médicales
    #         recap_specialities = (
    #             f'<span style="font-weight: 900;">({medecin_nbr}) Medical </span>'
    #         )

    #         count_per_specialitys = " ".join(
    #             f'<b>({detail["dcount"]})</b> {detail["specialite"]}'
    #             for detail in (
    #                 Medecin.objects.filter(id__in=medecins_list.values("id"))
    #                 .exclude(specialite__in=exclude_specialties)
    #                 .values("specialite")
    #                 .annotate(dcount=Count("specialite"))
    #             )
    #         )

    #         # Concaténer le récapitulatif et les spécialités
    #         count_specialitys = f"{recap_specialities} : {count_per_specialitys}"

    #         print("recap " + str(count_specialitys))

    #         print("-----------------------------------------------")
    #         include_specialties = ["Pharmacie", "Grossiste", "SuperGros"]

    #         medecin_nbr_commercial = Medecin.objects.filter(
    #             id__in=medecins_list.values("id"), specialite__in=include_specialties
    #         ).count()

    #         # Récapitulatif avant la liste des spécialités médicales
    #         recap_specialities_commercial = f'<span style="font-weight: 900;">({medecin_nbr_commercial}) commerciale </span>'

    #         count_per_specialitys_commercial = " ".join(
    #             f'<b>({detail["dcount"]})</b> {detail["specialite"]}'
    #             for detail in (
    #                 Medecin.objects.filter(
    #                     id__in=medecins_list.values("id"),
    #                     specialite__in=include_specialties,
    #                 )
    #                 .values("specialite")
    #                 .annotate(dcount=Count("specialite"))
    #             )
    #         )

    #         # Concaténer le récapitulatif et les spécialités
    #         count_specialitys_commercial = (
    #             f"{recap_specialities_commercial} : {count_per_specialitys_commercial}"
    #         )
    #         print(str(count_specialitys_commercial))

    #     # Remplir les tableaux
    #     index = 1  # Initialiser l'index à 1
    #     speciality_table_rows_1 = []  # Lignes du premier tableau
    #     speciality_table_rows_2 = []  # Lignes du second tableau

    #     # Vous pouvez définir le point de division entre les deux tableaux ici (par exemple 6, mais ajustable)
    #     split_point = 8

    #     for wilaya, communes in specialities_by_wilaya_commune.items():
    #         for commune, specialites in communes.items():
    #             specialites_str = ", ".join(specialites)
    #             row = f"<tr><td>{index}</td><td><b>{wilaya}</b></td><td>{commune}</td><td>{specialites_str}</td></tr>"

    #             # Si l'index est inférieur ou égal au point de division, on ajoute au premier tableau
    #             if index <= split_point:
    #                 speciality_table_rows_1.append(row)
    #             else:
    #                 speciality_table_rows_2.append(row)

    #             index += 1  # Incrémenter l'index

    #     # Créer les tableaux HTML uniquement s'ils ont des lignes
    #     speciality_table_1 = ""
    #     if speciality_table_rows_1:
    #         speciality_table_1 = (
    #             "<table class='table'><thead><tr><th>#</th><th>Wilaya</th><th>Commune</th><th>Spécialités</th></tr></thead><tbody>"
    #             + "".join(speciality_table_rows_1)
    #             + "</tbody></table>"
    #         )

    #     speciality_table_2 = ""
    #     if speciality_table_rows_2:
    #         speciality_table_2 = (
    #             "<table class='table'><thead><tr><th>#</th><th>Wilaya</th><th>Commune</th><th>Spécialités</th></tr></thead><tbody>"
    #             + "".join(speciality_table_rows_2)
    #             + "</tbody></table>"
    #         )

    #     # Passer les deux tableaux au contexte du rendu
    #     context = {
    #         "medecins": medecins_list,
    #         "commerciale": user,
    #         "details": count_specialitys,
    #         "details_commercial": count_specialitys_commercial,
    #         "client_par_region": details_str,
    #         "speciality_details_1": speciality_table_1,
    #         "speciality_details_2": speciality_table_2,
    #         "nbr_clients": medecin_nbr,
    #     }

    #     rendered = render_to_string("medecins/PDF.html", context, request=request)
    #     return HttpResponse(rendered)

    def get(self, request):
        # Récupération de la clé commerciale et extraction de l'utilisateur
        commercial_key = request.GET.get("commercial")
        specialite = request.GET.get("specialite")
        commune = request.GET.get("commune")
        commune_first = request.GET.get("commune")
        wilaya = request.GET.get("wilaya")
        visites = request.GET.get("visites")
        user = None
        print(str(request))

        # Extraction de l'utilisateur à partir de la clé commerciale
        if commercial_key:
            username = commercial_key.split(" - ")[0]  # Extraire le nom d'utilisateur
            user = User.objects.filter(username=username).first()
            # Obtenir la liste des médecins pour l'utilisateur, filtrée par commune si spécifiée
            medecins_list = Medecin.objects.filter(users=user)
            print("TOUS LES MEDECINS BY USER")
        else:
            medecins_list = Medecin.objects.all()

        if commune != "0":  # Si la commune est spécifiée
            medecins_list = medecins_list.filter(commune=commune)

        if wilaya != "0":  # Si la wilaya est spécifiée
            medecins_list = medecins_list.filter(wilaya=wilaya)
            print(str(medecins_list))

        if visites == "0":
            medecins_list = medecins_list.filter(visite__isnull=True)
        elif visites == "1":
            medecins_list = medecins_list.filter(visite__isnull=False)
        elif visites == "2":
            #medecin with more then one visite
            medecins_list = medecins_list.annotate(visite_count=Count("visite")).filter(visite_count__gt=1)

        # Application des filtres de spécialité
        if specialite:
            if specialite == "medicale":
                exclude_specialties = ["Pharmacie", "Grossiste", "SuperGros"]
                medecins_list = medecins_list.exclude(
                    specialite__in=exclude_specialties
                )
            elif specialite == "commerciale":
                include_specialties = ["Pharmacie", "Grossiste", "SuperGros"]
                medecins_list = medecins_list.filter(specialite__in=include_specialties)
            else:
                medecins_list = medecins_list.filter(specialite=specialite)

        medecin_nbr = medecins_list.count()

        # Détails par wilaya et commune
        wilaya_details = medecins_list.values("wilaya__nom", "commune__nom").annotate(
            nbr_clients=Count("id")
        )

        # Regroupement des communes par wilaya
        communes_by_wilaya = defaultdict(list)
        for detail in wilaya_details:
            wilaya = detail["wilaya__nom"]
            commune = detail["commune__nom"]
            count = detail["nbr_clients"]
            communes_by_wilaya[wilaya].append(f"{commune} ({count})")

        details_str = "; ".join(
            f"<b>{wilaya}</b>: {', '.join(communes)}"
            for wilaya, communes in communes_by_wilaya.items()
        )

        # Détails par spécialité, commune et wilaya
        specialite_details = (
            medecins_list.values("wilaya__nom", "commune__nom", "specialite")
            .annotate(nbr_clients=Count("id"))
            .distinct()
        )

        # Regroupement des spécialités par wilaya et commune
        specialities_by_wilaya_commune = defaultdict(lambda: defaultdict(list))
        for detail in specialite_details:
            wilaya = detail["wilaya__nom"]
            commune = detail["commune__nom"]
            specialite = detail["specialite"]
            count = detail["nbr_clients"]
            specialities_by_wilaya_commune[wilaya][commune].append(
                f"{specialite} ({count})"
            )

        # Récapitulatif et comptage par spécialité
        count_specialitys = ""
        count_specialitys_commercial = ""

        if user and user.userprofile.speciality_rolee == "Commercial":
            include_specialties = ["Pharmacie", "Grossiste", "SuperGros"]
            medecin_nbr_commercial = Medecin.objects.filter(
                id__in=medecins_list.values("id"), specialite__in=include_specialties
            ).count()

            # Récapitulatif des spécialités commerciales
            recap_specialities_commercial = f'<span style="font-weight: 900;">({medecin_nbr_commercial}) Commerciale </span>'
            count_per_specialitys_commercial = " ".join(
                f'<b>({detail["dcount"]})</b> {detail["specialite"]}'
                for detail in (
                    Medecin.objects.filter(
                        id__in=medecins_list.values("id"),
                        specialite__in=include_specialties,
                    )
                    .values("specialite")
                    .annotate(dcount=Count("specialite"))
                )
            )
            count_specialitys_commercial = (
                f"{recap_specialities_commercial} : {count_per_specialitys_commercial}"
            )

        else:
            exclude_specialties = ["Pharmacie", "Grossiste", "SuperGros"]
            medecin_nbr = (
                Medecin.objects.filter(id__in=medecins_list.values("id"))
                .exclude(specialite__in=exclude_specialties)
                .count()
            )

            # Récapitulatif des spécialités médicales
            recap_specialities = (
                f'<span style="font-weight: 900;">({medecin_nbr}) Médicale </span>'
            )
            count_per_specialitys = " ".join(
                f'<b>({detail["dcount"]})</b> {detail["specialite"]}'
                for detail in (
                    Medecin.objects.filter(id__in=medecins_list.values("id"))
                    .exclude(specialite__in=exclude_specialties)
                    .values("specialite")
                    .annotate(dcount=Count("specialite"))
                )
            )
            count_specialitys = f"{recap_specialities} : {count_per_specialitys}"

        # Récupérer le nombre de médecins par commune
        commune_counts = (
            medecins_list.values("commune__nom")
            .annotate(nbr_contacts=Count("id"))
            .distinct()
        )

        # Créer un dictionnaire pour un accès rapide au nombre de contacts par commune
        commune_count_dict = {
            item["commune__nom"]: item["nbr_contacts"] for item in commune_counts
        }

        # Remplir les tableaux
        speciality_table_rows_1 = []  # Lignes du premier tableau
        speciality_table_rows_2 = []  # Lignes du second tableau
        index = 1  # Initialiser l'index à 1
        split_point = 8  # Point de division entre les deux tableaux

        for wilaya, communes in specialities_by_wilaya_commune.items():
            for commune, specialites in communes.items():
                specialites_str = ", ".join(specialites)

                # Récupérer le nombre de contacts pour la commune
                nbr_de_contact = commune_count_dict.get(
                    commune, 0
                )  # Par défaut, 0 si non trouvé

                row = f"<tr><td>{index}</td><td><b>{wilaya}</b></td><td>{commune} <span style='color: red; font-weight: bold;'>({nbr_de_contact})</span></td><td>{specialites_str}</td></tr>"

                # Si l'index est inférieur ou égal au point de division, on ajoute au premier tableau
                if index <= split_point:
                    speciality_table_rows_1.append(row)
                else:
                    speciality_table_rows_2.append(row)

                index += 1  # Incrémenter l'index

        # Créer les tableaux HTML uniquement s'ils ont des lignes
        speciality_table_1 = (
            "<table class='table'><thead><tr><th>#</th><th>Wilaya</th><th>Commune</th><th>Spécialités</th></tr></thead><tbody>"
            + "".join(speciality_table_rows_1)
            + "</tbody></table>"
            if speciality_table_rows_1
            else ""
        )

        speciality_table_2 = (
            "<table class='table'><thead><tr><th>#</th><th>Wilaya</th><th>Commune</th><th>Spécialités</th></tr></thead><tbody>"
            + "".join(speciality_table_rows_2)
            + "</tbody></table>"
            if speciality_table_rows_2
            else ""
        )

        # Passer les tableaux et autres informations au contexte du rendu
        print("----> " + str(medecins_list))
        if commune_first == "0":
            commune_first = "-"
        context = {
            "medecins": medecins_list,
            "commerciale": user,
            "wilaya": wilaya,
            "commune": commune_first,
            "details": count_specialitys,
            "details_commercial": count_specialitys_commercial,
            "client_par_region": details_str,
            "speciality_details_1": speciality_table_1,
            "speciality_details_2": speciality_table_2,
            "nbr_clients": medecin_nbr,
        }

        rendered = render_to_string("medecins/PDF.html", context, request=request)
        return HttpResponse(rendered)


from datetime import datetime


class HomeMedecin(LoginRequiredMixin, TemplateView):
    def get(self, request):
        # today=datetime.date.today()

        medecins_list = Medecin.objects.filter(users=request.user)
        # visited=Medecin.objects.filter(users=request.user,visite__rapport__added__month=today.month)

        if request.GET.get("cat") == "0":
            # medecins_list=Medecin.objects.filter(users=request.user).exclude(id__in=visited.values("id"))
            medecins_list = Medecin.objects.filter(users=request.user)
        # if request.GET.get("cat")=="1":
        #     medecins_list=visited

        medecin_nbr = (
            len(medecins_list)
            - len(medecins_list.filter(specialite__in=["Pharmacie", "Grossiste"]))
            - 1
        )

        details = (
            Medecin.objects.filter(id__in=medecins_list.values("id"))
            .values("specialite")
            .annotate(dcount=Count("specialite"))
        )
        other_details = f"<b>{medecin_nbr}</b> medecins "
        other_details += " ".join(
            [
                f'<b>({detail["dcount"]})</b> {detail["specialite"]}'
                for detail in details
            ]
        )

        print(str(other_details))

        paginator = Paginator(medecins_list, 15)
        page = request.GET.get("page")
        print("home medecin")
        medecins = paginator.get_page(page)
        return render(
            request,
            "medecins/home.html",
            {
                "medecins": medecins,
                "page_title": "liste des medecins",
                "medecin_number": len(Medecin.objects.filter(users=request.user)),
                "nbr": len(medecins_list),
                "details": other_details,
            },
        )


from django.db.models import Case, When, Value, CharField


class VisitesMedecin(LoginRequiredMixin, TemplateView):
    # def get(self,request,id):
    #     if request.user.userprofile.speciality_rolee in ["Superviseur_national", "CountryManager"] or request.user.is_superuser:
    #         filters={}
    #         produit=''
    #         mindate = '2023-01-01'

    #         if  request.GET.get("month") :
    #             filters['rapport__added__month']=request.GET.get("month")
    #             filters['rapport__added__year']=datetime.date.today().year

    #         # if  request.GET.get("mindate") :
    #         #     filters['rapport__added__gte']=request.GET.get("mindate")
    #         if  mindate :
    #             filters['rapport__added__gte']=mindate

    #         if  request.GET.get("maxdate") :
    #             filters['rapport__added__lte']=request.GET.get("maxdate")

    #         if  request.GET.get("priority") and request.GET.get("priority")!="0" :
    #             filters['priority']=request.GET.get("priority")

    #         if  request.GET.get("produit"):
    #             filters['produits__id']=request.GET.get("produit")
    #             produit+=f'{Produit.objects.get(id=request.GET.get("produit")).nom} '

    #         visites=Visite.objects.filter(medecin__id=id).filter(**filters).order_by('-rapport__added')

    #         return render(request,'medecins/visites.html',{
    #         'visites':visites,
    #         "medecin":Medecin.objects.get(id=id),
    #         'nbr_visites':len(visites),
    #         'produit':produit
    #         })

    def get(self, request, id):
        print("*****************VisitesMedecin*****************")
        # if (
        #     request.user.userprofile.speciality_rolee
        #     in ["Superviseur_national", "CountryManager"]
        #     or request.user.is_superuser
        # ):
        filters = {}
        produit = ""
        mindate = "2023-01-01"
        if request.GET.get("month"):
            filters["rapport__added__month"] = request.GET.get("month")
            filters["rapport__added__year"] = datetime.date.today().year
        if mindate:
            filters["rapport__added__gte"] = mindate
        if request.GET.get("maxdate"):
            filters["rapport__added__lte"] = request.GET.get("maxdate")
        if request.GET.get("priority") and request.GET.get("priority") != "0":
            filters["priority"] = request.GET.get("priority")
        if request.GET.get("produit"):
            filters["produits__id"] = request.GET.get("produit")
            produit += f'{Produit.objects.get(id=request.GET.get("produit")).nom} '
        # Conditional ordering: put visits with specified specialties at the end
        visites = Visite.objects.filter(medecin__id=id, **filters).order_by(
            Case(
                When(
                    medecin__specialite__in=["Pharmacie", "Grossiste", "SuperGros"],
                    then=Value("ZZZZZ"),
                ),
                default=Value(""),
                output_field=CharField(),
            ),
            "-rapport__added",
        )
        return render(
            request,
            "medecins/visites.html",
            {
                "visites": visites,
                "medecin": Medecin.objects.get(id=id),
                "nbr_visites": len(visites),
                "produit": produit,
            },
        )


def medecin_last_six_months(request, id):
    today = datetime.datetime.now()
    last_six_month = today - relativedelta.relativedelta(months=6)
    visites = Visite.objects.filter(medecin__id=id, rapport__added__gte=last_six_month)

    return render(
        request,
        "medecins/visites.html",
        {
            "visites": visites,
            "medecin": Medecin.objects.get(id=id),
            "nbr_visites": len(visites),
        },
    )


def ChangeFlag(request, id):
    medecin = Medecin.objects.get(id=id)
    medecin.flag = not medecin.flag
    medecin.save()
    return HttpResponse(status=200)


from django.shortcuts import redirect
from django.contrib import messages
from .models import Medecin, MedecinModificationHistory

from django.shortcuts import redirect
from django.contrib import messages
from .models import Medecin, MedecinModificationHistory


def ChangeUser(request):
    print("*****************ChangeUser*****************")

    # Récupérer les médecins concernés
    medecins = Medecin.objects.filter(id__in=request.POST.get("medecins").split(","))
    medecins_to_exclude = Medecin.objects.filter(
        specialite__in=["Pharmacie", "Grossiste", "SuperGros"]
    )

    # Récupérer les utilisateurs vers lesquels le médecin sera transféré
    users = User.objects.filter(id__in=request.POST.getlist("changeusers"))

    # for user in userss:
    #     if user.doctor_count >=160:
    #         okay=False
    excluded_specialities = ["Pharmacie", "Grossiste", "SuperGros"]

    for medecin in medecins:
        print("medecin = " + str(medecin.specialite in excluded_specialities))
        if medecin.specialite not in excluded_specialities:
            userss = User.objects.filter(
                id__in=request.POST.getlist("changeusers")
            ).annotate(
                doctor_count=Count(
                    "medecin", filter=~Q(medecin__specialite__in=excluded_specialities)
                )
            )

            print("userss = " + str(userss))
            for user in userss:
                okay = True
                print("nombre de medecins" + str(user.doctor_count))
                if user.username != "Medecin_Recycle_Bin" and user.doctor_count >= 160:
                    okay = False
                    messages.warning(
                        request,
                        f"{user.username} à {user.doctor_count} plus de 160 medecins sur son PF vous ne pouvez pas lui attribuer plus de medecins",
                    )
                if okay:
                    user_count = medecin.users.count()
                    if user_count == 1 or request.user.is_superuser:
                        # Sauvegarder les utilisateurs avant la modification
                        users_before = list(medecin.users.all())

                        # Effacer les utilisateurs actuels
                        medecin.users.clear()

                        # Définir les nouveaux utilisateurs
                        medecin.users.set(users)

                        # Sauvegarder les utilisateurs après la modification
                        users_after = list(users)

                        # Enregistrer l'historique de la modification
                        modification_history = MedecinModificationHistory(
                            medecin=medecin,
                            user=request.user,
                            action="transfert d'utilisateurs",
                        )
                        modification_history.save()

                        # Définir les utilisateurs avant la modification dans l'historique
                        print("users before: " + str(users_before))
                        print("users after: " + str(users_after))
                        modification_history.users_before.set(users_before)

                        # Définir les utilisateurs après la modification dans l'historique
                        modification_history.users_after.set(users_after)
                    else:
                        # Si l'utilisateur n'est pas un superutilisateur et que le médecin est partagé, afficher un message d'avertissement
                        messages.warning(
                            request,
                            "Vous ne pouvez pas modifier un médecin partagé entre plusieurs utilisateurs.",
                        )
        else:
            user_count = medecin.users.count()
            # if user_count == 1 or request.user.is_superuser:
            # Sauvegarder les utilisateurs avant la modification
            users_before = list(medecin.users.all())
            # Effacer les utilisateurs actuels
            medecin.users.clear()
            # Définir les nouveaux utilisateurs
            medecin.users.set(users)
            # Sauvegarder les utilisateurs après la modification
            users_after = list(users)
            # Enregistrer l'historique de la modification
            modification_history = MedecinModificationHistory(
                medecin=medecin,
                user=request.user,
                action="transfert d'utilisateurs",
            )
            modification_history.save()
            # Définir les utilisateurs avant la modification dans l'historique
            print("users before: " + str(users_before))
            print("users after: " + str(users_after))
            modification_history.users_before.set(users_before)
            # Définir les utilisateurs après la modification dans l'historique
            modification_history.users_after.set(users_after)
            # else:
            #     # Si l'utilisateur n'est pas un superutilisateur et que le médecin est partagé, afficher un message d'avertissement
            #     messages.warning(
            #         request,
            #         "Vous ne pouvez pas modifier un médecin partagé entre plusieurs utilisateurs.",
            #     )

    return redirect("/admin/medecins/medecin/")


# def ChangeUser(request):
#     print('*****************ChangeUser*****************')

#     # Récupérer les médecins concernés
#     medecins = Medecin.objects.filter(id__in=request.POST.get("medecins").split(","))

#     # Récupérer les utilisateurs vers lesquels le médecin sera transféré
#     users = User.objects.filter(id__in=request.POST.getlist("changeusers"))

#     for medecin in medecins:
#         user_count = medecin.users.count()
#         if user_count == 1 or request.user.is_superuser:
#             # Sauvegarder les utilisateurs avant la modification
#             users_before = list(medecin.users.all())

#             # Effacer les utilisateurs actuels
#             medecin.users.clear()

#             # Définir les nouveaux utilisateurs
#             medecin.users.set(users)

#             # Sauvegarder les utilisateurs après la modification
#             users_after = list(users)

#             # Enregistrer l'historique de la modification
#             modification_history = MedecinModificationHistory(
#                 medecin=medecin,
#                 user=request.user,
#                 action="transfert d'utilisateurs",
#             )
#             modification_history.save()

#             # Définir les utilisateurs avant la modification dans l'historique
#             print("users before: "+str(users_before))
#             print("users after: "+str(users_after))
#             modification_history.users_before.set(users_before)

#             # Définir les utilisateurs après la modification dans l'historique
#             modification_history.users_after.set(users_after)
#         else:
#             # Si l'utilisateur n'est pas un superutilisateur et que le médecin est partagé, afficher un message d'avertissement
#             messages.warning(request, "Vous ne pouvez pas modifier un médecin partagé entre plusieurs utilisateurs.")

#     return redirect("/admin/medecins/medecin/")


# def ChangeUser(request):
#     print('*************************************************ChangeUser')
#     medecins=Medecin.objects.filter(id__in=request.POST.get("medecins").split(","))
#     users=User.objects.filter(id__in=request.POST.getlist("changeusers"))

#     for medecin in medecins:
#         user_count = medecin.users.count()
#         print("USERS:"+str(user_count))
#         if (user_count==1):
#             medecin.users.clear()
#             medecin.users.set(users)
#         else:
#             if request.user.is_superuser:
#                 medecin.users.clear()
#                 medecin.users.set(users)
#             else:
#                 messages.warning(request, "Vous ne pouvez pas modifier un medecin partagé entre plusieurs utilisateurs      |   لا يمكنك تعديل طبيب مشترك   ")

#     # medecins.usersset.set(users)
#     return redirect("/admin/medecins/medecin/")


def ChangeMedecin(request):
    print("**********ChangeVisite******")
    visites = Visite.objects.filter(id__in=request.POST.get("medecins").split(","))
    to_medecins = Medecin.objects.filter(id__in=request.POST.getlist("changeusers"))

    for visite in visites:
        visite.medecin = (
            to_medecins.first()
        )  # Assuming you want to set only one Medecin
        visite.save()
        print("changed")
    # medecins.usersset.set(users)
    return redirect("/admin/rapports/visite/")


def PdfStatisticMedecinsPerUser(request):
    # Render the HTML template
    template_name = "medecins/pdf_medecin_per_user.html"
    return render(request, template_name)


# HELP


def update_wilaya(request):
    # Filter Medecin instances where wilaya is None or an empty string
    medecins = Medecin.objects.filter(wilaya__isnull=True)

    # Print the count of such Medecin instances
    print(f"Number of Medecin instances with wilaya empty or null: {medecins.count()}")

    # Print the details of these Medecin instances
    for medecin in medecins:
        commune = medecin.commune
        if commune:
            medecin.wilaya = commune.wilaya
            medecin.save()
            print("done")
    return Response(status=200)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
import datetime


class MedecinInfo(APIView):
    def get(self, request, format=None):
        user_id = request.GET.get("user")
        month = request.GET.get("month")
        year = datetime.datetime.now().year
        q3 = request.GET.get("q3")
        doctor_ids = request.GET.getlist("doctor_ids", [])
        if any(doctor_ids):
            # Checking if any element in doctor_ids is non-empty
            print("doctor_ids is not empty:", doctor_ids)

            if q3 == None:
                medecin_info = {}
                for doctor_id in doctor_ids:
                    try:
                        medecin = Medecin.objects.get(id=doctor_id)
                        medecin_visite_dates = self.get_visite_dates(
                            medecin, user_id, month, year
                        )
                        medecin_info[medecin.id] = {
                            "specialite": medecin.specialite,
                            "classification": medecin.classification,
                            "visite_dates": medecin_visite_dates,
                            "added": medecin.added,
                        }
                    except Medecin.DoesNotExist:
                        pass

                return Response(medecin_info, status=status.HTTP_200_OK)
            else:
                medecin_info = {}
                for doctor_id in doctor_ids:
                    try:
                        medecin = Medecin.objects.get(id=doctor_id)
                        medecin_info[medecin.id] = {
                            "specialite": medecin.specialite,
                            "classification": medecin.classification,
                            "added": medecin.added,
                            # 'wilaya': medecin.wilaya.nom,
                            "wilaya": (
                                medecin.wilaya.nom
                                if hasattr(medecin, "wilaya") and medecin.wilaya
                                else ""
                            ),
                            "commune": medecin.commune.nom,
                        }
                    except Medecin.DoesNotExist:
                        pass

                print(str(medecin_info))

                return Response(medecin_info, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_200_OK)

    def get_visite_dates(self, medecin, user_id, month, year):
        visite_dates = Visite.objects.filter(
            medecin=medecin,
            rapport__user=user_id,
            rapport__added__month=month,
            rapport__added__year=year,
        ).values_list("rapport__added", flat=True)

        return list(visite_dates)


# VIEW TO DELETE MEDECIN USING NAME
class DeleteMedecinView(APIView):
    def get(self, request, *args, **kwargs):
        # # Get the medecins with nom = "allouane épouse Bella"
        # medecins_to_delete = Medecin.objects.filter(nom="derouiche fatiha")

        # # Delete the medecins
        # # print(len(medecins_to_delete))
        # medecins_to_delete.delete()
        # medecins_to_delete.delete()

        # # Redirect to a success URL or return a success response
        # return HttpResponse("Medecins deleted successfully.")
        medecins_empty_users = Medecin.objects.filter(users__isnull=True)

        # Pass the queryset to a template for rendering
        print(list(medecins_empty_users))
        medecins_empty_users.delete()
        # return render(request, 'empty_users_medecin.html', context)
        return HttpResponse("Medecins deleted successfully.")


# UPLOADING MEDECINS EXCEL
import pandas as pd
from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from .forms import UploadExcelForm
from .models import Medecin, MedecinSpecialite, Wilaya, Commune

# @staff_member_required
# def upload_excel(request):
#     if request.method == "POST":
#         form = UploadExcelForm(request.POST, request.FILES)
#         if form.is_valid():
#             fichier_excel = request.FILES['fichier_excel']
#             df = pd.read_excel(fichier_excel, sheet_name='Template')

#             # Normaliser les noms de colonnes
#             df.columns = df.columns.str.strip().str.lower()

#             # Vérifier les colonnes du template
#             # expected_columns = ['nom', 'specialite', 'classification', 'telephone', 'email', 'wilaya', 'commune', 'adresse', 'users']
#             # if list(df.columns) != expected_columns:
#             #     return render(request, 'medecins/upload_excel.html', {
#             #         'form': form,
#             #         'error': 'Le fichier Excel doit suivre le template de colonnes : ' + ', '.join(expected_columns)
#             #     })

#             # Créer des objets Medecin à partir des données de l'Excel
#             for _, row in df.iterrows():
#                 wilaya = Wilaya.objects.get(nom=row['wilaya']) if not pd.isna(row['wilaya']) else None
#                 commune = Commune.objects.get(nom=row['commune'])
#                 telephone = '0' + str(row['telephone'])
#                 print(str(row))

#                 # Préparer les données pour l'objet Medecin
#                 medecin_data = {
#                     'nom': row['pharmacie nom'],
#                     'specialite': "Pharmacie",
#                     'classification': 'a',
#                     'telephone': telephone,
#                     'email': row['email'],
#                     'wilaya': wilaya,
#                     'commune': commune,
#                     'uploaded_from_excel': True,
#                     'adresse': row['adresse']
#                 }

#                 # Ajouter les champs optionnels seulement s'ils ne sont pas vides ou null
#                 optional_fields = ['specialite_fk', 'flag', 'updatable', 'blocked', 'contact', 'lat', 'lon', 'note']
#                 for field in optional_fields:
#                     if field in df.columns and pd.notna(row[field]):
#                         medecin_data[field] = row[field]

#                 # Créer l'objet Medecin
#                 medecin = Medecin.objects.create(**medecin_data)

#                 # Ajouter les utilisateurs
#                 if pd.notna(row['users']):
#                     usernames = row['users'].split('-')
#                     for username in usernames:
#                         try:
#                             user = User.objects.get(username=username.strip())
#                             medecin.users.add(user)
#                         except User.DoesNotExist:
#                             print(f"User {username} does not exist.")

#                 medecin.save()

#             return redirect('https://app.liliumpharma.com/admin/medecins/medecin/')
#     else:
#         form = UploadExcelForm()

#     return render(request, 'medecins/upload_excel.html', {'form': form})


@staff_member_required
def upload_excel(request):
    if request.method == "POST":
        form = UploadExcelForm(request.POST, request.FILES)
        if form.is_valid():
            fichier_excel = request.FILES["fichier_excel"]
            df = pd.read_excel(fichier_excel, sheet_name="Template")

            # Normaliser les noms de colonnes
            df.columns = df.columns.str.strip().str.lower()

            # Créer des objets Medecin à partir des données de l'Excel
            for _, row in df.iterrows():
                wilaya = (
                    Wilaya.objects.get(nom=row["wilaya"])
                    if not pd.isna(row["wilaya"])
                    else None
                )
                commune = Commune.objects.get(nom=row["commune"])
                telephone = "0" + str(row["telephone"])

                # Préparer les données pour l'objet Medecin
                medecin_data = {
                    "nom": row["pharmacie nom"],
                    "specialite": "Pharmacie",
                    "classification": "a",
                    "telephone": telephone,
                    "email": row["email"],
                    "wilaya": wilaya,
                    "commune": commune,
                    "uploaded_from_excel": True,
                    "adresse": row["adresse"],
                }

                # Ajouter les champs optionnels seulement s'ils ne sont pas vides ou null
                optional_fields = [
                    "specialite_fk",
                    "flag",
                    "updatable",
                    "blocked",
                    "contact",
                    "lat",
                    "lon",
                    "note",
                ]
                for field in optional_fields:
                    if field in df.columns and pd.notna(row[field]):
                        medecin_data[field] = row[field]

                # Créer l'objet Medecin
                medecin = Medecin.objects.create(**medecin_data)

                # Transférer les visites des médecins existants vers le nouveau
                if "id_change" in df.columns and pd.notna(row["id_change"]):
                    ids = str(row["id_change"]).split("+")
                    for medecin_id in ids:
                        try:
                            ancien_medecin = Medecin.objects.get(id=int(medecin_id))
                            rb = User.objects.filter(
                                username="Pharmacie_Recycle_Bin"
                            ).first()
                            Visite.objects.filter(medecin=ancien_medecin).update(
                                medecin=medecin
                            )
                            print("---> ph rb -->" + str(rb))
                            medecin_instance = Medecin.objects.filter(
                                id=medecin_id
                            ).first()
                            medecin_instance.users.set([rb])
                        except Medecin.DoesNotExist:
                            print(f"Medecin with ID {medecin_id} does not exist.")

                # Ajouter les utilisateurs
                if pd.notna(row["users"]):
                    usernames = row["users"].split("-")
                    for username in usernames:
                        try:
                            user = User.objects.get(username=username.strip())
                            medecin.users.add(user)
                        except User.DoesNotExist:
                            print(f"User {username} does not exist.")

                medecin.save()

            return redirect("https://app.liliumpharma.com/admin/medecins/medecin/")
    else:
        form = UploadExcelForm()

    return render(request, "medecins/upload_excel.html", {"form": form})


from django.shortcuts import render


def excel_loading_view(request):
    return render(request, "../templates/medecins/loading_excel.html")


from django.http import JsonResponse
from django.views import View
from django.contrib.auth.models import User

from django.http import JsonResponse
from django.views import View
from django.contrib.auth.models import User
from .models import Medecin

class DeleteMedecinsView(View):
    def get(self, request, *args, **kwargs):
        # Liste pour stocker les ID des médecins supprimés
        deleted_medecins_with_users = []
        deleted_medecins_without_users = []

        # Supprimer les médecins ayant des utilisateurs avec les IDs 102 et 103
        medecins_to_delete = Medecin.objects.filter(users__id__in=[102])
        for medecin in medecins_to_delete:
            print(f"Deleting medecin with ID: {medecin.id}, name: {medecin.nom}")  # Afficher dans le terminal
            deleted_medecins_with_users.append(medecin.id)  # Ajouter l'ID à la liste
            medecin.delete()  # Supprimer le médecin

        # Supprimer les médecins n'ayant aucun utilisateur
        medecins_without_users = Medecin.objects.filter(users__isnull=True)
        for medecin in medecins_without_users:
            print(f"Deleting medecin with ID: {medecin.id}, name: {medecin.nom}")  # Afficher dans le terminal
            deleted_medecins_without_users.append(medecin.id)  # Ajouter l'ID à la liste
            medecin.delete()  # Supprimer le médecin

        # Retourner une réponse JSON avec les ID des médecins supprimés
        return JsonResponse({
            'medecins_deleted_with_users_102_103': deleted_medecins_with_users,
            'medecins_deleted_without_users': deleted_medecins_without_users
        })

