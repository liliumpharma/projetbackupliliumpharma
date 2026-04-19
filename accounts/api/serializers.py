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
        lines_raw = getattr(obj.userprofile, 'lines', None) or ''
        lines = [l.strip() for l in lines_raw.split(',') if l.strip()]
        if lines:
            return f"{obj.username} - {' - '.join(lines)}"
        return obj.username

    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email", "country"]


class MedecinSpecialiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedecinSpecialite
        fields = "__all__"
