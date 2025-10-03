from django.shortcuts import render
from django.http import JsonResponse

from .models import *

# Create your views here.
def front_main(request):
    print("Front Main")
    return render(request, 'main/list.html')

def front_add(request):
    return render(request, 'main/index.html')

import requests
from django.http import JsonResponse

def proxy_openrouteservice(request):
    start = request.GET.get('start')
    end = request.GET.get('end')

    # Remplacez par votre propre clé API OpenRouteService
    api_key = '5b3ce3597851110001cf62480f0f56a3b8da4df384f203a20d3eb034'

    url = f"https://api.openrouteservice.org/v2/directions/driving-car"
    params = {
        "api_key": api_key,
        "start": start,
        "end": end
    }

    # Faire la requête vers l'API OpenRouteService
    response = requests.get(url, params=params)

    # Retourner la réponse sous forme de JSON
    return JsonResponse(response.json())

import re
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Deplacement, NuitDetail

@csrf_exempt
def create_deplacement(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        raw_distance = data.get('distance', '')
        cleaned_distance = re.sub(r'[^\d.]', '', raw_distance)  # Keep only numbers and decimal points

        print(str(data))

        # Save Deplacement
        deplacement = Deplacement.objects.create(
            start_date=data['startDate'],
            end_date=data['endDate'],
            nb_jours=data['nbJours'],
            nb_nuits=data['nbNuits'],
            wilaya1=data['wilaya1'],
            wilaya2=data['wilaya2'],
            distance=cleaned_distance,
            user=request.user
        )

        # Save NuitDetails
        for nuit in data.get('nuitsDetails', []):
            NuitDetail.objects.create(
                deplacement=deplacement,
                nuit=nuit['nuit'],
                start_date=nuit['startDate'],
                end_date=nuit['endDate']
            )
        print("deplacement created succefully")

        return JsonResponse({'status': 'success', 'message': 'Deplacement created successfully!'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)



from django.http import JsonResponse
from .models import Deplacement
from django.db.models import Q

from django.http import JsonResponse
from .models import Deplacement

def get_deplacements(request):
    print("GETTING DEPLACEMNTS")
    filters = {}
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    nb_jours = request.GET.get('nb_jours')
    nb_nuits = request.GET.get('nb_nuits')

    if start_date:
        filters['start_date__gte'] = start_date
    if end_date:
        filters['end_date__lte'] = end_date
    if nb_jours:
        filters['nb_jours'] = nb_jours
    if nb_nuits:
        filters['nb_nuits'] = nb_nuits

    deplacements = Deplacement.objects.filter(**filters).select_related('user').prefetch_related('nuits_details')
    data = []
    for deplacement in deplacements:
        nuits_details = [
            {
                'nuit': nuit.nuit,
                'start_date': nuit.start_date.strftime('%Y-%m-%d'),
                'end_date': nuit.end_date.strftime('%Y-%m-%d'),
            }
            for nuit in deplacement.nuits_details.all()
        ]
        data.append({
            'id': deplacement.id,
            'user': deplacement.user.username,
            'status': deplacement.status,
            'start_date': deplacement.start_date.strftime('%Y-%m-%d'),
            'end_date': deplacement.end_date.strftime('%Y-%m-%d'),
            'nb_jours': deplacement.nb_jours,
            'nb_nuits': deplacement.nb_nuits,
            'wilaya1': deplacement.wilaya1,
            'wilaya2': deplacement.wilaya2,
            'distance': deplacement.distance,
            'created_at': deplacement.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'nuits_details': nuits_details,
        })
    
    return JsonResponse(data, safe=False)


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from .models import Deplacement
import json

@csrf_exempt
def update_status(request, deplacement_id):
    if request.method == 'PATCH':
        try:
            # Parse the request body
            data = json.loads(request.body)
            next_status = data.get('status')
            
            # Get the Deplacement object
            deplacement = get_object_or_404(Deplacement, id=deplacement_id)

            # Update the status
            deplacement.status = next_status
            deplacement.save()

            # Respond with the updated status
            return JsonResponse({'status': 'success', 'new_status': deplacement.status})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    # Return a 405 if the method is not allowed
    return JsonResponse({'error': 'Method not allowed'}, status=405)
