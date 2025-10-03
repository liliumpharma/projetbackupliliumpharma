from django.shortcuts import render
from .models import *
from django.http import Http404 
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.db.models import Q, Count
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from .models import *

from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import authentication, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.authentication import SessionAuthentication, TokenAuthentication, BasicAuthentication

from rest_framework.authtoken.models import Token
from django.shortcuts import render,redirect
from django.core.mail import EmailMessage

from django.contrib.auth.decorators import login_required

from datetime import date


@login_required
def versement_front(request):
    return render(request, "versement/index.html")

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views import View
import json
from .forms import VersementModelForm  # Import the VersementModelForm here

from datetime import date

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from django.core.files.base import ContentFile
import base64
from datetime import date

from .forms import VersementModelForm
from .models import PaybookUser, Versement

from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import date
from .models import Versement
from .forms import VersementModelForm

from django.http import JsonResponse
from .models import PaybookUser

def paybook_user_list(request):
    # Filter PaybookUser instances based on the current user
    paybook_users = PaybookUser.objects.filter(user=request.user, still_using = True)
    
    # Serialize the queryset to a list of dictionaries
    serialized_data = list(paybook_users.values())
    
    # Return the serialized data as a JSON response
    return JsonResponse(serialized_data, safe=False)


class CreateVersementAPI(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        data = request.data.copy()

        # Supprimez le token CSRF s'il est présent
        if 'csrfmiddlewaretoken' in data:
            del data['csrfmiddlewaretoken']
        file = request.FILES.get('attachement')
        type_f = type(file)
        print("attachement type" + str(type_f))
        paybook_user = PaybookUser.objects.get(user=request.user, still_using=True)

        today_date = date.today().strftime('%Y-%m-%d')

        mapped_data = {
            'added': today_date,
            'date_document': data.get('date_document'),
            'num_recu': data.get('num_recu'),
            'recu': data.get('client'),
            'somme': data.get('somme'),
            'way_of_payment': data.get('type'),
            'link': data.get('link'),
            'numero_de_cheque': data.get('numero_de_cheque', '-') if not data.get('numero_de_cheque') else data.get('numero_de_cheque'),
            'paybook': paybook_user,
            'attachement': request.FILES.get('attachement') 
        }
        print("Data received:", data)
        print("Mapped data:", mapped_data)
        print("File received:", request.FILES.get('attachement'))

        model_form = VersementModelForm(mapped_data, instance=Versement())

        if model_form.is_valid():
            # Enregistrez le formulaire si valide
            model_form.save()
            return Response({'success': 'Versement créé avec succès'})
        else:
            # Si le formulaire n'est pas valide, renvoyez les erreurs
            errors = model_form.errors
            print(errors)
            return Response({'error': 'Échec de la création du versement', 'errors': errors}, status=status.HTTP_400_BAD_REQUEST)


from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Creance

class CreanceAPI(APIView):

    def get(self, request):
        user = request.user
        creances = Creance.objects.filter(user=user)
        creances_client = CreanceClient.objects.filter(user=user)
        all_list = []
        creances_list = []
        for creance in creances:
            creance_dict = {
                'id': creance.id,
                'date': creance.date,
                'date_echeance': creance.date_echeance,
                'user': creance.user.username if creance.user else None,
                'attachement': creance.attachement.url if creance.attachement else None
            }
            creances_list.append(creance_dict)

        creances_list_client = []

        for creance in creances_client:
            creance_dict_client = {
                'id': creance.id,
                'date': creance.date,
                'user': creance.user.username if creance.user else None,
                'client': creance.client.nom,
                'attachement': creance.attachement.url if creance.attachement else None
            }
            creances_list_client.append(creance_dict_client)
        
        all_list.append(creances_list)
        all_list.append(creances_list_client)

        return Response(all_list)



class EncaissementAPI(APIView):

    def get(self, request):
        user = request.user
        versement_list = []
        id = request.GET.get("id")
        print("**********"+str(id))
        if id:
            print("***************UPDATE***************")
            versement = Versement.objects.filter(id=id).first()
            if versement is not None:
                versement_dict = {
                    'id': versement.id,
                    'bon': versement.num_recu,
                    'date': versement.date_document,
                    'client': versement.recu,
                    'type': versement.way_of_payment,
                    'num_cheque':versement.numero_de_cheque,
                    'montant': versement.somme,
                }
                versement_list.append(versement_dict)



        else:
            print("***************GETTING***************")
            if request.user.is_superuser or request.user.username=="MAALEM":
                versements = Versement.objects.all()
            else:
                versements = Versement.objects.filter(paybook__user=user)

            for versement in versements:
                versement_dict = {
                    'id': versement.id,
                    'carnet': versement.paybook.number,
                    'bon': versement.num_recu,
                    'date': versement.date_document,
                    'client': versement.recu,
                    'type': versement.way_of_payment,
                    'montant': versement.somme,
                    'attachement': versement.link,
                    'updatable': versement.updatable,
                }
                versement_list.append(versement_dict)
        return Response(versement_list)
