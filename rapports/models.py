from collections import defaultdict
from django.db import models
from django.dispatch import receiver
import datetime
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from clients.models import UserTargetMonth, UserTargetMonthProduct
from medecins.models import Medecin, MEDICAL, COMMERCIAL
from produits.models import Produit, ProduitVisite
from django.db.models import Count
from django.utils import timezone
from django.core.exceptions import ValidationError
from plans.models import Plan
from django.contrib.humanize.templatetags.humanize import naturalday
from notifications.models import Notification
from deals.models import Deal
import json
from django.db.models import Sum
from django.db.models.signals import post_save, pre_delete, post_delete, pre_save


from leaves.models import Absence


def upload_location(instance, filename):
    dte = str(datetime.datetime.today().date())
    dte = dte.replace("-", "")
    return f'rapports/{instance.user.username}/{instance.user.username}{dte}.{filename.split(".")[-1]}'


def upload_location2(instance, filename):
    dte = str(datetime.datetime.today().date())
    dte = dte.replace("-", "")
    return f'rapports/{instance.user.username}/{instance.user.username}{dte}2.{filename.split(".")[-1]}'


class Rapport(models.Model):
    added = models.DateField(default=timezone.now, blank=True, db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=upload_location)
    image2 = models.ImageField(blank=True, null=True, upload_to=upload_location2)
    can_update = models.BooleanField(default=True)
    note = models.PositiveIntegerField(default=0, db_index=True)
    observation = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ("added", "user")

    def __str__(self):
        return str(self.added) + self.user.username

    def is_updatable(self):
        if self.added == datetime.datetime.today().date():
            return True
        else:
            return self.can_update

    def stars(self):
        return range(self.note)

    @property
    def rapport_region(self):
        return {"communes": self.user.userprofile.commune.nom}

    @property
    def rapport_regions(self):
        return ", ".join(
            [v.medecin.commune.nom for v in Visite.objects.filter(rapport=self)]
        )

    @property
    def rapport_commercial(self):
        commercial = self.user.userprofile
        return {
            "nom": f"{commercial.user.first_name} {commercial.user.last_name} ",
            # "telephone":commercial.telephone,
            # "email":commercial.user.email,
            "pays": commercial.commune.wilaya.pays.nom,
            "visites_month": commercial.user_visites_month,
            "other_details": commercial.monthly_rapport_details,
            "username": commercial.user.username,
        }

    @property
    def visites_list(self):
        visites = Visite.objects.filter(rapport=self)
        visites_list = []
        for visite in visites:
            visites_list.append(
                {
                    "id": visite.id,
                    "observation": visite.observation,
                    # "priorite":visite.priority,
                    "produits": visite.products_to_json(),
                    "medecin": {
                        "id": visite.medecin.id,
                        "nom": visite.medecin.nom,
                        "specialite": visite.medecin.specialite,
                        "classification": visite.medecin.classification,
                        "telephone": visite.medecin.telephone,
                        "deals": [
                            deals.id
                            for deals in Deal.objects.filter(
                                medecin__id=visite.medecin.id
                            )
                        ],
                    },
                    # "commune":visite.medecin.commune.nom,
                }
            )
        return visites_list

    # @property
    # def rapport_details(self):

    #     produits=Produit.objects.filter(pays=self.user.userprofile.commune.wilaya.pays)
    #     month = self.added.month

    #     user = self.user.username

    #     visites=Visite.objects.filter(rapport=self)

    #     medecins=Medecin.objects.filter(visite__in=visites).distinct()

    #     medecin_nbr=len(medecins)-len(medecins.filter(specialite__in=['Pharmacie','Grossiste',"SuperGros"]))
    #     medecin_commercial=len(medecins.filter(specialite__in=['Pharmacie','Grossiste',"SuperGros"]))

    #     details=Medecin.objects.filter(id__in=medecins.values("id")).values('specialite').annotate(dcount=Count('specialite'))

    #     other_details=f"<b>({len(visites)})</b> visites<br/><b>({len(medecins) + medecin_commercial})</b> Clients<br/>"
    #     other_details=f"Nombre total des visites <b>({medecin_nbr})</b><br/><b>({medecin_nbr})</b> Medical | <b>({medecin_commercial})</b> Commercial<br/>"
    #     # other_details+=f"<b>({medecin_nbr})</b> medecins<br/>"
    #     other_details+=" ".join([f'<b>({detail["dcount"]})</b> {detail["specialite"]} ' for detail in details])
    #     other_details+="<br/>"
    #     # other_details+=" ".join(["<b>("+str(len(visites.filter(produits__id=produit.id)))+")</b> "+produit.nom for produit in produits])
    #     user_target_months = UserTargetMonth.objects.filter(user=self.user, date__month = month)
    #     for user_target_month in user_target_months:
    #         user_target_month_products = UserTargetMonthProduct.objects.filter(usermonth=user_target_month)

    #         for p in user_target_month_products:
    #             len_visits = len(visites.filter(produits__id=p.product.id))
    #             product_string = f"<b>({len_visits})</b> {p.product.nom}"
    #             other_details += product_string + " "

    #     return other_details

    # @property
    # def rapport_details(self):

    #     produits=Produit.objects.filter(pays=self.user.userprofile.commune.wilaya.pays)
    #     month = self.added.month
    #     user = self.user.username
    #     visites=Visite.objects.filter(rapport=self)
    #     medecins=Medecin.objects.filter(visite__in=visites).distinct()
    #     medecin_nbr=len(medecins)-len(medecins.filter(specialite__in=['Pharmacie','Grossiste',"SuperGros"]))
    #     medecin_commercial=len(medecins.filter(specialite__in=['Pharmacie','Grossiste',"SuperGros"]))
    #     details=Medecin.objects.filter(id__in=medecins.values("id")).values('specialite').annotate(dcount=Count('specialite'))

    #     # other_details+=f"<b>({medecin_nbr})</b> medecins<br/>"
    #     other_details=""

    #     specialites_a_exclure=["Pharmacie", "Grossiste","SuperGros"]
    #     similarity_percentage=0
    #     for plan in Plan.objects.filter(user=self.user, day=self.added):
    #         matching_doctors = 0
    #         clients_list = plan.clients.exclude(specialite__in=specialites_a_exclure)

    #         rapports = Rapport.objects.filter(added=self.added, user=self.user)
    #         for rapport in rapports:
    #             doctors = Visite.objects.filter(rapport=rapport).exclude(medecin__specialite__in=specialites_a_exclure)
    #             for doctor in doctors :
    #                 doctors_list = doctor.medecin
    #                 if doctors_list in clients_list:
    #                     matching_doctors+=1
    #                 else:
    #                     pass

    #             if len(clients_list) == 0:
    #                 client_list_count = 1
    #             else:
    #                 client_list_count=len(clients_list)

    #             similarity_percentage = (matching_doctors*100)/client_list_count
    #             similarity_percentage = int(similarity_percentage)
    #             if similarity_percentage < 30:
    #                 color = 'red'
    #             elif 30 <= similarity_percentage < 50:
    #                 color = 'orange'
    #             else:
    #                 color = 'green'

    #             reee = f"<b>Similarité Planning / Rapport: <b>{similarity_percentage}%</b></b><br/>"
    #             other_details+=reee
    #             other_details+=''

    #     visited_communes = set()
    #     other_details+=f"<b>Régions visités ce jour : </b>"
    #     for visite in visites:
    #         visited_communes.add((visite.medecin.commune.wilaya.nom + "/" + visite.medecin.commune.nom + " - "))

    #     other_details += ", ".join(visited_communes)

    #     if len(medecins) < 10:
    #         color = 'red'
    #     else:
    #         color = 'green'

    #     other_details+="<br/>"
    #     other_details += f"<b>Total des visites ce jour:</b> <b>({len(medecins)}) clients </b> "

    #     other_specialties = []
    #     end_specialties = []

    #     for detail in details:
    #         if detail["specialite"] in ["SuperGros", "Grossiste", "Pharmacie"]:
    #             end_specialties.append(detail)
    #         else:
    #             other_specialties.append(detail)

    #     sorted_specialties = other_specialties + end_specialties

    #     # Displaying specialties
    #     medical_specialties = [detail for detail in sorted_specialties if detail["specialite"] not in ["SuperGros", "Grossiste", "Pharmacie"]]
    #     commercial_specialties = [detail for detail in sorted_specialties if detail["specialite"] in ["SuperGros", "Grossiste", "Pharmacie"]]

    #     other_details += f"<br/><b>"
    #     other_details += f"<b>({(medecin_nbr)}) Medical:</b> " + " ".join([f'<b>({detail["dcount"]})</b> {detail["specialite"]} ' for detail in medical_specialties])
    #     other_details += "<br/>"
    #     other_details += f"</b>"
    #     other_details += f"<b>"
    #     other_details += f"<b> ({(medecin_commercial)}) Commercial:</b> " + " ".join([f'<b>({detail["dcount"]})</b> {detail["specialite"]} ' for detail in commercial_specialties])
    #     other_details += f"</b>"

    #     # other_details += f"</br><span style='mergin-left:50px'>({(medecin_nbr)}) Medical: </span>" + " ".join([f'<b>({detail["dcount"]})</b> {detail["specialite"]} ' for detail in medical_specialties])
    #     # other_details += "</br>"
    #     # other_details += f'({(medecin_commercial)}) Commercial: ' + " ".join([f'<b>({detail["dcount"]})</b> {detail["specialite"]} ' for detail in commercial_specialties])

    #     # other_details+=" ".join([f'<b>({detail["dcount"]})</b> {detail["specialite"]} ' for detail in details])

    #     # other_details+=f"<b>({len(medecins) + medecin_commercial}) Clients</b>"

    #     # other_details+=" ".join(["<b>("+str(len(visites.filter(produits__id=produit.id)))+")</b> "+produit.nom for produit in produits])
    #     # other_details += f"</br><span style='font-weight: bold;font-size:16px'>Total des clients par jour:</span> <b>({len(medecins)}) : </b> "
    #     other_details+="<br/>"

    #     user_target_months = UserTargetMonth.objects.filter(user=self.user, date__month = month)
    #     other_details+="<b>Medical Produits presentés ce jour:</b><br/>"
    #     # Initialize a dictionary to store product information
    #     product_info = {}
    #     # for user_target_month in user_target_months:
    #     #     user_target_month_products = UserTargetMonthProduct.objects.filter(usermonth=user_target_month)

    #     for p in Produit.objects.all():
    #         # Retrieve visits excluding specific specialties
    #         excluded_specialties = ["Pharmacie", "Grossiste", "Supergros"]
    #         len_visits = len(visites.exclude(medecin__specialite__in=excluded_specialties).filter(produits__id=p.id))

    #         # Add product information to the dictionary
    #         product_info[p.nom] = len_visits

    #     # Sort products based on len_visits from highest to lowest
    #     sorted_products = sorted(product_info.items(), key=lambda x: x[1], reverse=True)

    #     # Construct the string
    #     count_med = 0  # Variable pour compter les produits ajoutés

    #     for product, len_visits in sorted_products:
    #         if len_visits > 0:
    #             product_string = f"<b>({product} : <b>{len_visits} fois</b> )</b>"
    #             other_details += product_string + " "
    #             count_med += 1  # Incrémenter le compteur de produits ajoutés
    #             if count_med % 3 == 0:  # Vérifier si le compteur est un multiple de 2
    #                 other_details += "<br/>"

    #     other_details+="<br/>"

    #     other_details+="<b><b>Commercial</b> Produits presentés ce jour:</b><br/>"
    #     # Initialize a dictionary to store product information
    #     product_info = {}

    #     for p in Produit.objects.all():
    #         # Retrieve visits excluding specific specialties
    #         included_specialties = ["Pharmacie", "Grossiste", "Supergros"]
    #         len_visits = len(visites.filter(medecin__specialite__in=included_specialties).filter(produits__id=p.id))

    #         # Add product information to the dictionary
    #         product_info[p.nom] = len_visits

    #     # Sort products based on len_visits from highest to lowest
    #     sorted_products = sorted(product_info.items(), key=lambda x: x[1], reverse=True)
    #     count=0
    #     # Construct the string
    #     for product, len_visits in sorted_products:
    #         if len_visits > 0:
    #             product_string = f"<b>({product} : <b>{len_visits} fois</b> )</b>"
    #             other_details += product_string + " "
    #             count += 1  # Incrémenter le compteur de produits ajoutés
    #             if count % 3 == 0:  # Vérifier si le compteur est un multiple de 2
    #                 other_details += "<br/>"

    #     other_details+="<br/>"

    #     other_details += f"<b>Stock disponible:</b><br/>"

    #     string=''
    #     prod = Produit.objects.filter(productcompany__family='lilium pharma')

    #     # Iterate over user_target_month_products
    #     for p in prod:
    #         # Retrieve visits excluding specific specialties
    #         included_specialties = ["Pharmacie", "Grossiste", "Supergros"]
    #         visits = visites.filter(medecin__specialite__in=included_specialties, produits__id=p.id)  # Assuming p represents the current product
    #         # Calculate total quantity
    #         total_qtt = ProduitVisite.objects.filter(visite__in=visits, produit=p)
    #         # Initialize total quantity for the product
    #         qtt = 0
    #         string = ""
    #         # Sum up the quantities for the product
    #         for produit_visite in total_qtt:
    #             qtt += produit_visite.qtt
    #         # Format the string for the product
    #         string += f"<b>{p.nom}</b>: {qtt}  -   "
    #         other_details += f"{string}"

    #     # other_details += f"{string}"

    #     # Sort products based on len_visits from highest to lowest
    #     # sorted_products = sorted(product_info.items(), key=lambda x: x[1], reverse=True)

    #     # Construct the string
    #     # for product, len_visits in sorted_products:
    #     #     product_string = f"<b style='font-size:13px'>({product} : <b style='color:green'>{len_visits} fois</b> )</b>"
    #     #     other_details += product_string + " "

    #     other_details+="<br/>"

    #     return other_details

    # @property
    # def rapport_details(self):
    #     # Retrieve required objects
    #     produits = Produit.objects.filter(
    #         pays=self.user.userprofile.commune.wilaya.pays
    #     )
    #     visites = Visite.objects.filter(rapport=self)
    #     # visites = self.visite_set.all()
    #     medecins = Medecin.objects.filter(visite__in=visites).distinct()
    #     medecin_nbr = medecins.exclude(
    #         specialite__in=["Pharmacie", "Grossiste", "SuperGros"]
    #     ).count()
    #     medecin_commercial = medecins.filter(
    #         specialite__in=["Pharmacie", "Grossiste", "SuperGros"]
    #     ).count()
    #     other_details = ""
    #     details = (
    #         Medecin.objects.filter(id__in=medecins.values("id"))
    #         .values("specialite")
    #         .annotate(dcount=Count("specialite"))
    #     )

    #     # # Initialize variables
    #     specialites_a_exclure = ["Pharmacie", "Grossiste", "SuperGros"]

    #     # Calculate similarity_percentage and add to other_details
    #     # for plan in Plan.objects.filter(user=self.user, day=self.added):
    #     #     matching_doctors = (
    #     #         sum(
    #     #             1 for rapport in Rapport.objects.filter(added=self.added, user=self.user)
    #     #             for doctor in Visite.objects.filter(rapport=rapport)
    #     #             if doctor.medecin in plan.clients.exclude(specialite__in=specialites_a_exclure)
    #     #         )
    #     #     )
    #     #     client_list_count = max(1, plan.clients.exclude(specialite__in=specialites_a_exclure).count())
    #     #     similarity_percentage = int((matching_doctors * 100) / client_list_count)
    #     #     color = 'red' if similarity_percentage < 30 else ('orange' if 30 <= similarity_percentage < 50 else 'green')
    #     #     other_details += f"<b>Similarité Planning / Rapport: <b>{similarity_percentage}%</b></b><br/>"

    #     # Calculate visited_communes and add to other_details
    #     visited_communes = set()
    #     other_details += f"<b>Régions visités ce jour : </b>"
    #     for visite in visites:
    #         visited_communes.add(
    #             (
    #                 visite.medecin.commune.wilaya.nom
    #                 + "/"
    #                 + visite.medecin.commune.nom
    #                 + " - "
    #             )
    #         )
    #     other_details += ", ".join(visited_communes)

    #     # # Add total visits count to other_details
    #     # color = 'red' if len(medecins) < 10 else 'green'
    #     other_details += (
    #         f"<br/><b>Total des visites ce jour:</b> <b>({len(medecins)}) clients </b> "
    #     )

    #     # Separate specialties and add to other_details
    #     medical_specialties = [
    #         detail
    #         for detail in details
    #         if detail["specialite"] not in specialites_a_exclure
    #     ]
    #     commercial_specialties = [
    #         detail
    #         for detail in details
    #         if detail["specialite"] in specialites_a_exclure
    #     ]

    #     other_details += f"<br/><b>({medecin_nbr}) Medical:</b> " + " ".join(
    #         [
    #             f'<b>({detail["dcount"]})</b> {detail["specialite"]} '
    #             for detail in medical_specialties
    #         ]
    #     )
    #     other_details += "<br/>"
    #     other_details += f"<b>({medecin_commercial}) Commercial:</b> " + " ".join(
    #         [
    #             f'<b>({detail["dcount"]})</b> {detail["specialite"]} '
    #             for detail in commercial_specialties
    #         ]
    #     )

    #     # Add medical and commercial product presentations
    #     # Add product information
    #     if self.user.userprofile.speciality_rolee == "Commercial":
    #         commercial_products_info = self._generate_product_info(
    #             visites.filter(medecin__specialite__in=specialites_a_exclure), produits
    #         )
    #         other_details += f"<br/><b>Commercial Produits presentés ce jourrr:</b><br/>{commercial_products_info}"

    #     # Add medical products information
    #     else:
    #         medical_products_info = self._generate_product_info(
    #             visites.exclude(medecin__specialite__in=specialites_a_exclure), produits
    #         )
    #         other_details += f"<br/><b>Medical Produits presentés ce jour:</b><br/>{medical_products_info}"

    #     # # Add stock information
    #     # if medecin_commercial > 0:
    #     #     other_details += "<br/><b>Stock disponible:</b><br/>"
    #     #     other_details += self._generate_stock_info(visites)

    #     return other_details

    @property
    def rapport_details(self):
        # Retrieve required objects
        produits = Produit.objects.filter(
            pays=self.user.userprofile.commune.wilaya.pays
        ).prefetch_related("visite_set")

        visites = Visite.objects.filter(rapport=self).select_related(
            "medecin__commune__wilaya"
        )

        medecins = Medecin.objects.filter(visite__in=visites).distinct()

        specialites_a_exclure = ["Pharmacie", "Grossiste", "SuperGros"]

        # Count medecins by specialization
        medecin_nbr = medecins.exclude(specialite__in=specialites_a_exclure).count()
        medecin_commercial = medecins.filter(
            specialite__in=specialites_a_exclure
        ).count()

        # Aggregate specialities
        details = medecins.values("specialite").annotate(dcount=Count("specialite"))

        # Initialize other details
        other_details = []

        # Calculate visited communes
        visited_communes = {
            visite.medecin.commune.wilaya.nom + "/" + visite.medecin.commune.nom
            for visite in visites
        }
        other_details.append(
            f"<b>Régions visités ce jour : </b>{', '.join(visited_communes)}"
        )

        # Total visits count
        other_details.append(
            f"<br/><br/><b>Total des visites ce jour:</b> <b>({len(medecins)}) clients </b>"
        )

        # Separate specialties
        medical_specialties = [
            detail
            for detail in details
            if detail["specialite"] not in specialites_a_exclure
        ]
        commercial_specialties = [
            detail
            for detail in details
            if detail["specialite"] in specialites_a_exclure
        ]

        # Add specialty counts to other details
        other_details.append(
            f"<br/><b>({medecin_nbr}) Medical:</b> "
            + " ".join(
                [
                    f'<b>({detail["dcount"]})</b> {detail["specialite"]} '
                    for detail in medical_specialties
                ]
            )
        )

        other_details.append("<br/>")
        other_details.append(
            f"<b>({medecin_commercial}) Commercial:</b> "
            + " ".join(
                [
                    f'<b>({detail["dcount"]})</b> {detail["specialite"]} '
                    for detail in commercial_specialties
                ]
            )
        )

        # Add product information
        if self.user.userprofile.speciality_rolee == "Commercial":
            commercial_products_info = self._generate_product_info(
                visites.filter(medecin__specialite__in=specialites_a_exclure), produits
            )
            other_details.append(
                f"<br/><br/><b>Commercial Produits presentés ce jour:</b><br/>{commercial_products_info}"
            )
        # else:
            # medical_products_info = self._generate_product_info(
            #     visites.exclude(medecin__specialite__in=specialites_a_exclure), produits
            # )
            # other_details.append(
            #     f"<br/><br/><b>Medical Produits presentés ce jour:</b><br/>{medical_products_info}"
            # )
        
        # other_details.append(
        #         f"<br/><br/>"
        #     )

        return "".join(other_details)

    # @property
    # def rapport_details(self):
    #     # Retrieve required objects
    #     produits = Produit.objects.filter(pays=self.user.userprofile.commune.wilaya.pays)
    #     month = self.added.month
    #     user = self.user.username
    #     visites = Visite.objects.filter(rapport=self)
    #     medecins = Medecin.objects.filter(visite__in=visites).distinct()
    #     medecin_nbr = len(medecins.exclude(specialite__in=['Pharmacie', 'Grossiste', "SuperGros"]))
    #     medecin_commercial = len(medecins.filter(specialite__in=['Pharmacie', 'Grossiste', "SuperGros"]))
    #     details = Medecin.objects.filter(id__in=medecins.values("id")).values('specialite').annotate(dcount=Count('specialite'))

    #     # Initialize variables
    #     other_details = ""
    #     specialites_a_exclure = ["Pharmacie", "Grossiste", "SuperGros"]
    #     visited_communes = set()

    #     # Calculate similarity_percentage and add to other_details
    #     for plan in Plan.objects.filter(user=self.user, day=self.added):
    #         matching_doctors = sum(1 for rapport in Rapport.objects.filter(added=self.added, user=self.user) for doctor in
    #                                Visite.objects.filter(rapport=rapport).exclude(medecin__specialite__in=specialites_a_exclure)
    #                                if doctor.medecin in plan.clients.exclude(specialite__in=specialites_a_exclure))
    #         client_list_count = max(1, len(plan.clients.exclude(specialite__in=specialites_a_exclure)))
    #         similarity_percentage = int((matching_doctors * 100) / client_list_count)
    #         color = 'red' if similarity_percentage < 30 else ('orange' if 30 <= similarity_percentage < 50 else 'green')
    #         other_details += f"<b>Similarité Planning / Rapport: <b>{similarity_percentage}%</b></b><br/>"

    #     # Calculate visited_communes and add to other_details
    #     other_details += f"<b>Régions visités ce jour : </b>"
    #     for visite in visites:
    #         visited_communes.add((visite.medecin.commune.wilaya.nom + "/" + visite.medecin.commune.nom + " - "))
    #     other_details += ", ".join(visited_communes)

    #     # Add total visits count to other_details
    #     color = 'red' if len(medecins) < 10 else 'green'
    #     other_details += f"<br/><b>Total des visites ce jour:</b> <b>({len(medecins)}) clients </b> "

    #     # Separate specialties and add to other_details
    #     other_specialties = []
    #     end_specialties = []
    #     for detail in details:
    #         (end_specialties if detail["specialite"] in ["SuperGros", "Grossiste", "Pharmacie"] else other_specialties).append(detail)
    #     sorted_specialties = other_specialties + end_specialties
    #     medical_specialties = [detail for detail in sorted_specialties if detail["specialite"] not in ["SuperGros", "Grossiste", "Pharmacie"]]
    #     commercial_specialties = [detail for detail in sorted_specialties if detail["specialite"] in ["SuperGros", "Grossiste", "Pharmacie"]]
    #     other_details += f"<br/><b>({(medecin_nbr)}) Medical:</b> " + " ".join([f'<b>({detail["dcount"]})</b> {detail["specialite"]} ' for detail in medical_specialties])
    #     other_details += "<br/>"
    #     other_details += f"<b>({(medecin_commercial)}) Commercial:</b> " + " ".join([f'<b>({detail["dcount"]})</b> {detail["specialite"]} ' for detail in commercial_specialties])

    #     # Add medical and commercial product presentations
    #     other_details += "<br/><b>Medical Produits presentés ce jour:</b><br/>"
    #     other_details += self._generate_product_info(visites.exclude(medecin__specialite__in=["Pharmacie", "Grossiste", "Supergros"]), Produit.objects.all())
    #     # other_details += self._generate_product_info(visites.filter(medecin__specialite__in=["Pharmacie", "Grossiste", "Supergros"]), Produit.objects.all())

    #     other_details += "<br/><b>Commercial Produits presentés ce jour:</b><br/>"
    #     other_details += self._generate_product_info(visites.filter(medecin__specialite__in=["Pharmacie", "Grossiste", "Supergros"]), Produit.objects.all())

    #     # Add stock information
    #     other_details += "<br/><b>Stock disponible:</b><br/>"
    #     other_details += self._generate_stock_info(visites)

    #     return other_details

    def _generate_product_info(self, visites, produits):
        product_visits = defaultdict(int)
        for visite in visites:
            for product in visite.produits.all():
                product_visits[product.nom] += 1

        result = ""
        count_med = 0
        for product, len_visits in sorted(
            product_visits.items(), key=lambda x: x[1], reverse=True
        ):
            if len_visits > 0:
                product_string = f"<b style='font-size:12px'>({product} : {len_visits} fois)</b>"
                result += product_string + " "
                count_med += 1
                if count_med % 3 == 0:
                    result += "<br/>"
        return result

    def _generate_stock_info(self, visites):
        result = ""
        for product in Produit.objects.filter(productcompany__family="lilium pharma"):
            total_qtt = sum(
                produit_visite.qtt
                for visite in visites
                for produit_visite in ProduitVisite.objects.filter(
                    visite=visite, produit=product
                )
            )
            result += f"<b>{product.nom}</b>: {total_qtt}  -   "
        return result

    def related_plan(self):
        return Plan.objects.get(day=self.added, user=self.user)


