from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication,TokenAuthentication
from rest_framework import status
from .models import *
from .serializers import *
from django.views.generic import TemplateView
from django.shortcuts import render,redirect
from django.shortcuts import HttpResponse
import xlsxwriter
from produits.models import *
from datetime import date


class DealsAPI(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]


    def get(self, request):
        serial = DealSerializer(instance=Deal.objects.all().first()).data
        return Response(serial)

    def post(self, request, format=None):
        # Extract data from request.data
        min_date = request.data.get('min_date')
        max_date = request.data.get('max_date')
        medecin_id = request.data.get('medecin')  # Assuming only one medecin_id is sent
        items = request.data.get('items', [])
        cost = request.data.get('cost')
        dtype_id = request.data.get('dtype')
        description = request.data.get('description')
        starting_date = request.data.get('starting_date')
        ending_date = request.data.get('ending_date')

        # Create a new Deal object
        deal = Deal.objects.create(
            # min_date=min_date,
            # max_date=max_date,
            cost=cost,
            description=description,
            starting_date=starting_date,
            ending_date=ending_date,
            dtype_id=dtype_id,
            user=request.user,  # Assuming the user is authenticated
        )

        # Associate medecin with the deal
        # Convert medecin_id to a list to handle it
        medecin_id = [medecin_id]

        # Associate medecin with the deal
        for medecin in medecin_id:
            med = Medecin.objects.get(pk=medecin)
            deal.medecin.add(med)

        # Create DealProduct instances and associate them with the deal
        for item in items:
            product_id = item.get('product')
            qtt = item.get('qtt')
            product = Produit.objects.get(pk=product_id)  # Get the Product instance
            DealProduct.objects.create(deal=deal, product=product, qtt=qtt)

        return Response({'message': 'Deal created successfully'}, status=201)

    # def post(self,request,format=None):
    #     serializer = DealSerializer(data=request.data,context={"user":request.user})
    #     if serializer.is_valid():
    #         print('Valid')
    #         instance=serializer.save()
    #         print("saved .....",instance.__json__())
    #         return Response(instance.__json__())
    #     else:
    #         print(serializer.errors)

    #     return Response(serializer.errors)



class DealTypesAPI(APIView):
    def get(self, request):
        return Response([d.__json__() for d in DealType.objects.all()])

class DealStatusAPI(APIView):
    def get(self, request):
        return Response([t.__json__() for t in DealStatus.objects.all()])


class DealPDF(TemplateView):
    def get(self, request, id):
        deal = Deal.objects.get(id=id)
        # Récupère les instances de Delegue_Representant associées à ce deal (en fonction de la relation que tu as définie)
        delegues = Delegue_Representant.objects.filter(deal=deal)  # Exemple, adapte selon la relation
        return render(request, 'deals/pdf.html', {'deals': [deal], 'delegues': delegues})


class DealMedecin(TemplateView):
    def get(self,request,medecin_id):
        return render(request,'deals/pdf.html', {'deals': Deal.objects.filter(medecin_id=medecin_id)})

class DealExportExcel(APIView):
    def get(self, request):
        year = request.GET.get("year", date.today().year)
        deals = Deal.objects.filter(starting_date__year=year)

        response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response['Content-Disposition'] = f"attachment; filename=Deals.xlsx"
    
        workbook = xlsxwriter.Workbook(response, {'in_memory': True})
    
        worksheet = workbook.add_worksheet('Deals')
        # Set the title of the table
        title = 'Deals table'
        title_format = workbook.add_format({'bold': True, 'font_size': 20, 'align': 'center', 'valign': 'vcenter'})
        worksheet.write('A1', title, title_format)
        worksheet.merge_range('A1:C1', title, title_format)

        #Set the header of the table
        worksheet.write(1, 0,"N°")
        worksheet.write(1, 1,"Added")
        worksheet.write(1, 2,"Starting Date")
        worksheet.write(1, 3,"Ending Date")
        worksheet.write(1, 4,"Payment Date")
        worksheet.write(1, 5,"Description")
        worksheet.write(1, 6,"Cost")
        worksheet.write(1, 7,"Status")
        worksheet.write(1, 8,"Deal Type")
        worksheet.write(1, 9,"User")
        worksheet.write(1, 10,"Medecin")

        prod = Produit.objects.all()
        column = 11
        for p in prod:
            worksheet.write(1, column, p.nom)
            column+=1

        worksheet.write(1, column,"Commentaires")

        if deals.exists():
            row=2
            for deal in deals :
                worksheet.write(row, 0, deal.id)
                worksheet.write(row, 1, deal.added)
                worksheet.write(row, 2, deal.starting_date)
                worksheet.write(row, 3, deal.ending_date)
                worksheet.write(row, 4, deal.payment_date)
                worksheet.write(row, 5, deal.description)
                worksheet.write(row, 6, deal.cost)
                worksheet.write(row, 7, str(deal.status))
                worksheet.write(row, 8, deal.dtype.description)
                worksheet.write(row, 9, str(deal.user))
                worksheet.write(row, 10, deal.medecin.nom)

                col = 10
                for p in prod:
                    dealproduct = deal.dealproduct_set.filter(product = p)
                    col+=1
                    if dealproduct.exists():
                        qtt = dealproduct.first().qtt
                        worksheet.write(row, col, qtt)
                        continue
                    worksheet.write(row, col, 0)
                comments =""
                for dc in deal.dealcomment_set.all():
                    comments+=f"{dc.comment} | "

                worksheet.write(row, col+1, comments)

                row+=1
        workbook.close()
        return response
