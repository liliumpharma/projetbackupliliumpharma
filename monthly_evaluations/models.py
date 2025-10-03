from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from notifications.models import Notification
from accounts.models import UserProfile
from django.db.models.signals import post_save, pre_delete, post_delete, pre_save


class Monthly_Evaluation(models.Model):
    added = models.DateField(default=timezone.now, blank=True, db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    sup_evaluation = models.BooleanField(
        verbose_name="Le superviseur à fait l'évaluation du délégué", default=False
    )
    user_sup_evaluation = models.BooleanField(
        verbose_name="Le délégué à évalué son superviseur", default=True
    )
    user_direction_evaluation = models.BooleanField(
        verbose_name="La direction à consulté l'évaluation", default=False
    )

    own_perc = models.CharField(
        max_length=200, null=True, blank=True, verbose_name="Pourcentage"
    )

    q1 = models.PositiveIntegerField(
        verbose_name="Combien de médecins visités au cours du mois?",
        null=True,
        blank=True,
    )
    q2 = models.TextField(
        verbose_name="Qui sont les médecins qui ont été visités plus d'une fois ce mois-ci, et la raison?",
        null=True,
        blank=True,
    )
    q3 = models.TextField(
        verbose_name="Combien de médecins n'ont pas été visités ce mois-ci, en mentionnant le nom du médecin et la raison de la non-visite ?",
        null=True,
        blank=True,
    )
    q4 = models.TextField(
        verbose_name="Qui sont les médecins visités ce mois-ci avec Superviseur et quel est le but de la visite ?",
        null=True,
        blank=True,
    )
    q5 = models.TextField(
        verbose_name="Écrivez cinq médecins importants en ecriture pour chaque produit",
        null=True,
        blank=True,
    )
    q6 = models.TextField(
        verbose_name="Mentionnez 10 médecins qui ont visité plus de trois visites et n'ont pas encore écrit, en expliquant la raison à votre avis",
        null=True,
        blank=True,
    )
    q7 = models.TextField(
        verbose_name="Quels plus avez-vous apporté avec les médecins ce mois-ci, en mentionnant le nom du médecin et le type du plus",
        null=True,
        blank=True,
    )
    q8 = models.TextField(
        verbose_name="Quels sont les médecins que vous suggérez de retirer de la liste, en mentionnant la raison",
        null=True,
        blank=True,
    )
    q9 = models.TextField(
        verbose_name="Quelles sont vos suggestions pour les médecins qui sont visités régulièrement et qui n'écrivent pas encore bien. Mentionner le nom du médecin et la suggestion",
        null=True,
        blank=True,
    )
    q10 = models.TextField(
        verbose_name="Écrivez cinq médecins que vous souhaitez gagner afin qu'ils puissent écrire vos produits pour vous car ils ont de nombreux patients, le nom du médecin et le produit",
        null=True,
        blank=True,
    )
    # COMMERCIAL
    q11 = models.TextField(
        verbose_name="Combien de pharmacies et de grossistes avez vous visités au cours du mois ?",
        null=True,
        blank=True,
    )
    q12 = models.TextField(
        verbose_name="Combien de super grossistes avez vous visité ce mois-ci, en mentionnant le nom du super grossistes et la raison de la visite",
        null=True,
        blank=True,
    )
    q13 = models.TextField(
        verbose_name="Combien de bon de commandes durant ce mois, en mentionnant le nom du client, le produit et la quantité",
        null=True,
        blank=True,
    )
    q14 = models.TextField(
        verbose_name="Quelles sont vos suggestions pour améliorer les ventes",
        null=True,
        blank=True,
    )
    q15 = models.TextField(
        verbose_name="Evaluation du superviseur", null=True, blank=True
    )

    updatable = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.added}"

    class Meta:
        verbose_name = "Delegate Evaluation"


@receiver(post_save, sender=Monthly_Evaluation)
def notifiate_on_create(sender, **kwargs):
    instance = kwargs["instance"]

    notification = Notification.objects.create(
        title=f"Nouvelle Evaluation Mensuelle !",
        description=f"{instance.user.username} vient d'ajouter son évaluation pour le mois {str(instance.added.month)}",
    )
    notification.users.set(
        [usr for usr in instance.user.userprofile.get_users_to_notify()]
    )
    # notification.send()


