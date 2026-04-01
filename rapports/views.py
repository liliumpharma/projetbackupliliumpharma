from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, JsonResponse
from django.db.models import F


from orders.models import Order, OrderItem
from .forms import *
from .models import Rapport, Comment
from produits.models import Produit, ProduitVisite
from medecins.models import Medecin
from regions.models import *
from leaves.models import *
import csv
from .utils import render_to_pdf
from django.db.models import Q
from django.db.models import Count
from .get_rapports import rapport_list, get_visites
from itertools import chain
from datetime import datetime, date, timedelta
from accounts.models import UserProfile
from rest_framework.views import APIView
from rapports.api.serializers import RapportSerializer
from rest_framework.response import Response
from django.template.loader import render_to_string
from weasyprint import HTML
from produits.get_produits_stock import get_stock
from django.utils import timezone
from rest_framework import status
from regions.models import Commune
from calendar import monthrange
from rest_framework.authentication import (
    SessionAuthentication,
    TokenAuthentication,
    BasicAuthentication,
)
from django.shortcuts import get_object_or_404
from django.views import View
from django.http import HttpResponse, HttpResponseRedirect
from .models import Rapport
from django.urls import reverse
from django.shortcuts import render
from django.utils.timezone import now

def get_user_by_id(request, user_id):
    print(f"Le type de id est {id}")
    try:
        user = User.objects.get(pk=user_id)
        data = {
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,  # facultatif
            'username': user.username,
        }
        print(f"DATA : {data}")
    except User.DoesNotExist:
        data = {'error': 'Utilisateur introuvable'}

    return JsonResponse(data)

def get_visite(id):
    try:
        return Visite.objects.get(id=id)
    except:
        raise Http404


def get_rapport(id):
    try:
        return Rapport.objects.get(id=id)
    except:
        raise Http404


def get_medecin(id):
    try:
        return Medecin.objects.get(id=id)
    except:
        raise Http404

#def aaa(request):
#    print("test")
#    form = RapportForm(request.POST or None, request.FILES or None)
#    if request.method == "POST" and form.is_valid():
#        rapport = form.save(commit=False)
#        print(request.user)
#        rapport.user = request.user
#        rapport.save()
#        m = "Rapport bien ajouter"
#        return render(request, "rapports/aaa.html", {"m":m})
#    return render(request, "rapports/aaa.html")

class aaa(LoginRequiredMixin, TemplateView):
    def get(self, request):
        return render(request, "rapports/aaa.html")
    
    def post(self, request):
        form = RapportForm(request.POST, request.FILES)
        try:
            aujourdhui = now() + timedelta(hours=1)
            aujourdhui = aujourdhui.date()
            visite = Rapport.objects.get(added=aujourdhui) 
            m="Vous ne pouvez pas ajouter un autre rapport, car un seul rapport par jour"
            return render(request, "rapports/aaa.html", {"m":m})
        except Rapport.DoesNotExist:
            if form.is_valid():
                instance = form.save(commit=False)
                form.set_the_user(request.user)  # ✅ Assigne l'utilisateur avant de sauvegarder
                instance.added = aujourdhui
                instance.save()
                m = "Rapport bien ajouter"
                return render(request, "rapports/aaa.html", {"m":m})
        return render(request, "rapports/aaa.html")

class vis(LoginRequiredMixin, TemplateView):
    def get(self, request, id):
        print(id)
        vis = Visite.objects.filter(rapport=id)
        return render(request, "rapports/vis.html", {"id":id, "visites":vis})

class Listvisit(LoginRequiredMixin, TemplateView):
    def get(self, request):
        year = int(request.GET.get("year", timezone.now().year))
        month = int(request.GET.get("month", timezone.now().month))
        med_id = request.GET.get("med_id")
        med_nom = request.GET.get("med_nom")
        username = request.GET.get("user")
        total = request.GET.get("total")
        d = request.GET.get("date")
        user = get_object_or_404(User, username=username)
        med = get_object_or_404(Medecin, id=med_id)
        # Définir l'intervalle du mois
        start_of_month = datetime(year, month, 1)
        print(f"start of mont {start_of_month}")
        if month == 12:
            end_of_month = datetime(year + 1, 1, 1)
        else:
            end_of_month = datetime(year, month + 1, 1)
        start_of_month = timezone.make_aware(start_of_month)
        end_of_month = timezone.make_aware(end_of_month)
        visites = Visite.objects.filter(
            rapport__user=user,
            medecin=med,
            rapport__added__gte=start_of_month,
            rapport__added__lt=end_of_month
        ).order_by('rapport__added')
        context = {
            "visites": visites,
            "commune": med,
            "year": year,
            "month": month,
            "user": user,
            "total":total
        }
        if d == "1":
            context = {
                "dates": [
                    {"date": t.rapport.added.strftime("%Y-%m-%d")}
                    for t in visites
                ]
            }
            return JsonResponse(context)
        return render(request, "rapports/listvisit.html", context)


class HomeRapport(LoginRequiredMixin, TemplateView):
    def get(self, request):
        print(request.user.username)
        rapports = (
            Rapport.objects.filter(
                user__username=request.user.username,
                added__month=datetime.now().month,
                added__year=datetime.now().year,
            )
            .order_by("-added")
            .distinct()
        )
        # rapport_updatable=Rapport.objects.filter(user=request.user,can_update=True).exclude(id__in=rapports_month.values('id')).order_by('-added')
        # rapports=list(chain(rapports_month,rapport_updatable))
        produits = Produit.objects.filter(
            pays=request.user.userprofile.commune.wilaya.pays
        )

        visites = Visite.objects.filter(rapport__in=rapports)

        medecins = Medecin.objects.filter(visite__in=visites).distinct()

        medecin_nbr = len(medecins) - len(
            medecins.filter(specialite__in=["Pharmacie", "Grossiste"])
        )

        details = (
            Medecin.objects.filter(id__in=medecins.values("id"))
            .values("specialite")
            .annotate(dcount=Count("specialite"))
        )
        other_details = " ".join(
            [
                f'<b class="text-green">{detail["dcount"]}</b> {detail["specialite"]} '
                for detail in details
            ]
        )

        other_details += "<br/>"
        other_details += " ".join(
            [
                "<b class='text-green'>"
                + str(len(visites.filter(produits__id=produit.id)))
                + "</b> "
                + produit.nom
                for produit in produits
            ]
        )

        return render(
            request,
            "rapports/home.html",
            {
                "page_title": "",
                "rapports": rapports,
                "visitesnbr": len(visites),
                "details": f'<b class="text-green">{len(medecins)}</b> clients <b class="text-green">{medecin_nbr}</b> medecins {other_details}',
            },
        )


class DeleteVisite(LoginRequiredMixin, TemplateView):
    def get(self, request, id):
        visite = get_visite(id)
        if visite.rapport.is_updatable() and visite.rapport.user == request.user:
            visite.delete()
        return redirect("test")


class UpdateRapport(LoginRequiredMixin, TemplateView):
    template_name = "rapports/update.html"
    page_title = "Modifier le rapport"

    def get(self, request, id):
        rapport = get_rapport(id=id)
        if rapport.is_updatable() and rapport.user == request.user:
            return render(
                request,
                self.template_name,
                {
                    "page_title": self.page_title,
                    "rapport": rapport,
                    "form": RapportForm(),
                },
            )
        else:
            return redirect("HomeRapport")

    def post(self, request, id):
        rapport = get_rapport(id=id)
        if rapport.is_updatable() and rapport.user == request.user:
            form = RapportForm(request.POST, request.FILES, instance=rapport)
            if form.is_valid():
                form.set_the_user(request.user)
                form.save()
                return redirect("HomeRapport")
            else:
                return render(
                    request,
                    self.template_name,
                    {
                        "form": form,
                        "page_title": self.page_title,
                    },
                )
        else:
            return redirect("HomeRapport")


class AddRapport(LoginRequiredMixin, TemplateView):
    template_name = "rapports/add.html"
    page_title = "Ajouter un rapport"

    def get(self, request):
        try:
            Rapport.objects.get(added=datetime.today(), user=request.user)
            return redirect("HomeRapport")

        except Rapport.DoesNotExist:
            plan = Plan.objects.filter(
                day=datetime.today(),
                valid_commune=True,
                valid_clients=True,
                user=request.user,
            )

            if len(plan) != 1:
                return redirect("HomeRapport")
            else:
                return render(
                    request,
                    self.template_name,
                    {
                        "form": RapportForm(),
                        "page_title": self.page_title,
                    },
                )

    def post(self, request):
        try:
            user=request.user
            user_plan = Plan.objects.filter(user=user).first
            if user_plan.valid_commune and  user_plan.valid_clients :
                Rapport.objects.get(added=datetime.today(), user=user)
                return redirect("HomeRapport")
        except Rapport.DoesNotExist:
            print("plan not valid")
            return Response(status=404)
            # form = RapportForm(request.POST, request.FILES)
            # if form.is_valid():
            #     form.set_the_user(request.user)
            #     form.save()
            #     return redirect("HomeRapport")
            # else:
            #     return render(
            #         request,
            #         self.template_name,
            #         {
            #             "form": form,
            #             "page_title": self.page_title,
            #         },
            #     )


class AddVisite(LoginRequiredMixin, TemplateView):
    template_name = "rapports/visites/add_visite.html"
    page_title = "Ajouter une visite"

    def get_the_rapport(self, id, user):
        try:
            if id == 0:
                return Rapport.objects.get(added=datetime.today(), user=user)
            else:
                return Rapport.objects.get(id=id, user=user)
        except:
            raise Http404

    def get(self, request, id=0):
        try:
            if id == 0:
                Rapport.objects.get(added=datetime.today(), user=request.user)
            else:
                Rapport.objects.get(id=id, user=request.user)

        except Rapport.DoesNotExist:
            return redirect("AddRapport")

        return render(
            request,
            self.template_name,
            {
                "page_title": self.page_title,
                "produits": Produit.objects.filter(
                    pays=request.user.userprofile.commune.wilaya.pays
                ),
                "wilayas": Wilaya.objects.filter(
                    pays=request.user.userprofile.commune.wilaya.pays
                ),
            },
        )

    def post(self, request, id=0):
        visite = Visite(
            rapport=self.get_the_rapport(id, request.user),
            priority=request.POST.get("priority"),
            observation=request.POST.get("observation"),
            medecin=get_medecin(id=request.POST.get("medecin")),
        )
        visite.save()
        try:
            for produit in request.POST.get("produits").split(","):
                produit_instance = Produit.objects.get(id=produit.split(":")[0])
                qtt = produit.split(":")[1]
            try:
                ProduitVisite.objects.create(
                    produit=produit_instance, visite=visite, qtt=qtt
                )
            except:
                pass
        except:
            pass

        visite.save()
        return redirect("HomeRapport")


class UpdateVisite(LoginRequiredMixin, TemplateView):
    template_name = "rapports/visites/update.html"
    page_title = "Modifier une visite"

    def get(self, request, id):
        visite = get_visite(id)
        if visite.rapport.is_updatable() and visite.rapport.user == request.user:
            return render(
                request,
                self.template_name,
                {
                    "page_title": self.page_title,
                    "visite": visite,
                    "produits": Produit.objects.filter(
                        pays=request.user.userprofile.commune.wilaya.pays
                    ),
                    "wilayas": Wilaya.objects.filter(
                        pays=request.user.userprofile.commune.wilaya.pays
                    ),
                },
            )
        else:
            return redirect("HomeRapport")

    def post(self, request, id):
        visite = get_visite(id)
        if visite.rapport.is_updatable() and visite.rapport.user == request.user:
            visite.observation = request.POST.get("observation")
            visite.medecin = get_medecin(id=request.POST.get("medecin"))
            visite.priority = request.POST.get("priority")
            visite.produits.clear()
            visite.save()
            try:
                ProduitVisite.objects.filter(visite=visite).delete()
                for produit in request.POST.get("produits").split(","):
                    produit_instance = Produit.objects.get(id=produit.split(":")[0])
                    qtt = produit.split(":")[1]
                    try:
                        ProduitVisite.objects.create(
                            produit=produit_instance, visite=visite, qtt=qtt
                        )
                    except:
                        pass
            except:
                pass

            visite.save()
        return redirect("HomeRapport")


class RapportCSV(LoginRequiredMixin, TemplateView):
    def get(self, request):
        return redirect("HomeRapport")

