from rest_framework import serializers
from . models import *
from produits.api.serializers import ProduitSerializer 




class OrderSerializer(serializers.ModelSerializer):

    items=serializers.SerializerMethodField()
    pharm=serializers.SerializerMethodField()
    grs=serializers.SerializerMethodField()
    sgros=serializers.SerializerMethodField()
    username=serializers.SerializerMethodField()
    username_transfert=serializers.SerializerMethodField()
    cause=serializers.SerializerMethodField()

    def get_items(self,obj):
        return OrderItemSerializer(OrderItem.objects.filter(order=obj),many=True).data

    def get_pharm(self,obj):
        return {"id":obj.pharmacy.id,"nom":obj.pharmacy.nom} if obj.pharmacy else {"id":0,"nom":""} 

    def get_grs(self,obj):
        return {"id":obj.gros.id,"nom":obj.gros.nom}  if obj.gros else {"id":0,"nom":""}

    def get_sgros(self,obj):
        return {"id":obj.super_gros.id,"nom":obj.super_gros.name} if obj.super_gros else {"id":0,"nom":""}

    def get_username(self,obj):
        return obj.user.username 
    
    def get_cause(self,obj):
        return obj.cause 

    def get_username_transfert(self,obj):
        return obj.touser.username if obj.touser else "" 

    class Meta:
        model = Order
        fields ='__all__'



class OrderItemSerializer(serializers.ModelSerializer):
    product=serializers.SerializerMethodField()
    

    def get_product(self,obj):
        return {"nom":obj.produit.nom}        
    class Meta:
        model = OrderItem
        fields ='__all__'






class ExitOrderSerializer(serializers.ModelSerializer):

    items=serializers.SerializerMethodField()
    username=serializers.SerializerMethodField()
 

    def get_items(self,obj):
        return ExitOrderItemSerializer(ExitOrderItem.objects.filter(order=obj),many=True).data

    def get_username(self,obj):
        return obj.user.username    



    class Meta:
        model = ExitOrder
        fields ='__all__'



class ExitOrderItemSerializer(serializers.ModelSerializer):
    product=serializers.SerializerMethodField()

    def get_product(self,obj):
        return {"nom":obj.produit.nom}        
    class Meta:
        model = ExitOrderItem
        fields ='__all__'