class SupEvaluation(models.Model):
    added = models.DateField(default=timezone.now, blank=True, db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    note = models.CharField(max_length=200, null=True, blank=True, verbose_name="Note")
    perc = models.CharField(
        max_length=200, null=True, blank=True, verbose_name="Pourcentage"
    )

    responses_okay = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name="Le superviseur est d;accord avec les réponses du délégué ?",
    )
    probs = models.CharField(
        max_length=2000, null=True, blank=True, verbose_name="problémes"
    )

    # Connaissances produits
    q1 = models.BooleanField(
        verbose_name="Connaissance pathologie et motif de prescription", default=False
    )
    q2 = models.BooleanField(
        verbose_name="Connaissance des Caractéristiques produit", default=False
    )
    q3 = models.BooleanField(
        verbose_name="Connaissance des mécanismes d'action", default=False
    )
    q4 = models.BooleanField(
        verbose_name="Connaissance études, donnes et références scientifiques ",
        default=False,
    )
    q5 = models.BooleanField(
        verbose_name="Positionnement produit vis-à-vis les concurrents ", default=False
    )

    # Porte feuille medecins
    q6 = models.BooleanField(
        verbose_name="Ratio spécialités ciblée / le nombre globale des medecins ",
        default=False,
    )
    q7 = models.BooleanField(
        verbose_name="Ratio nombre des potentiels A/  le nombre globale des medecins",
        default=False,
    )
    q8 = models.BooleanField(
        verbose_name="Informations medecins (contact, spécialité, potentialité, adresse et adresse mail)",
        default=False,
    )
    q9 = models.BooleanField(
        verbose_name="cycles des visites (nombre de visites par medecins, durée entre 2 visites)",
        default=False,
    )
    q10 = models.BooleanField(verbose_name="Couverture secteur", default=False)

    # Visite medicale
    q11 = models.BooleanField(
        verbose_name="Communication et adaptation des types de présentations au profil du médecin",
        default=False,
    )
    q12 = models.BooleanField(
        verbose_name="Préparation avant la visite (fiche médecin)", default=False
    )
    q13 = models.BooleanField(
        verbose_name=" Traitement des objections medecins", default=False
    )
    q14 = models.BooleanField(
        verbose_name=" Traitement des d'objections pharmaciens", default=False
    )
    q15 = models.BooleanField(verbose_name="Gestion de temps", default=False)

    # Visite medicale
    q16 = models.BooleanField(
        verbose_name="Ciblage medecins spécialités", default=False
    )
    q17 = models.BooleanField(
        verbose_name="Ciblage medecins potentialités", default=False
    )
    q18 = models.BooleanField(verbose_name="Ciblage secteur", default=False)
    q19 = models.BooleanField(verbose_name="Planning hebdomadaire", default=False)
    q20 = models.BooleanField(verbose_name="timing d'introduction", default=False)

    # Rapport
    q21 = models.BooleanField(
        verbose_name="Nombre des présentations/ produit", default=False
    )
    q22 = models.BooleanField(
        verbose_name="Informations récoltées Medecins", default=False
    )
    q23 = models.BooleanField(
        verbose_name="Informations récoltées pharmacies (état de stock + medecins prescripteurs)",
        default=False,
    )
    q24 = models.BooleanField(
        verbose_name="Conformité des griffes de passages (date + clarté)", default=False
    )
    q25 = models.BooleanField(verbose_name="Timing d'introduction", default=False)

    # Ethique professionnelle
    q26 = models.BooleanField(verbose_name="Engagement et Intégrité", default=False)
    q27 = models.BooleanField(verbose_name="Confidentialité", default=False)
    q28 = models.BooleanField(verbose_name="Transparence", default=False)
    q29 = models.BooleanField(verbose_name="Conflits d'intérêts", default=False)
    q30 = models.BooleanField(
        verbose_name="Relations avec les professionnels de la santé", default=False
    )

    updatable = models.BooleanField(default=False)

    def __str__(self):
        return f"Supervisor Evaluation - {self.user}"

    class Meta:
        verbose_name = "Supervisor to Delegate"