from django.db.models import Count
class RapportPDF(LoginRequiredMixin, TemplateView):
    def get(self, request, id=0):
        print(request)
        print("##### here baby ")
        commercial_input = request.GET.get("commercial", "").strip()
        # Vérification si commercial_input est un identifiant numérique
        if commercial_input.isdigit():
            # Récupération de l'utilisateur avec l'ID correspondant
            try:
                commercial_input = User.objects.get(id=commercial_input)
            except User.DoesNotExist:
                commercial_input = None  # Gérer le cas où l'utilisateur n'existe pas
        else:
            # Extraction du username avant le " - ", s'il existe
            if " - " in commercial_input:
                username = commercial_input.split(" - ")[0].strip()
            else:
                username = commercial_input
            # Si c'est un username, tu peux chercher l'utilisateur avec le username
            try:
                commercial_input = User.objects.get(username=username)
            except User.DoesNotExist:
                commercial_input = None  # Gérer le cas où l'utilisateur n'existe pas    
        date_start =""
        date_end=""
        if request.GET.get("mindate"):
            date_start = datetime.strptime(
                request.GET.get("mindate"), "%Y-%m-%d"
            ).date()
        else:
            date_start = datetime.strptime("2020-06-01", "%Y-%m-%d").date()
        family = request.GET.get("family")
        if request.GET.get("maxdate"):
            date_end = datetime.strptime(
                request.GET.get("maxdate"), "%Y-%m-%d"
            ).date()

        else:
            today = datetime.now()
            date_end = datetime.strptime(
                f"{today.year}-{today.month}-{today.day}", "%Y-%m-%d"
            ).date()
        usern = ""
        visited_commune_medecin_count= {}
        min_date=date_start
        max_date=date_end
        from_to = f"{min_date} Au {max_date}"
        non_visite_communes = {}
        all_plans = []
        delta_day = timedelta(days=1)
        print(str(commercial_input))   
        rapports=0
        if id == 0:
            rapports = rapport_list(request, 1)
            template_name = "rapports/rapports_pdf.html"
            print("id est 0")
        else:
            print("id n'est pas 0")
            rapports = [
                Rapport.objects.get(id=id),
            ]
            template_name = "rapports/single_rapport_pdf.html"

        print("here 1")
        

        #rapports_avec_moins_de_6_visites = rapports.annotate(nb_visites=Count("visite")).filter(nb_visites__lt=6)
        
        rapports_avec_moins_de_6_visites = [
            rapport for rapport in rapports
            if rapport.visite_set.count() < 6  # ou rapport.visites.count() selon ta relation
        ]
        
        rapports_avec_moins_de_6_visites = [
            rapport for rapport in rapports_avec_moins_de_6_visites
            if not Plan.objects.filter(
                user=rapport.user,
                day=rapport.added,
                valid_tasks=True
            ).exists()
        ]
        
        visites = Visite.objects.filter(rapport__in=rapports)
        medecins = Medecin.objects.filter(visite__in=visites).distinct()
        details = (
            Medecin.objects.filter(id__in=medecins.values("id"))
            .values("specialite")
            .annotate(dcount=Count("specialite"))
        )
        medecin_nbr = len(medecins)
        other_details = ""

        medical_specialties = ["Pharmacie", "Grossiste", "SuperGros"]
        medecin_nbr_medical = len(medecins.exclude(specialite__in=medical_specialties))
        medecin_nbr_commercial = len(medecins) - medecin_nbr_medical

        # medical_specialties_list = [detail["specialite"] for detail in details if detail["specialite"] not in medical_specialties]
        commercial_specialties = [
            f'({detail["dcount"]}) {detail["specialite"]}'
            for detail in details
            if detail["specialite"] in medical_specialties
        ]
        medical_specialties_l = [
            f'({detail["dcount"]}) {detail["specialite"]}'
            for detail in details
            if detail["specialite"] not in medical_specialties
        ]

        if request.GET.get("produit") and request.GET.get("produit") != "":
            prd_visites = visites.filter(produits__id=request.GET.get("produit"))
            prd_medecins = Medecin.objects.filter(
                id__in=prd_visites.values("medecin__id")
            )
            other_details = f" dont ({len(prd_visites)} visites et {len(prd_medecins)} medecins) contenant le produit"
        if family != '1':
            user_by_reg = User.objects.filter(userprofile__region=family)
 
        print("je suis avant le travail")
        commercial_input = request.GET.get("commercial", "").strip()
        if commercial_input:
            # Extraction du username avant le " - ", s'il existe
            # if " - " in commercial_input:
            #     username = commercial_input.split(" - ")[0].strip()
            # else:
            #     username = commercial_input
            if int(commercial_input) != 1000000:
                
                commercial = User.objects.get(id=commercial_input)
                commerciale_name = f"{commercial.first_name} {commercial.last_name}"
                

                # Filtrer l'utilisateur par son nom d'utilisateur
                user = User.objects.filter(id=commercial_input).first()
                usern = str(user)

                

                # Récupérer les plans de l'utilisateur
                if (
                    request.user.is_superuser
                    or request.user.userprofile.rolee == "Superviseur"
                    or request.user.userprofile.rolee == "CountryManager"
                ):
                    plans = Plan.objects.filter(
                    user=user, day__gte=min_date, day__lte=max_date,plantask__isnull=False
                    ).distinct()
                else:
                    plans = Plan.objects.filter(
                    user=request.user, day__gte=min_date, day__lte=max_date,plantask__isnull=False
                    ).distinct()

                # Filtrer les jours de travail (non free_day)
                plans = [p for p in plans if not p.free_day]

                # Obtenir les communes des plans visités
                visited_communes = set()
                for plan in plans:
                    visited_communes.update(
                        plan.communes.all()
                    )               # Récupérer toutes les communes liées au plan

                # Récupérer les médecins associés à l'utilisateur
                medecins = Medecin.objects.filter(
                    users=user
                )  # Filtrer les médecins associés à l'utilisateur

                # Extraire toutes les communes associées aux médecins
                all_communes = set(medecin.commune for medecin in medecins)

                # Dictionnaire pour stocker le nombre de médecins par commune visitée
                excluded_specialities = ["Pharmacie", "Grossiste", "SuperGros"]

                visited_commune_medecin_count = {
                    commune: Medecin.objects.filter(commune=commune, users=user)
                    .exclude(specialite__in=excluded_specialities)
                    .count()
                for commune in visited_communes
                }

                # Dictionnaire pour stocker le nombre de médecins et de pharmacies par commune non visitée
                non_visite_communes = {}

                # Identifier les communes non visitées pour le secteur médical et commercial
                for commune in all_communes:
                    if commune not in visited_communes:
                        medecin_count = (
                            Medecin.objects.filter(commune=commune, users=user)
                            .exclude(specialite__in=["Pharmacie", "Grossiste", "SuperGros"])
                            .count()
                        )
                        pharmacie_count = Medecin.objects.filter(
                            commune=commune, users=user, specialite="Pharmacie"
                        ).count()

                        # Ajouter au dictionnaire uniquement si on a des médecins ou des pharmacies
                        if medecin_count > 0 or pharmacie_count > 0:
                            non_visite_communes[commune] = {
                                "medecins": medecin_count,
                                "pharmacies": pharmacie_count,
                            }

                # Regrouper les plans par tranche de 5
                plans = [plans[i : i + 5] for i in range(0, len(plans), 5)]
                all_plans.append(plans)
            else:
                commercial = "TOUS"
                commerciale_name = "TOUS"

            # Orders created by the commercial
            if int(commercial_input) != 1000000:
                orders_commercial = Order.objects.filter(user=commercial)
            else:
                profile = UserProfile.objects.get(user=request.user)
                if profile.speciality_rolee == "Superviseur_regional":
                    orders_commercial = Order.objects.filter(user__in=profile.usersunder.all())
                else:
                    if family =='1':
                        orders_commercial = Order.objects.all()
                    else:
                        #user_by_reg = User.objects.filter(userprofile__region=family)
                        orders_commercial = Order.objects.filter(user__in=user_by_reg)
            
                
            orders_transferred_to = ""
            # Orders transferred to the commercial
            if int(commercial_input) != 1000000:
                orders_transferred_to = Order.objects.filter(touser=commercial)
            else:
                profile = UserProfile.objects.get(user=request.user)
                if profile.speciality_rolee == "Superviseur_regional":
                    orders_transferred_to = Order.objects.filter(user__in=profile.usersunder.all())
                else:
                    if family =="1":
                        orders_commercial = Order.objects.all()
                    else:
                        orders_transferred_to = Order.objects.filter(user__in=user_by_reg)

            # Orders transferred from the commercial
            if int(commercial_input) != 1000000:
                orders_transferred_from = Order.objects.filter(user=commercial).exclude(
                touser=commercial
                )
            else:
                profile = UserProfile.objects.get(user=request.user)
                if profile.speciality_rolee == "Superviseur_regional":
                    orders_transferred_from = Order.objects.filter(user__in=profile.usersunder.all())
                else:
                    if family == '1':
                        orders_transferred_from = Order.objects.all()
                    else:
                        orders_transferred_from = Order.objects.filter(user__in=user_by_reg)
            

            days = {
                "mon": 0,
                "tue": 1,
                "wed": 2,
                "thu": 3,
                "fri": 4,
                "sat": 5,
                "sun": 6,
            }

            dt = date_start
            et = date_end
            day_count = 0

            absence_dates = []
            if int(commercial_input) != 1000000:
                if commercial.userprofile.commune.wilaya.pays.nom == "algerie":
                    absences = Absence.objects.filter(
                    Q(date__range=[date_start, date_end]), user=commercial
                    )
                elif commercial.commune.wilaya.pays.nom == "Tunisie":
                    absences = Absence.objects.filter(
                    Q(date__range=[date_start, date_end]), user=commercial
                    )
            else:
                profile = UserProfile.objects.get(user=request.user)
                if profile.speciality_rolee == "Superviseur_regional":
                    absences = Absence.objects.filter(
                    Q(date__range=[date_start, date_end]), user__in=profile.usersunder.all()
                    )
                else:
                    if family == '1':
                        absences = Absence.objects.filter(
                            Q(date__range=[date_start, date_end])
                            )
                    else:
                        absences = Absence.objects.filter(Q(date__range=[date_start, date_end]), user__in=user_by_reg)

            #absence_dates = absences.values_list("date", flat=True)
            absence_dates = absences.values_list("user__first_name", "user__last_name", "date")
            absence = absences.count()
            print(str(absence))
        else:
            day_count = "/"
            absence = ""
            absence_dates = []
            conges_dates = []
        commercial_input = request.GET.get("commercial", "").strip()
        print("je suis de la ligne 558")
        if commercial_input:

            visites = Visite.objects.filter(rapport__in=rapports)
            medecins = Medecin.objects.filter(visite__in=visites)
            total_similarity_percentage = 0
            plan_count = 0
            specialites_a_exclure = ["Pharmacie", "Grossiste", "SuperGros"]
            # Filter Rapport objects

            # rapports = Rapport.objects.filter(
            #     added__month=date_start.month, added__year=date_end.year, user=commercial
            # )
            today = timezone.now().date()

            # Set default values for date_start and date_end
            date_start = datetime.strptime(
                    request.GET.get("mindate", "2020-06-01"), "%Y-%m-%d"
                ).date()
            today = datetime.now()
            date_end = datetime.strptime(
                    request.GET.get(
                        "maxdate", f"{today.year}-{today.month}-{today.day}"
                    ),
                    "%Y-%m-%d",
                ).date()
            if not date_start:
                date_start = today  # or use datetime.combine(today, datetime.min.time()) for full day
            if not date_end:
                date_end = today  # or use datetime.combine(today, datetime.max.time()) for full day

            print("je suis dans la ligne 589")
            # Filter the rapports
            if int(commercial_input) == 1000000:
                profile = UserProfile.objects.get(user=request.user)
                if profile.speciality_rolee == "Superviseur_regional":
                    pass
                    #rapports = Rapport.objects.filter(
                    #added__range=(date_start, date_end), user__in=profile.usersunder.all()
                    #)
                else:
                    pass
                    #rapports = Rapport.objects.filter(
                    #added__range=(date_start, date_end)
                    #)
            else:
                rapports = Rapport.objects.filter(
                added__range=(date_start, date_end), user=commercial
                )
            # Count plans and calculate total similarity percentage
            plan_count = rapports.count()
            valid_plan_count = 0
            total_similarity_percentage = 0
            if int(commercial_input) == 1000000:
                profile = UserProfile.objects.get(user=request.user)
                if profile.speciality_rolee == "Superviseur_regional":
                    #planss = Plan.objects.filter(
                    #day__month=date_start.month, day__year=date_start.year, user__in=profile.usersunder.all()
                    #)
                    planss = Plan.objects.filter(
                        day__range=[date_start, date_end],
                        user__in=profile.usersunder.all()
                    )
                else:
                    if family == '1':
                        planss = Plan.objects.filter(
                        day__month=date_start.month, day__year=date_start.year
                        )
                        planss = Plan.objects.filter(
                            day__range=[date_start, date_end],
                            #user=commercial
                        )
                    else:
                        #planss= Plan.objects.filter(day__month=date_start.month, day__year=date_start.year, user__in=user_by_reg)
                        planss = Plan.objects.filter(
                            day__range=[date_start, date_end],
                            user__in=user_by_reg
                        )

            else:
                #planss = Plan.objects.filter(
                #day__month=date_start.month, day__year=date_start.year, user=commercial
                #)
                planss = Plan.objects.filter(
                    day__range=[date_start, date_end],
                    user=commercial
                )

    
            for plan in planss:
                clients_list = plan.clients.all()
                if clients_list.count() == 0:
                    continue  # Ignore plans without clients
                valid_plan_count += 1
                #clients_list = plan.clients.exclude(
                #    specialite__in=specialites_a_exclure
                #)
                
                print(f"clients_list  {clients_list.count()}")
                o = Rapport.objects.filter(added=plan.day, user=plan.user)
                matching_doctors = (
                    Visite.objects.filter(
                        rapport__in=o, medecin__in=clients_list
                    )
                    .distinct()
                    .count()
                )
                print(f"matching_doctors  {matching_doctors}")
                #matching_doctors = (
                #    Visite.objects.filter(
                #        rapport__in=rapports, medecin__in=clients_list
                #    )
                #    #.exclude(medecin__specialite__in=specialites_a_exclure)
                #    .distinct()
                #    .count()
                #)
                #client_list_count = clients_list.count() or 1
                #similarity_percentage = (matching_doctors * 100) / client_list_count
                #total_similarity_percentage += similarity_percentage
                
                client_list_count = clients_list.count() or 1
                similarity_percentage = round((matching_doctors / client_list_count) * 100, 2)
                total_similarity_percentage += similarity_percentage
                # Calculate average similarity percentage
            average_similarity_percentage = (
                total_similarity_percentage / valid_plan_count if valid_plan_count > 0 else 0
            )

            if not average_similarity_percentage:
                average_similarity_percentage = 0

            if average_similarity_percentage > 100:
                average_similarity_percentage = 100

            # GETTING DISTINCT MEDICAL COUNT
            medecin_nbr = len(medecins) - len(
                medecins.filter(specialite__in=["Pharmacie", "Grossiste", "SuperGros"])
            )
            # Assuming 'commercial' is a list of User instances
            #total_medecin_count = (
            #    Medecin.objects.filter(users=commercial).exclude(
            #        specialite__in=["Pharmacie", "Grossiste", "SuperGros"]
            #    )
            #).count()
            if int(commercial_input) == 1000000:
                pass
                #total_medecin_count = (
                #Medecin.objects.all().exclude(
                #    specialite__in=["Pharmacie", "Grossiste", "SuperGros"]
                #)
                #).count()
            else:
                pass
                #total_medecin_count = (
                #Medecin.objects.filter(users=commercial).exclude(
                #    specialite__in=["Pharmacie", "Grossiste", "SuperGros"]
                #)
                #).count()
            #total_commercial_count = (
            #    Medecin.objects.filter(
            #        users=commercial,
            #        specialite__in=["Pharmacie", "Grossiste", "SuperGros"],
            #    )
            #).count()
            if int(commercial_input) == 1000000:
                pass
                #total_commercial_count = (
                #Medecin.objects.filter(
                #    specialite__in=["Pharmacie", "Grossiste", "SuperGros"],
                #)
                #).count()
            else:
                pass
                #total_commercial_count = (
                #Medecin.objects.filter(
                #    users=commercial,
                #    specialite__in=["Pharmacie", "Grossiste", "SuperGros"],
                #)
                #).count()

            print("je suis dans la ligne 674")
            # GETTING DISTINCT COMMERCIAL COUNT
            commercial_nbr = len(
                medecins.filter(specialite__in=["Pharmacie", "Grossiste", "SuperGros"])
            )
            # GETTING ALL COMMERCIAL COUNT
            medecin_commercial = len(
                medecins.filter(specialite__in=["Pharmacie", "Grossiste", "SuperGros"])
            )
            medecin_commercial_client = len(
                medecins.filter(
                    specialite__in=["Pharmacie", "Grossiste", "SuperGros"]
                ).distinct()
            )
            # GETTING SPECIALITYS FOR ALL MEDECINS
            details = (
                Medecin.objects.filter(id__in=medecins.values("id"))
                .values("specialite")
                .annotate(dcount=Count("specialite"))
            )
            # GETTING SPECIALITYS FOR DISTINCT MEDECINS

            visited_communes = set()
            other_details += f"<b style='color:black; font-size:19px'>Régions visités / المناطق المزاره :</b></br>"
            for visite in visites:
                visited_communes.add(
                    (
                        visite.medecin.commune.wilaya.nom
                        + "/"
                        + visite.medecin.commune.nom
                        + " - "
                    )
                )

            other_details += f"<span style='color:black;font-size:13px'>{', '.join(visited_communes)}</span>"

            other_details += "</br> </br>"

            details_distinct = (
                Medecin.objects.filter(id__in=medecins.values("id"))
                .distinct()
                .values("specialite")
                .annotate(dcount=Count("specialite"))
            )

            other_details += f"""                    <div class="row mb-2">
          <div class="col-md-6 d-flex"><h5 style="color:black"><b>Total des visites / مجموع الزيارات :</b></h5></div>
          <div class="col-md-6 text-right"><h5 style="color:green">{len(medecins)}</h5></div>
        </div>"""

            # TOTAL DES VISITES MED/COM SPECIALITIES

            # Displaying specialties
            print("je suis dans la ligne 727")
            # TOTAL DES CLIENTS MED/COM SPECIALITIES
            other_specialties = []
            end_specialties = []
            for detail in details_distinct:
                if detail["specialite"] in ["SuperGros", "Grossiste", "Pharmacie"]:
                    end_specialties.append(detail)
                else:
                    other_specialties.append(detail)
            sorted_specialties = other_specialties + end_specialties
            print("je suis dans la ligne 737")
            # Displaying specialties
            medical_specialties = [
                detail
                for detail in sorted_specialties
                if detail["specialite"] not in ["SuperGros", "Grossiste", "Pharmacie"]
            ]
            commercial_specialties = [
                detail
                for detail in sorted_specialties
                if detail["specialite"] in ["SuperGros", "Grossiste", "Pharmacie"]
            ]
            medical_specialties_sorted = sorted(
                medical_specialties, key=lambda x: x["dcount"], reverse=True
            )
            print("je suis dans la ligne 752")
            other_details += f"""
            <div class="row mb-2">
                <div class="col-md-6 d-flex">
                    <h5 style="color:black"><b>Total des visites Medical / مجموع زيارات الاطباء:</b></h5>
                </div>
                <div class="col-md-6 text-right">
                    <h5 style="color:black"><span style="color:green">{medecin_nbr}</span></h5>
                </div>
            </div>
            <div class="row mb-2">
                <div class="col-md-12">
                    {" ".join(
                        [f'<span style="color:black; font-size:14px">({detail["dcount"]}) {detail["specialite"]}</span>'
                         for detail in medical_specialties_sorted]
                    )}
                </div>
            </div>
            """
            other_details += f"</span>"
            other_details += f"<span style='margin-left: 10px;color:black'>"

            # Assuming commercial_specialties is a list of dictionaries
            commercial_specialties_sorted = sorted(
                commercial_specialties, key=lambda x: x["dcount"], reverse=True
            )
            print("je suis dans la ligne 778")
            # Generate the HTML with sorted specialties
            other_details += f"""
            <div class="row mb-2">
                <div class="col-md-6 d-flex">
                    <h5 style="color:black"><b>Total des visites Commercial / مجموع زيارات الكومرسيال :</b></h5>
                </div>
                <div class="col-md-6 text-right">
                    <h5 style="color:black"><span style="color:green">{medecin_commercial_client}</span></h5>
                </div>
            </div>
            <div class="row mb-2">
                <div class="col-md-12">
                    {" ".join(
                        [f'<span style="color:black; font-size:14px">({detail["dcount"]}) {detail["specialite"]}</span>'
                         for detail in commercial_specialties_sorted]
                    )}
                </div>
            </div>
            """
            print("je suis dans la ligne 798")
            other_details += f"</span>"
            # PRODUITS PRESENTES MEDICAL
            # PRODUITS PRESENTES MEDICAL
            other_details += "<h5><b> Total des présentations médicale / عدد مرات  تقديم المنتج للاطباء : </b></h5>"
            product_info = {}
            excluded_specialties = ["Pharmacie", "Grossiste", "Supergros"]

            # Loop through all products
            for p in Produit.objects.all():
                # Count visits excluding the specified specialties
                len_visits = len(
                    visites.exclude(
                        medecin__specialite__in=excluded_specialties
                    ).filter(produits__id=p.id)
                )
                product_info[p.nom] = len_visits
            print("je suis dans la ligne 815")
            # Sort products by the number of visits in descending order
            sorted_products = sorted(
                product_info.items(), key=lambda x: x[1], reverse=True
            )

            count_med = 0
            for product, len_visits in sorted_products:
                if len_visits > 0:
                    product_string = f"<span style='color:black;font-size:13px'>({product} : <span style='color:green'>{len_visits} fois</span>)</span>"
                    other_details += product_string + " "
                    count_med += 1

            # Debugging: Print the product_info dictionary to verify counts
            print(product_info)

            # PRODUITS PRESENTES COMMERCIAL
            other_details += "</br><h5><b>Total des présentations commerciale / عدد مرات تقديم المنتج في للكومرسيال   : </b></h5>"
            product_info = {}
            for p in Produit.objects.all():
                included_specialties = ["Pharmacie", "Grossiste", "Supergros"]
                len_visits = len(
                    visites.filter(medecin__specialite__in=included_specialties).filter(
                        produits__id=p.id
                    )
                )
                product_info[p.nom] = len_visits
            sorted_products = sorted(
                product_info.items(), key=lambda x: x[1], reverse=True
            )
            count = 0
            print("je suis dans la ligne 846")
            for product, len_visits in sorted_products:
                if len_visits > 0:
                    product_string = f"<span style='color:black;font-size:13px'>({product} : <span style='color:green'>{len_visits} fois</span> )</span>"
                    other_details += product_string + " "
                    count += 1

            # if count % 3 > 0:
            other_details += "<br/>"

            rapports_count = rapports.count()
            if int(commercial_input) == 1000000:
                profile = UserProfile.objects.get(user=request.user)
                if profile.speciality_rolee == "Superviseur_regional":
                    leaves = Leave.objects.filter(
                        user__in=profile.usersunder.all(),
                    start_date__lte=date_end,  # Leave starts before or on the end date of the filter
                    end_date__gte=date_start,
                    ).exclude(
                        end_date=date_end
                    ).order_by(F("start_date").asc(nulls_last=True))
                else:
                    if family =='1':
                        leaves = Leave.objects.filter(
                        start_date__lte=date_end,  # Leave starts before or on the end date of the filter
                        end_date__gte=date_start,
                        ).exclude(
                            end_date=date_end
                        ).order_by(F("start_date").asc(nulls_last=True))
                    else:
                        leaves = Leave.objects.filter(
                            user__in=user_by_reg,
                            start_date__lte=date_end,  # Leave starts before or on the end date of the filter
                            end_date__gte=date_start,
                            ).exclude(
                                end_date=date_end
                            ).order_by(F("start_date").asc(nulls_last=True))
            else:
                leaves = Leave.objects.filter(
                user=commercial,
                start_date__lte=date_end,  # Leave starts before or on the end date of the filter
                end_date__gte=date_start,
                ).exclude(
                    end_date=date_end
                ).order_by(F("start_date").asc(nulls_last=True))

            print("leaves : " + str(leaves))
            dt = date_start
            et = date_end
            if int(commercial_input) != 1000000:
                while dt <= date_end:
                    if int(commercial_input) != 1000000:
                        if commercial.userprofile.commune.wilaya.pays.nom == "algerie":
                            if dt.weekday() != days["fri"] and dt.weekday() != days["sat"]:
                                day_count += 1
                        elif commercial.commune.wilaya.pays.nom == "Tunisie":
                            if dt.weekday() != days["sat"] and dt.weekday() != days["sun"]:
                                day_count += 1

                    dt += delta_day
            else:
                while dt <= date_end:
                    if dt.weekday() != days["fri"] and dt.weekday() != days["sat"]:
                        day_count += 1
                    dt += delta_day
                profile = UserProfile.objects.get(user=request.user)
                if profile.speciality_rolee == "Superviseur_regional":
                    total_rapp = profile.usersunder.all().count()
                else:
                    if family == '1':
                        total_rapp = UserProfile.objects.filter(speciality_rolee__in=["Medico_commercial", "Commercial", "Superviseur_regional","Superviseur_national","CountryManager"], hidden=False, user__is_active=True).count()
                    else:
                        total_rapp = UserProfile.objects.filter(speciality_rolee__in=["Medico_commercial", "Commercial", "Superviseur_regional","Superviseur_national","CountryManager"], hidden=False, user__is_active=True, region=family).count()
                day_count = day_count * total_rapp

            # Prepare leaves data for the context
            print("je suis dans la ligne 884")
            leaves_data = [
                {
                    "start_date": f"{leave.user.first_name} {leave.user.last_name} - {leave.start_date}",
                    "end_date": leave.end_date,
                    "leave_type": leave.leave_type.description,  # Accessing the leave type description
                }
                for leave in leaves
            ]
            
            #Les rapports vides
            print(f"Je suis dans la ligne 966 et voici les rapports vides {rapports_avec_moins_de_6_visites}")
            rapports_vides = []
            rapports_vides = [
                {
                    "infos": f"{rap.user.first_name} {rap.user.last_name} {rap.added.strftime('%d/%m/%Y')}",
                }
                for rap in rapports_avec_moins_de_6_visites
            ]
            # Convertir en datetime.datetime
            date_start = datetime.combine(date_start, time.min)
            date_end = datetime.combine(date_end, time.max)

            # S'assurer que ce sont des objets "aware"
            if timezone.is_naive(date_start):
                date_start = timezone.make_aware(date_start)

            if timezone.is_naive(date_end):
                date_end = timezone.make_aware(date_end)
            a = []
            b = []
            c = []
            if int(commercial_input) == 1000000:
                print("je suis dans la ligne 906")
                profile = UserProfile.objects.get(user=request.user)
                if profile.speciality_rolee == "Superviseur_regional":
                    orders = Order.objects.filter(
                    added__range=(date_start, date_end),
                    user__in=profile.usersunder.all()
                    )
                    for user_undr in profile.usersunder.all():
                        ords = Order.objects.filter(
                            user=user_undr, added__range=(date_start, date_end)
                        )
                        check = 0
                        c = []
                        for o in ords:
                            item = OrderItem.objects.filter(order=o)
                            check = 0
                            for i in item:
                                for t in c:
                                    if t['produit'] == i.produit:
                                        t['qtt'] = t['qtt'] + i.qtt
                                        check = 1
                                if check == 0:
                                    new = {
                                        "produit":i.produit,
                                        "qtt":i.qtt
                                    }
                                    c.append(new)
                                    
                        details= {
                            "User": f"{user_undr.last_name} {user_undr.first_name}",
                            "Nombre_Orders": ords.count(),
                            "c" : c
                        }
                        if ords.count() == 0:
                            b.append(details)
                        else:
                            a.append(details)
                else:
                    if family == '1':
                        orders = Order.objects.filter(
                        added__range=(date_start, date_end)
                        )
                        usrs = User.objects.filter(
                        userprofile__speciality_rolee__in=["Commercial", "Medico_commercial"]
                        ).exclude(id__in=leaves) \
                         .exclude(userprofile__hidden=True) \
                         .exclude(userprofile__is_human=False) \
                         .exclude(userprofile__speciality_rolee__in=["Office","chargé_de_communication","gestionnaire_de_stock","Finance_et_comptabilité","Admin"]) \
                         .exclude(userprofile__family__in=["production"])
                    else:
                        orders = Order.objects.filter(
                        added__range=(date_start, date_end), user__in=user_by_reg
                        )
                        usrs = User.objects.filter(
                        userprofile__speciality_rolee__in=["Commercial", "Medico_commercial"],
                        userprofile__region=family
                        ).exclude(id__in=leaves) \
                         .exclude(userprofile__hidden=True) \
                         .exclude(userprofile__is_human=False) \
                         .exclude(userprofile__speciality_rolee__in=["Office","chargé_de_communication","gestionnaire_de_stock","Finance_et_comptabilité","Admin"]) \
                         .exclude(userprofile__family__in=["production"])
                    
                    for usr in usrs:
                        ords = Order.objects.filter(
                            user=usr, added__range=(date_start, date_end)
                        )
                        check = 0
                        c = []
                        for o in ords:
                            item = OrderItem.objects.filter(order=o)
                            for i in item:
                                check = 0
                                for t in c:
                                    if t['produit'] == i.produit:
                                        t['qtt'] = t['qtt'] + i.qtt
                                        check = 1
                                if check == 0:
                                    new = {
                                        "produit":i.produit,
                                        "qtt":i.qtt
                                    }
                                    c.append(new)
                        details= {
                            "User": f"{usr.last_name} {usr.first_name}",
                            "Nombre_Orders": ords.count(),
                            "c" : c
                        }
                        if ords.count() == 0:
                            b.append(details)
                        else:
                            a.append(details)
            else:
                orders = Order.objects.filter(
                user=commercial, added__range=(date_start, date_end)
                )
                details= {
                            "User": commercial,
                            "Nombre_Orders": orders.count()
                        }
                a.append(details)

            print("orders " + str(len(orders)))

            # 1. Compter les commandes avec pharmacie et grossiste non vides
            orders_with_pharmacy_and_gros = orders.filter(
                pharmacy__isnull=False, gros__isnull=False
            )
            count_orders_with_pharmacy_and_gros = orders_with_pharmacy_and_gros.count()
            print("orders " + str(count_orders_with_pharmacy_and_gros))

            product_qty_pharmacy_and_gros = {}
            for order in orders_with_pharmacy_and_gros:
                # Obtenir les OrderItems associés à chaque order
                order_items = OrderItem.objects.filter(order=order)

                for item in order_items:
                    product_name = item.produit.nom  # Nom du produit
                    qty = item.qtt  # Quantité

                    # Ajouter au dictionnaire ou mettre à jour la quantité existante
                    if product_name in product_qty_pharmacy_and_gros:
                        product_qty_pharmacy_and_gros[product_name] += qty
                    else:
                        product_qty_pharmacy_and_gros[product_name] = qty
            #product_qty_pharmacy_and_gros = dict(sorted(product_qty_pharmacy_and_gros.items(), key=lambda item: item[1], reverse=True))
            # 2. Compter les commandes avec grossiste et super gros non vides
            print("je suis dans la ligne 927")
            orders_with_gros_and_super_gros = orders.filter(
                gros__isnull=False, super_gros__isnull=False
            )
            count_orders_with_gros_and_super_gros = (
                orders_with_gros_and_super_gros.count()
            )

            product_qty_gros_and_super_gros = {}

            for order in orders_with_gros_and_super_gros:
                order_items = OrderItem.objects.filter(order=order)

                for item in order_items:
                    product_name = item.produit.nom
                    qty = item.qtt

                    if product_name in product_qty_gros_and_super_gros:
                        product_qty_gros_and_super_gros[product_name] += qty
                    else:
                        product_qty_gros_and_super_gros[product_name] = qty
            #product_qty_gros_and_super_gros = dict(sorted(product_qty_gros_and_super_gros.items(), key=lambda item: item[1], reverse=True))
            print(
                "count_orders_with_pharmacy_and_gros "
                + str(product_qty_pharmacy_and_gros)
            )
            print(
                "count_orders_with_gros_and_super_gros "
                + str(product_qty_gros_and_super_gros)
            )

            # Création d'un ensemble de produits uniques
            all_products = set(product_qty_pharmacy_and_gros.keys()).union(
                product_qty_gros_and_super_gros.keys()
            )

            # Conversion en liste pour faciliter l'itération dans le template
            all_products = list(all_products)

            unique_products = set(product_qty_pharmacy_and_gros.keys()).union(
                set(product_qty_gros_and_super_gros.keys())
            )
            print("je suis dans la ligne 969")
            print(len(visites))
            print(len(medecins))
            print(other_details)
            context = {
                "visites": len(visites),
                "clients": len(medecins),
                "details": other_details,
                "orders_per_user": a,
                "user_with_no_orders":b,
                # "rapports": rapports,
                "rapports_count": rapports_count,
                "rapports_vides":rapports_vides,
                "days": day_count,
                "orders_commercial": orders_commercial,
                "orders_transferred_to": orders_transferred_to,
                "orders_transferred_from": orders_transferred_from,
                "product_qty_gros_and_super_gros": product_qty_gros_and_super_gros,
                "product_qty_pharmacy_and_gros": product_qty_pharmacy_and_gros,
                "unique_products": list(unique_products),
                "count_orders_with_pharmacy_and_gros": count_orders_with_pharmacy_and_gros,
                "count_orders_with_gros_and_super_gros": count_orders_with_gros_and_super_gros,
                "orders_with_pharmacy_and_gros": orders_with_pharmacy_and_gros,
                "orders_with_gros_and_super_gros": orders_with_gros_and_super_gros,
                "absence": absence,
                "average_similarity_percentage": average_similarity_percentage,
                "commerciale_name": commerciale_name,
                "absence_dates": absence_dates,
                "other_details": other_details,
                "leaves": leaves_data,
                # "all_products": all_products,
                "all_plans": all_plans,
                "user": usern,
                "from_to": from_to,
                "periode": today,
                "non_visite_communes": non_visite_communes,  # Retourne uniquement les communes non visitées avec les comptes
                "visited_commune_medecin_count": dict(
                    visited_commune_medecin_count
                ),
            }

            if "IMAGE" in request.path:
                template_name = "rapports/rapports_images.html"

            return render(request, template_name, context)
        else:

            print("------ not commercial input ------")

            # Filter visites and medecins once
            visites = Visite.objects.filter(rapport__in=rapports).select_related(
                "medecin__commune__wilaya"
            )
            medecins = Medecin.objects.filter(visite__in=visites).distinct()

            # Count specialties efficiently
            specialites_count = medecins.values("specialite").annotate(
                dcount=Count("specialite")
            )
            print("je suis dans la ligne 727")
            # Separate medical and commercial specialties
            medical_specialties = ["Pharmacie", "Grossiste", "SuperGros"]
            medecin_nbr_medical = medecins.exclude(
                specialite__in=medical_specialties
            ).count()
            medecin_nbr_commercial = medecins.filter(
                specialite__in=medical_specialties
            ).count()

            # Filter based on product selection
            if produit_id := request.GET.get("produit"):
                prd_visites = visites.filter(produits__id=produit_id)
                prd_medecins = Medecin.objects.filter(
                    id__in=prd_visites.values("medecin__id")
                )
                other_details = f" dont ({prd_visites.count()} visites et {prd_medecins.count()} medecins) contenant le produit"
            else:
                other_details = ""

            # Handle absence calculations efficiently
            commercial_input = request.GET.get("commercial", "").strip()
            print(f"iciiiii com inp {commercial_input} et le type {type(commercial_input)}")
            if commercial_input == 1000000:
                print("commercial egale a 1000000")
                pass
            if commercial_input and int(commercial_input) != 1000000:
                username = (
                    commercial_input.split(" - ")[0].strip()
                    if " - " in commercial_input
                    else commercial_input
                )
                commercial = User.objects.get(username=username)

                date_start = datetime.strptime(
                    request.GET.get("mindate", "2020-06-01"), "%Y-%m-%d"
                ).date()
                today = datetime.now()
                date_end = datetime.strptime(
                    request.GET.get(
                        "maxdate", f"{today.year}-{today.month}-{today.day}"
                    ),
                    "%Y-%m-%d",
                ).date()

                # Absence logic with filters based on country and weekdays
                days = {
                    "mon": 0,
                    "tue": 1,
                    "wed": 2,
                    "thu": 3,
                    "fri": 4,
                    "sat": 5,
                    "sun": 6,
                }
                absence_dates = []
                delta_day = timedelta(days=1)
                country = commercial.userprofile.commune.wilaya.pays.nom
                while date_start <= date_end:
                    if (
                        country == "algerie"
                        and date_start.weekday() not in [days["fri"], days["sat"]]
                    ) or (
                        country == "Tunisie"
                        and date_start.weekday() not in [days["sat"], days["sun"]]
                    ):
                        if not Rapport.objects.filter(
                            added=date_start, user=commercial
                        ).exists():
                            absence_dates.append(date_start)
                    date_start += delta_day

                day_count = len(absence_dates)
                absence = day_count - len(rapports)
            else:
                day_count, absence, absence_dates = "/", "", []

            # Gather region visits
            visited_communes = {
                f"{visite.medecin.commune.wilaya.nom}/{visite.medecin.commune.nom}"
                for visite in visites
            }
            other_details += (
                f"<b>Régions visitées ce jour :</b> {', '.join(visited_communes)}<br>"
            )

            # Display medical and commercial specialties
            sorted_specialties = sorted(
                specialites_count, key=lambda x: x["specialite"] in medical_specialties
            )
            medical_specialties_list = [
                f"({detail['dcount']}) {detail['specialite']}"
                for detail in sorted_specialties
                if detail["specialite"] not in medical_specialties
            ]
            commercial_specialties_list = [
                f"({detail['dcount']}) {detail['specialite']}"
                for detail in sorted_specialties
                if detail["specialite"] in medical_specialties
            ]

            other_details += f"<b style='font-size:15px;color:grey'>Total des visites aujourd'hui:</b> <b style='color:green'>({len(medecins)})</b><br>"
            other_details += f"<b style='font-size:15px;color:green'>({medecin_nbr_medical}) Médical:</b> {' '.join(medical_specialties_list)}<br>"
            other_details += f"<b style='font-size:14px;color:green'>({medecin_nbr_commercial}) Commercial:</b> {' '.join(commercial_specialties_list)}<br>"

            # Gather product presentation data
            product_visits = defaultdict(int)
            for visite in visites:
                for product in visite.produits.all():
                    product_visits[product.nom] += 1

            # Sort and display product visits
            sorted_product_visits = sorted(
                product_visits.items(), key=lambda x: x[1], reverse=True
            )
            other_details += "<b style='font-size:16px'><span style='color:red'>Medical</span> Produits présentés aujourd'hui:</b><br>"
            other_details += (
                " ".join(
                    [
                        f"<b>({product}: <span style='color:green'>{count} fois</span>)</b>"
                        for product, count in sorted_product_visits
                        if count > 0
                    ]
                )
                + "<br>"
            )
            print("je suis a la ligne 1435")
            # Final context
            context = {
                "visites": visites.count(),
                "clients": medecins.count(),
                "details": other_details,
                "rapports": rapports,
                "days": day_count,
                "absence": absence,
                "absence_dates": absence_dates,
                "other_details": other_details,
                "all_plans": all_plans,
                "user": usern,
                "from_to": from_to,
                "periode": today,
                "non_visite_communes": non_visite_communes,  # Retourne uniquement les communes non visitées avec les comptes
                "visited_commune_medecin_count": dict(
                    visited_commune_medecin_count
                ),
            }

        if "IMAGE" in request.path:
            template_name = "rapports/rapports_images.html"

        return render(request, template_name, context)

        rendered = render_to_string(template_name, context)

        htmldoc = HTML(string=rendered, base_url="http://app.liliumpharma.com")
        return HttpResponse(htmldoc.write_pdf(), content_type="application/pdf")

        # return HttpResponse(pdf, content_type='application/pdf')
