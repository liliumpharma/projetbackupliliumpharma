from calendar import month
import time
from django.db import models
from regions.models import Commune, Wilaya
from django.contrib.auth.models import User
from django.db.models import Count
import datetime
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
import subprocess
from django.utils import timezone
from plans.models import Plan


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


class Specialite(models.TextChoices):
    generaliste = "Généraliste"
    diabetologue = "Diabetologue"
    neurologue = "Neurologue"
    psychologue = "Psychologue"
    gynecologue = "Gynécologue"
    rumathologue = "Rumathologue"
    allergologue = "Allergologue "
    phtisio = "Phtisio"
    cardiologue = "Cardiologue"
    urologue = "Urologue"
    hematologue = "Hematologue"
    orthopedie = "Orthopedie"
    nutritionist = "Nutritionist"
    dermatologue = "Dermatologue"
    interniste = "Interniste"
    pharmacie = "Pharmacie"
    grossiste = "Grossiste"
    supergros = "SuperGros"
    gastrologue = "Gastrologue"
    endocrinologue = "Endocrinologue"
    dentiste = "Dentiste"
    orl = "ORL"
    maxilo_facial = "Maxilo facial"
    sage_femme = "Sage Femme"
    pediatre = "Pediatre"

class Classification(models.TextChoices):
    a = "a"
    b = "b"
    c = "c"
    d = "d"
    e = "e"
    f = "f"
    g = "g"
    p = "p"


class MedecinSpecialite(models.Model):
    description = models.CharField(max_length=255, unique=True, db_index=True)
    ismedical = models.BooleanField(default=False)

    def __str__(self):
        return self.description


