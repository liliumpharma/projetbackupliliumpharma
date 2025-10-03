from rest_framework import serializers
from rapports.models import Rapport,Comment,Visite,ProduitVisite
from accounts.api.serializers import UserSerializer

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile

from requests import get
import pathlib

from plans.models import PlanTask


class CommentSerializer(serializers.ModelSerializer):
    user=UserSerializer()
    class Meta:
        model = Comment
        fields="__all__"

# class RapportAppSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Rapport
#         fields ='__all__'


class VisiteSerializer(serializers.ModelSerializer):
    # produits=ProduitVisiteSerializer(many=True)
    class Meta:
        model = Visite
        fields ='__all__'
        
    # def create(self, validated_data):
    #     produits_data = validated_data.pop('produits')
    #     visite = Visite.objects.create(**validated_data)
    #     for produit_data in produits_data:
    #         ProduitVisite.objects.create(visite=visite, **produit_data)
    #     return album
        

class CommentAppSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields="__all__"

class RapportSerializer(serializers.ModelSerializer):
    visites=serializers.ReadOnlyField(source='visites_list')
    # priorite=serializers.ReadOnlyField(source='rapport_priorite')
    details=serializers.ReadOnlyField(source='rapport_details')
    commercial=serializers.ReadOnlyField(source='rapport_commercial')
    comments=serializers.SerializerMethodField()
    is_updatable=serializers.SerializerMethodField()
    tasks=serializers.SerializerMethodField()
    
    def get_comments(self, obj):
        # Get all comments related to the given rapport
        comments = Comment.objects.filter(rapport=obj)
        
        # Serialize the comments
        serialized_comments = CommentSerializer(comments, many=True).data
        
        # Print the serialized comments to the console
        print("Comments for Rapport:", obj.id, serialized_comments)
        
        # Return the serialized comments data
        return serialized_comments
    
    def get_is_updatable(self,obj):
        return obj.is_updatable()

    def get_tasks(self,obj):
        return [
            {
                "id": task.id,
                "task":task.task,
                "completed":task.completed
            }
            for task in PlanTask.objects.filter(plan__day=obj.added,plan__user=obj.user)
        ]




    class Meta:
        model = Rapport
        fields ='__all__'


class RapportAppSerializer(serializers.ModelSerializer):
    visites=serializers.ReadOnlyField(source='visites_list')
    # priorite=serializers.ReadOnlyField(source='rapport_priorite')
    details=serializers.ReadOnlyField(source='rapport_details')
    commercial=serializers.ReadOnlyField(source='rapport_commercial')
    comments=serializers.SerializerMethodField()
    tasks=serializers.SerializerMethodField()
    # has_deal=serializers.SerializerMethodField()


    def get_comments(self,obj):
        return CommentSerializer(Comment.objects.filter(rapport=obj),many=True).data



    # def get_has_deal(self.obj):
    #     for v in 
    #     return False

    def get_tasks(self,obj):
        return [
            {
                "id": task.id,
                "task":task.task,
                "completed":task.completed,
                "rapport": obj.id
            }
            for task in PlanTask.objects.filter(plan__day=obj.added,plan__user=obj.user)
        ]


    class Meta: 
        model = Rapport
        fields ='__all__'


    # def scan_image(self, io_bytes, user, date):
    #     from random import randrange
    #     buffer = io_bytes.getbuffer()
    #     filename = f'{user}_{date.year}-{date.month}-{date.day}-{randrange(1000)}.jpg'
    #     path = f'media/rapports/{user}/{filename}'
    #     pathlib.Path(path).write_bytes(buffer)

    #     return path

    # def validate(self, data):

    #     user = self.instance.user
    #     date = self.instance.added

    #     image_1 = data.get('image')
    #     image_2 = data.get('image2')

    #     if not image_1:
    #         raise ValidationError('Image was not provided')

    #     image_1_path = '/'.join(self.scan_image(image_1.file, user, date).split('/')[1:])
    #     is_image_valid = True if get(f'http://document_scanner_api:8002/scan-document?path={image_1_path}').status_code == 200 else False

    #     if not is_image_valid:
    #         raise ValidationError('Image doen\'t meet the necessary requirements')


    #     self.context['image'] = f'{image_1_path}'

    #     if image_2:
    #         image_2_path = '/'.join(self.scan_image(image_2.file, user, date).split('/')[1:])
    #         is_image_valid = True if get(f'http://document_scanner_api:8002/scan-document?path={image_2_path}').status_code == 200 else False

    #         if not is_image_valid:
    #             raise ValidationError('Image doen\'t meet the necessary requirements')

    #         self.context['image2'] = f'{image_2_path}'

    #     return data

    # def create(self, validated_data):
    #     super().create(validated_data)
    #     instance.image = self.context.get('image')
    #     instance.save(update_fields=['image'])

    #     if self.context.get('image2'):
    #         instance.image2 = self.context.get('image2')
    #         instance.save(update_fields=['image2'])
        
    #     return instance
    # def update(self, instance, validated_data):
        
    #     super().update(instance, validated_data)

    #     instance.image = self.context.get('image')
    #     instance.save(update_fields=['image'])

    #     if self.context.get('image2'):
    #         instance.image2 = self.context.get('image2')
    #         instance.save(update_fields=['image2'])
        
    #     return instance
        