#la classe de rayan avec chatgpt
# class RapportPDF(LoginRequiredMixin, TemplateView):
#     def get(self, request, id=0):

#         commercial_input = request.GET.get("commercial", "").strip()
#         # Vérification si commercial_input est un identifiant numérique
#         if commercial_input.isdigit():
#             # Récupération de l'utilisateur avec l'ID correspondant
#             try:
#                 commercial_input = User.objects.get(id=commercial_input)
#             except User.DoesNotExist:
#                 commercial_input = None  # Gérer le cas où l'utilisateur n'existe pas
#         else:
#             # Extraction du username avant le " - ", s'il existe
#             if " - " in commercial_input:
#                 username = commercial_input.split(" - ")[0].strip()
#             else:
#                 username = commercial_input
#             # Si c'est un username, tu peux chercher l'utilisateur avec le username
#             try:
#                 commercial_input = User.objects.get(username=username)
#             except User.DoesNotExist:
#                 commercial_input = None  # Gérer le cas où l'utilisateur n'existe pas    

#         if id == 0:
#             rapports = rapport_list(request, 1)
#             template_name = "rapports/rapports_pdf.html"
#             print("id est 0")
#         else:
#             print("id n'est pas 0")
#             rapports = [
#                 Rapport.objects.get(id=id),
#             ]
#             template_name = "rapports/single_rapport_pdf.html"

        