class Visite(models.Model):
    rapport = models.ForeignKey(Rapport, on_delete=models.CASCADE)
    observation = models.TextField(null=True, blank=True)
    medecin = models.ForeignKey(Medecin, on_delete=models.CASCADE)
    produits = models.ManyToManyField(Produit, through="produits.ProduitVisite")
    priority = models.PositiveIntegerField(
        validators=[
            MaxValueValidator(5),
        ],
        default=0,
        db_index=True,
    )

    class Meta:
        unique_together = ("medecin", "rapport")
        ordering = ["medecin__specialite"]

    @property
    def date_rapport(self):
        return str(self.rapport.added)

    @property
    def type(self):
        return "medicale" if self.medecin.specialite in MEDICAL else "commercial"

    def products_to_json(self):
        product_list = []
        for produit in self.produitvisite_set.all():
            product_list.append(
                {
                    "id": produit.produit.id,
                    "nom": produit.produit.nom,
                    "qtt": produit.qtt,
                    "prescription": produit.prescription,
                }
            )
        return product_list

    def products_to_admin(self):
        return " , ".join(
            f"{produit.produit.nom} : {produit.qtt} "
            for produit in self.produitvisite_set.all()
        )

    def products_to_pdf(self):
        return " , ".join(
            f"{produit.produit.nom}  {produit.qtt if self.medecin.specialite in COMMERCIAL else ''} "
            for produit in self.produitvisite_set.all()
        )
        # return "<br>".join(f"<span style='font-size: 12px;'>{produit.produit.nom} {produit.qtt if self.medecin.specialite in COMMERCIAL else ''}</span>" for produit in self.produitvisite_set.all())

    def products_to_str(self):
        return ",".join(
            f"{produit.produit.id}:{produit.qtt}"
            for produit in self.produitvisite_set.all()
        )

    # def clean(self):
    #     # medecin.objects.get(id=self.cleaned_data["medecin"])
    #     try:
    #         Visite.objects.get(rapport=self.rapport,medecin=self.medecin)
    #         raise ValidationError("Veuillez choisir un autre medecin ")
    #     except Visite.DoesNotExist:
    #         pass
    #     except Visite.MultipleObjectsReturned:
    #         raise ValidationError("Veuillez choisir un autre medecin ")


