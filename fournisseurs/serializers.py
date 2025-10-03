from rest_framework import serializers
from .models import Fournisseur, Information, Item, Achat, Sortie


# Serializer for Fournisseur model
class FournisseurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fournisseur
        fields = '__all__'


# Serializer for Information model
class InformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Information
        fields = '__all__'


# Serializer for Item model
class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'


# Serializer for Achat model
class AchatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achat
        fields = '__all__'


# Serializer for Sortie model
class SortieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sortie
        fields = '__all__'