#         #rapports_avec_moins_de_6_visites = rapports.annotate(nb_visites=Count("visite")).filter(nb_visites__lt=6)
        
        
        
#         visites = Visite.objects.filter(rapport__in=rapports)
#         medecins = Medecin.objects.filter(visite__in=visites).distinct()
#         details = (
#             Medecin.objects.filter(id__in=medecins.values("id"))
#             .values("specialite")
#             .annotate(dcount=Count("specialite"))
#         )
#         medecin_nbr = len(medecins)
#         other_details = ""

#         medical_specialties = ["Pharmacie", "Grossiste", "SuperGros"]
#         medecin_nbr_medical = len(medecins.exclude(specialite__in=medical_specialties))
#         medecin_nbr_commercial = len(medecins) - medecin_nbr_medical

#         # medical_specialties_list = [detail["specialite"] for detail in details if detail["specialite"] not in medical_specialties]
#         commercial_specialties = [
#             f'({detail["dcount"]}) {detail["specialite"]}'
#             for detail in details
#             if detail["specialite"] in medical_specialties
#         ]
#         medical_specialties_l = [
#             f'({detail["dcount"]}) {detail["specialite"]}'
#             for detail in details
#             if detail["specialite"] not in medical_specialties
#         ]

#         if request.GET.get("produit") and request.GET.get("produit") != "":
#             prd_visites = visites.filter(produits__id=request.GET.get("produit"))
#             prd_medecins = Medecin.objects.filter(
#                 id__in=prd_visites.values("medecin__id")
#             )
#             other_details = f" dont ({len(prd_visites)} visites et {len(prd_medecins)} medecins) contenant le produit"

#         commercial_input = request.GET.get("commercial", "").strip()
#         if commercial_input:
#             # Extraction du username avant le " - ", s'il existe
#             # if " - " in commercial_input:
#             #     username = commercial_input.split(" - ")[0].strip()
#             # else:
#             #     username = commercial_input
#             if int(commercial_input) != 1000000:
#                 commercial = User.objects.get(id=commercial_input)
#                 commerciale_name = f"{commercial.first_name} {commercial.last_name}"
#                 print("------------->>>>>>> "+str(commerciale_name))
#             else:
#                 commercial = "TOUS"
#                 commerciale_name = "TOUS"

#             # Orders created by the commercial
#             if int(commercial_input) != 1000000:
#                 orders_commercial = Order.objects.filter(user=commercial)
#             else:
#                 profile = UserProfile.objects.get(user=request.user)
#                 if profile.speciality_rolee == "Superviseur_regional":
#                     orders_commercial = Order.objects.filter(user__in=profile.usersunder.all())
#                 else:
#                     orders_commercial = Order.objects.all()
            
                
#             orders_transferred_to = ""
#             # Orders transferred to the commercial
#             if int(commercial_input) != 1000000:
#                 orders_transferred_to = Order.objects.filter(touser=commercial)
#             else:
#                 profile = UserProfile.objects.get(user=request.user)
#                 if profile.speciality_rolee == "Superviseur_regional":
#                     orders_transferred_to = Order.objects.filter(user__in=profile.usersunder.all())
#                 else:
#                     orders_commercial = Order.objects.all()

#             # Orders transferred from the commercial
#             if int(commercial_input) != 1000000:
#                 orders_transferred_from = Order.objects.filter(user=commercial).exclude(
#                 touser=commercial
#                 )
#             else:
#                 profile = UserProfile.objects.get(user=request.user)
#                 if profile.speciality_rolee == "Superviseur_regional":
#                     orders_transferred_from = Order.objects.filter(user__in=profile.usersunder.all())
#                 else:
#                     orders_transferred_from = Order.objects.all()

#             if request.GET.get("mindate"):
#                 date_start = datetime.strptime(
#                     request.GET.get("mindate"), "%Y-%m-%d"
#                 ).date()
#             else:
#                 date_start = datetime.strptime("2020-06-01", "%Y-%m-%d").date()

#             if request.GET.get("maxdate"):
#                 date_end = datetime.strptime(
#                     request.GET.get("maxdate"), "%Y-%m-%d"
#                 ).date()

#             else:
#                 today = datetime.now()
#                 date_end = datetime.strptime(
#                     f"{today.year}-{today.month}-{today.day}", "%Y-%m-%d"
#                 ).date()

#             delta_day = timedelta(days=1)

#             days = {
#                 "mon": 0,
#                 "tue": 1,
#                 "wed": 2,
#                 "thu": 3,
#                 "fri": 4,
#                 "sat": 5,
#                 "sun": 6,
#             }

#             dt = date_start
#             et = date_end
#             day_count = 0

#             absence_dates = []
#             if int(commercial_input) != 1000000:
#                 if commercial.userprofile.commune.wilaya.pays.nom == "algerie":
#                     absences = Absence.objects.filter(
#                     Q(date__range=[date_start, date_end]), user=commercial
#                     )
#                 elif commercial.commune.wilaya.pays.nom == "Tunisie":
#                     absences = Absence.objects.filter(
#                     Q(date__range=[date_start, date_end]), user=commercial
#                     )
#             else:
#                 profile = UserProfile.objects.get(user=request.user)
#                 if profile.speciality_rolee == "Superviseur_regional":
#                     absences = Absence.objects.filter(
#                     Q(date__range=[date_start, date_end]), user__in=profile.usersunder.all()
#                     )
#                 else:
#                     absences = Absence.objects.filter(
#                         Q(date__range=[date_start, date_end])
#                         )

#             #absence_dates = absences.values_list("date", flat=True)
#             absence_dates = absences.values_list("user__first_name", "user__last_name", "date")
#             absence = absences.count()
#             print(str(absence))
#         else:
#             day_count = "/"
#             absence = ""
#             absence_dates = []
#             conges_dates = []
#             commercial_input = request.GET.get("commercial", "").strip()
#             print("je suis de la ligne 558")

#             print ("||||||||||||||||||||")
#             print ("||||||||||||||||||||")
#             print ("||||||||||||||||||||")
#             print ("||||||||||||||||||||")
#             print ("||||||||||||||||||||")

#         if commercial_input:

#             visites = Visite.objects.filter(rapport__in=rapports)
#             medecins = Medecin.objects.filter(visite__in=visites)
#             total_similarity_percentage = 0
#             plan_count = 0
#             specialites_a_exclure = ["Pharmacie", "Grossiste", "SuperGros"]
#             # Filter Rapport objects

#             # rapports = Rapport.objects.filter(
#             #     added__month=date_start.month, added__year=date_end.year, user=commercial
#             # )
#             today = timezone.now().date()

#             # Set default values for date_start and date_end
#             date_start = datetime.strptime(
#                     request.GET.get("mindate", "2020-06-01"), "%Y-%m-%d"
#                 ).date()
#             today = datetime.now()
#             date_end = datetime.strptime(
#                     request.GET.get(
#                         "maxdate", f"{today.year}-{today.month}-{today.day}"
#                     ),
#                     "%Y-%m-%d",
#                 ).date()
#             if not date_start:
#                 date_start = today  # or use datetime.combine(today, datetime.min.time()) for full day
#             if not date_end:
#                 date_end = today  # or use datetime.combine(today, datetime.max.time()) for full day

#             print("je suis dans la ligne 589")
#             # Filter the rapports
#             if int(commercial_input) == 1000000:
#                 profile = UserProfile.objects.get(user=request.user)
#                 if profile.speciality_rolee == "Superviseur_regional":
#                     rapports = Rapport.objects.filter(
#                     added__range=(date_start, date_end), user__in=profile.usersunder.all()
#                     )
#                 else:
#                     rapports = Rapport.objects.filter(
#                     added__range=(date_start, date_end)
#                     )
#             else:
#                 rapports = Rapport.objects.filter(
#                 added__range=(date_start, date_end), user=commercial
#                 )

#             rapports_vides = []
#             print("les rapports selon la selection")
#             print(rapports)
#             rapports_avec_moins_de_6_visites = [
#                 rapport for rapport in rapports
#                     if rapport.visite_set.count() < 6  # ou rapport.visites.count() selon ta relation
#             ]
#             print("les rapport moin de 6 visistes avant le filter")
#             print(rapports_avec_moins_de_6_visites)
            
#             rapports_avec_moins_de_6_visites = [
#                 rapporta for rapporta in rapports_avec_moins_de_6_visites
#                     if not Plan.objects.filter(
#                         user=rapporta.user,
#                         day=rapporta.added,
#                         valid_tasks=True
#                     ).exists()
#             ]
#             print("les rapport moin de 6 visistes")
#             print(rapports_avec_moins_de_6_visites)
#             rapports_vides = [
#                 {
#                     "infos": f"{rap.user.first_name} {rap.user.last_name} {rap.added.strftime('%d/%m/%Y')}",
#                 }
#                 for rap in rapports_avec_moins_de_6_visites
#             ]
#             print("les rapports videeeeeeee")
#             print(rapports_vides)
#             # Count plans and calculate total similarity percentage
#             plan_count = rapports.count()
#             total_similarity_percentage = 0
#             if int(commercial_input) == 1000000:
#                 profile = UserProfile.objects.get(user=request.user)
#                 if profile.speciality_rolee == "Superviseur_regional":
#                     planss = Plan.objects.filter(
#                     day__month=date_start.month, day__year=date_start.year, user__in=profile.usersunder.all()
#                     )
#                 else:
#                     planss = Plan.objects.filter(
#                     day__month=date_start.month, day__year=date_start.year
#                     )
#             else:
#                 planss = Plan.objects.filter(
#                 day__month=date_start.month, day__year=date_start.year, user=commercial
#                 )
#             for plan in planss:
#                 clients_list = plan.clients.exclude(
#                     specialite__in=specialites_a_exclure
#                 )
#                 matching_doctors = (
#                     Visite.objects.filter(
#                         rapport__in=rapports, medecin__in=clients_list
#                     )
#                     .exclude(medecin__specialite__in=specialites_a_exclure)
#                     .distinct()
#                     .count()
#                 )
#                 client_list_count = clients_list.count() or 1
#                 similarity_percentage = (matching_doctors * 100) / client_list_count
#                 total_similarity_percentage += similarity_percentage
#                 # Calculate average similarity percentage
#                 average_similarity_percentage = (
#                     total_similarity_percentage / plan_count if plan_count else 0
#                 )

#                 if not average_similarity_percentage:
#                     average_similarity_percentage = 0

#                 if average_similarity_percentage > 100:
#                     average_similarity_percentage = 100

#             # GETTING DISTINCT MEDICAL COUNT
#             medecin_nbr = len(medecins) - len(
#                 medecins.filter(specialite__in=["Pharmacie", "Grossiste", "SuperGros"])
#             )
#             # Assuming 'commercial' is a list of User instances
#             #total_medecin_count = (
#             #    Medecin.objects.filter(users=commercial).exclude(
#             #        specialite__in=["Pharmacie", "Grossiste", "SuperGros"]
#             #    )
#             #).count()
#             if int(commercial_input) == 1000000:
#                 pass
#                 #total_medecin_count = (
#                 #Medecin.objects.all().exclude(
#                 #    specialite__in=["Pharmacie", "Grossiste", "SuperGros"]
#                 #)
#                 #).count()
#             else:
#                 pass
#                 #total_medecin_count = (
#                 #Medecin.objects.filter(users=commercial).exclude(
#                 #    specialite__in=["Pharmacie", "Grossiste", "SuperGros"]
#                 #)
#                 #).count()
#             #total_commercial_count = (
#             #    Medecin.objects.filter(
#             #        users=commercial,
#             #        specialite__in=["Pharmacie", "Grossiste", "SuperGros"],
#             #    )
#             #).count()
#             if int(commercial_input) == 1000000:
#                 pass
#                 #total_commercial_count = (
#                 #Medecin.objects.filter(
#                 #    specialite__in=["Pharmacie", "Grossiste", "SuperGros"],
#                 #)
#                 #).count()
#             else:
#                 pass
#                 #total_commercial_count = (
#                 #Medecin.objects.filter(
#                 #    users=commercial,
#                 #    specialite__in=["Pharmacie", "Grossiste", "SuperGros"],
#                 #)
#                 #).count()

#             print("je suis dans la ligne 674")
#             # GETTING DISTINCT COMMERCIAL COUNT
#             commercial_nbr = len(
#                 medecins.filter(specialite__in=["Pharmacie", "Grossiste", "SuperGros"])
#             )
#             # GETTING ALL COMMERCIAL COUNT
#             medecin_commercial = len(
#                 medecins.filter(specialite__in=["Pharmacie", "Grossiste", "SuperGros"])
#             )
#             medecin_commercial_client = len(
#                 medecins.filter(
#                     specialite__in=["Pharmacie", "Grossiste", "SuperGros"]
#                 ).distinct()
#             )
#             # GETTING SPECIALITYS FOR ALL MEDECINS
#             details = (
#                 Medecin.objects.filter(id__in=medecins.values("id"))
#                 .values("specialite")
#                 .annotate(dcount=Count("specialite"))
#             )
#             # GETTING SPECIALITYS FOR DISTINCT MEDECINS

#             visited_communes = set()
#             other_details += f"<b style='color:black; font-size:19px'>Régions visités / المناطق المزاره :</b></br>"
#             for visite in visites:
#                 visited_communes.add(
#                     (
#                         visite.medecin.commune.wilaya.nom
#                         + "/"
#                         + visite.medecin.commune.nom
#                         + " - "
#                     )
#                 )

#             other_details += f"<span style='color:black;font-size:13px'>{', '.join(visited_communes)}</span>"

#             other_details += "</br> </br>"

#             details_distinct = (
#                 Medecin.objects.filter(id__in=medecins.values("id"))
#                 .distinct()
#                 .values("specialite")
#                 .annotate(dcount=Count("specialite"))
#             )

#             other_details += f"""                    <div class="row mb-2">
#             <div class="col-md-6 d-flex"><h5 style="color:black"><b>Total des visites / مجموع الزيارات :</b></h5></div>
#             <div class="col-md-6 text-right"><h5 style="color:green">{len(medecins)}</h5></div>
#             </div>"""

#             # TOTAL DES VISITES MED/COM SPECIALITIES