class Comment(models.Model):
    added = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    rapport = models.ForeignKey(Rapport, on_delete=models.CASCADE)


@receiver(pre_delete, sender=Visite)
def pre_delete_visite(sender, **kwargs):
    medecin = kwargs["instance"].medecin
    #   print("******************** pre deleting ")
    #   print(f"{medecin.nom} {kwargs['instance'].id} {medecin.last_visite()} ")
    ProduitVisite.objects.filter(visite=kwargs["instance"]).delete()
    if medecin.last_visite():
        ProduitVisite.objects.filter(visite=medecin.last_visite()).update(
            medecin=medecin
        )


@receiver(post_delete, sender=Visite)
def post_delete_visite(sender, **kwargs):
    medecin = kwargs["instance"].medecin
    #   print("******************** post deleting ")
    ProduitVisite.objects.filter(visite=medecin.last_visite()).update(medecin=medecin)


# @receiver(pre_save, sender=Rapport)
# def check_if_exists_on_create(sender, **kwargs):
#     instance=kwargs['instance']
#     try:
#         Rapport.objects.get(user__username=instance.user.username,added=instance.added)
#         raise(" repport already exists ")
#     except ObjectDoesNotExist:
#         pass


# ----------FROM HERE -----------


@receiver(post_save, sender=Rapport)
def notifiate_on_create(sender, **kwargs):
    from rapports.api.serializers import RapportSerializer

    instance = kwargs["instance"]

    # Deleting Absence if Exists
    absence = Absence.objects.filter(date=instance.added, user=instance.user)
    if absence.exists():
        absence.delete()


