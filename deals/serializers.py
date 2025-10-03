from rest_framework import serializers
from rest_framework.exceptions import ValidationError
import json

from .models import *

class PostSerializer(serializers.ModelSerializer):
    def create_related(self, serializer, data, many=True):
        model_name = self.instance.__class__.__name__.lower()

        print('Model Name >', model_name)

        if many:
            data = [{**{f'{key}': value.id if hasattr(value, '__dict__') else value for key, value in d.items()}, f'{model_name}': self.instance.id} for d in data]

            print('Data >', data)

            serialized = serializer(data=data, many=True)
            if serialized.is_valid():
                serialized.save()
                return
            else:
                errors = serialized.errors
            
        self.instance.delete()
        raise ValidationError(errors)


class DealProductSerializer(serializers.ModelSerializer):
    class Meta:
        model=DealProduct
        exclude=["deal"]


class DealSerializer(serializers.ModelSerializer):
    print("heree serializer called ")
    items = DealProductSerializer(source='dealproduct_set', many=True)
    medecins = serializers.PrimaryKeyRelatedField(queryset=Medecin.objects.all(), many=True)

    class Meta:
        model = Deal
        exclude = ["user", "added", "status"]

    def create(self, validated_data):
        print(validated_data)
        items_data = validated_data.pop('dealproduct_set', None)
        medecins_data = validated_data.pop('medecins', None)  # Change to 'medecins'

        instance = Deal.objects.create(user=self.context.get("user"), status=DealStatus.objects.first(), **validated_data)

        if items_data:
            for item_data in items_data:
                DealProduct.objects.create(deal=instance, **item_data)

        if medecins_data:
            instance.medecin.set(medecins_data)  # Update to use 'medecins'

        return instance  # Return 'instance' instead of 'self.instance'


            
        # if type(items) == list:
        #     print('Is List')
        #     self.create_related(DealProductSerializer, items)

            # items_serialized = DealProductSerializer(data=[{**i, "deal" :self.instance} for i in items], many=True)
            # items_serialized = DealProductSerializer(data=items,many=True)

            # print([{**i, 'deal': instance} for i in items])

            # if items_serialized.is_valid():
            #     items_serialized.save()
            # else:
            #     # self.instance.delete()
            #     print(items_serialized.errors)


        # return self.instance





# class DealSerializer(serializers.ModelSerializer):
    
#     items = DealProductSerializer(source='dealproduct_set',many=True)
    
#     class Meta:
#         model=Deal
#         exclude=["user","added", "status"]

#     def create(self, validated_data):
#         items = validated_data.pop('dealproduct_set')
        
#         self.instance =Deal.objects.create(user=self.context.get("user"),status=DealStatus.objects.first(),**validated_data)
#         # self.instance = super().create(validated_data)
#         try:
#             for item in  items:
#                 print(item)
#                 DealProduct.objects.create(deal=self.instance,**item)
#         except ValidationError: 
#             self.instance.delete()
#             raise ValidationError("error on save products")        

            
#         # if type(items) == list:
#         #     print('Is List')
#         #     self.create_related(DealProductSerializer, items)

#             # items_serialized = DealProductSerializer(data=[{**i, "deal" :self.instance} for i in items], many=True)
#             # items_serialized = DealProductSerializer(data=items,many=True)

#             # print([{**i, 'deal': instance} for i in items])

#             # if items_serialized.is_valid():
#             #     items_serialized.save()
#             # else:
#             #     # self.instance.delete()
#             #     print(items_serialized.errors)


#         return self.instance
    
    
    
    