class Medecin(models.Model):
    added = models.DateField(auto_now_add=True)
    nom = models.CharField(max_length=255, db_index=True)
    specialite = models.CharField(
        max_length=15,
        choices=Specialite.choices,
        default=Specialite.generaliste,
        db_index=True,
    )

    specialite_fk = models.ForeignKey(
        to=MedecinSpecialite, null=True, blank=True, on_delete=models.SET_NULL
    )

    classification = models.CharField(
        max_length=15,
        choices=Classification.choices,
        default=Classification.c,
        db_index=True,
    )
    telephone = models.CharField(max_length=300, null=True, blank=True)
    email = models.CharField(max_length=50, null=True, blank=True)
    wilaya = models.ForeignKey(Wilaya, on_delete=models.CASCADE, null=True, blank=True)
    commune = models.ForeignKey(Commune, on_delete=models.CASCADE)
    adresse = models.CharField(max_length=255, null=True)
    flag = models.BooleanField(default=False)
    updatable = models.BooleanField(default=True)
    blocked = models.BooleanField(default=False)
    contact = models.CharField(max_length=255, blank=True, null=True)
    lat = models.CharField(max_length=255, blank=True, null=True)
    lon = models.CharField(max_length=255, blank=True, null=True)
    users = models.ManyToManyField(User)
    note = models.CharField(max_length=255, blank=True, null=True)
    uploaded_from_excel = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.id} - {self.nom}"

    def clean_nom(self):
        return self.cleaned_data["nom"].upper()

    def save(self, *args, **kwargs):

        if kwargs.get("created", False):
            # Define your Docker command
            docker_command = "docker exec -it lilium_api python set_redis_medecins.py"

            # REFRESHING REDIS MEDECINS
            subprocess.run(docker_command, shell=True)

        self.nom = self.nom.replace("(BLOCKED) ", "").lower()
        
        if self.blocked:
            self.nom = f"(BLOCKED) {self.nom}"

        super(Medecin, self).save(*args, **kwargs)

    # def save(self, *args, **kwargs):
    #     # Récupérer l'utilisateur actuel de la session
    #     current_user = kwargs.pop('current_user', None)

    #     # Effectuez vos opérations de sauvegarde
    #     self.nom = self.nom.replace('(BLOCKED) ', '').lower()
    #     if self.blocked:
    #         self.nom = f'(BLOCKED) {self.nom}'

    #     # Si un utilisateur actuel est fourni, mettez à jour last_user_updater
    #     if current_user:
    #         self.last_user_updater = current_user

    #     super(Medecin, self).save(*args, **kwargs)

    @property
    def medecin_nom(self):
        return f"{self.nom} {self.specialite}"

    @property
    def medecin_commercial(self):
        return "  -  ".join(
            [f"{usr.first_name} {usr.last_name}" for usr in self.users.all()]
        )

    @property
    def medecin_commercial_poste(self):
        return "  -  ".join(
            [
                f"{usr.first_name} {usr.last_name}"
                for usr in self.users.filter(userprofile__speciality_rolee="Commercial")
            ]
        )

    @property
    def medecin_commercial_lilium_1(self):
        return "  -  ".join(
            [
                f"{usr.first_name} {usr.last_name}"
                for usr in self.users.filter(userprofile__lines__contains="L1")
            ]
        )

    @property
    def medecin_commercial_lilium_2(self):
        return "  -  ".join(
            [
                f"{usr.first_name} {usr.last_name}"
                for usr in self.users.filter(userprofile__lines__contains="L2")
            ]
        )

    @property
    def medecin_commercial_l3(self):
        return "  -  ".join(
            [
                f"{usr.first_name} {usr.last_name}"
                for usr in self.users.filter(userprofile__lines__contains="L3")
            ]
        )

    @property
    def medecin_commercial_com(self):
        return "  -  ".join(
            [
                f"{usr.first_name} {usr.last_name}"
                for usr in self.users.filter(userprofile__lines__contains="COM")
            ]
        )

    @property
    def medecin_region(self):
        return f"{self.commune.wilaya.pays.nom} {self.commune.wilaya.nom} {self.commune.nom}"

    @property
    def medecin_wilaya_commune(self):
        return f"{self.commune.wilaya.nom}-{self.commune.nom}"

    # @property
    # def has_deal(self):
    #     # return True
    #     # return len(self.deal_set.all()) > 0
    #     return self.deal_set.exists()

    @property
    def has_deal(self):
        return self.medecin.exists()

    @property
    def medecin_visites(self):
        from rapports.models import Visite

        """
        SELECT medecin_id,  
        EXTRACT(YEAR FROM rapports_rapport.added ) as year , 
        EXTRACT(MONTH FROM rapports_rapport.added) as month, 
        Count(*) as nbr_visites

        FROM rapports_visite 

        JOIN rapports_rapport ON rapports_visite.rapport_id=rapports_rapport.id

        WHERE rapports_rapport.added BETWEEN date_trunc('month', CURRENT_DATE - interval '6 month') AND CURRENT_DATE and medecin_id=16 
        
        GROUP BY medecin_id, 
                EXTRACT(YEAR FROM rapports_rapport.added ) , 
                EXTRACT(MONTH FROM rapports_rapport.added)
                
        ORDER BY medecin_id

        """

        today = datetime.date.today()
        six_months_ago = today - datetime.timedelta(days=180)

        return (
            Visite.objects.filter(
                medecin=self, rapport__added__range=[six_months_ago, today]
            )
            .values("rapport__added__year", "rapport__added__month")
            .annotate(nbr_visite=Count("id"))
        )

    @property
    def nbr_visites_year(self):
        from rapports.models import Visite

        today = datetime.date.today()
        # nbr_visites=Visite.objects.filter(medecin=self,rapport__added__year=today.year).annotate(nbr_visite=Count('id'))
        nbr_visites = len(
            Visite.objects.filter(medecin=self, rapport__added__year=today.year)
        )
        return nbr_visites if nbr_visites > 0 else 0

    def medecin_visites_links(self):
        from rapports.models import Visite
        import datetime

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
        visites = ""
        for i in range(6):
            mm = m - i if m - i != 0 else 12
            if mm < 0:
                mm = 12 - (i - m)
            nbr_visite = len(
                Visite.objects.filter(medecin=self, rapport__added__month=mm)
            )
            visites += f'{months[mm]}: <a href="/medecins/visites/PDF/{self.id}/?month={mm}">{nbr_visite}</a>, '
        return visites

    def last_visite(self):
        from rapports.models import Visite

        # print("+++++++++++++++from medecin "+str(Visite.objects.filter(medecin=self).order_by("rapport__added").last().id))
        return Visite.objects.filter(medecin=self).order_by("rapport__added").last()

    def get_last_visite(self):
        try:
            retruned_str = str(self.last_visite().rapport.added.strftime("%Y-%m-%d"))
            retruned_str += " Par " + str(self.last_visite().rapport.user)
            return retruned_str
        except:
            return "Non visité"

    def get_last_visite2(self):
        try:
            retruned_str = str(self.last_visite().rapport.added.strftime("%Y-%m-%d"))
            retruned_str += " Par " + str(self.last_visite().rapport.user)
            return retruned_str
        except:
            return "Non visité"

    # def get_id_name_region(self):
    #     try:
    #         retruned_str = str(self.id)
    #         # retruned_str += " | " + str(self.nom)
    #         # retruned_str += " | " + str(self.commune)
    #         retruned_str += " | " + str(self.nom)
    #         retruned_str += " | " + str(self.commune)
    #         return retruned_str
    #     except:
    #         return "-"
    def get_id_name_region(self):
        try:
            retruned_str = str(self.id)
            # retruned_str += " | " + str(self.nom)
            # retruned_str += " | " + str(self.commune)
            combined_str = f"{self.nom} |  {self.commune}"
            retruned_str += " | " + combined_str
            return retruned_str
        except:
            return "-"

    def is_medical(self):
        return self.specialite in MEDICAL

    def user_can_update(self, user):
        if user in self.users.all():
            return True
        if user.userprofile.rolee == "CountryManager" or user.is_superuser:
            return True
        for usr in self.users.all():
            print(usr)
            if user in User.objects.filter(userprofile__usersunder=usr):
                return True
        return False

    def get_stock(self, product):
        from rapports.models import ProduitVisite

        try:
            return ProduitVisite.objects.get(medecin=self, produit=product).qtt
        except:
            return 0

    def count_plans_for_user(self, request):
        # Obtenir le premier et le dernier jour du mois courant
        today = timezone.now()
        first_day_of_month = today.replace(day=1)
        last_day_of_month = (first_day_of_month + timezone.timedelta(days=31)).replace(
            day=1
        ) - timezone.timedelta(days=1)

        # Compter le nombre de fois où ce médecin est mentionné dans les plannings
        count = Plan.objects.filter(
            day__range=(first_day_of_month, last_day_of_month),
            clients=self,  # Filtrer par le médecin actuel
            user=request.user,  # Filtrer par l'utilisateur connecté
        ).count()

        return count