#     existing_notification = Notification.objects.filter(
#         users=instance.user,
#         data__navigate_to__params__rapport=instance.id,
#         data__navigate_to__params__should_fetch=True
#     )
#     if not existing_notification.exists():

#         notification=Notification.objects.create(
#                     title=f"{instance.user.username}  ",
#                     description=f"Date du rapport: {str(instance.added)}",
#                     data={
#                             "name":"Rapports",
#                             "title":"Rapport",
#                             # "message":f"{instance.user.username} vient d'ajouter son rapport du  {str(instance.added)}",
#                             "message":f"{instance.user.username} vient d'ajouter son rapport",
#                             "confirm_text":"voir le rapport",
#                             "cancel_text":"plus tard",
#                             "StackName":"Rapports",
#                             "navigate_to":json.dumps({
#                                    "screen":"Details",
#                                     "params":{
#                                         "rapport":instance.id,
#                                         "should_fetch":True
#                                         }

#                                 })
#                         },
#                 )
#         notification.users.set([usr for usr in instance.user.userprofile.get_users_to_notify()])
#         notification.send()


# @receiver(post_save, sender=Visite)
# def notifiate_on_create(sender, **kwargs):
#     from rapports.api.serializers import RapportSerializer
#     instance=kwargs['instance']
#     notification=Notification.objects.create(
#                 title=f"{instance.rapport.user.username}  viens juste d'ajouter une visite {instance.type}",
#                 description=f"Rapport du: {str(instance.rapport.added)}\nclient: {instance.medecin.nom} ",
#                 data={
#                         "name":"Rapports",
#                         "title":"Rapport",
#                         # "message":f"{instance.rapport.user.username} vient d'ajouter une visite sur  son rapport du  {str(instance.rapport.added)}",
#                         "message":f"{instance.rapport.user.username} vient d'ajouter une visite",
#                         "confirm_text":"voir le rapport",
#                         "cancel_text":"plus tard",
#                         "StackName":"Rapports",
#                         "navigate_to":json.dumps({
#                                "screen":"Details",
#                                 "params":{
#                                     "rapport":instance.rapport.id,
#                                     "should_fetch":True
#                                     }

