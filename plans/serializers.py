from downloads.models import Downloadable
from rest_framework import serializers
import json


from .models import *
from medecins.api.serializers import MedecinSimpleSerializer


class PlanTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanTask
        fields = ["id", "task", "order"]


class PlanCommentSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="user.username")

    class Meta:
        model = PlanComment
        fields = "__all__"


class PlanSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="user.username")
    clients = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    communes = serializers.SerializerMethodField()
    tasks = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    isfree = serializers.SerializerMethodField()
    griffe_de_passage_medical = serializers.SerializerMethodField()
    griffe_de_passage_commercial = serializers.SerializerMethodField()

    class Meta:
        model = Plan
        fields = "__all__"

    def get_isfree(self, obj):
        return obj.isfree

    def get_clients(self, obj):
        return MedecinSimpleSerializer(obj.clients, many=True).data

    def get_comments(self, obj):
        return PlanCommentSerializer(obj.plancomment_set.all(), many=True).data

    def get_username(self, obj):
        return obj.user.username

    def get_communes(self, obj):
        user_in_context = self.context.get(
            "user"
        )  # Récupérer l'utilisateur dans le contexte
        return [
            {
                "id": commune.id,
                "nom": commune.nom,
                "wilaya_name": commune.wilaya.nom,
                "client_count": commune.nbr_medecins(obj.user),
                "client_all_count": commune.nbr_medecins_all(user_in_context),
                "commercial_count": commune.nbr_commercial(obj.user),
                "commercial_all_count": commune.nbr_commercial_all(
                    self.context.get("user")
                ),
            }
            for commune in obj.communes.all()
        ]

    def get_tasks(self, obj):
        return [
            {
                "id": task.id,
                "task": task.task,
                "added": task.added,
                "order": task.order,
                "is_transferred": task.is_transferred,
                "transferred_by": (
                    f"{task.transferred_by.first_name} {task.transferred_by.last_name}"
                    if task.transferred_by
                    else None
                ),
                "transferred_at": task.transferred_at,
            }
            for task in obj.plantask_set.all()
        ]

    def get_griffe_de_passage_medical(self, obj):

        # Récupérer le nom d'utilisateur et la date minimale
        username = obj.user.username
        min_date = self.context.get(
            "min_date"
        )  # Assuming min_date is passed via context

        # Ensure min_date is not None or empty
        if min_date:
            if isinstance(min_date, str):
                try:
                    # Convertir min_date en objet datetime si c'est une chaîne
                    min_date = datetime.strptime(min_date, "%Y-%m-%d")
                except ValueError:
                    print(f"Invalid date format for min_date: {min_date}")
                    min_date = timezone.now()  # Fallback to current date
        else:
            # Handle the case where min_date is not provided
            min_date = timezone.now()  # Use current date if min_date is not available

        # Extraire le mois de min_date
        min_month = min_date.strftime("%m")

        link_name = f"{username}_02.pdf"

        # Essayer de récupérer le fichier Downloadable
        try:
            downloadable = Downloadable.objects.get(link_name=link_name, users=obj.user)
            return f"https://app.liliumpharma.com/media/{downloadable.attachement}"
        except Downloadable.DoesNotExist:
            return f""  # Si le fichier n'existe pas, retourner None

    def get_griffe_de_passage_commercial(self, obj):  # Renommé ici
        # Récupérer le nom d'utilisateur et le mois courant
        username = obj.user.username
        current_month = timezone.now().strftime(
            "%m"
        )  # Obtient le mois courant au format MM


        link_name = f"Griffe de passage pharmacie_{username}_2"

        # Essayer de récupérer le fichier Downloadable
        try:
            downloadable = Downloadable.objects.get(link_name=link_name, users=obj.user)
            return f"https://app.liliumpharma.com/media/{downloadable.attachement}"  # Préfixe l'URL
        except Downloadable.DoesNotExist:
            return f""  # Si le fichier n'existe pas, retourner None