#             # Displaying specialties
#             print("je suis dans la ligne 727")
#             # TOTAL DES CLIENTS MED/COM SPECIALITIES
#             other_specialties = []
#             end_specialties = []
#             for detail in details_distinct:
#                 if detail["specialite"] in ["SuperGros", "Grossiste", "Pharmacie"]:
#                     end_specialties.append(detail)
#                 else:
#                     other_specialties.append(detail)
#             sorted_specialties = other_specialties + end_specialties
#             print("je suis dans la ligne 737")
#             # Displaying specialties
#             medical_specialties = [
#                 detail
#                 for detail in sorted_specialties
#                 if detail["specialite"] not in ["SuperGros", "Grossiste", "Pharmacie"]
#             ]
#             commercial_specialties = [
#                 detail
#                 for detail in sorted_specialties
#                 if detail["specialite"] in ["SuperGros", "Grossiste", "Pharmacie"]
#             ]
#             medical_specialties_sorted = sorted(
#                 medical_specialties, key=lambda x: x["dcount"], reverse=True
#             )
#             print("je suis dans la ligne 752")
#             other_details += f"""
#             <div class="row mb-2">
#                 <div class="col-md-6 d-flex">
#                     <h5 style="color:black"><b>Total des visites Medical / مجموع زيارات الاطباء:</b></h5>
#                 </div>
#                 <div class="col-md-6 text-right">
#                     <h5 style="color:black"><span style="color:green">{medecin_nbr}</span></h5>
#                 </div>
#             </div>
#             <div class="row mb-2">
#                 <div class="col-md-12">
#                     {" ".join(
#                         [f'<span style="color:black; font-size:14px">({detail["dcount"]}) {detail["specialite"]}</span>'
#                          for detail in medical_specialties_sorted]
#                     )}
#                 </div>
#             </div>
#             """
#             other_details += f"</span>"
#             other_details += f"<span style='margin-left: 10px;color:black'>"

#             # Assuming commercial_specialties is a list of dictionaries
#             commercial_specialties_sorted = sorted(
#                 commercial_specialties, key=lambda x: x["dcount"], reverse=True
#             )
#             print("je suis dans la ligne 778")
#             # Generate the HTML with sorted specialties
#             other_details += f"""
#             <div class="row mb-2">
#                 <div class="col-md-6 d-flex">
#                     <h5 style="color:black"><b>Total des visites Commercial / مجموع زيارات الكومرسيال :</b></h5>
#                 </div>
#                 <div class="col-md-6 text-right">
#                     <h5 style="color:black"><span style="color:green">{medecin_commercial_client}</span></h5>
#                 </div>
#             </div>
#             <div class="row mb-2">
#                 <div class="col-md-12">
#                     {" ".join(
#                         [f'<span style="color:black; font-size:14px">({detail["dcount"]}) {detail["specialite"]}</span>'
#                          for detail in commercial_specialties_sorted]
#                     )}
#                 </div>
#             </div>
#             """
#             print("je suis dans la ligne 798")
#             other_details += f"</span>"
#             # PRODUITS PRESENTES MEDICAL
#             # PRODUITS PRESENTES MEDICAL
#             other_details += "<h5><b> Total des présentations médicale / عدد مرات  تقديم المنتج للاطباء : </b></h5>"
#             product_info = {}
#             excluded_specialties = ["Pharmacie", "Grossiste", "Supergros"]

#             # Loop through all products
#             for p in Produit.objects.all():
#                 # Count visits excluding the specified specialties
#                 len_visits = len(
#                     visites.exclude(
#                         medecin__specialite__in=excluded_specialties
#                     ).filter(produits__id=p.id)
#                 )
#                 product_info[p.nom] = len_visits
#             print("je suis dans la ligne 815")
#             # Sort products by the number of visits in descending order
#             sorted_products = sorted(
#                 product_info.items(), key=lambda x: x[1], reverse=True
#             )

#             count_med = 0
#             for product, len_visits in sorted_products:
#                 if len_visits > 0:
#                     product_string = f"<span style='color:black;font-size:13px'>({product} : <span style='color:green'>{len_visits} fois</span>)</span>"
#                     other_details += product_string + " "
#                     count_med += 1

#             # Debugging: Print the product_info dictionary to verify counts
#             print(product_info)

#             # PRODUITS PRESENTES COMMERCIAL
#             other_details += "</br><h5><b>Total des présentations commerciale / عدد مرات تقديم المنتج في للكومرسيال   : </b></h5>"
#             product_info = {}
#             for p in Produit.objects.all():
#                 included_specialties = ["Pharmacie", "Grossiste", "Supergros"]
#                 len_visits = len(
#                     visites.filter(medecin__specialite__in=included_specialties).filter(
#                         produits__id=p.id
#                     )
#                 )
#                 product_info[p.nom] = len_visits
#             sorted_products = sorted(
#                 product_info.items(), key=lambda x: x[1], reverse=True
#             )
#             count = 0
#             print("je suis dans la ligne 846")
#             for product, len_visits in sorted_products:
#                 if len_visits > 0:
#                     product_string = f"<span style='color:black;font-size:13px'>({product} : <span style='color:green'>{len_visits} fois</span> )</span>"
#                     other_details += product_string + " "
#                     count += 1

#             # if count % 3 > 0:
#             other_details += "<br/>"

#             rapports_count = rapports.count()
#             if int(commercial_input) == 1000000:
#                 profile = UserProfile.objects.get(user=request.user)
#                 if profile.speciality_rolee == "Superviseur_regional":
#                     leaves = Leave.objects.filter(
#                         user__in=profile.usersunder.all(),
#                     start_date__lte=date_end - timedelta(days=1),  # Leave starts before or on the end date of the filter
#                     end_date__gte=date_start,
#                     ).exclude(
#                         end_date=date_end  # Exclure ceux dont la date de fin est exactement date_end
#                     ).order_by(F("start_date").asc(nulls_last=True))
#                 else:
#                     leaves = Leave.objects.filter(
#                     start_date__lte=date_end - timedelta(days=1),  # Leave starts before or on the end date of the filter
#                     end_date__gte=date_start,
#                     ).exclude(
#                         end_date=date_end  # Exclure ceux dont la date de fin est exactement date_end
#                     ).order_by(F("start_date").asc(nulls_last=True))
#             else:
#                 leaves = Leave.objects.filter(
#                 user=commercial,
#                 start_date__lte=date_end - timedelta(days=1),  # Leave starts before or on the end date of the filter
#                 end_date__gte=date_start,
#                 ).exclude(
#                 end_date=date_end  # Exclure ceux dont la date de fin est exactement date_end
#                 ).order_by(F("start_date").asc(nulls_last=True))

#             print("leaves : " + str(leaves))
#             dt = date_start
#             et = date_end
#             if int(commercial_input) != 1000000:
#                 while dt <= date_end:
#                     if int(commercial_input) != 1000000:
#                         if commercial.userprofile.commune.wilaya.pays.nom == "algerie":
#                             if dt.weekday() != days["fri"] and dt.weekday() != days["sat"]:
#                                 day_count += 1
#                         elif commercial.commune.wilaya.pays.nom == "Tunisie":
#                             if dt.weekday() != days["sat"] and dt.weekday() != days["sun"]:
#                                 day_count += 1

#                     dt += delta_day
#             else:
#                 while dt <= date_end:
#                     if dt.weekday() != days["fri"] and dt.weekday() != days["sat"]:
#                         day_count += 1
#                     dt += delta_day
#                 profile = UserProfile.objects.get(user=request.user)
#                 if profile.speciality_rolee == "Superviseur_regional":
#                     total_rapp = profile.usersunder.all().count()
#                 else:
#                     total_rapp = UserProfile.objects.filter(speciality_rolee__in=["Medico_commercial", "Commercial", "Superviseur_regional"], hidden=False, user__is_active=True).count()
#                 day_count = day_count * total_rapp

#             # Prepare leaves data for the context
#             print("je suis dans la ligne 884")
#             leaves_data = [
#                 {
#                     "start_date": f"{leave.user.first_name} {leave.user.last_name} - {leave.start_date}",
#                     "end_date": leave.end_date,
#                     "leave_type": leave.leave_type.description,  # Accessing the leave type description
#                 }
#                 for leave in leaves
#             ]
            
#             #Les rapports vides
#             print(f"Je suis dans la ligne 966 et voici les rapports vides {rapports_avec_moins_de_6_visites}")
            
#             # Convertir en datetime.datetime
#             date_start = datetime.combine(date_start, time.min)
#             date_end = datetime.combine(date_end, time.max)

#             # S'assurer que ce sont des objets "aware"
#             if timezone.is_naive(date_start):
#                 date_start = timezone.make_aware(date_start)

#             if timezone.is_naive(date_end):
#                 date_end = timezone.make_aware(date_end)
#             a = []
#             b = []
#             c = []
#             if int(commercial_input) == 1000000:
#                 print("je suis dans la ligne 906")
#                 profile = UserProfile.objects.get(user=request.user)
#                 if profile.speciality_rolee == "Superviseur_regional":
#                     orders = Order.objects.filter(
#                     added__range=(date_start, date_end),
#                     user__in=profile.usersunder.all()
#                     )
#                     for user_undr in profile.usersunder.all():
#                         ords = Order.objects.filter(
#                             user=user_undr, added__range=(date_start, date_end)
#                         )
#                         check = 0
#                         c = []
#                         for o in ords:
#                             item = OrderItem.objects.filter(order=o)
#                             check = 0
#                             for i in item:
#                                 for t in c:
#                                     if t['produit'] == i.produit:
#                                         t['qtt'] = t['qtt'] + i.qtt
#                                         check = 1
#                                 if check == 0:
#                                     new = {
#                                         "produit":i.produit,
#                                         "qtt":i.qtt
#                                     }
#                                     c.append(new)
                                    
#                         details= {
#                             "User": f"{user_undr.last_name} {user_undr.first_name}",
#                             "Nombre_Orders": ords.count(),
#                             "c" : c
#                         }
#                         if ords.count() == 0:
#                             b.append(details)
#                         else:
#                             a.append(details)
#                 else:
#                     # 1️⃣ Sélection des utilisateurs
#                     if int(commercial_input) == 1000000:
#                         usrs = User.objects.all()
#                     else:
#                         usrs = commercial_input 


#                     # 2️⃣ Récupérer tous les users absents ou en congé sur la période
#                     absent_users = User.objects.filter(
#                         Q(leave__start_date__lte=date_end - timedelta(days=1), leave__end_date__gte=date_start) |
#                         Q(absence__date__range=(date_start, date_end))
#                     ).distinct()

#                     # 3️⃣ Exclure les absents
#                     operational_users = usrs.exclude(id__in=absent_users) \
#                         .exclude(userprofile__hidden=True) \
#                         .exclude(userprofile__is_human=False) \
#                         .exclude(userprofile__speciality_rolee__in=["Office","chargé_de_communication","gestionnaire_de_stock","Finance_et_comptabilité","Admin"]) \
#                         .exclude(userprofile__family__in=["production"])

#                     # Structures globales pour cumuler les données
#                     product_qty_pharmacy_and_gros = {}
#                     product_qty_gros_and_super_gros = {}
#                     count_orders_with_pharmacy_and_gros = 0
#                     count_orders_with_gros_and_super_gros = 0

#                     a, b = [], []  # utilisateurs avec et sans commandes

#                     # 4️⃣ Boucle sur les utilisateurs opérationnels
#                     for usr in operational_users:
#                         orders = Order.objects.filter(
#                             user=usr,
#                             added__range=(date_start, date_end)
#                         )

#                         # --- Comptage commandes par produit (pour 'c') ---
#                         c = []
#                         for o in orders:
#                             for i in OrderItem.objects.filter(order=o):
#                                 print(f"{o.user} -> {i.produit} -> {i.qtt}")
#                                 for t in c:
#                                     if t['produit'] == i.produit:
#                                         t['qtt'] += i.qtt
#                                         break
#                                 else:
#                                     c.append({"produit": i.produit, "qtt": i.qtt})

#                         details = {
#                             "User": f"{usr.last_name} {usr.first_name}",
#                             "Nombre_Orders": orders.count(),
#                             "c": c
#                         }
#                         if orders.count() == 0:
#                             b.append(details)
#                         else:
#                             a.append(details)

#                         # --- Cumuler Pharmacy + Gros ---
#                         orders_pg = orders.filter(pharmacy__isnull=False, gros__isnull=False)
#                         count_orders_with_pharmacy_and_gros += orders_pg.count()

#                         for item in OrderItem.objects.filter(order__in=orders_pg):
#                             nom = item.produit.nom
#                             product_qty_pharmacy_and_gros[nom] = product_qty_pharmacy_and_gros.get(nom, 0) + item.qtt

#                         # --- Cumuler Gros + Super Gros ---
#                         orders_gsg = orders.filter(gros__isnull=False, super_gros__isnull=False)
#                         count_orders_with_gros_and_super_gros += orders_gsg.count()

#                         for item in OrderItem.objects.filter(order__in=orders_gsg):
#                             nom = item.produit.nom
#                             product_qty_gros_and_super_gros[nom] = product_qty_gros_and_super_gros.get(nom, 0) + item.qtt

#                     # Produits uniques
#                     unique_products = set(product_qty_pharmacy_and_gros.keys()) | set(product_qty_gros_and_super_gros.keys())

#                     context = {
#                         "visites": len(visites),
#                         "clients": len(medecins),
#                         "details": other_details,
#                         "orders_per_user": a,
#                         "user_with_no_orders": b,
#                         "rapports_count": rapports_count,
#                         "rapports_vides": rapports_vides,
#                         "days": day_count,
#                         "orders_commercial": orders_commercial,
#                         "orders_transferred_to": orders_transferred_to,
#                         "orders_transferred_from": orders_transferred_from,
#                         "product_qty_gros_and_super_gros": product_qty_gros_and_super_gros,
#                         "product_qty_pharmacy_and_gros": product_qty_pharmacy_and_gros,
#                         "unique_products": list(unique_products),
#                         "count_orders_with_pharmacy_and_gros": count_orders_with_pharmacy_and_gros,
#                         "count_orders_with_gros_and_super_gros": count_orders_with_gros_and_super_gros,
#                         "absence": absence,
#                         "average_similarity_percentage": average_similarity_percentage,
#                         "commerciale_name": commerciale_name,
#                         "absence_dates": absence_dates,
#                         "other_details": other_details,
#                         "leaves": leaves_data,
#                     }

#                     if "IMAGE" in request.path:
#                         template_name = "rapports/rapports_images.html"

                    
#                     return render(request, template_name, context)

#         # return HttpResponse(pdf, content_type='application/pdf')