#                             })
#                     },
#             )
#     notification.users.set([usr for usr in instance.rapport.user.userprofile.get_users_to_notify()])
#     notification.send()

# ----------TO HERE -----------




class QRCodeModel(models.Model):
    identifier = models.CharField(max_length=8, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.identifier


class GeneratedPDF(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE
    )  # Link to the user who generated the PDF
    title = models.CharField(max_length=255)
    pdf_file = models.FileField(upload_to=upload_location)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title



from django.contrib.auth.models import User
from django.utils import timezone

class Anomalies(models.Model):
    rapport = models.ForeignKey(Rapport, on_delete=models.CASCADE, null=True, blank=True)  # Optional rapport
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # ForeignKey to User
    Anomalie = models.TextField(null=True, blank=True)
    date = models.DateTimeField(null=True,blank=True)  # Auto add current date and time
    added = models.DateTimeField(auto_now_add=True)  # Auto add current date and time

    def upload_location(instance, filename):
        # This function will place the files in the rapport/anomalie folder
        return f"rapport/anomalie/{filename}"

    image1 = models.ImageField(upload_to=upload_location, null=True, blank=True)
    image2 = models.ImageField(upload_to=upload_location, null=True, blank=True)
    image3 = models.ImageField(upload_to=upload_location, null=True, blank=True)
    image4 = models.ImageField(upload_to=upload_location, null=True, blank=True)



    def __str__(self):
        return self.Anomalie

    class Meta:
        verbose_name = "Anomaly"
        verbose_name_plural = "Anomalies"
        ordering = ['rapport']

