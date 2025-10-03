
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status



class DetailsView(APIView):
    #  RETRIEVE , UPDATE OR  DELETE  A MODEL INSTANCE
    
    def can_delete(self, request, instance): # DELETE PERMISSION
        return True
    
    def can_update(self, request, instance): # UPDATE PERMISSION
        return True
    
    def can_create(self, request): # CREATE PERMISSION
        return True
    
    def can_get(self, request, instance): # RETRIEVE PERMISSION
        return True
    

    def update_args(self, request, instance): # UPDATE ARGS
        return {"data":request.data, "instance": instance, "context":{'request': request}, "partial":True}
    
    def create_args(self, request):  # CREATE ARGS
        return {"data":request.data, "context":{'request': request} }
    


    
    def get_object(self, pk):
        try:
            return self.model.objects.get(pk=pk)
        except self.model.DoesNotExist:
            raise Http404
        
        

    def get(self, request, pk, format=None):
        instance = self.get_object(pk)
        if self.can_get(request, instance):
            serializer = self.serializer(instance)
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)
    

    # CREATE
    def post(self, request, format=None):
        if self.can_create(request):
            serializer = self.create_serializer(**self.create_args(request))
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


    # UPDATE 
    def put(self, request, pk, format=None):
        instance = self.get_object(pk)
        if self.can_update(request, instance):
            serializer = self.update_serializer(**self.update_args(request, instance))
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

    # DELETE
    def delete(self, request, pk, format=None):
        instance = self.get_object(pk)
        if self.can_delete(request, instance):
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)