from django.db import models
from django.contrib.auth.models import User
import datetime
from django.db.models.signals import post_save, post_delete
from django.shortcuts import get_object_or_404
from rest_framework.authtoken.models import Token
from re import sub
import hashlib
import os
from binascii import hexlify
from regions.models import *
from medecins.models import Medecin
from rapports.models import *

from produits.models import Produit
from plans.models import Plan
from django.db.models import Count
from produits.models import Produit, ProduitVisite
import datetime
import calendar
from django.core.validators import RegexValidator


class UserProxyManager(models.Manager):
    def get_queryset(self):
        try:
            return (
                super(UserProxyManager, self)
                .get_queryset()
                .filter(userprofile__hidden=False)
            )
        except:
            return super(UserProxyManager, self).get_queryset()

    # pass


class UserProxy(User):
    class Meta:
        proxy = True
        verbose_name = "User"
        verbose_name_plural = "Users"

    objects = UserProxyManager()


# class UserProxyMiddleWare(object):
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         header_token = request.META.get('HTTP_AUTHORIZATION', None)
#         if header_token is not None:
#             try:
#                 token = header_token.split(' ')[-1]
#                 token_obj = Token.objects.get(key = token)
#                 request.user = get_object_or_404(UserProxy, id=token_obj.user.id)
#             except Token.DoesNotExist:
#                 pass
#         return self.get_response(request)


numeric = RegexValidator(r"^\d+$", "Enter a valid numeric value.")


class SpecialityRolee(models.TextChoices):
    medico_commercial = "Medico_commercial"
    commercial = "Commercial"
    superviseur_regional = "Superviseur_regional"
    superviseur_national = "Superviseur_national"
    superviseur = "Superviseur"
    countrymanager = "CountryManager"
    admin = "Admin"
    Office = "Office"
    chargé_de_communication = "chargé_de_communication"
    gestionnaire_de_stock = "gestionnaire_de_stock"
    Finance_et_comptabilité = "Finance_et_comptabilité"

class Region(models.TextChoices):
    ouest = "Ouest"
    est = "Est"
    centre = "Centre"
    sud = "Sud"
    Vide = "-"
class Rolee(models.TextChoices):
    commercial = "Commercial"
    superviseur = "Superviseur"
    countrymanager = "CountryManager"


class Gender(models.TextChoices):
    homme = "Homme"
    femme = "femme"


class Situation(models.TextChoices):
    celibataire = "celibataire"
    maried = "marrié"


class family(models.TextChoices):
    lilium_Pharma = "lilium Pharma"
    lilium1 = "Lilium1"
    lilium2 = "Lilium2"
    orient = "orient Bio"
    aniya_pharm = "Aniya_Pharm"
    production = "production"
    administration = "Administration"


class Company(models.TextChoices):
    lilium_Pharma = "lilium pharma"
    production = "production"
    orient_bio = "orient bio"
    aniya_pharm = "aniya pharma"
    all_ = "all"


def createactive():
    return hashlib.md5(str(datetime.datetime.now()).encode()).hexdigest()


class SectionFamily(models.TextChoices):
    MED = "MED"
    ADMIN = "ADMIN"
    COM = "COM"