class RapportSinglePDF(LoginRequiredMixin, TemplateView):
    def get(self, request, id=0):
        if id == 0:
            rapports = rapport_list(request)
            template_name = "rapports/rapports_pdf.html"
        else:
            rapports = [
                Rapport.objects.get(id=id),
            ]
            template_name = "rapports/single_rapport_pdf.html"

        visites = Visite.objects.filter(rapport__in=rapports)
        medecins = Medecin.objects.filter(visite__in=visites).distinct()
        details = (
            Medecin.objects.filter(id__in=medecins.values("id"))
            .values("specialite")
            .annotate(dcount=Count("specialite"))
        )
        medecin_nbr = len(medecins)
        other_details = ""

        medical_specialties = ["Pharmacie", "Grossiste", "SuperGros"]
        medecin_nbr_medical = len(medecins.exclude(specialite__in=medical_specialties))
        medecin_nbr_commercial = len(medecins) - medecin_nbr_medical

        # medical_specialties_list = [detail["specialite"] for detail in details if detail["specialite"] not in medical_specialties]
        commercial_specialties = [
            f'({detail["dcount"]}) {detail["specialite"]}'
            for detail in details
            if detail["specialite"] in medical_specialties
        ]
        medical_specialties_l = [
            f'({detail["dcount"]}) {detail["specialite"]}'
            for detail in details
            if detail["specialite"] not in medical_specialties
        ]

        if request.GET.get("produit") and request.GET.get("produit") != "":
            prd_visites = visites.filter(produits__id=request.GET.get("produit"))
            prd_medecins = Medecin.objects.filter(
                id__in=prd_visites.values("medecin__id")
            )
            other_details = f" dont ({len(prd_visites)} visites et {len(prd_medecins)} medecins) contenant le produit"

        commercial_input = request.GET.get("commercial", "").strip()

        if commercial_input:
            # Extraction du username avant le " - ", s'il existe
            if " - " in commercial_input:
                username = commercial_input.split(" - ")[0].strip()
            else:
                username = commercial_input

            commercial = User.objects.get(username=username)

            if request.GET.get("mindate"):
                date_start = datetime.strptime(
                    request.GET.get("mindate"), "%Y-%m-%d"
                ).date()
            else:
                date_start = datetime.strptime("2020-06-01", "%Y-%m-%d").date()

            if request.GET.get("maxdate"):
                date_end = datetime.strptime(
                    request.GET.get("maxdate"), "%Y-%m-%d"
                ).date()
            else:
                today = datetime.now()
                date_end = datetime.strptime(
                    f"{today.year}-{today.month}-{today.day}", "%Y-%m-%d"
                ).date()

            delta_day = timedelta(days=1)

            days = {
                "mon": 0,
                "tue": 1,
                "wed": 2,
                "thu": 3,
                "fri": 4,
                "sat": 5,
                "sun": 6,
            }

            dt = date_start
            et = date_end
            day_count = 0

            # print(str(request.GET.get("commercial")))
            # absences = Absence.objects.filter(
            #     Q(user__username=request.GET.get("commercial")) &
            #     Q(date__gte=dt) &
            #     Q(date__lte=et)
            # )
            # print(str(absences))
            absence_dates = []
            # absence=len(absences)
            # print()

            # for absence in absences:
            #     absence_dates.append(absence.date)

            while dt <= date_end:
                if commercial.userprofile.commune.wilaya.pays.nom == "algerie":
                    if dt.weekday() != days["fri"] and dt.weekday() != days["sat"]:
                        day_count += 1
                        if not Rapport.objects.filter(
                            added=dt, user=commercial
                        ).exists():
                            absence_dates.append(dt)
                elif commercial.commune.wilaya.pays.nom == "Tunisie":
                    if dt.weekday() != days["sat"] and dt.weekday() != days["sun"]:
                        day_count += 1
                        if not Rapport.objects.filter(
                            added=dt, user=commercial.user
                        ).exists():
                            absence_dates.append(dt)
                dt += delta_day
            absence = day_count - len(rapports)
        else:
            day_count = "/"
            absence = ""
            absence_dates = []

        visites = Visite.objects.filter(rapport__in=rapports)
        medecins = Medecin.objects.filter(visite__in=visites)
        total_similarity_percentage = 0
        plan_count = 0
        specialites_a_exclure = ["Pharmacie", "Grossiste", "SuperGros"]
        # Filter Rapport objects
        # rapports = Rapport.objects.filter(
        #     added__month=datetime.now().month,
        #     added__year=datetime.now().year,
        #     user=70
        # )
        # # Count plans and calculate total similarity percentage
        # plan_count = rapports.count()
        # total_similarity_percentage = 0
        # for plan in Plan.objects.filter(
        #     user=self.user.id,
        #     day__month=datetime.datetime.now().month,
        #     day__year=datetime.datetime.now().year
        # ):
        # clients_list = plan.clients.exclude(specialite__in=specialites_a_exclure)
        # matching_doctors = Visite.objects.filter(
        #     rapport__in=rapports,
        #     medecin__in=clients_list
        # ).exclude(
        #     medecin__specialite__in=specialites_a_exclure
        # ).distinct().count()
        # client_list_count = clients_list.count() or 1
        # similarity_percentage = (matching_doctors * 100) / client_list_count
        # total_similarity_percentage += similarity_percentage
        # Calculate average similarity percentage
        # average_similarity_percentage = total_similarity_percentage / plan_count if plan_count else 0
        # Format color based on average similarity percentage
        # if average_similarity_percentage < 30:
        #     color = 'red'
        # elif 30 <= average_similarity_percentage < 50:
        #     color = 'orange'
        # else:
        #     color = 'green'
        # Display details
        # other_details = f"<p style='font-weight: bold; margin: 0;font-size:16px; color:black'>Moyenne Similarité Planning / Rapport: <span style='font-weight:bold; color:{color}'>{int(average_similarity_percentage)}%</span></p>"

        # GETTING DISTINCT MEDICAL COUNT
        medecin_nbr = len(medecins) - len(
            medecins.filter(specialite__in=["Pharmacie", "Grossiste", "SuperGros"])
        )
        # GETTING DISTINCT COMMERCIAL COUNT
        commercial_nbr = len(
            medecins.filter(specialite__in=["Pharmacie", "Grossiste", "SuperGros"])
        )
        # GETTING ALL COMMERCIAL COUNT
        medecin_commercial = len(
            medecins.filter(specialite__in=["Pharmacie", "Grossiste", "SuperGros"])
        )
        medecin_commercial_client = len(
            medecins.filter(
                specialite__in=["Pharmacie", "Grossiste", "SuperGros"]
            ).distinct()
        )
        # GETTING SPECIALITYS FOR ALL MEDECINS
        details = (
            Medecin.objects.filter(id__in=medecins.values("id"))
            .values("specialite")
            .annotate(dcount=Count("specialite"))
        )
        # GETTING SPECIALITYS FOR DISTINCT MEDECINS

        visited_communes = set()
        other_details += f"<b>Régions visités ce jour : </b>"
        for visite in visites:
            visited_communes.add(
                (
                    visite.medecin.commune.wilaya.nom
                    + "/"
                    + visite.medecin.commune.nom
                    + " - "
                )
            )
        other_details += ", ".join(visited_communes)

        other_details += "<br>"

        details_distinct = (
            Medecin.objects.filter(id__in=medecins.values("id"))
            .distinct()
            .values("specialite")
            .annotate(dcount=Count("specialite"))
        )
        other_details += f"<b style='font-size:15px;color:grey'> Total des <span style='color:red'>visites</span> aujourd'hui </b><b style='font-size:15px; color:green'>({len(medecins)})</b><br/>"
        # TOTAL DES VISITES MED/COM SPECIALITIES

        # Displaying specialties

        # TOTAL DES CLIENTS MED/COM SPECIALITIES
        other_specialties = []
        end_specialties = []
        for detail in details_distinct:
            if detail["specialite"] in ["SuperGros", "Grossiste", "Pharmacie"]:
                end_specialties.append(detail)
            else:
                other_specialties.append(detail)
        sorted_specialties = other_specialties + end_specialties
        # Displaying specialties
        medical_specialties = [
            detail
            for detail in sorted_specialties
            if detail["specialite"] not in ["SuperGros", "Grossiste", "Pharmacie"]
        ]
        commercial_specialties = [
            detail
            for detail in sorted_specialties
            if detail["specialite"] in ["SuperGros", "Grossiste", "Pharmacie"]
        ]
        other_details += f"<span style='margin-left: 10px;color:grey'>"
        other_details += (
            f"<b style='font-size:15px;color:green'>({(medecin_nbr)}) Medical:</b> "
            + " ".join(
                [
                    f'<b>({detail["dcount"]})</b> {detail["specialite"]} '
                    for detail in medical_specialties
                ]
            )
        )
        other_details += "</br>"
        other_details += f"</span>"
        other_details += f"<span style='margin-left: 10px;color:grey'>"
        other_details += (
            f"<b style='font-size:14px;color:green'> ({(medecin_commercial_client)}) Commercial:</b> "
            + " ".join(
                [
                    f'<b>({detail["dcount"]})</b> {detail["specialite"]} '
                    for detail in commercial_specialties
                ]
            )
        )
        other_details += f"</span>"
        other_details += "</br>"
        # PRODUITS PRESENTES MEDICAL
        other_details += "<b style='font-size:16px'><span style='color:red' >Medical</span><span style='color:grey'> Produits presentés ce aujourd'hui:<span></b></br>"
        product_info = {}
        for p in Produit.objects.all():
            excluded_specialties = ["Pharmacie", "Grossiste", "Supergros"]
            len_visits = len(
                visites.exclude(medecin__specialite__in=excluded_specialties).filter(
                    produits__id=p.id
                )
            )
            product_info[p.nom] = len_visits
        sorted_products = sorted(product_info.items(), key=lambda x: x[1], reverse=True)
        count_med = 0
        for product, len_visits in sorted_products:
            if len_visits > 0:
                product_string = f"<b style='font-size:13px; color:grey'>({product} : <b style='color:green'>{len_visits} fois</b> )</b>"
                other_details += product_string + " "
                count_med += 1
                if count_med % 3 == 0:
                    other_details += "</br>"
        if count_med % 3 > 0:
            other_details += "<br/>"
        # PRODUITS PRESENTES COMMERCIAL
        other_details += "<b style='font-size:16px'><span style='color:red' >Commercial</span> <span style='color:grey'> Produits presentés aujourd'hui:</span></b></br>"
        product_info = {}
        for p in Produit.objects.all():
            included_specialties = ["Pharmacie", "Grossiste", "Supergros"]
            len_visits = len(
                visites.filter(medecin__specialite__in=included_specialties).filter(
                    produits__id=p.id
                )
            )
            product_info[p.nom] = len_visits
        sorted_products = sorted(product_info.items(), key=lambda x: x[1], reverse=True)
        count = 0
        for product, len_visits in sorted_products:
            if len_visits > 0:
                product_string = f"<b style='font-size:13px; color:grey'>({product} : <b style='color:green'>{len_visits} fois</b> )</b>"
                other_details += product_string + " "
                count += 1
                if count % 3 == 0:
                    other_details += "</br>"
        if count % 3 > 0:
            other_details += "<br/>"

        # print(absence_dates)
        context = {
            "visites": len(visites),
            "clients": len(medecins),
            "details": other_details,
            "rapports": rapports,
            "days": day_count,
            "absence": absence,
            "absence_dates": absence_dates,
            "other_details": other_details,
        }
        if "IMAGE" in request.path:
            template_name = "rapports/rapports_images.html"

        return render(request, template_name, context)

        rendered = render_to_string(template_name, context)

        htmldoc = HTML(string=rendered, base_url="http://app.liliumpharma.com")
        return HttpResponse(htmldoc.write_pdf(), content_type="application/pdf")

        # return HttpResponse(pdf, content_type='application/pdf')


# class RapportPDF(LoginRequiredMixin, TemplateView):
#     def get(self, request, id=0):
#         if id == 0:
#             rapports = rapport_list(request)
#             template_name = 'rapports/rapports_pdf.html'
#         else:
#             rapports = [Rapport.objects.get(id=id), ]
#             template_name = 'rapports/single_rapport_pdf.html'

#         visites = Visite.objects.filter(rapport__in=rapports)
#         medecins = Medecin.objects.filter(visite__in=visites).distinct()
#         details = Medecin.objects.filter(id__in=medecins.values("id")).values('specialite').annotate(dcount=Count('specialite'))
#         medecin_nbr = len(medecins)

#         medical_specialties = ['Pharmacie', 'Grossiste', 'SuperGros']
#         medecin_nbr_medical = len(medecins.exclude(specialite__in=medical_specialties))
#         medecin_nbr_commercial = len(medecins) - medecin_nbr_medical

#         # medical_specialties_list = [detail["specialite"] for detail in details if detail["specialite"] not in medical_specialties]
#         commercial_specialties = [f'({detail["dcount"]}) {detail["specialite"]}' for detail in details if detail["specialite"] in medical_specialties]
#         medical_specialties_l = [f'({detail["dcount"]}) {detail["specialite"]}' for detail in details if detail["specialite"] not in medical_specialties]

#         other_details = f"</br><b>Medical : ({medecin_nbr_medical})</br></b> <span style='font-size: 14px; margin-left: 20px;'>{', '.join(medical_specialties_l)}</span> </br> <b>Commercial : ({medecin_nbr_commercial}) </br></b>  <span style='font-size: 14px; margin-left: 20px;'> {', '.join(commercial_specialties)}</span>"


#         if request.GET.get("produit") and request.GET.get("produit") != "":
#             prd_visites = visites.filter(produits__id=request.GET.get("produit"))
#             prd_medecins = Medecin.objects.filter(id__in=prd_visites.values('medecin__id'))
#             other_details += f" dont ({len(prd_visites)} visites et {len(prd_medecins)} medecins) contenant le produit"

#         if request.GET.get("commercial"):
#             commercial = UserProfile.objects.get(user__username=request.GET.get("commercial"))

#             if request.GET.get("mindate"):
#                 date_start = datetime.strptime(request.GET.get("mindate"), '%Y-%m-%d').date()
#             else:
#                 date_start = datetime.strptime("2020-06-01", '%Y-%m-%d').date()

#             if request.GET.get("maxdate"):
#                 date_end = datetime.strptime(request.GET.get("maxdate"), '%Y-%m-%d').date()
#             else:
#                 today = datetime.now()
#                 date_end = datetime.strptime(f'{today.year}-{today.month}-{today.day}', '%Y-%m-%d').date()

#             delta_day = timedelta(days=1)

#             days = {'mon': 0, 'tue': 1, 'wed': 2, 'thu': 3, 'fri': 4, 'sat': 5, 'sun': 6}

#             dt = date_start
#             et = date_end
#             day_count = 0


#             # print(str(request.GET.get("commercial")))
#             # absences = Absence.objects.filter(
#             #     Q(user__username=request.GET.get("commercial")) &
#             #     Q(date__gte=dt) &
#             #     Q(date__lte=et)
#             # )
#             # print(str(absences))
#             absence_dates = []
#             # absence=len(absences)
#             # print()

#             # for absence in absences:
#             #     absence_dates.append(absence.date)


#             while dt <= date_end:
#                 if commercial.commune.wilaya.pays.nom == "algerie":
#                     if dt.weekday() != days['fri'] and dt.weekday() != days['sat']:
#                         day_count += 1
#                         if not Rapport.objects.filter(added=dt, user=commercial.user).exists():
#                             absence_dates.append(dt)
#                 elif commercial.commune.wilaya.pays.nom == "Tunisie":
#                     if dt.weekday() != days['sat'] and dt.weekday() != days['sun']:
#                         day_count += 1
#                         if not Rapport.objects.filter(added=dt, user=commercial.user).exists():
#                             absence_dates.append(dt)
#                 dt += delta_day
#             absence = day_count - len(rapports)
#         else:
#             day_count = "/"
#             absence = ""
#             absence_dates = []

#         # print(absence_dates)
#         context = {
#             "visites": len(visites),
#             "clients": len(medecins),
#             "details": other_details,
#             "rapports": rapports,
#             "days": day_count,
#             "absence": absence,
#             "absence_dates": absence_dates,
#         }
#         if "IMAGE" in request.path:
#             template_name="rapports/rapports_images.html"

#         return render(request,template_name,context)

#         rendered = render_to_string(template_name, context)


#         htmldoc = HTML(string=rendered, base_url="http://app.liliumpharma.com")
#         return HttpResponse(htmldoc.write_pdf(), content_type='application/pdf')

#         # return HttpResponse(pdf, content_type='application/pdf')


class VisitesPDF(LoginRequiredMixin, TemplateView):
    def get(self, request):
        if (
            request.user.userprofile.speciality_rolee
            in ["CountryManager", "Superviseur_national"]
            or request.user.is_superuser
        ):
            produit, region, specialite, classification, visites = get_visites(request)
            produitsvisites = get_stock(request)
            print(str(specialite))

            details = " ".join(
                [
                    f'<small><b style="color:#2da231">({pv["total"]})</b> {pv["produit__nom"]}</small>'
                    for pv in produitsvisites
                ]
            )

            return render(
                request,
                "rapports/visites/visites_PDF.html",
                {
                    "visites": visites,
                    "nbr_visites": len(visites),
                    "produit": produit,
                    "region": region,
                    "specialite": specialite,
                    "classification": classification,
                    "details": details,
                },
            )


class export_rapport_csv(APIView):
    def get(self, request, year):
        rapports = Rapport.objects.filter(added__year=year)
        serializer = RapportSerializer(rapports, many=True)
        return Response(serializer.data, status=200)


def export_visite_csv(request, id):
    rapport = Rapport.objects.get(id=id)
    visites = Visite.objects.filter(rapport=rapport)
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = (
        f'attachment; filename="visites-{rapport.user.username}-{rapport.added}.csv"'
    )

    writer = csv.writer(response)
    writer.writerow(
        [
            "id",
            "observation",
            "medecin",
            "specialite",
            "produits",
            "priority",
        ]
    )
    for visite in visites:
        obs = visite.observation if visite.observation else ""
        writer.writerow(
            [
                visite.id,
                obs,
                visite.medecin.nom,
                visite.medecin.specialite,
                " / ".join([produit.nom for produit in visite.produits.all()]),
                visite.priority,
            ]
        )

    return response


class AddComment(LoginRequiredMixin, TemplateView):
    def get(self, request, id):
        Comment.objects.create(
            user=request.user,
            rapport=Rapport.objects.get(id=id),
            comment=request.GET.get("content"),
        )
        return JsonResponse(
            {
                "user": {"username": request.user.username},
                "comment": request.GET.get("content"),
            }
        )

    def post(self, request, id):
        form = CommentForm(
            request.POST,
            instance=Comment(user=request.user, rapport=Rapport.objects.get(id=id)),
        )
        if form.is_valid():
            form.save()
        return redirect("HomeRapport")


def AddNote(request, id):
    Rapport.objects.filter(id=id).update(note=request.GET.get("note"))
    return JsonResponse(
        {
            "user": {"username": request.user.username},
            "comment": request.GET.get("content"),
        }
    )


