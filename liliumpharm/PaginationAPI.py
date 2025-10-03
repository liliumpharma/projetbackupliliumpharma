from rest_framework.views import APIView
from rest_framework import status
from django.core.paginator import Paginator
from django.db.models import Q
from rest_framework.response import Response



class PaginationAPI(APIView):

    item_by_page=10
    

    def additional(self,queryset):
        return []

    def pagination_response(self, request, queryset):

        paginator = Paginator(queryset, self.item_by_page)
        page = request.GET.get('page') if request.GET.get('page') and request.GET.get('page')!="0" else None
        data=paginator.get_page(page)

        data_json=self.serializer(data,many=True)

        
        response={
        'pages':data.paginator.num_pages,
        'result':data_json.data,
        "additional":{},
        'length':len(queryset),
        }


        for key,value in self.additional(queryset):
            response["additional"][key]=value 

        try:
            response['previous']=data.previous_page_number()
        except:
            pass
        try:
            response['next']=data.next_page_number()
        except:
            pass
        return Response( response, status=200)
    

    def get_queryset(self,request):
        return self.model.objects.all()

    def get(self, request, format=None):
        instances=self.get_queryset(request)
        return self.pagination_response(request, instances)

    