from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from .serializers import ProduitKnowledgeSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import (
    SessionAuthentication,
    BasicAuthentication,
    TokenAuthentication,
)
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated

from django.views.generic import TemplateView
from django.contrib.auth.models import User
from .models import *
from accounts.models import *

from clients.functions import (
    get_order_source_details,
    get_target_per_user,
    get_target_details_per_user,
    get_target_all_users,
    get_target_for_supervisor,
)
from clients.views import target_report

class Prolist(TemplateView):
    def get(self, request):
        target_report(request)
        prls = UserProduct.objects.filter(user=request.user)
        return render(request, 'produits/prolist.html', {"prls":prls})

class ProductsKnowledgeList(generics.ListAPIView):
    serializer_class = ProduitKnowledgeSerializer
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def get_queryset(self):
        print(self.request.user)
        # user = self.request.user
        # print(f"User: {user}")  # Print the user accessing the view
        # username = user_profile.user.username
        # print(f"User family: {username}")

        # user = User.objects.filter(id=1).first()
        # user = self.request.user
        # user_profile = user.userprofile
        # user_family = user_profile.company
        # if user_family == "all":
        #     produits = Produit.objects.filter(pays=user_profile.commune.wilaya.pays)
        # else:
        #     produits = Produit.objects.filter(
        #         pays=user_profile.commune.wilaya.pays,
        #         productcompany__family=user_family,
        #     )
                    
                    
        produits = Produit.objects.all()


        return produits


@api_view(["GET"])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def QualiquantityInformations(request):
    id = request.GET.get("id")
    print("heree okay")
    prod = Produit.objects.get(id=id)
    response = []

    response_info = []
    response_active = []
    response_inactive = []

    product_informations = get_object_or_404(ProductInformations, product=prod)
    response_info.append(
        {
            "product_name": product_informations.product_name,
            "code_ref": product_informations.code_reference,
            "galenic_form": product_informations.galenic_form,
            "classification": product_informations.product_classification,
            "presentation": product_informations.presentation,
            "weight": product_informations.weight,
            "serving_size": product_informations.serving_size,
            "with_inactive": product_informations.with_inactive_ingredient,
            # ---------
            "product_identifier": product_informations.product_identifier,
            "suggested_use": product_informations.suggested_use,
            "dosage_form": product_informations.dosage_form,
            "description": product_informations.description,
            "tablet_size": product_informations.Tablet_size,
            "tablet_weight": product_informations.Tablet_weight,
            "producer": product_informations.producer,
        }
    )
    product_active_ing = ProductActiveIngerients.objects.filter(produit=prod)
    if product_active_ing.exists():
        for ing in product_active_ing:
            response_active.append(
                {
                    "ingredient": ing.ingredient,
                    "qtt": ing.quantity,
                    "unit": ing.unit,
                }
            )
    product_inactive_ing = ProductInactiveIngredients.objects.filter(produit=prod)
    if product_inactive_ing.exists():
        for ing in product_inactive_ing:
            response_inactive.append(
                {
                    "ingredient": ing.ingredient,
                    "qtt": ing.quantity,
                    "unit": ing.unit,
                }
            )
    response.append(response_info)
    response.append(response_active)
    response.append(response_inactive)
    print(str(response))
    return Response(response)


# VIEW FOR PRINT BUTTON ADMINISTRATION
class QualiquantityPDF(APIView):
    authentication_classes = (
        TokenAuthentication,
        SessionAuthentication,
    )
    permission_classes = (IsAuthenticated,)

    def get(self, request, id):
        product = Produit.objects.get(id=id)
        return render(request, "produits/qualiquantity.html", {"product": product})


class DataSheet(APIView):
    authentication_classes = (
        TokenAuthentication,
        SessionAuthentication,
    )
    permission_classes = (IsAuthenticated,)

    def get(self, request, id):
        product = Produit.objects.get(id=id)
        return render(request, "produits/data_sheet.html", {"product": product})


class ProductData(APIView):
    authentication_classes = (
        TokenAuthentication,
        SessionAuthentication,
    )
    permission_classes = (IsAuthenticated,)

    def get(self, request, id):
        product = Produit.objects.get(id=id)
        return render(request, "produits/fiche_technique.html", {"product": product})

    # VISITE PAR PRODUIT IN TEST


from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count
from datetime import datetime
from .models import ProduitVisite


class VisiteProduitAPIView(APIView):
    def get(self, request):
        # Récupérer la date actuelle
        current_date = datetime.now()

        # Filtrer les visites de produits pour l'année courante jusqu'au mois actuel
        # visites_produit = ProduitVisite.objects.filter(
        #     (
        #         Q(visite__rapport__added__year=current_date.year - 1) &
        #         Q(visite__rapport__added__month__gte=1)
        #     ) | (
        #         Q(visite__rapport__added__year=current_date.year) &
        #         Q(visite__rapport__added__month__lte=current_date.month)
        #     )
        # )
        visites_produit = ProduitVisite.objects.filter(
            (
                Q(visite__rapport__added__year=current_date.year - 1)
                & Q(visite__rapport__added__month__gte=1)
            )
            | (
                Q(visite__rapport__added__year=current_date.year)
                & Q(visite__rapport__added__month__lte=current_date.month)
            )
        )

        # Filtrer par utilisateur si spécifié dans la requête GET
        # user_id = request.GET.get("user")
        user = request.user
        if user.userprofile.rolee in ["Commercial", "Superviseur"]:
            visites_produit = visites_produit.filter(visite__rapport__user_id=user)
        else:
            if user.userprofile.rolee in ["CountryManager"] or user.is_superuser:
                visites_produit = visites_produit.all()

        product_name = request.GET.get("product")

        if product_name:
            product = Produit.objects.filter(nom=product_name).first()
            visites_produit = visites_produit.filter(produit=product)

        # Calculer le nombre d'occurrences de chaque produit distinct
        visites_agregate = visites_produit.values(
            "visite__rapport__added__year",
            "visite__rapport__added__month",
            "produit__nom",  # Ajout du nom du produit
        ).annotate(
            count=Count(
                "id"
            )  # Compte le nombre d'occurrences de chaque produit distinct
        )

        # Construire la réponse JSON
        data = []
        for visite in visites_agregate:
            data.append(
                {
                    "year": visite["visite__rapport__added__year"],
                    "month": visite["visite__rapport__added__month"],
                    "product": visite["produit__nom"],  # Nom du produit
                    "count": visite["count"],  # Nombre d'occurrences de chaque produit
                }
            )

        return Response(data)


