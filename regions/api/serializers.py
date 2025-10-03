from rest_framework import serializers
from regions.models import Pays


class PaysSerializer(serializers.ModelSerializer):
    wilayas_list=serializers.ReadOnlyField(source='wilayas')
    class Meta:
        model = Pays
        fields ='__all__'
