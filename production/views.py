from django.shortcuts import render
from django.http import JsonResponse

from .models import *

# Create your views here.

def front_main(request):
    return render(request, 'production_home.html')


def mp_front(request):
    return render(request, 'mp/index.html')


def mp_front_index(request):
    return render(request, 'mp/mp_index.html')

def pesee_front(request):
    return render(request, 'pesee/index.html')

def mp_pesee_front(request):
    return render(request, 'mp_pesee/index.html')

def tableting_front(request):
    return render(request, 'tablette/index.html')

def mp_approvisonnement_front(request):
    return render(request, 'mp/approvisionement.html')

def op_front(request):
    return render(request, 'OP/index.html')

def add_op_front(request):
    return render(request, 'OP/add_order.html')

def mp_op_front(request):
    return render(request, 'mp/order_production.html')

def pesee_front(request):
    return render(request, 'pesee/index.html')

def mp_coating_front(request):
    return render(request, 'mp/coating.html')

def mp_excipient_front(request):
    return render(request, 'mp/excipient.html')

def mp_active_ingredients_front(request):
    return render(request, 'mp/active_ingredients.html')

def mp_premix_front(request):
    return render(request, 'mp/premix.html')

def mp_mp_front(request):
    return render(request, 'mp/mp_index.html')

def mp_retour_front(request):
    return render(request, 'mp/retour.html')

def mp_sortie_front(request):
    return render(request, 'mp/sortie.html')

from django.http import JsonResponse
from .models import Entree

def entree_list(request):
    # Récupérer les filtres depuis l'URL
    print("$$$$ oh yeah fuck me baby $$$$$")
    e_type = request.GET.get('e_type', None)
    subtype = request.GET.get('subtype', None)
    fournisseur = request.GET.get('fournisseur', None)
    qtt = request.GET.get('qtt', None)
    unite = request.GET.get('unite', None)
    produit = request.GET.get('produit', None)

    # Filtrer les données selon les paramètres fournis
    # Récupérer les entrées où la quantité est supérieure à 0
    entrees = Entree.objects.filter(quantity__gt=0)

    # Appliquer les filtres si des paramètres sont fournis
    if e_type:
        entrees = entrees.filter(e_type=e_type)
    if subtype:
        entrees = entrees.filter(subtype=subtype)
    if fournisseur:
        entrees = entrees.filter(fournisseur__societe=fournisseur)
    if produit:
        entrees = entrees.filter(produit__nom=produit)





    
    print("----->"+str(entrees))


    # Préparer les données à retourner
    entree_data = [
        {
            'id': entree.id,  # ou autre champ du User si nécessaire
            'user': entree.user.username,  # ou autre champ du User si nécessaire
            'added': entree.added.strftime('%Y-%m-%d %H:%M:%S'),
            'fournisseur': entree.fournisseur.societe,  # Champ lié au fournisseur
            'number': entree.number,
            'qc_approval': entree.qc_approval,
            'lot': entree.lot,
            'manifacture_date': entree.manifacture_date,
            'expiry_date': entree.expiry_date,
            'ingredient_name': entree.ingredient_name,
            'e_type': entree.get_e_type_display(),
            'subtype': entree.get_subtype_display(),
            'produit': entree.produit.nom,  # Champ lié au produit
            'quantity': entree.quantity,
            'main_quantity': entree.quantity,
            'unite': entree.get_unite_display(),
            'price': str(entree.price),  # Convertir en chaîne pour JSON
            'devise': entree.get_devise_display(),
            'attachement': entree.attachement.url if entree.attachement else None,
        } for entree in entrees
    ]

    return JsonResponse(entree_data, safe=False)


from collections import defaultdict
from django.http import JsonResponse

from django.http import JsonResponse
from collections import defaultdict
from .models import Entree, Sortie, Retour, OrderProduction, ItemOrderProduction

from collections import defaultdict
from django.http import JsonResponse
from .models import Entree, Sortie, Retour, OrderProduction, ItemOrderProduction

def all_list(request):
    # Récupérer les filtres depuis l'URL
    e_type = request.GET.get('e_type', None)
    subtype = request.GET.get('subtype', None)
    fournisseur = request.GET.get('fournisseur', None)
    qtt = request.GET.get('qtt', None)

    # Filtrer les données selon les paramètres fournis
    entrees = Entree.objects.all()
    sorties = Sortie.objects.all()
    retours = Retour.objects.all()
    
    # Filtrer les OrderProduction avec transfered_from_stock=True
    transfered_ops = OrderProduction.objects.filter(transfered_from_stock=True)

    # Préparer les données des entrées
    entree_data = [
        {
            'id': entree.id,
            'type': "Entry",
            'user': entree.user.username,
            'added': entree.added.strftime('%Y-%m-%d %H:%M:%S'),
            'fournisseur': entree.fournisseur.societe,
            'number': entree.number,
            'qc_approval': entree.qc_approval,
            'lot': entree.lot,
            'manifacture_date': entree.manifacture_date,
            'expiry_date': entree.expiry_date,
            'e_type': entree.get_e_type_display(),
            'subtype': entree.get_subtype_display(),
            'produit': entree.produit.nom,
            'quantity': entree.quantity,
            'main_quantity': entree.main_quantity,
            'unite': entree.get_unite_display(),
            'price': str(entree.price),
            'devise': entree.get_devise_display(),
            'attachement': entree.attachement.url if entree.attachement else None,
        } for entree in entrees
    ]

    # Préparer les données des sorties
    sortie_data = [
        {
            'id': sortie.id,
            'type': "Sortie",
            'user': sortie.user.username,
            'lot': sortie.entree.lot,
            'added': sortie.added.strftime('%Y-%m-%d %H:%M:%S'),
            'fournisseur': sortie.fournisseur.societe,
            'number': 1,
            'qc_approval': sortie.entree.qc_approval,
            'manifacture_date': sortie.entree.manifacture_date,
            'expiry_date': sortie.entree.expiry_date,
            'e_type': sortie.get_e_type_display(),
            'subtype': sortie.get_subtype_display(),
            'produit': sortie.produit.nom,
            'quantity': sortie.quantity,
            'unite': sortie.get_unite_display(),
            'price': str(sortie.price),
            'devise': sortie.get_devise_display(),
            'attachement': sortie.attachement.url if sortie.attachement else None,
        } for sortie in sorties
    ]

    # Préparer les données des retours
    retour_data = [
        {
            'id': retour.id,
            'type': "Retour",
            'user': retour.user.username,
            'lot': retour.entree.lot,
            'added': retour.added.strftime('%Y-%m-%d %H:%M:%S'),
            'fournisseur': retour.fournisseur.societe,
            'number': 1,
            'qc_approval': retour.entree.qc_approval,
            'manifacture_date': retour.entree.manifacture_date,
            'expiry_date': retour.entree.expiry_date,
            'e_type': retour.get_e_type_display(),
            'subtype': retour.get_subtype_display(),
            'produit': retour.produit.nom,
            'quantity': retour.quantity,
            'unite': retour.get_unite_display(),
            'price': str(retour.price),
            'devise': retour.get_devise_display(),
            'attachement': retour.attachement.url if retour.attachement else None,
        } for retour in retours
    ]

    # Préparer les données des OrderProduction et leurs items associés
    op_data = []
    for op in transfered_ops:
        item_orders = ItemOrderProduction.objects.filter(order_production=op)
        op_data.append({
            'id': op.id,
            'type': "Transferred",
            'user': op.user.username,
            'produit': op.produit.nom,
            'batch_number': op.batch_number,
            'process_type': op.get_process_type_display(),
            'location': op.get_location_display(),
            'status': op.get_status_display(),
            'transfered_from_stock': op.transfered_from_stock,
            'returned_from_weight': op.returned_from_weight,
            'items': [
                {
                    'item_id': item.id,
                    'entree_lot': item.entree.lot if item.entree else None,
                    'produit': item.entree.produit.nom if item.entree else None,
                    'qtt': item.qtt,
                    'qtt_from_stock_to_weight': item.qtt_from_stock_to_weight,
                    'qtt_from_weight_to_stock': item.qtt_from_weight_to_stock,
                    'expiry_date': item.entree.expiry_date if item.entree else None,
                    'lot': item.entree.lot,
                    'added': item.entree.added.strftime('%Y-%m-%d %H:%M:%S'),
                    'fournisseur': item.entree.fournisseur.societe,
                    'number': 1,
                    'qc_approval': item.entree.qc_approval,
                    'manifacture_date': item.entree.manifacture_date,
                    'expiry_date': item.entree.expiry_date,
                    'e_type': item.entree.get_e_type_display(),
                    'subtype': item.entree.get_subtype_display(),
                    'produit': item.entree.produit.nom,
                    'quantity': item.entree.quantity,
                    'unite': item.entree.get_unite_display(),
                    'price': str(item.entree.price),
                    'devise': item.entree.get_devise_display(),
                    'attachement': item.entree.attachement.url if item.entree.attachement else None,
                } for item in item_orders
            ]
        })

    print("----->"+str(op_data))
    # Calcul de la quantité restante pour chaque produit/e_type/subtype
    recap_data = defaultdict(lambda: {'produit': '', 'e_type': '', 'subtype': '', 'qtt_restante': 0})
    
    # Ajouter les quantités des entrées
    for entree in entrees:
        key = (entree.produit.nom, entree.e_type, entree.subtype)
        recap_data[key]['produit'] = entree.produit.nom
        recap_data[key]['e_type'] = entree.get_e_type_display()
        recap_data[key]['subtype'] = entree.get_subtype_display()
        recap_data[key]['qtt_restante'] += entree.quantity

    # Transformer recap_data en liste
    recap_list = [
        {
            'produit': data['produit'],
            'e_type': data['e_type'],
            'subtype': data['subtype'],
            'qtt_restante': data['qtt_restante']
        } for key, data in recap_data.items()
    ]

    # Combiner les données des entrées, sorties, retours, et OrderProduction
    combined_data = {
        'entrees': entree_data,
        'sorties': sortie_data,
        'retours': retour_data,
        'recap': recap_list,  # Ajouter la récap des quantités restantes
        'order_productions': op_data  # Ajouter les OrderProduction et leurs items
    }

    return JsonResponse(combined_data, safe=False)