class ContractFamily(models.TextChoices):
    CDD = "CDD"
    CDI = "CDI"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null="True")
    company = models.CharField(
        max_length=40,
        choices=Company.choices,
        default=Company.lilium_Pharma,
        verbose_name="Employee of",
    )
    family = models.CharField(
        max_length=40, choices=family.choices, default=family.lilium1
    )
    speciality_rolee = models.CharField(
        max_length=35,
        choices=SpecialityRolee.choices,
        default=SpecialityRolee.commercial,
    )
    rolee = models.CharField(
        max_length=35, choices=Rolee.choices, default=Rolee.commercial
    )
    telephone = models.CharField(null="True", max_length=10, blank=True)
    adresse = models.CharField(max_length=325, default="alger")
    commune = models.ForeignKey(Commune, on_delete=models.CASCADE, null="true")
    activate = models.CharField(max_length=255, unique="True", blank=True, null=True)
    # ---------------------
    # IN TEST
    # -----------------------
    usersunder = models.ManyToManyField(User, related_name="under", blank=True)
    can_send_receive_tasks = models.BooleanField(default=False)
    can_add_medecin = models.BooleanField(default=False)
    can_update_medecin = models.BooleanField(default=False)
    can_add_client = models.BooleanField(default=False)
    can_view_visites = models.BooleanField(default=False)
    notification_token = models.CharField(max_length=255, blank=True, null=True)
    ios_notification_token = models.CharField(max_length=255, blank=True, null=True)
    recive_mail = models.BooleanField(default=True)
    gender = models.CharField(
        max_length=15, choices=Gender.choices, default=Gender.homme
    )
    region = models.CharField(
        max_length=35,
        choices=Region.choices,
        default=Region.Vide,
    )
    # Target Fields
    sectors = models.ManyToManyField(to=Wilaya, null=True, blank=True)

    CNAS = models.CharField(max_length=255, null=True, blank=True)
    entry_date = models.DateField(default=datetime.date.today())
    conge = models.FloatField(max_length=255, default=0)
    bank_account = models.CharField(max_length=255, null=True, blank=True)
    bank_name = models.CharField(max_length=255, null=True, blank=True)
    pc_paie_id = models.CharField(
        max_length=255, null=True, blank=True, validators=[numeric]
    )
    situation = models.CharField(
        max_length=15, choices=Situation.choices, default=Situation.celibataire
    )
    job_name = models.CharField(max_length=255, null=True, blank=True)

    code_section = models.CharField(
        max_length=100,
        choices=SectionFamily.choices,
        null=True,
        blank=True,
        default=SectionFamily.MED,
    )
    code_contrat = models.CharField(
        max_length=100,
        choices=ContractFamily.choices,
        null=True,
        blank=True,
        default=ContractFamily.CDD,
    )

    salary = models.PositiveIntegerField(null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    contract = models.FileField(blank=True, null=True, verbose_name="scanned contract")
    hidden = models.BooleanField(default=False)

    work_as_commercial = models.BooleanField(default=False)
    is_human = models.BooleanField(default=True)

    def __str__(self):
        return self.user.username

    @property
    def user_nom(self):
        return self.user.first_name + " " + self.user.last_name

    @property
    def user_email(self):
        return self.user.email

    @property
    def user_rapports(self):
        return len(Rapport.objects.filter(user=self.user))

    @property
    def user_region(self):
        return (
            self.commune.wilaya.pays.nom
            + " "
            + self.commune.wilaya.nom
            + " "
            + self.commune.nom
        )

    @property
    def user_visitess_details(self):

        today = datetime.date.today()
        months = [
            "",
            "Jan",
            "Fev",
            "Mar",
            "Avr",
            "Mai",
            "Jui",
            "Juil",
            "Aut",
            "Sep",
            "Oct",
            "Nov",
            "Déc",
        ]
        m = today.month
        y = today.year
        visites = ""
        for i in range(6):
            mm = m - i if m - i != 0 else 12
            if mm < 0:
                mm = 12 - (i - m)
            nbr_visite = len(
                Visite.objects.filter(
                    rapport__user=self.user,
                    rapport__added__month=mm,
                    rapport__added__year=y,
                )
            )
            visites += f"{months[mm]}: {nbr_visite}, "
        return visites

    @property
    def user_visites_month(self):
        from rapports.models import Visite


        today = datetime.date.today()
        m = today.month
        y = today.year
        visites = ""
        nbr_visite = len(
            Visite.objects.filter(
                rapport__user=self.user, rapport__added__month=m, rapport__added__year=y
            )
        )
        return nbr_visite

    # HERE IS PORTION OF CODE IN LIST RAPPORT TO DISPLAY INFORMATIONS PER MONTH
    @property
    def monthly_rapport_details(self):
        from rapports.models import Rapport
        from rapports.models import Visite


        current_month = datetime.datetime.now().month
        current_year = datetime.datetime.now().year

        # Obtenir le nombre de jours dans le mois en cours
        nbr_jour_mois = calendar.monthrange(current_year, current_month)[1]

        # Compter le nombre de jours ouvrables (en excluant les vendredis et samedis)
        working_days = 0
        for day in range(1, nbr_jour_mois + 1):
            date = datetime.datetime(current_year, current_month, day)
            if date.weekday() not in [4, 5]:  # 4: Vendredi, 5: Samedi
                working_days += 1

        # GETTING MONTHLY DATA
        rapports = Rapport.objects.filter(
            user=self.user,
            added__month=datetime.datetime.now().month,
            added__year=datetime.datetime.now().year,
        ).order_by("-added")
        visites = Visite.objects.filter(rapport__in=rapports)
        medecins = Medecin.objects.filter(visite__in=visites)
        other_details = f"<b style='font-size:15px;color:grey'>Nombre des rapports ce mois </b><b style='font-size:15px; color:green'><b style='color:red'>({len(rapports)})</b> / ({working_days})</b><br/>"

        total_similarity_percentage = 0
        plan_count = 0
        specialites_a_exclure = ["Pharmacie", "Grossiste", "SuperGros"]

        # Filter Rapport objects
        rapports = Rapport.objects.filter(
            added__month=datetime.datetime.now().month,
            added__year=datetime.datetime.now().year,
            user=self.user.id,
        )

        # Count plans and calculate total similarity percentage
        plan_count = rapports.count()
        total_similarity_percentage = 0

        for plan in Plan.objects.filter(
            user=self.user.id,
            day__month=datetime.datetime.now().month,
            day__year=datetime.datetime.now().year,
        ):
            clients_list = plan.clients.all()
            o = Rapport.objects.filter(added=plan.day, user=plan.user)
            matching_doctors = (
                Visite.objects.filter(rapport__in=o, medecin__in=clients_list)
                .distinct()
                .count()
            )
            if plan.plantask_set.exists():
                total_similarity_percentage += 100
            else:
                client_list_count = clients_list.count() or 1
                #similarity_percentage = (matching_doctors / client_list_count) * 100
                similarity_percentage = round((matching_doctors / client_list_count) * 100, 2)
                total_similarity_percentage += similarity_percentage

        # Calculate average similarity percentage
        average_similarity_percentage = (
            total_similarity_percentage / plan_count if plan_count else 0
        )

        # Format color based on average similarity percentage
        if average_similarity_percentage < 30:
            color = "red"
        elif 30 <= average_similarity_percentage < 50:
            color = "orange"
        else:
            color = "green"
        if average_similarity_percentage > 100:
            average_similarity_percentage = 100
        # Display details
        other_details += f"<p style='font-weight: bold; margin: 0;font-size:16px; color:black'>Moyenne Similarité Planning / Rapport: <span style='font-weight:bold; color:{color}'>{int(average_similarity_percentage)}%</span></p>"

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
        details_distinct = (
            Medecin.objects.filter(id__in=medecins.values("id"))
            .distinct()
            .values("specialite")
            .annotate(dcount=Count("specialite"))
        )

        other_details += f"<b style='font-size:15px;color:grey'> Total des <span style='color:red'>visites</span> ce mois </b><b style='font-size:15px; color:green'>({len(medecins)})</b><br/>"
        # TOTAL DES VISITES MED/COM SPECIALITIES
        other_specialties = []
        end_specialties = []

        for detail in details:
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
            f"<b style='font-size:14px;color:green'> ({(medecin_commercial)}) Commercial:</b> "
            + " ".join(
                [
                    f'<b>({detail["dcount"]})</b> {detail["specialite"]} '
                    for detail in commercial_specialties
                ]
            )
        )
        other_details += f"</span>"
        other_details += "</br>"

        other_details += f"<b style='font-size:15px;color:grey'> Total des <span style='color:red'>clients</span> ce mois </b><b style='font-size:15px; color:green'>({medecin_nbr+medecin_commercial_client})</b><br/>"

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
        return other_details


    # @property
    # def monthly_rapport_details(self):
    #     # current_month = datetime.datetime.now().month
    #     # current_year = datetime.datetime.now().year

    #     # Obtenir le nombre de jours dans le mois en cours
    #     # nbr_jour_mois = calendar.monthrange(current_year, current_month)[1]

    #     other_details = "ccccccc"

        # # PRODUITS PRESENTES MEDICAL
        # other_details+="<b style='font-size:16px'><span style='color:red' >Medical</span><span style='color:grey'> Produits presentés ce mois:<span></b></br>"
        # product_info = {}

        # for p in Produit.objects.all():
        #     excluded_specialties = ["Pharmacie", "Grossiste", "Supergros"]
        #     len_visits = len(visites.exclude(medecin__specialite__in=excluded_specialties).filter(produits__id=p.id))
        #     product_info[p.nom] = len_visits

        # sorted_products = sorted(product_info.items(), key=lambda x: x[1], reverse=True)

        # count_med = 0

        # for product, len_visits in sorted_products:
        #     if len_visits > 0:
        #         product_string = f"<b style='font-size:13px; color:grey'>({product} : <b style='color:green'>{len_visits} fois</b> )</b>"
        #         other_details += product_string + " "
        #         count_med += 1
        #         if count_med % 3 == 0:
        #             other_details += "</br>"

        # if (count_med % 3 > 0):
        #     other_details+="<br/>"

        # PRODUITS PRESENTES COMMERCIAL
        # other_details+="<b style='font-size:16px'><span style='color:red' >Commercial</span> <span style='color:grey'> Produits presentés ce mois:</span></b></br>"
        # product_info = {}
        # for p in Produit.objects.all():
        #     included_specialties = ["Pharmacie", "Grossiste", "Supergros"]
        #     len_visits = len(visites.filter(medecin__specialite__in=included_specialties).filter(produits__id=p.id))
        #     product_info[p.nom] = len_visits

        # sorted_products = sorted(product_info.items(), key=lambda x: x[1], reverse=True)

        # count = 0

        # for product, len_visits in sorted_products:
        #     if len_visits > 0:
        #         product_string = f"<b style='font-size:13px; color:grey'>({product} : <b style='color:green'>{len_visits} fois</b> )</b>"
        #         other_details += product_string + " "
        #         count += 1
        #         if count % 3 == 0:
        #             other_details += "</br>"

        # if (count % 3 > 0):
        #     other_details+="<br/>"

        # STOCK DISPONIBLE
        # other_details += f"<span style='font-size:16px; color:red;'>Stock disponible ce mois:</span><br>"
        # string=''
        # prod = Produit.objects.filter(productcompany__family='lilium pharma')

        # for p in prod:
        #     included_specialties = ["Pharmacie", "Grossiste", "Supergros"]
        #     visits = visites.filter(medecin__specialite__in=included_specialties, produits__id=p.id)
        #     total_qtt = ProduitVisite.objects.filter(visite__in=visits, produit=p)
        #     qtt = 0
        #     string = ""
        #     for produit_visite in total_qtt:
        #         qtt += produit_visite.qtt
        #     string += f"<b style='font-size:10px; color:black'>{p.nom}</b>: {qtt}  -   "
        #     other_details += f"{string}"

        # return other_details

    @property
    def ismale(self):
        return self.gender == "Homme"

    # def get_users_to_notify(self):
    #     users_to_notify_set = {
    #         u.user
    #         for u in [
    #             *UserProfile.objects.filter(rolee="CountryManager", commune__wilaya__pays=self.commune.wilaya.pays),
    #             *UserProfile.objects.filter(usersunder=self.user)
    #         ] if u.notification_token
    #     } | set(User.objects.filter(is_superuser=True, userprofile__notification_token__isnull=False))

    #     users_to_notify = list(users_to_notify_set)
    #     print(f"Users to notify: {users_to_notify}")
    #     return users_to_notify

    def get_users_to_notify(self):
        users_to_notify_set = {
            u.user
            for u in [
                # *UserProfile.objects.filter(rolee="CountryManager", commune__wilaya__pays=self.commune.wilaya.pays),
                *UserProfile.objects.filter(
                    speciality_rolee="Superviseur_regional",
                    commune__wilaya__pays=self.commune.wilaya.pays,
                    usersunder=self.user,
                ),
                *UserProfile.objects.filter(
                    speciality_rolee="Superviseur_national",
                    commune__wilaya__pays=self.commune.wilaya.pays,
                    usersunder=self.user,
                ),
            ]
            if u.notification_token
        }

        users_to_notify = list(users_to_notify_set)
        print(f"Users to notify: {users_to_notify}")
        return users_to_notify

    # def is_superior(self,usr=None):
    #     if self.rolee in ["Superviseur","CountryManager"] or self.user.is_superuser or self.user.username  in ["ibtissemdz","liliumdz"]:
    #         if self.rolee == "Superviseur":
    #             if usr not in self.usersunder.all()
    #                 return False
    #             return True
    #         return False


