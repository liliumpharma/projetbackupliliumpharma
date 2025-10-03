from plans.models import Plan
from rest_framework import serializers
from django.utils import timezone

import json

from medecins.models import Medecin
from produits.api.serializers import ProduitVisiteSerializer
from produits.models import ProduitVisite


class MedecinSerializer(serializers.ModelSerializer):
    visites = serializers.ReadOnlyField(source="medecin_visites")
    region = serializers.ReadOnlyField(source="medecin_wilaya_commune")
    commercial = serializers.ReadOnlyField(source="medecin_commercial")
    stock = serializers.SerializerMethodField()
    last_visite = serializers.SerializerMethodField()
    current_year_visites = serializers.SerializerMethodField()
    deals = serializers.SerializerMethodField()

    def get_current_year_visites(self, obj):
        return obj.nbr_visites_year
        # return

    def get_last_visite(self, obj):
        try:
            return f"{obj.last_visite().rapport.added} Par {obj.last_visite().rapport.user}"
        except:
            return " "

    def get_stock(self, obj):
        return ProduitVisiteSerializer(
            ProduitVisite.objects.filter(medecin=obj), many=True
        ).data

    def get_deals(self, obj):
        # return [d.__json__() for d in obj.deal_set.all()]
        return []

    class Meta:
        model = Medecin
        fields = "__all__"


from rest_framework import serializers


class MedecinPlanSerializer(serializers.ModelSerializer):
    visites = serializers.ReadOnlyField(source="medecin_visites")
    region = serializers.ReadOnlyField(source="medecin_wilaya_commune")
    commercial = serializers.ReadOnlyField(source="medecin_commercial")
    last_visite = serializers.SerializerMethodField()
    selected_medecin_in_month_plan = serializers.SerializerMethodField()
    planning_dates = (
        serializers.SerializerMethodField()
    )  # Ajout du champ pour les dates de planning

    def get_last_visite(self, obj):
        # On utilise l'annotation `last_visite_date` ajoutée dans la vue
        try:
            if obj.last_visite_date:
                return f"Le {obj.last_visite_date.strftime('%d/%m/%Y')}"
            return "Aucune visite"
        except AttributeError:
            return " "

    def get_selected_medecin_in_month_plan(self, obj):
        # Obtenez l'utilisateur depuis le contexte du serializer
        request = self.context.get("request")
        if request is not None:
            # Appelez la méthode du médecin pour obtenir le nombre de plans
            return obj.count_plans_for_user(request)  # Appel de la méthode ici
        return 0  # Retourne 0 si request n'est pas disponible

    def get_planning_dates(self, obj):
        # Obtenir la date actuelle
        today = timezone.now()
        first_day_of_month = today.replace(day=1)
        last_day_of_month = (first_day_of_month + timezone.timedelta(days=31)).replace(
            day=1
        ) - timezone.timedelta(days=1)

        request = self.context.get("request")
        user = request.user if request else None

        # Obtenir les dates de planning pour le mois courant
        plans = Plan.objects.filter(
            clients=obj,
            day__range=(first_day_of_month, last_day_of_month),
            user=user,  # Filtrer par l'utilisateur connecté
        ).values_list("day", flat=True)
        return list(plans)  # Retourne une liste des dates

    class Meta:
        model = Medecin
        fields = "__all__"


"""
    nom=models.CharField(max_length=255,db_index=True)
    specialite = models.CharField(max_length=15,choices=Specialite.choices,default=Specialite.generaliste,db_index=True)
    commune=models.ForeignKey(Commune,on_delete=models.CASCADE)
    adresse=models.CharField(max_length=255)
    flag=models.BooleanField(default=False)
    users=models.ManyToManyField(User,blank=True)
"""


class MedecinSimpleSerializer(serializers.ModelSerializer):
    users = serializers.SerializerMethodField()
    region = serializers.SerializerMethodField()
    last_visite = serializers.SerializerMethodField()

    class Meta:
        model = Medecin
        fields = [
            "id",
            "nom",
            "specialite",
            "region",
            "flag",
            "users",
            "telephone",
            "classification",
            "last_visite",
            "lat",
            "lon",
        ]

    def get_users(self, obj):
        return [user.username for user in obj.users.all()]

    def get_region(self, obj):
        return f"{obj.commune.wilaya} {obj.commune.nom}"

    def get_last_visite(self, obj):
        try:
            return obj.last_visite().rapport.added
        except:
            return "non visité"
