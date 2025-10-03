from rest_framework import serializers
from .models import Downloadable


class DownloadableSerializer(serializers.ModelSerializer):

    class Meta:
        model = Downloadable
        fields ='__all__'