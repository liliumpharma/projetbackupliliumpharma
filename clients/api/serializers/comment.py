from rest_framework.serializers import ModelSerializer

from clients.models import MonthComment


class MonthComment(ModelSerializer):
    class Meta:
        model = MonthComment
        fields = '__all__'