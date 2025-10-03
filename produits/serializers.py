from rest_framework import serializers
from .models import *


class ProduitKnowledgeSerializer(serializers.ModelSerializer):
    files=serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        return  f"https://app.liliumpharma.com{obj.image.url if obj.image else '/media/box.png'}" 

    def get_files(self,obj):
        return [ {"file": "https://app.liliumpharma.com"+f.fil.url, "type":f.file_type, "name":f.name, }  for f in obj.productfile_set.all()]


    class Meta:
        model = Produit
        fields ='__all__'


# class ProductActiveIngredientsSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ProductActiveIngredients
#         fields = ['ingredient', 'unit', 'quantity', 'convert', 'quantity_mg']

# class ProductInactiveIngredientsSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ProductInactiveIngredients
#         fields = ['ingredient', 'unit', 'quantity', 'e_num']

# class ProductProductionInfosSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ProductProductionInfos
#         fields = ['tablet_weight', 'tablet_per_blister', 'blister_per_box']