class visitesProduitFront(APIView):
    authentication_classes = (
        TokenAuthentication,
        SessionAuthentication,
    )
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        # return render(request, 'produits/visite_produit.html')
        return render(request, "produits/test_scanner.html")




# -------PRODUCTION-------

# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from .models import Produit, ProductActiveIngredients, ProductInactiveIngredients, ProductProductionInfos
# from .serializers import ProductActiveIngredientsSerializer, ProductInactiveIngredientsSerializer, ProductProductionInfosSerializer

# class ProductDetailView(APIView):
    
#     def get(self, request, produit_id):
#         try:
#             produit = Produit.objects.get(id=produit_id)

#             # Récupérer les informations des ingrédients actifs
#             active_ingredients = ProductActiveIngredients.objects.filter(produit=produit)
#             active_ingredients_serializer = ProductActiveIngredientsSerializer(active_ingredients, many=True)
            
#             # Récupérer les informations des ingrédients inactifs
#             inactive_ingredients = ProductInactiveIngredients.objects.filter(produit=produit)
#             inactive_ingredients_serializer = ProductInactiveIngredientsSerializer(inactive_ingredients, many=True)
            
#             # Récupérer les informations de production
#             production_infos = ProductProductionInfos.objects.filter(produit=produit).first()
#             production_infos_serializer = ProductProductionInfosSerializer(production_infos)
            
#             # Construire la réponse
#             data = {
#                 'product_id': produit_id,
#                 'active_ingredients': active_ingredients_serializer.data,
#                 'inactive_ingredients': inactive_ingredients_serializer.data,
#                 'production_info': production_infos_serializer.data if production_infos else None
#             }
#             return Response(data, status=status.HTTP_200_OK)

#         except Produit.DoesNotExist:
#             return Response({"error": "Produit non trouvé"}, status=status.HTTP_404_NOT_FOUND)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
# from .models import ProductActiveIngredients

class ProductDetailView(APIView):
    
    def get(self, request):
        try:
            print("$$$$$$$$$$$$$$$$$$")
            product_name = request.GET.get("produit")
            produit = Produit.objects.get(nom=product_name)
            produit_infos = ProductInformations.objects.get(product__nom=product_name)
            produit_prod_infos = ProductProductionInfos.objects.get(produit__nom=product_name)

            produit_data = {
                "id": produit.id,
                "nom": produit.nom,
                "galenic_form": produit_infos.galenic_form,
                "Tablet_weight": produit_infos.Tablet_weight,
                "serving_size": produit_infos.serving_size,
                "dosage_form": produit_infos.dosage_form,
                "packaging_form": produit_prod_infos.packaging_form,
                "Presentation": produit_infos.presentation,
            }


            # Récupérer les informations des ingrédients actifs
            active_ingredients = ProductActiveIngerients.objects.filter(produit__nom=produit)
            active_ingredients_data = [
                {
                    "ingredient": ingredient.ingredient,
                    "unit": ingredient.unit,
                    "quantity": ingredient.quantity,
                    "convert": ingredient.convert,
                    "quantity_mg": ingredient.quantity_mg
                }
                for ingredient in active_ingredients
            ]
            
            # Récupérer les informations des ingrédients inactifs
            inactive_ingredients = ProductInactiveIngredients.objects.filter(produit__nom=produit,coating_material = False)
            inactive_ingredients_data = [
                {
                    "ingredient": ingredient.ingredient,
                    "quantity_mg": ingredient.quantity,
                    "unit": ingredient.unit,
                    "quantity": ingredient.quantity,
                    "e_num": ingredient.e_num
                }
                for ingredient in inactive_ingredients
            ]

                        # Récupérer les informations des ingrédients inactifs
            coating_ingredients = ProductInactiveIngredients.objects.filter(produit__nom=produit,coating_material = True)
            coating_ingredients_data = [
                {
                    "ingredient": ingredient.ingredient,
                    "unit": ingredient.unit,
                    "quantity_mg": ingredient.quantity,
                    "e_num": ingredient.e_num
                }
                for ingredient in coating_ingredients
            ]
            
            # Récupérer les informations de production
            production_infos = ProductProductionInfos.objects.filter(produit=produit).first()
            production_info_data = {
                "tablet_weight": production_infos.tablet_weight,
                "tablet_per_blister": production_infos.tablet_per_blister,
                "blister_per_box": production_infos.blister_per_box
            } if production_infos else None
            
            # Construire la réponse
            data = {
                'produit': produit_data,  # Include the serialized produit data
                'active_ingredients': active_ingredients_data,
                'inactive_ingredients': inactive_ingredients_data,
                'coating_ingredients': coating_ingredients_data,
                'production_info': production_info_data
            }

            return Response(data, status=status.HTTP_200_OK)

        except Produit.DoesNotExist:
            return Response({"error": "Produit non trouvé"}, status=status.HTTP_404_NOT_FOUND)