import json
from django.http import JsonResponse
from django.shortcuts import redirect, render
from .forms import EntreeForm
from django.views.decorators.csrf import csrf_exempt

from django.views.decorators.csrf import csrf_protect

from django.http import JsonResponse
import json
from .forms import EntreeForm
from django.views.decorators.csrf import csrf_protect

from django.http import JsonResponse
import json
from .forms import EntreeForm
from django.views.decorators.csrf import csrf_protect

from rest_framework.views import APIView
from rest_framework.response import Response
from .forms import EntreeForm
from .models import Entree
import json
from datetime import date
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from fournisseurs.models import Fournisseur
from produits.models import Produit
from .models import Entree
from datetime import date
class AddEntree(APIView):
    def post(self, request):

        # Copy request data and remove CSRF token
        data = request.data.copy()
        data.pop("csrfmiddlewaretoken", None)  # Ensure csrfmiddlewaretoken is removed

        # Add the user to the data (assuming `request.user` is authenticated)
        data["user"] = request.user

        # Récupérer les éléments du panier
        cart_items = data.get("cartItems", [])

        # Vérification que le panier contient des éléments
        if not cart_items:
            return Response({'message': 'Le panier est vide'}, status=400)


        print(str(data))

        # Préparer une liste pour collecter les entrées créées ou les erreurs
        created_entrees = []
        errors = []

        for item in range(nbr_rows):
            print(str(item))
            try:
                # Récupérer les objets liés (fournisseur, produit)
                fournisseur = Fournisseur.objects.get(societe=data['fournisseur'])  # Adjust based on field name
                produit = Produit.objects.get(nom=item['produit'])  # Adjust based on field name
            except Fournisseur.DoesNotExist:
                errors.append({'message': f'Fournisseur {data["fournisseur"]} not found'})
                continue
            except Produit.DoesNotExist:
                errors.append({'message': f'Produit {item["produit"]} not found'})
                continue

            # Préparer les données pour créer une entrée
            print(str(data['ingredient_name']))
            entree_data = {
                "user": request.user,
                "fournisseur": fournisseur,
                "number": 1,  # Ajustez si besoin
                "e_type": data['e_type'],
                "subtype": data['subtype'],
                "lot": data['lot'],
                "ingredient_name": data['ingredient_name'],
                "manifacture_date": data['manifacture_date'],
                "expiry_date": data['expiry_date'],
                "produit": produit,
                "quantity": item['quantity'],
                "unite": "unité",  # Spécifiez l'unité ou récupérez-la si elle est fournie
                "price": item['price'],
                "devise": "DZD",  # Ajustez la devise si nécessaire
            }

            # Sauvegarder l'entrée
            try:
                entree = Entree(**entree_data)
                entree.save()  # Save the entree object
                created_entrees.append(entree)
            except Exception as e:
                # Collecter l'erreur pour cet élément
                errors.append({'message': f'Erreur lors de la création de l\'entrée pour le produit {item["produit"]}', 'error': str(e)})

        # Si des erreurs sont survenues
        if errors:
            return Response({'message': 'Certaines entrées n\'ont pas pu être créées', 'errors': errors}, status=400)

        return Response({'message': 'Entrées créées avec succès', 'created_entrees': [entree.id for entree in created_entrees]}, status=201)


def sortie_list(request):
    sortie = Sortie.objects.all()  # Récupère toutes les entrées
    sortie_data = [
        {
            'user': sortie.user.username,  # ou autre champ du User si nécessaire
            'added': sortie.added.strftime('%Y-%m-%d %H:%M:%S'),
            'fournisseur': sortie.fournisseur.societe,  # Champ lié au fournisseur
            'number': sortie.number,
            'qc_approval': sortie.qc_approval,
            'e_type': sortie.get_e_type_display(),
            'subtype': sortie.get_subtype_display(),
            'produit': sortie.produit.nom,  # Champ lié au produit
            's_quantity': sortie.quantity,
            'unite': sortie.get_unite_display(),
            'price': str(sortie.price),  # Convertir en chaîne pour JSON
            'devise': sortie.get_devise_display(),
            'attachement': sortie.attachement.url if sortie.attachement else None,
        } for sortie in sorties
    ]
    return JsonResponse(sortie_data, safe=False)



from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Sortie, Fournisseur, Produit
from django.contrib.auth.models import User

from decimal import Decimal