class RapportSummaryAPIView(APIView):
    authentication_classes = (
        TokenAuthentication,
        SessionAuthentication,
    )

    def get(self, request):
        u = request.GET.get('user')
        print(f"uuuuuuuu {u}")
        if u:
            user = User.objects.get(username=u)
            print(f"userrrrrrrrr {user}")
        else:
            user = request.user

        year = request.GET.get("year", datetime.now().year)

        # Récupérez le mois à partir de la requête GET, utilisez le mois actuel si aucun mois n'est fourni dans la requête
        month = request.GET.get("month", str(int(datetime.now().month) - 1))
        if month == "null":
            month = (datetime.now().month) - 1

        int_month = int(month)
        int_year = int(year)
        days_in_month = monthrange(int_year, int_month)[1]
        # Calculate the number of working days (excluding Fridays and Saturdays)
        num_working_days = sum(
            1
            for day in range(1, days_in_month + 1)
            if datetime(int_year, int_month, day).weekday() not in [4, 5]
        )

        start_date = datetime.strptime(f"{year}-{month}-01", "%Y-%m-%d").date()
        end_date = start_date.replace(day=28) + timedelta(days=4)
        end_date = end_date - timedelta(days=end_date.day)

        rapports = Rapport.objects.filter(
            user=user, added__year=year, added__month=month
        )
        # Counting the number of reports
        num_reports = rapports.count()
        
        print(f"nombre de rapport {num_reports} de user {user}")

        num_workdays = 0
        absence_dates = []
        dt = start_date
        while dt < end_date or dt.day == end_date.day:
            if dt.weekday() not in [4, 5]:  # Exclude Friday (4) and Saturday (5)
                if Rapport.objects.filter(added=dt, user=user).exists():
                    num_workdays += 1
                else:
                    absence_dates.append(dt)
                # num_workdays += 1
            dt += timedelta(days=1)

        num_absence = len(absence_dates)

        visites = Visite.objects.filter(rapport__in=rapports)
        num_visits = visites.count()

        specialites_a_exclure = ["Pharmacie", "Grossiste", "SuperGros"]

        num_visits_com = visites.filter(
            medecin__specialite__in=specialites_a_exclure
        ).count()
        num_visits_medical = visites.exclude(
            medecin__specialite__in=specialites_a_exclure
        ).count()

        num_medecins = visites.values("medecin").distinct().count()

        specialties_count = (
            Medecin.objects.filter(id__in=visites.values("medecin"))
            .values("specialite")
            .annotate(count=Count("specialite"))
        )

        specialties_data = {
            specialty["specialite"]: specialty["count"]
            for specialty in specialties_count
        }
        # Filtrer les spécialités médicales
        specialties_medical = {
            specialty["specialite"]: specialty["count"]
            for specialty in specialties_count
            if specialty["specialite"] not in ["Pharmacie", "Grossiste", "SuperGros"]
        }
        specialties_medical_count = len(specialties_medical)
        # Filtrer les spécialités commerciales
        specialties_commercial = {
            specialty["specialite"]: specialty["count"]
            for specialty in specialties_count
            if specialty["specialite"] in ["Pharmacie", "Grossiste", "SuperGros"]
        }
        specialties_commercial_count = len(specialties_commercial)

        absences_response = []
        absences_response_count = 0

        absences = Absence.objects.filter(user=user, date__year=year, date__month=month)
        if absences.exists():
            for ab in absences:
                absences_response.append(
                    {
                        "id": ab.id,
                        "date": ab.date,
                    }
                )
            absences_response_count = len(absences_response)

        leaves_response = []
        leaves_response_count = 0

        leaves = Leave.objects.filter(
            user=user, start_date__year=year, start_date__month=month
        )
        if leaves.exists():
            for lv in leaves:
                leaves_response.append(
                    {
                        "id": lv.id,
                        "starting_date": lv.start_date,
                        "ending_date": lv.end_date,
                        "type": lv.leave_type.description,
                    }
                )
                print("******************" + str(leaves_response))
            leaves_response_count = len(leaves_response)

        data = {
            "num_reports": num_reports,
            "days_in_month": num_working_days,
            "num_absence": num_absence,
            "absence_dates": absence_dates,
            "num_visits": num_visits,
            "num_visits_commercial": num_visits_com,
            "num_visits_medical": num_visits_medical,
            "num_medecins": num_medecins,
            "specialties_data": specialties_data,
            ###########################################
            "leaves_response": leaves_response,
            "absences_response_count": absences_response_count,
            "absences_response": absences_response,
            "leaves_response_count": leaves_response_count,
            ###########################################
            "specialties_medical": specialties_medical,
            "specialties_medical_count": specialties_medical_count,
            "specialties_commercial": specialties_commercial,
            "specialties_commercial_count": specialties_commercial_count,
        }

        return Response(data)


