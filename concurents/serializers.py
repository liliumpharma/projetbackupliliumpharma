from rest_framework import serializers
from rest_framework.exceptions import ValidationError
import json

from .models import *


class ListSerializer(serializers.ModelSerializer):
    components=serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        return f"https://app.liliumpharma.com{obj.image.url if obj.image else '/media/box.png'}" 

    def get_components(self,obj):
        return  [{"id":c.id, "name":c.name, "qtt":c.qtt } for c in obj.composition_set.all()]

    class Meta:
        model=CProduct
        fields="__all__"



class CProductSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        print("CProduct Created")
        request=self.context["request"]
        # instance=super().create(validated_data)
        validated_data["user"] = request.user  # Add request.user to the user attribute
        instance = super().create(validated_data)
        # print("*****************",[ c for c in  json.loads(request.data["components"])] )
        instance.composition_set.all().delete()
        serializer=ComponentsSerializer(data= [ {**c,"product":instance.id} for c in json.loads(request.data["components"]) ] , many=True)
        if serializer.is_valid():
            serializer.save()
        else:
            instance.delete()    
        return instance


    class Meta:
        model=CProduct
        fields = '__all__'
        # exclude= ["user",]



class ComponentsSerializer(serializers.ModelSerializer):
    class Meta:
        model=Composition
        fields="__all__"