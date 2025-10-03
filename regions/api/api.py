from regions.models import Pays
from .serializers import PaysSerializer
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class PaysApi(APIView):
    def get(self,request,format=None):
        pays=Pays.objects.all()
        serializer=PaysSerializer(pays,many=True)
        return Response(serializer.data, status=200)