class NonVisitedCommunesAPIView(APIView):
    authentication_classes = (
        TokenAuthentication,
        SessionAuthentication,
    )

    def get(self, request):
        # Récupérer le mois depuis les paramètres GET
        mois = request.GET.get("mois")
        uu = request.GET.get("user")
        
        if uu:
            usr = User.objects.get(username=uu)
        else:
            usr = request.user

        # Valider le paramètre du mois
        if not mois:
            return Response(
                {"error": "Paramètre de mois manquant"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            mois = int(mois)
        except ValueError:
            return Response(
                {"error": "Format de mois invalide"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Utiliser l'année actuelle
        annee = int(request.GET.get("year"))
        #annee = timezone.now().year

        # Définir les dates de début et de fin du mois spécifié
        start_of_month = datetime(annee, mois, 1)
        if mois == 12:
            end_of_month = datetime(annee + 1, 1, 1)
        else:
            end_of_month = datetime(annee, mois + 1, 1)

        # Récupérer les communes des médecins associés à l'utilisateur actuel
        medecins_associes = Medecin.objects.filter(users=usr)
        communes_associees = Commune.objects.filter(
            medecin__in=medecins_associes
        ).distinct()

        # Filtrer les visites effectuées durant le mois spécifié par les médecins associés à l'utilisateur actuel
        visites_specified_mois = Visite.objects.filter(
            rapport__added__gte=start_of_month,
            rapport__added__lt=end_of_month,
            rapport__user=usr,
            medecin__in=medecins_associes,
        )

        # Récupérer les communes des médecins associés à ces visites
        communes_visitees = communes_associees.filter(
            medecin__visite__in=visites_specified_mois
        ).distinct()

        # Exclure les communes visitées de la liste des communes associées
        communes_non_visitees = communes_associees.exclude(id__in=communes_visitees)

        total_non_visitees = communes_non_visitees.count()

        # Générer la chaîne des noms des communes non visitées séparés par des tirets
        communes_noms = [commune.nom for commune in communes_non_visitees]
        communes_concatenees = " - ".join(communes_noms)

        # Préparer la réponse finale avec le compte total et la chaîne concaténée
        response_data = {
            "total_non_visitees": total_non_visitees,
            "communes_concatenees": communes_concatenees,
        }
        # Retourner les communes non visitées dans la réponse
        return Response(response_data, status=status.HTTP_200_OK)


class MultipleVisitedCommunesAPIView(APIView):

    def get(self, request):
        # Récupérer le mois depuis les paramètres GET
        mois = request.GET.get("mois")
        if mois:
            print(f"oui ya de mois {mois}")
        else:
            print("oui pas de mois")
            mois = request.GET.get("month")
        uu = request.GET.get("user")
        
        if uu:
            usr = User.objects.get(username=uu)
        else:
            usr = request.user
        print("------------------------------------- TEST CALLING ")

        # Valider le paramètre du mois
        if not mois:
            return Response(
                {"error": "Paramètre de mois manquant"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            mois = int(mois)
        except ValueError:
            return Response(
                {"error": "Format de mois invalide"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Utiliser l'année actuelle
        annee = int(request.GET.get("year"))
        #annee = timezone.now().year
        print(f"year est {annee}")

        # Définir les dates de début et de fin du mois spécifié
        start_of_month = datetime(annee, mois, 1)
        print(f"start of mont {start_of_month}")
        if mois == 12:
            end_of_month = datetime(annee + 1, 1, 1)
        else:
            end_of_month = datetime(annee, mois + 1, 1)
        print(f"end of month {end_of_month}")
        # Récupérer les médecins associés à l'utilisateur actuel
        medecins_associes = Medecin.objects.filter(users=usr)

        # Filtrer les visites effectuées durant le mois spécifié par les médecins associés à l'utilisateur actuel
        visites_specified_mois = Visite.objects.filter(
            rapport__added__gte=start_of_month,
            rapport__added__lt=end_of_month,
            rapport__user=usr,
            medecin__in=medecins_associes,
        )

        # Annoter et grouper les visites par commune pour compter le nombre de visites
        visites_communes_counts = (
            visites_specified_mois.values("medecin__commune")
            .annotate(num_visites=Count("id"))
            .filter(num_visites__gt=1)
        )

        # Extraire les IDs des communes ayant plus d'une visite
        communes_ids = [item["medecin__commune"] for item in visites_communes_counts]
        ttl = defaultdict(set)
        dt = set()
        for i in communes_ids:
            visites_specified_mois_two = Visite.objects.filter(
                rapport__added__gte=start_of_month,
                rapport__added__lt=end_of_month,
                rapport__user=usr,
                medecin__in=medecins_associes,
                medecin__commune=i,
                )
            for s in visites_specified_mois_two:
                dt.add(s.rapport.added)
            ttl[i].add(len(dt))
            dt.clear()
        # Récupérer les objets Commune avec le nombre de visites
        communes_visitees = Commune.objects.filter(id__in=communes_ids).annotate(
            nombre_de_visites=Count(
                "medecin__visite",
                filter=Q(
                    medecin__visite__rapport__added__gte=start_of_month,
                    medecin__visite__rapport__added__lt=end_of_month,
                    medecin__visite__rapport__user=usr,
                ),
            )
        )
        print(f"communes_visitees {communes_visitees}")
        # Préparer la liste des communes visités plus d'une fois
        medecins_multiple_visites_table = []

        for index, commune in enumerate(communes_visitees):
            for x in ttl[commune.id]:
                t = x
            if t > 1:
                medecins_multiple_visites_table.append(
                    {
                        "id": commune.id,
                        "nom": commune.nom,
                        "nombre_de_visites": commune.nombre_de_visites,
                        "nombre_de_jours":ttl[commune.id]
                    }
                )

        # Calculer le nombre total de communes visitées plus d'une fois
        total_communes_visitees = len(medecins_multiple_visites_table)

        # Préparer les données de réponse
        response_data = {
            "total_communes_visitees": total_communes_visitees,
            "communes": medecins_multiple_visites_table,
        }

        # Retourner la réponse
        return Response(response_data, status=status.HTTP_200_OK)


class MultipleVisitedMedecinsAPIView(APIView):

    def get(self, request):
        # Récupérer le mois depuis les paramètres GET
        mois = request.GET.get("mois")
        uu = request.GET.get("user")

        # Valider le paramètre du mois
        if not mois:
            return Response(
                {"error": "Paramètre de mois manquant"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            mois = int(mois)
        except ValueError:
            return Response(
                {"error": "Format de mois invalide"}, status=status.HTTP_400_BAD_REQUEST
            )
        if uu:
            usr = User.objects.get(username=uu)
        else:
            usr = request.user
        # Utiliser l'année actuelle
        annee = int(request.GET.get("year"))
        #annee = timezone.now().year

        # Définir les dates de début et de fin du mois spécifié
        start_of_month = datetime(annee, mois, 1)
        if mois == 12:
            end_of_month = datetime(annee + 1, 1, 1)
        else:
            end_of_month = datetime(annee, mois + 1, 1)

        # Récupérer les médecins associés à l'utilisateur actuel
        medecins_associes = Medecin.objects.filter(users=usr)

        # Filtrer les visites effectuées durant le mois spécifié par les médecins associés à l'utilisateur actuel
        visites_specified_mois = Visite.objects.filter(
            rapport__added__gte=start_of_month,
            rapport__added__lt=end_of_month,
            rapport__user=usr,
            medecin__in=medecins_associes,
        )

        # Annoter et grouper les visites par médecin pour compter le nombre de visites
        visites_medecins_counts = (
            visites_specified_mois.values("medecin")
            .annotate(num_visites=Count("id"))
            .filter(num_visites__gt=1)
        )

        # Extraire les IDs des médecins ayant plus d'une visite
        medecins_ids = [item["medecin"] for item in visites_medecins_counts]

        # Récupérer les objets Medecin avec le nombre de visites
        medecins_visites = Medecin.objects.filter(id__in=medecins_ids).annotate(
            nombre_de_visites=Count(
                "visite",
                filter=Q(
                    visite__rapport__added__gte=start_of_month,
                    visite__rapport__added__lt=end_of_month,
                    visite__rapport__user=usr,
                ),
            )
        )

        # Préparer les données pour la réponse
        # Préparer les données pour la réponse
        medecins_non_visites_table = []

        for medecin_user in medecins_visites:
            medecins_non_visites_table.append(
                {
                    "id": medecin_user.pk,
                    "nom": medecin_user.nom,
                    "specialite":medecin_user.specialite,
                    "wilaya":medecin_user.wilaya.nom,
                    "commune":medecin_user.commune.nom,
                    "nombre_de_visites": medecin_user.nombre_de_visites,
                }
            )
        medecins_non_visites_table.sort(
            key=lambda x: x["nombre_de_visites"],
            reverse=True
        )
        # Calculer le nombre total de médecins non visités
        total_medecins_visites = len(medecins_non_visites_table)

        # Préparer les données de réponse
        response_data = {
            "total_medecins_visites": total_medecins_visites,
            "medecins": medecins_non_visites_table,
        }
        # Retourner les médecins visités plus d'une fois avec le nombre de visites dans la réponse
        return Response(response_data, status=status.HTTP_200_OK)


class MedecinsNonVisitesAPIView(APIView):

    def get(self, request):
        # Récupérer le mois depuis les paramètres GET
        print("CALLED BABY OH YEAH")
        mois = request.GET.get("mois")
        uu = request.GET.get("user")
        if uu:
            usr = User.objects.get(username=uu)
        else:
            usr = request.user
        grossistes_non_visites_table = []

        # Valider le paramètre du mois
        if not mois:
            return Response(
                {"error": "Paramètre de mois manquant"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            mois = int(mois)
        except ValueError:
            return Response(
                {"error": "Format de mois invalide"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Utiliser l'année actuelle
        annee = int(request.GET.get("year"))
        #annee = timezone.now().year

        # Définir les dates de début et de fin du mois spécifié
        start_of_month = datetime(annee, mois, 1)
        if mois == 12:
            end_of_month = datetime(annee + 1, 1, 1)
        else:
            end_of_month = datetime(annee, mois + 1, 1)

        # Récupérer les médecins avec spécialité 'grossiste'
        #medecins_grossistes = Medecin.objects.filter(
        #    users=usr, specialite="Grossiste"
        #)
        medecins_grossistes = Medecin.objects.filter(
            users=usr
        )

        # Filtrer les visites effectuées durant le mois spécifié
        visites_specified_mois = Visite.objects.filter(
            rapport__added__gte=start_of_month,
            rapport__added__lt=end_of_month,
            rapport__user=usr,
        )

        # Extraire les IDs des médecins visités durant le mois spécifié
        medecins_visites_ids = visites_specified_mois.values_list(
            "medecin_id", flat=True
        ).distinct()

        # Filtrer les médecins 'grossiste' qui n'ont pas été visités durant le mois
        medecins_non_visites = medecins_grossistes.exclude(id__in=medecins_visites_ids)

        for medecin_user in medecins_non_visites:
            a = Visite.objects.filter(rapport__user=usr, medecin_id=medecin_user.id).order_by('rapport__added').last()
            grossistes_non_visites_table.append(
                {
                    "id": medecin_user.pk,
                    "nom": medecin_user.nom,
                    "specialite":medecin_user.specialite,
                    "last_visit": a.rapport.added.strftime("%Y-%m-%d") if a else "Jamais visite par cet user",
                    "wilaya":medecin_user.wilaya.nom,
                    "commune":medecin_user.commune.nom,
                }
            )
        print(f"grossistes_non_visites_table{grossistes_non_visites_table}")
        # Calculer le nombre total de médecins non visités
        total_medecins_non_visites = len(grossistes_non_visites_table)

        # Préparer les données de réponse
        response_data = {
            "total_grossistes_non_visites": total_medecins_non_visites,
            "medecins": grossistes_non_visites_table,
        }
        # Retourner les médecins 'grossiste' non visités durant le mois spécifié
        return Response(response_data, status=status.HTTP_200_OK)


# HELP
class SupprimerDoublonsParDateView(View):
    def get(self, request, *args, **kwargs):
        today = datetime.today()
        # Filtrer les rapports ayant des doublons par date
        doublons_par_date = (
            Rapport.objects.values("added", "user")
            .annotate(nombre=Count("id"))
            .filter(nombre__gt=1)
        )

        # Récupérer les identifiants des doublons à supprimer
        rapports_a_supprimer_ids = []
        for doublon in doublons_par_date:
            rapports_a_supprimer = Rapport.objects.filter(
                added=doublon["added"], user=doublon["user"]
            ).order_by("id")[1:]
            rapports_a_supprimer_ids.extend(r.id for r in rapports_a_supprimer)

        # Supprimer les rapports en utilisant les identifiants récupérés
        Rapport.objects.filter(id__in=rapports_a_supprimer_ids).delete()

        # Rediriger vers une page appropriée après la suppression des doublons
        print("Deleted")
        return Response(status=200)


def obtenir_rapports_utilisateur(request):
    # Récupérer les rapports associés à l'utilisateur actuel (request.user)
    rapports_utilisateur = Rapport.objects.filter(user=request.user)

    # Créer une liste pour stocker les informations des rapports de l'utilisateur
    infos_rapports_utilisateur = []

    # Parcourir les rapports de l'utilisateur et récupérer les informations pertinentes
    for rapport in rapports_utilisateur:
        info_rapport = {
            "added": rapport.added,
            "user": rapport.user.username,  # Nom d'utilisateur
            "image_url": rapport.image.url,  # URL de l'image
            "image2_url": (
                rapport.image2.url if rapport.image2 else ""
            ),  # URL de l'image 2 s'il existe
            "can_update": rapport.can_update,
            "note": rapport.note,
            "observation": rapport.observation if rapport.observation else "",
        }
        infos_rapports_utilisateur.append(info_rapport)

    # Retourner les informations des rapports de l'utilisateur au format JSON
    return JsonResponse({"rapports_utilisateur": infos_rapports_utilisateur})


class ListRapport(LoginRequiredMixin, TemplateView):
    template_name = "rapports/liste_rapports.html"
    print("calleeddd")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        rapports = rapport_list(self.request)
        rapports = Rapport.objects.filter(user=self.request.user.id).order_by("-added")[:30]
        print("yesyesyesyes")
        print(self.request.user.id)
        print(rapports)
        for i in rapports:
            print(i.id)
            print(i.is_updatable)
            print(i.visite_set.all)
        context["page_title"] = ""
        context["rapports"] = rapports
        return context


import random
import string
from io import BytesIO
from django.shortcuts import render
from django.http import HttpResponse
from .models import QRCodeModel
from datetime import datetime, timedelta, time

# Assurez-vous d'importer le modèle approprié


from datetime import datetime, timedelta
from django.shortcuts import render
import random
import string

def generate_pages_task(user_id):
    eeee = 98
    date_debut = "2026-04-01"
    date_fin = "2026-04-30"
    user_id = int(user_id)
    eee = User.objects.get(id=user_id)
    Downloadable.objects.filter(link_name = f"{eee.username}_02.pdf").delete()
    # Convertir les dates en objets datetime
    date_debut = datetime.strptime(date_debut, "%Y-%m-%d")
    date_fin = datetime.strptime(date_fin, "%Y-%m-%d")

    # Calculer le nombre de jours entre les deux dates
    delta = date_fin - date_debut

    # Liste pour stocker les pages générées
    pages = []

    for i in range(delta.days + 1):
        # Date pour chaque jour
        current_date = date_debut + timedelta(days=i)

        # Générer un identifiant unique pour le QR code
        if current_date.weekday() in [4, 5]:
            continue  # Passer au jour suivant si c'est vendredi ou samedi

        unique_id = "".join(
                random.choices(string.ascii_letters + string.digits, k=8)
            )

            # Générer l'URL du QR code avec Google Chart API
        qr_code_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={unique_id}"
        print("generating qr code " + str(unique_id))
        qr_code_instance = QRCodeModel(identifier=unique_id)
        qr_code_instance.save()

            # Ajouter la page avec la date et le QR code à la liste
        pages.append(
                {
                    "nom":f"{eee.first_name} {eee.last_name}",
                    "date": current_date.strftime("%a. %d/%m/%Y"),
                    "qr_code_url": qr_code_url,  # URL du QR code unique
                }
            )
    html_content = render_to_string(
        "rapports/griffe_de_passage_medical_task.html", 
        {"pages": pages, "deleg": eee}  # Passer les pages générées et l'utilisateur au template
    )
    pdf_file = HTML(string=html_content).write_pdf(options={'orientation': 'landscape'})
    save_path = os.path.join(settings.MEDIA_ROOT, 'downloadable', f"{eee.username}_02.pdf")
    with open(save_path, 'wb') as f:
        f.write(pdf_file)
    downloadable = Downloadable.objects.create(attachement=f"downloadable/{eee.username}_02.pdf", link_name = f"{eee.username}_02.pdf")
    
    downloadable.users.set([eee])
    download_url = os.path.join(settings.MEDIA_URL, 'downloadable', os.path.basename(save_path))
    
    return 1
    #return HttpResponse(f'PDF généré avec succès! <a href="{download_url}" download>Télécharger le PDF</a>')
    # Retourner le PDF comme réponse HTTP
    #response = HttpResponse(pdf_file, content_type="application/pdf")
    #response['Content-Disposition'] = 'inline; filename="rapport.pdf"'

    return response
        # Renvoyer les pages générées au template
    return render(
            request, "rapports/griffe_de_passage_medical.html", {"pages": pages, "deleg":eee}
        )

    return render(request, "rapports/griffe_de_passage_medical.html")


def generate_pages(request):
    if request.method == "POST":
        eee = request.POST.get("user-select")
        date_debut = request.POST.get("date_debut")
        date_fin = request.POST.get("date_fin")

        # Convertir les dates en objets datetime
        date_debut = datetime.strptime(date_debut, "%Y-%m-%d")
        date_fin = datetime.strptime(date_fin, "%Y-%m-%d")

        # Calculer le nombre de jours entre les deux dates
        delta = date_fin - date_debut

        # Liste pour stocker les pages générées
        pages = []

        for i in range(delta.days + 1):
            # Date pour chaque jour
            current_date = date_debut + timedelta(days=i)

            # Générer un identifiant unique pour le QR code
            if current_date.weekday() in [4, 5]:
                continue  # Passer au jour suivant si c'est vendredi ou samedi

            unique_id = "".join(
                random.choices(string.ascii_letters + string.digits, k=8)
            )

            # Générer l'URL du QR code avec Google Chart API
            qr_code_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={unique_id}"
            print("generating qr code " + str(unique_id))
            qr_code_instance = QRCodeModel(identifier=unique_id)
            qr_code_instance.save()

            # Ajouter la page avec la date et le QR code à la liste
            pages.append(
                {
                    "nom":eee,
                    "date": current_date.strftime("%a. %d/%m/%Y"),
                    "qr_code_url": qr_code_url,  # URL du QR code unique
                }
            )

        # Renvoyer les pages générées au template
        return render(
            request, "rapports/griffe_de_passage_medical.html", {"pages": pages, "deleg":eee}
        )

    return render(request, "rapports/griffe_de_passage_medical.html")


# def generate_pages_pharmacie(request):
#     if request.method == "POST":
#         print("called here baby --")
#         date_debut = request.POST.get("date_debut")
#         date_fin = request.POST.get("date_fin")

#         # Convertir les dates en objets datetime
#         date_debut = datetime.strptime(date_debut, "%Y-%m-%d")
#         date_fin = datetime.strptime(date_fin, "%Y-%m-%d")

#         # Calculer le nombre de jours entre les deux dates
#         delta = date_fin - date_debut

#         # Liste pour stocker les pages générées
#         pages = []

#         for i in range(delta.days + 1):
#             # Date pour chaque jour
#             current_date = date_debut + timedelta(days=i)

#             # Générer un identifiant unique pour le QR code
#             unique_id = "".join(
#                 random.choices(string.ascii_letters + string.digits, k=8)
#             )

#             # Générer l'URL du QR code avec Google Chart API
#             qr_code_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={unique_id}"
#             print("generating qr code " + str(unique_id))
#             qr_code_instance = QRCodeModel(identifier=unique_id)
#             qr_code_instance.save()

#             # Ajouter la page avec la date et le QR code à la liste
#             pages.append(
#                 {
#                     "date": current_date.strftime("%d/%m/%Y"),
#                     "qr_code_url": qr_code_url,  # URL du QR code unique
#                 }
#             )

#         # Renvoyer les pages générées au template
#         return render(
#             request,
#             "rapports/griffe_de_passage_commercial.html",
#             {"pages": pages, "range_list": range(1, 15)},
#         )

#     return render(request, "rapports/griffe_de_passage_commercial.html")


from datetime import datetime, timedelta
import random
import string
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from downloads.models import Downloadable
from weasyprint import HTML, CSS
def generate_pages_pharmacie_task(user_id):
    print("called here baby --")
    a4_css = CSS(string='''
    @page {
        size: A4;
        margin-top: 0;
        margin-bottom: 0;
        margin-left: 1cm;
        margin-right: 1cm;
    }
    ''')


    #eeee = user_id
    date_debut = "2026-04-01"
    date_fin = "2026-04-30"
    user_id = int(user_id)
    eee = User.objects.get(id=user_id)
    Downloadable.objects.filter(link_name = f"Griffe de passage pharmacie_{eee.username}_2").delete()
    # Vérifier si les champs requis sont fournis
    if not date_debut or not date_fin:
        raise ValueError("Les champs 'date_debut' et 'date_fin' sont obligatoires")

    # Convertir les dates en objets datetime
    date_debut = datetime.strptime(date_debut, "%Y-%m-%d")
    date_fin = datetime.strptime(date_fin, "%Y-%m-%d")

    # Calculer le nombre de jours entre les deux dates
    delta = date_fin - date_debut

    # Liste pour stocker les pages générées
    pages = []

    for i in range(delta.days + 1):
            # Date pour chaque jour
            current_date = date_debut + timedelta(days=i)

            # Vérifier si le jour est un vendredi (4) ou un samedi (5)
            if current_date.weekday() in [4, 5]:
                continue  # Passer au jour suivant si c'est vendredi ou samedi

            # Générer un identifiant unique pour le QR code
            unique_id = "".join(
                random.choices(string.ascii_letters + string.digits, k=8)
            )

            # Générer l'URL du QR code avec Google Chart API
            qr_code_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={unique_id}"
            print("generating qr code " + str(unique_id))
            qr_code_instance = QRCodeModel(identifier=unique_id)
            qr_code_instance.save()

            # Ajouter la page avec la date et le QR code à la liste
            pages.append(
                {
                    "nom":f"{eee.first_name} {eee.last_name}"+" (1/2)",
                    "date": current_date.strftime("%a. %d/%m/%Y"),
                    "qr_code_url": qr_code_url,  # URL du QR code unique
                }
            )
            pages.append(
                    {
                        "nom": f"{eee.first_name} {eee.last_name}"+" (2/2)",
                        "date": current_date.strftime("%a. %d/%m/%Y"),
                        "qr_code_url": qr_code_url,  # URL du QR code unique
                    }
                )


    # Rendre les pages dans un template HTML
    html_content = render_to_string(
                "rapports/gp.html", 
                {"pages": pages, "range_list": range(1, 8)}
            )

    # Générer le PDF à partir du contenu HTML
    pdf_file = HTML(string=html_content).write_pdf(stylesheets=[a4_css])

    save_path = os.path.join(settings.MEDIA_ROOT, 'downloadable', f"Griffe_de_passage_pharmacie_{eee.username}_2.pdf")
    with open(save_path, 'wb') as f:
                f.write(pdf_file)
    download_url = os.path.join(settings.MEDIA_URL, 'downloable', os.path.basename(save_path))
    
    downloadable = Downloadable.objects.create(attachement=f"downloadable/Griffe_de_passage_pharmacie_{eee.username}_2.pdf", link_name = f"Griffe de passage pharmacie_{eee.username}_2")
    
    downloadable.users.set([eee])
    return 1
    #return HttpResponse(f'PDF généré avec succès! <a href="{download_url}" download>Télécharger le PDF</a>')
    # Retourner le PDF comme réponse HTTP
    #response = HttpResponse(pdf_file, content_type="application/pdf")
    #response['Content-Disposition'] = 'inline; filename="rapport.pdf"'

    return response
    return render(request, "rapports/griffe_de_passage_commercial.html")

    print(f"PDF généré pour {eee.username}")
def generate_pages_pharmacie(request):
    if request.method == "POST":
        print("called here baby --")
        eee = request.POST.get("user-select")
        date_debut = request.POST.get("date_debut")
        date_fin = request.POST.get("date_fin")

        # Convertir les dates en objets datetime
        date_debut = datetime.strptime(date_debut, "%Y-%m-%d")
        date_fin = datetime.strptime(date_fin, "%Y-%m-%d")

        # Calculer le nombre de jours entre les deux dates
        delta = date_fin - date_debut

        # Liste pour stocker les pages générées
        pages = []

        for i in range(delta.days + 1):
            # Date pour chaque jour
            current_date = date_debut + timedelta(days=i)

            # Vérifier si le jour est un vendredi (4) ou un samedi (5)
            if current_date.weekday() in [4, 5]:
                continue  # Passer au jour suivant si c'est vendredi ou samedi

            # Générer un identifiant unique pour le QR code
            unique_id = "".join(
                random.choices(string.ascii_letters + string.digits, k=8)
            )

            # Générer l'URL du QR code avec Google Chart API
            qr_code_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={unique_id}"
            print("generating qr code " + str(unique_id))
            qr_code_instance = QRCodeModel(identifier=unique_id)
            qr_code_instance.save()

            # Ajouter la page avec la date et le QR code à la liste
            pages.append(
                {
                    "nom":eee + "(1/2)",
                    "date": current_date.strftime("%a. %d/%m/%Y"),
                    "qr_code_url": qr_code_url,  # URL du QR code unique
                }
            )
            pages.append(
                    {
                        "nom": eee+" (2/2)",
                        "date": current_date.strftime("%a. %d/%m/%Y"),
                        "qr_code_url": qr_code_url,  # URL du QR code unique
                    }
                )

        # Renvoyer les pages générées au template
        return render(
            request,
            "rapports/griffe_de_passage_commercial.html",
            {"pages": pages, "range_list": range(1, 8)},
        )

    return render(request, "rapports/griffe_de_passage_commercial.html")


class griffePassageFront(APIView):
    authentication_classes = (
        TokenAuthentication,
        SessionAuthentication,
    )

    def get(self, request):
        return render(request, "rapports/griffe_de_passage_medical.html")


class griffePassagePharmacieFront(APIView):
    authentication_classes = (
        TokenAuthentication,
        SessionAuthentication,
    )

    def get(self, request):
        return render(request, "rapports/griffe_de_passage_commercial.html")


# from django.utils import timezone
# from django.http import JsonResponse
# from django.template.loader import render_to_string
# from weasyprint import HTML
# import random
# import string
# from django.core.files.base import ContentFile
# from .models import GeneratedPDF  # Ensure you import your model
# import logging

# logger = logging.getLogger(__name__)


# def generate_pdf_view(request):
#     if request.method == "POST":
#         # Get the current date range for the current month
#         today = timezone.now()
#         date_debut = today.replace(day=1)  # First day of the current month
#         next_month = (today.month % 12) + 1  # Next month
#         year = today.year + (today.month // 12)  # Adjust year if December
#         date_fin = timezone.datetime(
#             year, next_month, 1, tzinfo=timezone.utc
#         ) - timezone.timedelta(
#             days=1
#         )  # Last day of current month

#         # Generate pages data
#         pages = []
#         user_name = request.user.get_full_name() or request.user.username

#         # Calculate the number of days in the current month
#         delta = (date_fin - date_debut).days

#         for i in range(delta + 1):
#             current_date = date_debut + timezone.timedelta(days=i)
#             unique_id = "".join(
#                 random.choices(string.ascii_letters + string.digits, k=8)
#             )
#             qr_code_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={unique_id}"

#             pages.append(
#                 {
#                     "date": current_date.strftime("%d/%m/%Y"),
#                     "qr_code_url": qr_code_url,
#                     "user_name": user_name,
#                 }
#             )

#         # Log the pages data
#         logger.debug("Generated pages data: %s", pages)

#         # Render the HTML for the pages
#         html_string = render_to_string(
#             "rapports/griffe_de_passage_medical_2.html", {"pages": pages}
#         )

#         # Log the HTML string
#         logger.debug("Generated HTML string: %s", html_string)

#         # Convert HTML to PDF
#         pdf_file_content = HTML(string=html_string).write_pdf()

#         # Check if the PDF content is empty
#         if not pdf_file_content:
#             logger.error("Generated PDF content is empty.")
#             return JsonResponse({"message": "Error: PDF content is empty."}, status=500)

#         # Save the PDF to the model with ContentFile
#         pdf_instance = GeneratedPDF(
#             title=f"Griffe de passage - {today.strftime('%Y_%m')}",
#             user=request.user,  # Set the user field to the currently logged-in user
#         )
#         pdf_instance.pdf_file.save(
#             f"griffe_de_passage_{today.strftime('%Y_%m')}.pdf",
#             ContentFile(pdf_file_content),
#         )

#         return JsonResponse(
#             {
#                 "message": "PDF generated and saved successfully!",
#                 "pdf_url": pdf_instance.pdf_file.url,
#             }
#         )

#     return render(
#         request, "rapports/generate_pdf.html"
#     )  # Optional: A simple HTML page for the form


def reports_front(request):
    return render(request, "rapports/index-test.html")





def anomalies_print_view(request):
    # Récupérer l'ID de l'utilisateur à partir des paramètres de la requête
    user_id = request.GET.get('user_id')

    # Filtrer les anomalies par date d'aujourd'hui
    anomalies = Anomalies.objects.all()
    print("------>"+str(user_id))

    # Si l'ID de l'utilisateur est présent dans la requête, filtrer par cet utilisateur
    if user_id:
        print("use id getted")
        anomalies = anomalies.filter(user_id=user_id)
        print("------>"+str(anomalies))

    context = {
        'anomalies': anomalies,
        'today': now().date(),
    }
    return render(request, 'anomalies/anomalies_print.html', context)
