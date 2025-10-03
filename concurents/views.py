from django.http import Http404, HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication,TokenAuthentication
from rest_framework import status
from .models import *
from .serializers import *
from django.views.generic import TemplateView
from django.shortcuts import render,redirect
from liliumpharm.DetailsView import DetailsView 
from liliumpharm.PaginationAPI import PaginationAPI 
from .serializers import ListSerializer, CProductSerializer
from rest_framework import generics
import xlsxwriter
from rest_framework.authtoken.models import Token



class ShapeAPI(APIView):
    def get(self, request):
        return Response([{
            "id": s.id,
            "name":s.name
            } for s in Shape.objects.all()])

class CProductsList(generics.ListAPIView):
    serializer_class = ListSerializer

    def get_queryset(self):
        return CProduct.objects.filter(product__id=self.kwargs["id"])

class DetailCProduct(DetailsView):
    model=CProduct
    serializer=CProductSerializer
    create_serializer= CProductSerializer
    update_serializer=CProductSerializer

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    

    
    def can_create(self, request):
         print("*********************")
         print(request.user)
         return True

    def can_update(self, request, instance):
            return not instance.valid

    def can_delete(self, request, instance):
        return not instance.valid

class CProductsExportExcel(APIView):
    def get(self, request):

        response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response['Content-Disposition'] = f"attachment; filename=CProducts.xlsx"
    
        workbook = xlsxwriter.Workbook(response, {'in_memory': True})
    
        worksheet = workbook.add_worksheet('CProducts')

        title = 'CProducts table'
        title_format = workbook.add_format({'bold': True, 'font_size': 20, 'align': 'center', 'valign': 'vcenter'})
        worksheet.write('A1', title, title_format)
        worksheet.merge_range('A1:C1', title, title_format)
        # HEADERS
        worksheet.write(1, 0,"N°")
        worksheet.write(1, 1,"Lilium_product")
        worksheet.write(1, 2,"المنتج المنافس")
        worksheet.write(1, 3,"اسم الشركة المنافسة")
        worksheet.write(1, 4,"مكان الصنع")
        worksheet.write(1, 5,"السعر")
        worksheet.write(1, 6,"الشكل الصيدلاني")
        worksheet.write(1, 7,"مدة العلاج")
        worksheet.write(1, 8,"المكونات")
        worksheet.write(1, 9,"طريقة التسويق المعتمدة")
        worksheet.write(1, 10,"نقاط القوة")
        worksheet.write(1, 11,"نقاط الضعف")
        worksheet.write(1, 12,"ملاحظات")
        worksheet.write(1, 13,"الصور")

        # GETTING ALL CONCURENT PRODUCTS
        products = CProduct.objects.all()

        get_compositions = lambda products: ' | '.join([c.__str__() for c in products])
        
        if products.exists():
            row=2
            for product in products :
                 # GETTING IMAGE URL
                image_url = product.image.url if product.image else ''
                # APPENDING DOMAIN NAME
                complete_url = "https://app.liliumpharma.com"+image_url
                
                compositions = Composition.objects.filter(product=product)
                composition_names = [composition.name for composition in compositions]
                compositions_text = ", ".join(composition_names)


                worksheet.write(row, 0, product.id)
                worksheet.write(row, 1, str(product.product))
                worksheet.write(row, 2, product.name)
                worksheet.write(row, 3, product.company)
                worksheet.write(row, 4, product.country)
                worksheet.write(row, 5, product.price)
                worksheet.write(row, 6, str(product.shape))
                worksheet.write(row, 7, product.treatment_duration)
                worksheet.write(row, 8, compositions_text)
                worksheet.write(row, 9, product.marketing)
                worksheet.write(row, 10, product.good)
                worksheet.write(row, 11, product.bad)
                worksheet.write(row, 12, product.observations)
                worksheet.write(row, 13, complete_url)
                row+=1


        workbook.close()
        return response

def MsCocurrents(request):

    if request.user.is_authenticated:
        token = Token.objects.filter(user=request.user)

        if token.exists():
            token = token.first().key
        else:
            Token.objects.create(user=request.user)
            token = Token.objects.filter(user=request.user)
            token = token.first().key

    return render(request,"micro_frontends/competors/index.html",{
                "token":token if request.user.is_authenticated else ""
                
            })         