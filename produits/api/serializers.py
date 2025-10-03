from rest_framework import serializers
from produits.models import Produit,ProduitVisite


class ProduitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produit
        fields ='__all__'

class ProduitVisiteSerializer(serializers.ModelSerializer):
    product=serializers.SerializerMethodField()

    def get_product(self,obj):
        return ProduitSerializer(obj.produit).data
        
    class Meta:
        model = ProduitVisite
        fields ='__all__'