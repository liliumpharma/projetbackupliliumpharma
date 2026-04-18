from rest_framework import serializers
from accounts.models import UserProfile
from django.contrib.auth.models import User

from medecins.models import MedecinSpecialite


class UserProfileSerializer(serializers.ModelSerializer):
    nom = serializers.ReadOnlyField(source="user_nom")
    email = serializers.ReadOnlyField(source="user_email")
    region = serializers.ReadOnlyField(source="user_region")
    rapports = serializers.ReadOnlyField(source="user_rapports")
    visites_details = serializers.ReadOnlyField(source="user_visitess_details")
    other_details = serializers.ReadOnlyField(source="monthly_rapport_details")

    class Meta:
        model = UserProfile
        exclude = ["activate", "user"]


class EditProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.ReadOnlyField(source="user_first_name")
    last_name = serializers.ReadOnlyField(source="user_last_name")
    email = serializers.ReadOnlyField(source="user_email")

    class Meta:
        model = UserProfile
        exclude = ["activate", "user", "type", "id", "specialite"]


from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    country = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()

    def get_country(self, obj):
        return obj.userprofile.commune.wilaya.pays.id

    def get_username(self, obj):
        # Map family choices to their respective abbreviations
        family_abbreviation = {
            "lilium Pharma": "LP",
            "Lilium1": "L1",
            "Lilium2": "L2",
            "Lilium3": "L3",
            "Lilium1+2": "L1+2",
            "Lilium1+2+3": "L1+2+3",
            "ALL LINES": "ALL",
            "orient Bio": "ORI",
            "Aniya_Pharm": "AN",
            "production": "PROD",
        }

        # Get the abbreviation based on the family value
        family_value = obj.userprofile.family
        abbreviation = family_abbreviation.get(
            family_value, ""
        )  # Default to an empty string if no match

        # Return the desired username format with the abbreviation
        return f"{obj.username} - {abbreviation}"

    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email", "country"]


class MedecinSpecialiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedecinSpecialite
        fields = "__all__"