class AddSortie(APIView):
    def post(self, request):
        # Copy request data and remove CSRF token
        data = request.data.copy()
        data.pop("csrfmiddlewaretoken", None)
        data["user"] = request.user

        # Debug print to check the incoming data
        print("Received data:", data)

        # Récupérer les éléments du panier (cartItems)
        cart_items = data.get("cartItems", [])
        print("Cart items:", cart_items)

        # Vérification que le panier contient des éléments
        if not cart_items:
            return Response({'message': 'Le panier est vide'}, status=400)

        # Préparer une liste pour collecter les entrées créées ou les erreurs
        created_sortie = []
        errors = []

        # Loop through each cart item and process
        for item in cart_items:
            print("Processing item:", item)
            try:
                # Retrieve related objects (fournisseur, produit, entree)
                fournisseur = Fournisseur.objects.get(societe=item['fournisseur'])
                produit = Produit.objects.get(nom=item['produit'])
                entree = Entree.objects.get(id=item['id'])
                print(f"Found fournisseur: {fournisseur}, produit: {produit}, entree: {entree}")
            except Fournisseur.DoesNotExist:
                errors.append({'message': f'Fournisseur {item["fournisseur"]} not found'})
                print(f"Fournisseur {item['fournisseur']} not found")
                continue
            except Produit.DoesNotExist:
                errors.append({'message': f'Produit {item["produit"]} not found'})
                print(f"Produit {item['produit']} not found")
                continue
            except Entree.DoesNotExist:
                errors.append({'message': f'Entree {item["id"]} not found'})
                print(f"Entree {item['id']} not found")
                continue

            # Vérifier si la quantité demandée est disponible dans l'entrée
            quantity_requested = int(item['quantity'])
            if entree.quantity < quantity_requested:
                errors.append({'message': f'Quantité insuffisante pour le produit {item["produit"]}. Disponible: {entree.quantity}, Demandée: {quantity_requested}'})
                print(f"Quantité insuffisante pour {item['produit']}. Disponible: {entree.quantity}, Demandée: {quantity_requested}")
                continue

            # Prepare the data to create a Sortie entry
            try:
                sortie_data = {
                    "user": request.user,
                    "fournisseur": fournisseur,
                    "entree": entree,
                    "number": item.get('id', 1),
                    "e_type": item['type'],
                    "subtype": item['subType'],
                    "produit": produit,
                    "quantity": quantity_requested,  # Quantité demandée
                    "unite": "kg",
                    "price": item['price'],  # Ensure price is a decimal
                    "devise": "DZD",
                }
                sortie = Sortie(**sortie_data)
                sortie.save()
                created_sortie.append(sortie)

                entree.quantity = entree.quantity - int(item['quantity'])
                entree.save()  # Sauvegarder l'entrée mise à jour
            except Exception as e:
                errors.append({'message': f'Erreur lors de la création de la sortie pour le produit {item["produit"]}', 'error': str(e)})
                print(f"Error creating sortie for product {item['produit']}: {e}")

        # Si des erreurs sont rencontrées
        if errors:
            print("Errors encountered:", errors)
            return Response({'message': 'Certaines sorties n\'ont pas pu être créées', 'errors': errors}, status=400)

        # Réponse en cas de succès
        print(f"Created sorties: {[sortie.id for sortie in created_sortie]}")
        return Response({'message': 'Sorties créées avec succès', 'created_sortie': [sortie.id for sortie in created_sortie]}, status=201)

# ---------------------------


class AddRetour(APIView):
    def post(self, request):
        # Copy request data and remove CSRF token
        data = request.data.copy()
        data.pop("csrfmiddlewaretoken", None)
        data["user"] = request.user

        # Debug print to check the incoming data
        print("Received data:", data)

        # Récupérer les éléments du panier (cartItems)
        cart_items = data.get("cartItems", [])
        print("Cart items:", cart_items)

        # Vérification que le panier contient des éléments
        if not cart_items:
            return Response({'message': 'Le panier est vide'}, status=400)

        # Préparer une liste pour collecter les entrées créées ou les erreurs
        created_retour = []
        errors = []

        # Loop through each cart item and process
        for item in cart_items:
            print("Processing item:", item)
            try:
                # Retrieve related objects (fournisseur, produit, entree)
                fournisseur = Fournisseur.objects.get(societe=item['fournisseur'])
                produit = Produit.objects.get(nom=item['produit'])
                entree = Entree.objects.get(id=item['id'])
                print(f"Found fournisseur: {fournisseur}, produit: {produit}, entree: {entree}")
            except Fournisseur.DoesNotExist:
                errors.append({'message': f'Fournisseur {item["fournisseur"]} not found'})
                print(f"Fournisseur {item['fournisseur']} not found")
                continue
            except Produit.DoesNotExist:
                errors.append({'message': f'Produit {item["produit"]} not found'})
                print(f"Produit {item['produit']} not found")
                continue
            except Entree.DoesNotExist:
                errors.append({'message': f'Entree {item["id"]} not found'})
                print(f"Entree {item['id']} not found")
                continue

            # Vérifier si la quantité demandée est disponible dans l'entrée
            quantity_requested = int(item['quantity'])
            if entree.quantity < quantity_requested:
                errors.append({'message': f'Quantité insuffisante pour le produit {item["produit"]}. Disponible: {entree.quantity}, Demandée: {quantity_requested}'})
                print(f"Quantité insuffisante pour {item['produit']}. Disponible: {entree.quantity}, Demandée: {quantity_requested}")
                continue

            # Prepare the data to create a Sortie entry
            try:
                retour_data = {
                    "user": request.user,
                    "fournisseur": fournisseur,
                    "entree": entree,
                    "number": item.get('id', 1),
                    "e_type": item['type'],
                    "subtype": item['subType'],
                    "produit": produit,
                    "quantity": quantity_requested,  # Quantité demandée
                    "unite": "kg",
                    "price": item['price'],  # Ensure price is a decimal
                    "devise": "DZD",
                }
                retour = Retour(**retour_data)
                retour.save()
                created_retour.append(retour)
                entree.quantity = entree.quantity - int(item['quantity'])
                entree.save()  # Sauvegarder l'entrée mise à jour
            except Exception as e:
                errors.append({'message': f'Erreur lors de la création de la sortie pour le produit {item["produit"]}', 'error': str(e)})
                print(f"Error creating sortie for product {item['produit']}: {e}")

        # Si des erreurs sont rencontrées
        if errors:
            return Response({'message': 'Certaines sorties n\'ont pas pu être créées', 'errors': errors}, status=400)

        # Réponse en cas de succès
        return Response({'message': 'Sorties créées avec succès', 'created_retour': [retour.id for retour in created_retour]}, status=201)




def retour_list(request):
    retours = Retour.objects.all()  # Récupère toutes les entrées
    retour_data = [
        {
            'user': retour.user.username,  # ou autre champ du User si nécessaire
            'added': retour.added.strftime('%Y-%m-%d %H:%M:%S'),
            'fournisseur': retour.fournisseur.societe,  # Champ lié au fournisseur
            'number': retour.number,
            'qc_approval': retour.qc_approval,
            'e_type': retour.get_e_type_display(),
            'subtype': retour.get_subtype_display(),
            'produit': retour.produit.nom,  # Champ lié au produit
            'r_quantity': retour.quantity,
            'unite': retour.get_unite_display(),
            'price': str(retour.price),  # Convertir en chaîne pour JSON
            'devise': retour.get_devise_display(),
            'attachement': retour.attachement.url if retour.attachement else None,
        } for retour in retours
    ]
    return JsonResponse(retour_data, safe=False)




