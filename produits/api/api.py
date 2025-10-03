from produits.models import *
from datetime import date
from .serializers import ProduitSerializer
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from medecins.models import Medecin
from accounts.models import *
from clients.models import *


class ProduitApi(APIView):
    def get(self,request,format=None):
        produits=Produit.objects.all()
        # if not  request.user.is_superuser:
        produits=produits.filter(productcompany__family="lilium pharma")

        serializer=ProduitSerializer(produits,many=True)
        return Response(serializer.data, status=200)


# class ProduitAppApi(APIView):

#     authentication_classes = [TokenAuthentication]
#     permission_classes = [IsAuthenticated]

#     def get(self, request, format=None):
#         current_month = datetime.now().month - 1

#         # Filtrer les produits par pays
#         produits = Produit.objects.filter(pays=request.user.userprofile.commune.wilaya.pays)

#         # Filtrer les produits par famille de la société associée à l'utilisateur
#         user_company_family = request.user.userprofile.productcompany.family
#         produits = produits.filter(productcompany__family=user_company_family)

#         # Conditions supplémentaires en fonction du rôle de l'utilisateur
#         if request.user.userprofile.speciality_rolee in ["Commercial"] or request.user.is_superuser or request.user.userprofile.speciality_rolee in ["Office"]:
#             produits = Produit.objects.filter(pays=request.user.userprofile.commune.wilaya.pays)


#         # Utiliser le sérialiseur pour convertir les objets en JSON
#         serializer = ProduitSerializer(produits, many=True)

#         return Response(serializer.data, status=status.HTTP_200_OK)

class ProduitAppApi(APIView):

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self,request,format=None):
        print(str(request.user.userprofile.company))
        request.session['user_id'] = request.user.id
        print("USER_ID est met dabs session sur pruduit/aoi/app/")
        # produits=Produit.objects.filter(pays=request.user.userprofile.commune.wilaya.pays)
        user_family = request.user.userprofile.company
        produits=Produit.objects.all()
        # if(user_family == "lilium_Pharma"):
        # else:
        #     produits = Produit.objects.filter(pays=request.user.userprofile.commune.wilaya.pays,productcompany__family=user_family)
        print(str(produits))
        serializer = ProduitSerializer(produits, many=True)
        return Response(serializer.data, status=200)



class GetProduitAppApi(APIView):
    authentication_classes = (TokenAuthentication, SessionAuthentication,)
    permission_classes = (IsAuthenticated, )

    def get(self,request,format=None):
        print(str(request.user.userprofile.company))
        produits=Produit.objects.all()
        serializer=ProduitSerializer(produits,many=True)
        return Response(serializer.data, status=200)

class GetUserProducts(APIView):
    authentication_classes = (TokenAuthentication, SessionAuthentication,)
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        # user_products = UserProduct.objects.filter(user=request.user)
        products_data = []
        if request.user.userprofile.speciality_rolee == "Commercial":
            produits = Produit.objects.all()
            for produit in produits :
                product_data = {
                "product_id": produit.id,
                "product_name": produit.nom,
                # "quantity": user_product.quantity,
                }
                products_data.append(product_data)
        else:
            current_month = (date.today().month-1)
            current_year = datetime.now().year
            user = request.user
            previous_month = current_month - 1 if current_month > 1 else 12
            user_target_month = UserTargetMonthProduct.objects.filter(usermonth__user = user, usermonth__date__month=previous_month, usermonth__date__year = current_year)
            target_products = user_target_month.values_list('product__nom', flat=True).distinct()
            # target_products = Produit.objects.all()

            for user_product in target_products:
                produit = Produit.objects.get(nom=user_product)
                product_data = {
                    "product_id": produit.id,
                    "product_name": produit.nom,
                    # "quantity": user_product.quantity,
                }
                products_data.append(product_data)

        return Response(products_data) 


class ProductDetailApi(APIView):
    """
    API optimisée pour récupérer toutes les informations d'un produit par ID
    Exclut les compositions (ingrédients actifs/inactifs) et infos de production
    """
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, product_id):
        try:
            # Récupération optimisée avec select_related et prefetch_related
            produit = Produit.objects.select_related().prefetch_related(
                'pays',
                'productcompany_set',
                'productinformations_set',
                'productnote_set',
                'productfile_set'
            ).get(id=product_id)
            
            # Vérification de l'accès basée sur la famille du produit
            if not request.user.is_superuser:
                if not produit.productcompany_set.filter(family="lilium pharma").exists():
                    return Response(
                        {"error": "Accès non autorisé à ce produit"}, 
                        status=status.HTTP_403_FORBIDDEN
                    )

            # Construction de la réponse optimisée
            response_data = {
                "id": produit.id,
                "nom": produit.nom,
                "fname": produit.fname,
                "price": produit.price,
                "image": produit.image.url if produit.image else None,
                "pdf": produit.pdf.url if produit.pdf else None,
                "pdf_2": produit.pdf_2.url if produit.pdf_2 else None,
                
                # Informations des pays
                "pays": [{"id": pays.id, "nom": pays.nom} for pays in produit.pays.all()],
                
                # Informations de la compagnie
                "company": {
                    "family": produit.productcompany_set.first().family if produit.productcompany_set.exists() else None
                },
                
                # Informations détaillées du produit
                "informations": self._get_product_informations(produit),
                
                # Notes du produit
                "notes": [{"id": note.id, "note": note.note} for note in produit.productnote_set.all()],
                
                # Fichiers du produit
                "files": [
                    {
                        "id": file.id,
                        "name": file.name,
                        "file_type": file.file_type,
                        "file_url": file.fil.url if file.fil else None
                    } for file in produit.productfile_set.all()
                ]
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Produit.DoesNotExist:
            return Response(
                {"error": "Produit non trouvé"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": f"Erreur serveur: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _get_product_informations(self, produit):
        """Méthode helper pour récupérer les informations du produit"""
        try:
            infos = produit.productinformations_set.first()
            if not infos:
                return None
                
            return {
                "with_inactive_ingredient": infos.with_inactive_ingredient,
                "product_name": infos.product_name,
                "price_bba": infos.price_bba,
                "product_identifier": infos.product_identifier,
                "suggested_use": infos.suggested_use,
                "dosage_form": infos.dosage_form,
                "description": infos.description,
                "producer": infos.producer,
                "tablet_size": infos.Tablet_size,
                "tablet_weight": infos.Tablet_weight,
                "code_reference": infos.code_reference,
                "galenic_form": infos.galenic_form,
                "product_classification": infos.product_classification,
                "presentation": infos.presentation,
                "weight": infos.weight,
                "serving_size": infos.serving_size
            }
        except Exception:
            return None