# @receiver(post_save, sender=Medecin)
# def create_medecin_modification_history(sender, instance, created, **kwargs):
#     if not created:
#         action = "modifié"
#     else:
#         action = "ajouté"

#     # Récupérer l'utilisateur actuel qui effectue la modification
#     current_user = kwargs['update_fields']['last_user_updater']

#     # Récupérer les utilisateurs avant et après la modification
#     users_before = list(instance.users.all())
#     users_after = list(current_user.medecin_set.all())

#     # Créer une nouvelle instance de MedecinModificationHistory avec les utilisateurs avant et après
#     history_instance = MedecinModificationHistory.objects.create(
#         medecin=instance,
#         user=current_user,
#         action=action
#     )
#     history_instance.users_before.set(users_before)
#     history_instance.users_after.set(users_after)


# @receiver(post_save, sender=Medecin)
# def check_users_field(sender, instance, created, **kwargs):
#     if created and not instance.users.exists():
#         raise ValidationError("Le champ users ne peut pas être vide lors de la création d'un médecin.   لا يمكن أن يكون فارغًا Users عند إنشاء طبيب.")


class MedecinModificationHistory(models.Model):
    medecin = models.ForeignKey(Medecin, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    users_before = models.ManyToManyField(
        User, related_name="users_before_modification"
    )
    users_after = models.ManyToManyField(User, related_name="users_after_modification")

    def __str__(self):
        return f"{self.user} a {self.action} le medecin {self.medecin} le {self.timestamp.strftime('%d/%m/%Y à %H:%M')} (Utilisateurs avant: {', '.join([str(user) for user in self.users_before.all()])}, Utilisateurs après: {', '.join([str(user) for user in self.users_after.all()])})"


# @receiver(m2m_changed, sender=Medecin.users.through)
# def log_medecin_users_change(sender, instance, action, reverse, model, pk_set, **kwargs):
#     if action == 'pre_add':
#         instance._users_before = list(instance.users.all())
#     elif action == 'pre_remove':
#         instance._users_before = list(instance.users.all())
#     elif action == 'post_add':
#         users_after = list(instance.users.all())
#         MedecinModificationHistory.objects.create(
#             medecin=instance,
#             user=kwargs['user'],  # Assuming you pass the user who made the change
#             action='added' if not reverse else 'removed',
#             users_before=instance._users_before,
#             users_after=users_after
#         )
#         delattr(instance, '_users_before')
#     elif action == 'post_remove':
#         users_after = list(instance.users.all())
#         MedecinModificationHistory.objects.create(
#             medecin=instance,
#             user=kwargs['user'],  # Assuming you pass the user who made the change
#             action='removed' if not reverse else 'added',
#             users_before=instance._users_before,
#             users_after=users_after
#         )
#         delattr(instance, '_users_before')


import subprocess
from multiprocessing import Process


# @receiver(post_save, sender=Medecin)
# def check_and_delete_medecin(sender, instance, created, **kwargs):
#     if created:
#         for user in instance.users.all():
#             if user.medecin_set.exclude(specialite__in=['Pharmacie', 'Grossiste', 'SuperGros']).count() >= 160:
#                 instance.delete()
#                 raise ValidationError("Cet utilisateur a déjà trop de médecins associés, l'instance de Medecin a été supprimée.")


# @receiver(post_save, sender=Medecin)
# def run_command_after_save(sender, instance, created, **kwargs):
#     if created:
#         # Define your Docker command
#         docker_command = "docker exec -i lilium_api python set_redis_medecins.py"

#         # Define a function to run the command in a separate process
#         def execute_command():
#             subprocess.run(docker_command, shell=True)

#         # Start a new process to execute the command
#         command_process = Process(target=execute_command)
#         command_process.start()


@receiver(post_save, sender=Medecin)
def check_user_medecin_count(sender, instance, created, **kwargs):
    print("created" + str(created))
    if created:
        # Ensure that the associated users are fully saved before checking medecin count
        instance.refresh_from_db()
        for user in instance.users.all():
            if (
                user.medecin_set.exclude(
                    specialite__in=["Pharmacie", "Grossiste", "SuperGros"]
                ).count()
                >= 161
            ):
                # If user has more than 160 medecins, raise a ValidationError
                instance.delete()
                raise ValidationError(
                    "Cet utilisateur a déjà trop de médecins associés, l'instance de Medecin a été supprimée."
                )


from django.db.models.signals import m2m_changed
from django.dispatch import receiver


@receiver(m2m_changed, sender=Medecin.users.through)
def check_user_medecin_count(
    sender, instance, action, reverse, model, pk_set, **kwargs
):

    excluded_specialities = ["Pharmacie", "Grossiste", "SuperGros"]
    if action == "post_add" and not reverse:
        print("instance: " + str(instance.specialite))
        if instance.specialite not in excluded_specialities:
            for user_pk in pk_set:
                user = model.objects.get(pk=user_pk)
                if user.username != "Medecin_Recycle_Bin":
                    if (
                        user.medecin_set.exclude(
                            specialite__in=excluded_specialities
                        ).count()
                        >= 161
                    ):
                        raise ValidationError(
                            f"ATTENTION : {user} a plus de 160 Medecins   |    لديه أكثر من 160 طبيباً"
                        )


@receiver(post_save, sender=Medecin)
def associate_commune_with_wilaya(sender, instance, created, **kwargs):
    if created:
        # Récupérer la commune donnée dans l'instance de médecin
        commune_id = instance.commune_id
        try:
            # Récupérer la wilaya correspondante à cette commune
            wilaya = Commune.objects.get(pk=commune_id).wilaya
            # Associer la wilaya au médecin
            instance.wilaya = wilaya
            instance.save()
        except Commune.DoesNotExist:
            # Gérer le cas où la commune n'existe pas
            print("La commune spécifiée n'existe pas.")
        except Exception as e:
            # Gérer d'autres erreurs possibles
            print(
                "Une erreur s'est produite lors de l'association de la wilaya avec le médecin:",
                str(e),
            )