def entree_list(request):
    # Récupérer les filtres depuis l'URL
    print("$$$$ oh yeah fuck me baby $$$$$")
    e_type = request.GET.get('e_type', None)
    subtype = request.GET.get('subtype', None)
    fournisseur = request.GET.get('fournisseur', None)
    qtt = request.GET.get('qtt', None)
    unite = request.GET.get('unite', None)
    produit = request.GET.get('produit', None)

    # Filtrer les données selon les paramètres fournis
    # Récupérer les entrées où la quantité est supérieure à 0
    entrees = Entree.objects.filter(quantity__gt=0)

    # Appliquer les filtres si des paramètres sont fournis
    if e_type:
        entrees = entrees.filter(e_type=e_type)
    if subtype:
        entrees = entrees.filter(subtype=subtype)
    if fournisseur:
        entrees = entrees.filter(fournisseur__societe=fournisseur)
    if produit:
        entrees = entrees.filter(produit__nom=produit)





    
    print("----->"+str(entrees))


    # Préparer les données à retourner
    entree_data = [
        {
            'id': entree.id,  # ou autre champ du User si nécessaire
            'user': entree.user.username,  # ou autre champ du User si nécessaire
            'added': entree.added.strftime('%Y-%m-%d %H:%M:%S'),
            'fournisseur': entree.fournisseur.societe,  # Champ lié au fournisseur
            'number': entree.number,
            'qc_approval': entree.qc_approval,
            'lot': entree.lot,
            'manifacture_date': entree.manifacture_date,
            'expiry_date': entree.expiry_date,
            'ingredient_name': entree.ingredient_name,
            'e_type': entree.get_e_type_display(),
            'subtype': entree.get_subtype_display(),
            'produit': entree.produit.nom,  # Champ lié au produit
            'quantity': entree.quantity,
            'main_quantity': entree.quantity,
            'unite': entree.get_unite_display(),
            'price': str(entree.price),  # Convertir en chaîne pour JSON
            'devise': entree.get_devise_display(),
            'attachement': entree.attachement.url if entree.attachement else None,
        } for entree in entrees
    ]

    return JsonResponse(entree_data, safe=False)



from django.http import JsonResponse
def entree_list_op(request):
    # Récupérer les filtres depuis l'URL
    produit = request.GET.get('produit', None)
    qtt_getted = int(request.GET.get('qtt', 0))
    
    # Filtrer les entrées Premix et Premix powder
    entrees = Entree.objects.filter(e_type='Premix', subtype='Premix powder')

    # Si un produit est spécifié, on filtre aussi par produit
    if produit:
        entrees = entrees.filter(produit__nom=produit)

    # Trier les entrées par quantité (du plus petit au plus grand)
    entrees = entrees.order_by('quantity')

    # Accumuler les quantités jusqu'à atteindre qtt_getted
    selected_entrees = []
    total_qtt = 0

    for entree in entrees:
        selected_entrees.append(entree)
        total_qtt += entree.quantity
        if total_qtt >= qtt_getted:
            break

    # Récupérer les ingrédients inactifs ayant coating_material=True pour ce produit
    inactive_ingredients = ProductInactiveIngredients.objects.filter(produit__nom=produit, coating_material=True)

    # Vérifier si les ingrédients inactifs sont déjà dans les entrées
    ingredient_data = []
    for inactive in inactive_ingredients:
        # Chercher l'entrée correspondante avec ingredient_name
        entree_with_ingredient = next((e for e in selected_entrees if e.ingredient_name == inactive.ingredient), None)

        if entree_with_ingredient:
            # Si l'entrée existe, utiliser ses informations
            ingredient_data.append({
                'ingredient': entree_with_ingredient.ingredient_name,
                'quantity': entree_with_ingredient.quantity,
                'lot': entree_with_ingredient.lot,
                'manifacture_date': entree_with_ingredient.manifacture_date.strftime('%Y-%m-%d'),
                'expiry_date': entree_with_ingredient.expiry_date.strftime('%Y-%m-%d'),
            })
        else:
            # Sinon, retourner une entrée avec des valeurs "Pas disponible"
            ingredient_data.append({
                'ingredient': inactive.ingredient,
                'produit': produit,
                'quantity': inactive.quantity,
                'lot': 'Pas disponible',
                'manifacture_date': 'Pas disponible',
                'expiry_date': 'Pas disponible',
            })

    # Préparer la réponse
    response_data = {
        'entrees': [
            {
                'id': e.id,
                'produit': e.produit.nom,
                'e_type': e.e_type,
                'subtype': e.subtype,
                'ingredient_name': e.ingredient_name,
                'quantity': e.quantity,
                'lot': e.lot,
                'manifacture_date': e.manifacture_date.strftime('%Y-%m-%d'),
                'expiry_date': e.expiry_date.strftime('%Y-%m-%d'),
            }
            for e in selected_entrees
        ],
        'inactive_ingredients': ingredient_data  # Ajout des ingrédients inactifs
    }

    if total_qtt >= qtt_getted:
        return JsonResponse(response_data)
    else:
        return JsonResponse({'error': 'Quantité insuffisante'}, status=400)



from django.http import JsonResponse

def product_ingredients(request):
    # Récupérer les filtres depuis l'URL
    produit = request.GET.get('produit')
    qtt = request.GET.get('qtt')
    estimated = request.GET.get('estimated_tablets')

    # Vérifier que les paramètres requis sont fournis
    if not produit or not qtt or not estimated:
        return JsonResponse({"error": "Produit, quantité et estimation de tablettes requis"}, status=400)

    try:
        qtt = int(qtt)
        estimated = float(estimated)
    except ValueError:
        return JsonResponse({"error": "Quantité ou estimation invalide"}, status=400)

    # Filtrer les 'Entree' par produit, type et sous-type pour les ingrédients actifs
    entrees = Entree.objects.filter(produit__nom=produit, e_type="Premix", subtype="Premix powder")

    # Calculer la somme des quantités des 'Entree'
    total_quantity = sum(entree.quantity for entree in entrees)

    # Calcul du nombre de tablettes disponibles (chaque tablette pèse 1.65g)
    dosage_per_tablet = 1.67  # en grammes
    available_tablets_entrees = (total_quantity * 1000) / dosage_per_tablet if total_quantity > 0 else 0

    # Vérifier la disponibilité en fonction de la quantité demandée
    available = "yes" if total_quantity >= qtt else "no"

    # Récupérer les ingrédients inactifs ayant 'coating_material=True'
    inactive_ingredients = ProductInactiveIngredients.objects.filter(produit__nom=produit, coating_material=True)

    # Préparer la liste des ingrédients inactifs avec leurs détails
    inactive_ingredients_list = []
    for ingredient in inactive_ingredients:
        # Filtrer les 'Entree' par ingrédient inactif et produit
        total_quantity_ingredient = sum(
            entry.quantity for entry in Entree.objects.filter(
                produit__nom=produit, ingredient_name=ingredient.ingredient
            )
        ) *1000 *1000

        # Vérifier la disponibilité de l'ingrédient inactif
        ingredient_available = "yes" if total_quantity_ingredient > ingredient.quantity * estimated else "no"

        # Calcul du nombre de tablettes disponibles pour cet ingrédient
        concentration_per_tablet = ingredient.quantity / 1670
        print("1 - "+str(qtt))
        print("2 - "+str(total_quantity_ingredient))
        print("3 - "+str(ingredient.quantity))
        calc = total_quantity_ingredient/ingredient.quantity
        print("4 - "+str(calc/30))
        final_1 = int(calc/30)

        
        qtt_gr = qtt*1000
        final = qtt_gr*concentration_per_tablet

        # available_tablets_inactive = int((total_quantity_ingredient*1000) / ingredient.quantity) if total_quantity_ingredient > 0 else 0
        available_tablets_inactive = int((total_quantity_ingredient) * concentration_per_tablet) if total_quantity_ingredient > 0 else 0
        requested_qtt = (estimated*ingredient.quantity)/1000/1000

        print("---------- "+str(available_tablets_inactive/30))

        # Ajouter les détails de l'ingrédient inactif à la liste
        inactive_ingredients_list.append({
            "produit": produit,
            "e_type": "Coating",
            "sub_type": ingredient.ingredient,
            "quantity": str(total_quantity_ingredient/1000/1000),
            "quantity_requested": str(final),
            "tablets_disponibles": f"الكميه الاحماليه الموحوذه تكغي لانتاح {final_1} ",
            "disponible": ingredient_available
        })

    # Préparer la réponse JSON
    response_data = {
        "produit": produit,
        "e_type": "Premix",
        "sub_type": "Premix powder",
        "Qtt_disponible": str(total_quantity)+"Kg",
        "tablets_disponibles": available_tablets_entrees/30,
        "disponible": available,
        "inactive_ingredients": inactive_ingredients_list,
    }

    # Affichage dans la console pour le débogage
    print(response_data)

    return JsonResponse(response_data)