# def create_profile(sender, **kwargs):
#     if kwargs['created']:
#         user_profile = UserProfile.objects.create(user=kwargs['instance'],activate=createactive(),commune=Commune.objects.get(id=1))

# post_save.connect(create_profile, sender=User)


class UserProduct(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    product = models.ForeignKey(to=Produit, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(verbose_name="Target Quantity")

    class Meta:
        verbose_name = "Product Target"
        verbose_name_plural = "Products Target"


class UserFile(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    ffile = models.FileField()


class UserNotificationPermissions(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Permissions de notification
    can_receive_notification_comment = models.BooleanField(
        default=True
    )  # Notification de commentaire
    can_receive_notification_validation_planning = models.BooleanField(
        default=True
    )  # Notification de validation de planning
    can_receive_notification_bon_commande = models.BooleanField(
        default=True
    )  # Notification de bon de commande
    can_receive_notification_bon_sortie = models.BooleanField(
        default=True
    )  # Notification de bon de sortie
    can_receive_notification_versement = models.BooleanField(
        default=True
    )  # Notification de versement
    can_receive_notification_evaluation = models.BooleanField(
        default=True
    )  # Notification d'évaluation

    def __str__(self):
        return f"Notifications settings for {self.user.username}"

    class Meta:
        verbose_name_plural = "Notification"


class PersonalInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='personal_info')

    # Basic personal information
    nom = models.CharField(max_length=255, null=True, blank=True)
    prénom = models.CharField(max_length=255, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=15, choices=Gender.choices, null=True, blank=True)
    situation = models.CharField(max_length=15, choices=Situation.choices, null=True, blank=True)

    # Contact information
    email = models.EmailField(null=True, blank=True)
    telephone = models.CharField(max_length=15, null=True, blank=True)
    telephone_parent = models.CharField(max_length=15, null=True, blank=True)
    adresse = models.TextField(null=True, blank=True)
    commune = models.CharField(max_length=255, null=True, blank=True)

    # Employment information
    job_name = models.CharField(max_length=255, null=True, blank=True)
    code_section = models.CharField(max_length=100, choices=SectionFamily.choices, null=True, blank=True)
    code_contrat = models.CharField(max_length=100, choices=ContractFamily.choices, null=True, blank=True)
    pc_paie_id = models.CharField(max_length=255, null=True, blank=True)
    salary = models.PositiveIntegerField(null=True, blank=True)

    # Bank and other information
    cans = models.CharField(max_length=255, null=True, blank=True)
    bank_name = models.CharField(max_length=255, null=True, blank=True)
    bank_account = models.CharField(max_length=255, null=True, blank=True)

    # Documents
    carte_identite_scan = models.ImageField(upload_to='carte_identite/', null=True, blank=True)
    documents = models.FileField(upload_to='user_documents/', null=True, blank=True)

    def __str__(self):
        return f"{self.nom} {self.prénom}'s Personal Info"