class SupEvaluationToDirection(models.Model):
    added = models.DateField(default=timezone.now, blank=True, db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sup_evaluate_direction = models.BooleanField(
        verbose_name="Le superviseur à fait l'évaluation de la direction", default=True
    )
    direction_evaluate_sup = models.BooleanField(
        verbose_name="la direction à fait l'évaluation du superviseur", default=False
    )

    q1 = models.TextField(
        verbose_name="Avis du Superviseur sur la directrice", null=True, blank=True
    )

    updatable = models.BooleanField(default=False)

    def __str__(self):
        return f"Supervisor Evaluation To Direction- {self.user}"

    class Meta:
        verbose_name = "Supervisor to Direction"


class DirectionEvaluationToSup(models.Model):
    added = models.DateField(default=timezone.now, blank=True, db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    direction_evaluate_sup = models.BooleanField(
        verbose_name="la direction à fait l'évaluation du superviseur", default=True
    )

    q1 = models.TextField(
        verbose_name="Avis de la direction sur le superviseur", null=True, blank=True
    )

    updatable = models.BooleanField(default=False)

    def __str__(self):
        return f"Direction Evaluation To Supervisor- {self.user}"

    class Meta:
        verbose_name = "Direction to Supervisor"


class DirectionToDelegateEvaluation(models.Model):
    added = models.DateField(default=timezone.now, blank=True, db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Connaissances produits
    q1 = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name="Êtes-vous d'accord avec l'évaluation du superviseur sur le délégué ?",
    )
    explication = models.CharField(
        max_length=1000, null=True, blank=True, verbose_name="explication"
    )

    updatable = models.BooleanField(default=False)

    def __str__(self):
        return f"Direction To Delegate Evaluation - {self.user}"

    class Meta:
        verbose_name = "Direction To Delegate Evaluation"


@receiver(post_save, sender=DirectionToDelegateEvaluation)
def notifiate_on_create(sender, instance, **kwargs):
    # Fetch the family of the user associated with the evaluation
    user_family = instance.user.userprofile.family

    # Get all users who are 'superviseur_nationale' and belong to the same family
    users_to_notify = UserProfile.objects.filter(
        speciality_rolee="Superviseur_national", family=user_family
    ).values_list("user", flat=True)

    monthly_evaluation = Monthly_Evaluation.objects.filter(
        added__month=instance.added.month, user=instance.user
    ).first()

    # Create the notification
    notification = Notification.objects.create(
        title=f"Nouveau commentaire sur l'évaluation de {str(instance.user)} !",
        description="-",
        data={
            "name": "Évaluation mensuelle",
            "title": "Évaluation mensuelle",
            "message": "-",
            "confirm_text": "voir le commentaire",
            "cancel_text": "plus tard",
            "StackName": "Rapports",
            "url": f"https://app.liliumpharma.com/monthly_evaluation/monthly_evaluations/{monthly_evaluation.id}/",
        },
    )
    # Set the users for the notification
    notification.users.set(users_to_notify)

    # Send the notification
    # notification.send()


class Commercial_Monthly_Evaluation(models.Model):
    added = models.DateField(default=timezone.now, blank=True, db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    sup_evaluation = models.BooleanField(
        verbose_name="Le superviseur à fait l'évaluation du délégué", default=False
    )
    user_sup_evaluation = models.BooleanField(
        verbose_name="Le délégué à évalué son superviseur", default=True
    )
    user_direction_evaluation = models.BooleanField(
        verbose_name="La direction à consulté l'évaluation", default=False
    )

    own_perc = models.CharField(
        max_length=200, null=True, blank=True, verbose_name="Pourcentage"
    )

    q1 = models.PositiveIntegerField(null=True, blank=True)
    q2 = models.TextField(null=True, blank=True)
    q3 = models.TextField(null=True, blank=True)
    q4 = models.TextField(null=True, blank=True)
    q5 = models.TextField(null=True, blank=True)
    q6 = models.TextField(null=True, blank=True)
    q7 = models.TextField(null=True, blank=True)
    q8 = models.TextField(null=True, blank=True)
    q9 = models.TextField(null=True, blank=True)
    q10 = models.TextField(null=True, blank=True)

    updatable = models.BooleanField(default=False)