from django.http import JsonResponse
from rest_framework.views import APIView
from .models import OrderProduction
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404
from django.views import View
import json

# Liste et création de OrderProduction
class OrderProductionListCreateView(APIView):

    # Liste des commandes de production
    def get(self, request):
        orders = OrderProduction.objects.all()
        data = [{"id": order.id,"code": order.code, "batch_number": order.batch_number, "process_type": order.process_type, "added": order.added, "user": order.user.username, "produit": order.produit.nom,  "location": order.location,"status":order.status} for order in orders]
        return JsonResponse(data, safe=False)

    # Création d'une commande de production
    @method_decorator(csrf_exempt)  # Désactive CSRF pour faciliter les tests
    def post(self, request):
        try:
            data = json.loads(request.body)
            user = data.get('user')
            produit = data.get('produit')
            batch_number = data.get('batch_number')
            process_type = data.get('process_type')

            order = OrderProduction.objects.create(
                user_id=user,
                produit_id=produit,
                batch_number=batch_number,
                process_type=process_type
            )
            return JsonResponse({"id": order.id}, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

# Détails, mise à jour et suppression de OrderProduction
class OrderProductionDetailView(APIView):

    def get(self, request, pk):
        order = get_object_or_404(OrderProduction, pk=pk)
        data = {
            "id": order.id,
            "batch_number": order.batch_number,
            "process_type": order.process_type,
            "added": order.added,
            "user": order.user.username,
            "produit": order.produit.name
        }
        return JsonResponse(data)

    @method_decorator(csrf_exempt)
    def put(self, request, pk):
        try:
            data = json.loads(request.body)
            order = get_object_or_404(OrderProduction, pk=pk)
            order.batch_number = data.get('batch_number', order.batch_number)
            order.process_type = data.get('process_type', order.process_type)
            order.save()
            return JsonResponse({"id": order.id}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    @method_decorator(csrf_exempt)
    def delete(self, request, pk):
        try:
            order = get_object_or_404(OrderProduction, pk=pk)
            order.delete()
            return JsonResponse({"message": "Order deleted"}, status=204)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)



# Détails, mise à jour et suppression de OrderProduction
from django.http import JsonResponse
class OrderProductionPeseeDetailView(APIView):

    # Liste des commandes de production

    # Liste des commandes de production
    def get(self, request):
        print("^^^^^^")
        locations = ["pesee", "mp_pesee"]
        orders = OrderProduction.objects.filter(location__in=locations)

        data = [{
            "id": order.id,
            "batch_number": order.batch_number,
            "process_type": order.process_type,
            "added": order.added,
            "user": order.user.username,
            "produit": order.produit.nom,
            "location": order.location,
            "status": order.status,
            # Retrieve batch size from related ProductProductionInfos
            "bash_size": ProductProductionInfos.objects.filter(produit=order.produit).values_list('batch_size', flat=True).first()
        } for order in orders]

        return JsonResponse(data, safe=False)


    # Création d'une commande de production
    @method_decorator(csrf_exempt)  # Désactive CSRF pour faciliter les tests
    def post(self, request):
        try:
            data = json.loads(request.body)
            user = data.get('user')
            produit = data.get('produit')
            batch_number = data.get('batch_number')
            process_type = data.get('process_type')

            order = OrderProduction.objects.create(
                user_id=user,
                produit_id=produit,
                batch_number=batch_number,
                process_type=process_type
            )
            return JsonResponse({"id": order.id}, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


from django.http import JsonResponse
from rest_framework.views import APIView
from .models import ItemOrderProduction, OrderProduction
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404
import json

# Liste et création de ItemOrderProduction
class ItemOrderProductionListCreateView(APIView):

    # Liste des articles de commande de production
    def get(self, request):
        items = ItemOrderProduction.objects.all()
        data = [{"id": item.id, "order_production": item.order_production.id, "item": item.item, "qtt": item.qtt} for item in items]
        return JsonResponse(data, safe=False)

    # Création d'un article pour une commande de production
    @method_decorator(csrf_exempt)
    def post(self, request):
        try:
            data = json.loads(request.body)
            order_production = data.get('order_production')
            item = data.get('item')
            qtt = data.get('qtt')

            item_order = ItemOrderProduction.objects.create(
                order_production_id=order_production,
                item=item,
                qtt=qtt
            )
            return JsonResponse({"id": item_order.id}, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

# Détails, mise à jour et suppression de ItemOrderProduction
class ItemOrderProductionDetailView(APIView):

    def get(self, request, pk):
        item = get_object_or_404(ItemOrderProduction, pk=pk)
        data = {
            "id": item.id,
            "order_production": item.order_production.id,
            "item": item.item,
            "qtt": item.qtt
        }
        return JsonResponse(data)

    @method_decorator(csrf_exempt)
    def put(self, request, pk):
        try:
            data = json.loads(request.body)
            item = get_object_or_404(ItemOrderProduction, pk=pk)
            item.item = data.get('item', item.item)
            item.qtt = data.get('qtt', item.qtt)
            item.save()
            return JsonResponse({"id": item.id}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    @method_decorator(csrf_exempt)
    def delete(self, request, pk):
        try:
            item = get_object_or_404(ItemOrderProduction, pk=pk)
            item.delete()
            return JsonResponse({"message": "Item deleted"}, status=204)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

from django.http import JsonResponse
from rest_framework.views import APIView
from .models import ItemOrderProduction

class ItemOrderProductionsListView(APIView):
    """
    Récupère tous les ItemOrderProduction associés à une commande de production spécifique.
    """
    def get(self, request, order_production_id):
        items = ItemOrderProduction.objects.filter(order_production_id=order_production_id)
        
        # Préparer les données à envoyer
        data = [
            {
                "id": item.id,
                "order_production": item.order_production.id,
                "item": item.item,
                "qtt": item.qtt,
                "unite": item.unite,
                "produit": item.order_production.produit.nom,
            }
            for item in items
        ]
        
        return JsonResponse(data, safe=False)


class ReceptionnerOrderProductionView(View):
    def post(self, request, order_id):
        # Récupérer l'instance OrderProduction
        order = get_object_or_404(OrderProduction, id=order_id)

        # Mettre à jour la location à 'stock_mp'
        order.location = 'stock_mp'
        order.save()

        # Retourner une réponse JSON indiquant que la mise à jour a réussi
        return JsonResponse({"message": "Location mise à jour à stock_mp", "new_location": order.location})



class TransfertOrderProductionPeseeView(View):
    def post(self, request, order_id):
        # Récupérer l'instance OrderProduction
        print("----|||---")
        order = get_object_or_404(OrderProduction, id=order_id)

        # Mettre à jour la location à 'stock_mp'
        order.location = 'Tablette'
        order.status = 'waiting'
        order.save()

        # Retourner une réponse JSON indiquant que la mise à jour a réussi
        return JsonResponse({"message": "Location mise à jour à pesee", "new_location": order.location})

class TransfertOrderProductionMpPeseeView(View):
    # def post(self, request, order_id):
    #     # Récupérer l'instance OrderProduction
    #     print("----|||---")
    #     order = get_object_or_404(OrderProduction, id=order_id)

    #     # Mettre à jour la location à 'stock_mp'
    #     order.location = 'mp_pesee'
    #     order.status = 'waiting'
    #     order.save()

    #     # Retourner une réponse JSON indiquant que la mise à jour a réussi
    #     return JsonResponse({"message": "Location mise à jour à pesee", "new_location": order.location})



    def post(self, request, order_id):
        # Récupérer l'instance OrderProduction
        order = get_object_or_404(OrderProduction, id=order_id)

        # Charger les données POST sous forme de JSON
        data = json.loads(request.body)
        print(str(data))

        # Mettre à jour la location à 'pesee'
        order.status = 'in_process'
        order.returned_from_weight = True
        order.save()

        # Parcourir les transferts pour mettre à jour qtt_from_stock_to_weight
        transfer_data = data.get('transfer_data', [])
        for transfer in transfer_data:
            item_name = transfer.get('item')  # Nom de l'article
            item_id = transfer.get('item_id')  # Nom de l'article
            quantity_transferred = transfer.get('quantity_transferred')  # Quantité transférée

            # Vérifier si l'ItemOrderProduction pour cet article existe
            item_order = ItemOrderProduction.objects.filter(
                id=item_id
            ).first()

            print("----------")
            print("----------")
            print("----------")
            print(str(item_order))

            if item_order:
                # Mettre à jour la quantité dans qtt_from_stock_to_weight
                item_order.qtt_from_weight_to_stock = quantity_transferred
                item_order.save()
                print(f"Updated {item_name} with quantity: {quantity_transferred} in qtt_from_stock_to_weight.")
            else:
                print(f"Item {item_name} not found in OrderProduction {order_id}.")

        # Retourner une réponse JSON indiquant que la mise à jour a réussi
        return JsonResponse({
            "message": "Location mise à jour à pesee et quantités transférées mises à jour.",
            "new_location": order.location
        })







from django.shortcuts import get_object_or_404, redirect
from django.views import View
from .models import ItemOrderProduction, ItemOrderProductionTransfered

import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import ItemOrderProduction, ItemOrderProductionTransfered

class TransfertProductionOrderProductionMpPeseeView(View):
    def post(self, request, item_id):

        # Récupérer l'instance de ItemOrderProduction
        item_order_production = get_object_or_404(ItemOrderProduction, id=item_id)

        # Désérialiser les données JSON envoyées dans la requête
        try:
            data = json.loads(request.body)
            qtt = data.get('qtt')  # Récupérer la quantité depuis les données
            item_id = data.get('itemId')  # Optionnel, si tu veux utiliser itemId
        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON format"}, status=400)

        # Mettre à jour le champ 'location' de l'instance ItemOrderProduction
        item_order_production.location = 'in_process_tablet'  # Changer le nom de location selon tes besoins
        item_order_production.save() 

        # Créer une nouvelle instance de ItemOrderProductionTransfered
        new_transfer = ItemOrderProductionTransfered.objects.create(
            item=item_order_production,
            user=request.user,
            qtt=qtt,
            location = "in_process_tablet",
            # location='Tablette'  # Spécifie le champ 'location' avec 'Tablette'
        )

        # Répondre avec une réponse JSON pour indiquer que la mise à jour est effectuée
        return JsonResponse({
            "message": "Location mise à jour à Tablette", 
            "new_location": new_transfer.location
        })



from django.http import JsonResponse
from django.views import View
from django.shortcuts import get_object_or_404
import json
from .models import OrderProduction, ItemOrderProduction

class TransfertPeseeOrderProductionView(View):
    def post(self, request, order_id):
        # Récupérer l'instance OrderProduction
        order = get_object_or_404(OrderProduction, id=order_id)

        # Charger les données POST sous forme de JSON
        data = json.loads(request.body)
        print(str(data))

        # Mettre à jour la location à 'pesee'
        order.location = 'pesee'
        order.transfered_from_stock = True
        order.save()

        # Parcourir les transferts pour mettre à jour qtt_from_stock_to_weight
        transfer_data = data.get('transfer_data', [])
        for transfer in transfer_data:
            item_name = transfer.get('item')  # Nom de l'article
            item_id = transfer.get('item_id')  # Nom de l'article
            quantity_transferred = transfer.get('quantity_transferred')  # Quantité transférée

            # Vérifier si l'ItemOrderProduction pour cet article existe
            item_order = ItemOrderProduction.objects.filter(
                id=item_id
            ).first()

            print("----------")
            print("----------")
            print("----------")
            print(str(item_order))

            if item_order:
                # Mettre à jour la quantité dans qtt_from_stock_to_weight
                item_order.qtt_from_stock_to_weight = quantity_transferred
                item_order.qtt_from_weight_to_stock = 0
                item_order.save()
                print(f"Updated {item_name} with quantity: {quantity_transferred} in qtt_from_stock_to_weight.")
            else:
                print(f"Item {item_name} not found in OrderProduction {order_id}.")

        # Retourner une réponse JSON indiquant que la mise à jour a réussi
        return JsonResponse({
            "message": "Location mise à jour à pesee et quantités transférées mises à jour.",
            "new_location": order.location
        })






class ReceptionnerOrderProductionPeseeView(View):
    def post(self, request, order_id):
        # Récupérer l'instance OrderProduction
        order = get_object_or_404(OrderProduction, id=order_id)

        # Mettre à jour la location à 'stock_mp'
        order.location = 'pesee'
        order.status = 'received'
        order.save()

        # Retourner une réponse JSON indiquant que la mise à jour a réussi
        return JsonResponse({"message": "Location mise à jour à stock_mp", "new_location": order.location})


class ReceptionnerOrderProductionMpPeseeView(View):
    def post(self, request, order_id):
        # Récupérer l'instance OrderProduction
        order = get_object_or_404(OrderProduction, id=order_id)

        # Mettre à jour la location à 'stock_mp'
        order.location = 'mp_pesee'
        order.status = 'received'
        order.save()

        # Retourner une réponse JSON indiquant que la mise à jour a réussi
        return JsonResponse({"message": "Location mise à jour à mp pesee", "new_location": order.location})


class ItemOrderProductionListPeseeCreateView(APIView):

    # Liste des articles de commande de production
    def get(self, request):
        pk = request.GET.get("id")  # Get the 'id' from request
        if not pk:
            return JsonResponse({"error": "No id provided"}, status=400)

        print("id = "+str(pk))

        try:
            # Filter the items based on the provided 'id'
            items = ItemOrderProduction.objects.filter(order_production=pk)
            print("items = "+str(items))
            data = [
                {
                    "id": item.id,
                    "order_production": item.order_production.id,
                    "order_production_code": item.order_production.code,
                    "item": item.item,
                    "unite": item.unite,
                    "produit": item.order_production.produit.nom,
                    "qtt": item.qtt,
                    "qtt_from_stock_to_weight": item.qtt_from_stock_to_weight
                }
                for item in items
            ]
            return JsonResponse(data, safe=False)
        except ItemOrderProduction.DoesNotExist:
            return JsonResponse({"error": "Order production not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

     

class ReceptionnerOrderProductionTabletteView(View):
    def post(self, request, order_id):
        # Récupérer l'instance OrderProduction
        order = get_object_or_404(OrderProduction, id=order_id)

        # Mettre à jour la location à 'stock_mp'
        order.status = 'received'
        order.save()

        # Retourner une réponse JSON indiquant que la mise à jour a réussi
        return JsonResponse({"message": "Location mise à jour à stock_mp", "new_location": order.location})





from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from .models import OrderProduction, ItemOrderProduction, Produit, Entree
from django.contrib.auth.models import User
import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import OrderProduction, Produit, Entree, ItemOrderProduction
from datetime import datetime

def generate_order_code():
    # Récupérer l'année actuelle
    current_year = datetime.now().strftime('%y')

    # Récupérer le dernier order de production créé
    last_order = OrderProduction.objects.all().order_by('id').last()

    if last_order:
        # Extraire le numéro séquentiel de l'instance précédente
        last_code = last_order.code
        # Le format est OF-xxxx-yy, on extrait la partie xxxx
        last_seq_number = int(last_code.split('-')[1])
        new_seq_number = last_seq_number + 1
    else:
        # Si aucun order existant, commencer à 1
        new_seq_number = 1

    # Formatage avec padding pour obtenir un numéro séquentiel sur 4 chiffres
    new_code = f"OF-{new_seq_number:04d}-{current_year}"
    return new_code

@csrf_exempt  # Permet d'exempter la vue de la vérification CSRF, utile pour les tests locaux ou API
def create_order_production(request):
    if request.method == 'POST':
        try:
            # Charger les données POST sous forme de JSON
            data = json.loads(request.body)
            print(str(data))
            print("1")

            # Récupérer les informations principales pour OrderProduction
            produit_id = data.get('produit')  # L'ID du produit envoyé par le frontend
            batch_number = data.get('batchNo')  # Le numéro du lot
            quantite = data.get('quantite')  # La quantité demandée
            process_type = 'premix'  # Exemple: Défini à full_process, peut être modifié via postdata

            # Récupérer l'utilisateur et le produit
            user = request.user
            produit = Produit.objects.get(nom=produit_id)
            print("2")

            code = generate_order_code()

            # Créer l'instance OrderProduction
            order = OrderProduction.objects.create(
                user=user,
                code=code,
                produit=produit,
                batch_number=batch_number,
                process_type=process_type
            )
            print("3")

            # Parcourir les items pour créer les ItemOrderProduction associés
            items = data.get('items', [])  # Récupérer les items du postData
            print("4")
            print(str(items))

            for item_data in items:
                item_name = item_data.get('produit')
                requested_quantity = item_data.get('requested_quantity')  # La quantité demandée par l'utilisateur
                item_e_type = item_data.get('e_type')
                item_sub_type = item_data.get('sub_type')

                print("5")

                # Récupérer les entrées (Entree) correspondantes
                entree = Entree.objects.filter(
                    produit__nom=item_name,
                    e_type=item_e_type,
                    subtype=item_sub_type
                ).order_by('added').first()  # Récupérer les entrées par date croissante
                print("6")

                # Extraire la quantité numérique et l'unité
                try:
                    # Extraire la valeur numérique et l'unité
                    quantity_str = requested_quantity.replace('Kg', '').replace('g', '').strip()
                    qtt = float(quantity_str) if quantity_str else 0

                    # Extraire l'unité (Kg ou g)
                    if 'Kg' in requested_quantity:
                        unit = 'kg'
                    elif 'g' in requested_quantity:
                        unit = 'g'
                    elif 'mg' in requested_quantity:
                        unit = 'mg'
                    elif 'l' in requested_quantity:
                        unit = 'l'
                    elif 'ml' in requested_quantity:
                        unit = 'ml'
                    elif 'pcs' in requested_quantity:
                        unit = 'pcs'
                    elif 'box' in requested_quantity:
                        unit = 'box'
                    else:
                        unit = 'g'  # Par défaut, l'unité est 'g'
                    
                    # Afficher la quantité et l'unité extraites
                    print(f"Requested quantity: {qtt} {unit}")

                except ValueError:
                    qtt = 0  # Si la conversion échoue, mettre la quantité à 0
                    unit = 'g'  # L'unité par défaut est 'g'

                # Créer une instance de ItemOrderProduction associée à l'Entree
                ItemOrderProduction.objects.create(
                    order_production=order,
                    item=item_sub_type,
                    qtt=qtt,  # Utiliser la quantité convertie ici
                    entree=entree,  # Passer l'instance d'Entree ici
                    unite=unit  # Définir l'unité ici
                )

                print("success")
            return JsonResponse({
                'message': 'OrderProduction and ItemOrderProduction created successfully!',
                'order_id': order.id
            }, status=201)

        except Exception as e:
            # Retourner une erreur en cas de problème
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)



# from django.db.models import Sum

from django.db.models import Sum
# from django.db.models.functions import TruncDate

from django.db.models import F
# from django.db.models import Cast, IntegerField

# from django.http import JsonResponse
# from datetime import datetime

class OrderProductionMPPeseeDetailView(APIView):

    def get(self, request):
        print("^^^^^^")
        locations = ["pesee", "Tablette", "mp_pesee"]
        orders = OrderProduction.objects.filter(location__in=locations)

        # Construction de la réponse incluant les items
        data = []
        for order in orders:
            # Récupération des items liés à la commande
            items = ItemOrderProduction.objects.filter(order_production=order)

            item_data = []
            for item in items:
                # Récupérer les ItemOrderProductionTransfered associés à l'item
                transferred_items = ItemOrderProductionTransfered.objects.filter(item=item)
                
                # Somme des quantités pour chaque item transféré
                total_qtt_transferred = transferred_items.aggregate(Sum('qtt'))['qtt__sum'] or 0

                # Récapitulatif des actions de transfert par date et user pour chaque item
                transfer_summary = transferred_items.annotate(
                    date_and_time=F('added')  # Keep datetime as is
                ).values('date_and_time', 'user__username').annotate(
                    total_qtt_transferred_by_user=Sum('qtt') # Cast the sum to an integer
                ).order_by('date_and_time', 'user__username')

                # Format the date_and_time manually
                for transfer in transfer_summary:
                    transfer['date_and_time'] = transfer['date_and_time'].strftime('%Y/%m/%d at %H:%M:%S')

                item_data.append({
                    "id": item.id,
                    "item": item.item,
                    "qtt": item.qtt,
                    "location": item.location,
                    "qtt_from_stock_to_weight": item.qtt_from_stock_to_weight,
                    "qtt_from_weight_to_stock": item.qtt_from_weight_to_stock,
                    "total_qtt_transferred": total_qtt_transferred,  # Somme des quantités transférées
                    "transfer_summary": list(transfer_summary)  # Récapitulatif des actions de transfert pour cet item
                })

            # Ajouter les détails de la commande et ses items à la réponse
            data.append({
                "id": order.id,
                "batch_number": order.batch_number,
                "process_type": order.process_type,
                "added": order.added,
                "user": order.user.username,
                "produit": order.produit.nom,
                "location": order.location,
                "status": order.status,
                "items": item_data  # Ajout des items associés
            })

        return JsonResponse(data, safe=False)


    # Création d'une commande de production
    @method_decorator(csrf_exempt)  # Désactive CSRF pour faciliter les tests
    def post(self, request):
        try:
            data = json.loads(request.body)
            user = data.get('user')
            produit = data.get('produit')
            batch_number = data.get('batch_number')
            process_type = data.get('process_type')

            order = OrderProduction.objects.create(
                user_id=user,
                produit_id=produit,
                batch_number=batch_number,
                process_type=process_type
            )
            return JsonResponse({"id": order.id}, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)




from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import ItemOrderProduction, ItemOrderProductionBash

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import json
from .models import ItemOrderProductionBash, ItemOrderProduction, OrderProduction

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import json
from .models import ItemOrderProductionBash, ItemOrderProduction, OrderProduction

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import json
from .models import ItemOrderProduction, OrderProduction, ItemOrderProductionBash

import re
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import json
from .models import ItemOrderProduction, OrderProduction, ItemOrderProductionBash

def create_item_order_production_bash(request):
    if request.method == 'POST':
        try:
            # Récupérer les données envoyées dans la requête POST
            data = json.loads(request.body)
            print(f"Received data: {data}")  # Affiche les données reçues

            # Vérifier que les données contiennent des items
            if "items" not in data or not isinstance(data["items"], list):
                return JsonResponse({"error": "Invalid data format, 'items' list is required"}, status=400)

            # Parcourir les items envoyés dans la requête
            for item_data in data["items"]:
                try:
                    # Extraire les données de l'item
                    item_id = item_data.get("item_id")  # Récupérer l'ID de l'ItemOrderProduction
                    raw_quantity = item_data.get("quantity", "")  # Quantité brute envoyée
                    ref = item_data.get("group")  # Référence Bash Groupe envoyée

                    # Vérifier que les champs requis sont présents
                    if not all([item_id, raw_quantity, ref]):
                        print(f"Skipping item with missing fields: {item_data}")
                        continue

                    # Supprimer les unités et conserver uniquement la valeur numérique
                    quantity = re.sub(r"[^\d.]", "", raw_quantity)  # Garde uniquement chiffres et points
                    if not quantity:
                        raise ValueError(f"Invalid quantity: {raw_quantity}")

                    print(f"Processing item: item_id={item_id}, quantity={quantity}, ref={ref}")  # Affiche les informations de l'item

                    # Récupérer l'instance de ItemOrderProduction en fonction de l'ID
                    item_order_production = get_object_or_404(ItemOrderProduction, id=item_id)
                    print(f"Found ItemOrderProduction: {item_order_production}")  # Affiche l'instance trouvée

                    id_op = item_order_production.order_production.id
                    print(f"OrderProduction ID: {id_op}")  # Affiche l'ID de l'OrderProduction associé

                    # Récupérer l'instance de OrderProduction en fonction de l'ID
                    order_production = get_object_or_404(OrderProduction, id=id_op)
                    print(f"Found OrderProduction: {order_production}")  # Affiche l'instance d'OrderProduction

                    # Créer une nouvelle instance de ItemOrderProductionBash
                    item_bash = ItemOrderProductionBash(
                        item_order_production=item_order_production,  # Associer à l'instance ItemOrderProduction
                        qtt=quantity,  # Quantité nettoyée (sans unités)
                        location='mp_pesee',  # Par défaut, changer si nécessaire
                        ref=ref,  # Référence Bash Groupe
                    )

                    # Sauvegarder l'instance de ItemOrderProductionBash
                    item_bash.save()
                    print(f"Saved ItemOrderProductionBash: {item_bash}")  # Affiche l'instance sauvegardée

                except Exception as item_error:
                    print(f"Error processing item {item_data}: {str(item_error)}")

            # Mettre à jour la location de l'OrderProduction
            order_production.location = "mp_pesee"
            order_production.status = "waiting"
            order_production.save()
            print(f"Updated OrderProduction location: {order_production.location}")  # Affiche la nouvelle location

            return JsonResponse({"message": "Items Bash créés avec succès et OrderProduction mis à jour!"}, status=200)

        except Exception as e:
            print(f"Error: {str(e)}")  # Affiche l'erreur
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Method not allowed"}, status=405)



from django.shortcuts import render
from django.http import JsonResponse
from .models import ItemOrderProductionBash

from django.http import JsonResponse
from .models import ItemOrderProductionBash

def get_bash_items(request):
    """
    Vue pour récupérer les items bash groupés par leur référence (ref).
    """

    print("### DEBUG : Début de la vue get_bash_items ###")

    try:
        # Récupérer tous les items bash depuis la base de données
        bash_items = ItemOrderProductionBash.objects.filter(location="mp_pesee")
        print(f"Nombre total d'items bash trouvés : {bash_items.count()}")
        print(str(bash_items))

        # Grouper les items par leur ref
        grouped_items = {}
        for item in bash_items:
            print(f"Traitement de l'item : {item}")
            print(f"Item ID: {item.item_order_production.id}, Ref: {item.ref}, Quantité: {item.qtt}, Location: {item.location}")
            
            if item.ref not in grouped_items:
                grouped_items[item.ref] = []
                print(f"Nouvelle référence trouvée : {item.ref}")

            grouped_items[item.ref].append({
                "item_id": item.item_order_production.id,
                "item_name": item.item_order_production.item,  # Supposez que l'objet a un champ 'name'
                "quantity": item.qtt,
                "location": item.location,
            })
            print(f"Item ajouté sous le groupe : {item.ref}")

        print("### DEBUG : Résultat final des groupes ###")
        print(grouped_items)

        # Retourner les données sous format JSON
        return JsonResponse({"groups": grouped_items}, status=200)

    except Exception as e:
        print(f"### ERROR : Une erreur est survenue ###")
        print(f"Erreur : {str(e)}")
        return JsonResponse({"error": str(e)}, status=400)



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
from .models import ItemOrderProductionBash

@csrf_exempt
def send__bash_group(request):
    if request.method == "POST":
        try:
            # Charger le payload JSON
            data = json.loads(request.body)
            group_ref = data.get("ref")
            items = data.get("items", [])

            if not group_ref:
                return JsonResponse({"error": "Référence du groupe manquante."}, status=400)

            # Filtrer les items bash correspondants par référence
            bash_items = ItemOrderProductionBash.objects.filter(ref=group_ref)

            if not bash_items.exists():
                return JsonResponse({"error": "Aucun item trouvé pour la référence spécifiée."}, status=404)

            # Mettre à jour la localisation de ces items en "Tablette"
            bash_items.update(location="Tablette")


            return JsonResponse({
                "message": "Les items ont été transférés avec succès.",
            }, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Format JSON invalide."}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Méthode non autorisée."}, status=405)





from rest_framework.response import Response
from rest_framework.views import APIView

class OrderProductionsBashesTablette(APIView):
    def get(self, request):
        bashes = ItemOrderProductionBash.objects.select_related(
            "item_order_production"
        ).filter(location="Tablette")

        grouped_data = {}
        for bash in bashes:
            ref = bash.ref
            item_order_production = bash.item_order_production

            if ref not in grouped_data:
                grouped_data[ref] = {
                    "ref": ref,
                    "location": bash.location,
                    "items": [],
                }

            grouped_data[ref]["items"].append({
                "bash_id": bash.id,
                "qtt": bash.qtt,
                "location": bash.location,
                "added": bash.added,
                "item_order_production": {
                    "id": item_order_production.id,
                    "item": item_order_production.item,
                    "unite": item_order_production.unite,
                    "qtt": item_order_production.qtt,
                    "location": item_order_production.location,
                },
            })

        return Response(list(grouped_data.values()), status=200)
