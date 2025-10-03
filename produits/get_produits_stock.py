from .models import ProduitVisite
from django.db.models import Q,Sum
import datetime

def get_stock(request):

    stock_filters={}

    if  request.GET.get("mindate") :
        stock_filters['visite__rapport__added__gte']=request.GET.get("mindate")
    else:
        stock_filters['visite__rapport__added__year__gte']=datetime.datetime.today().year    

    if  request.GET.get("maxdate") :
        stock_filters['visite__rapport__added__lte']=request.GET.get("maxdate")


    if  request.GET.get("pays") and request.GET.get("pays")!="0" :
        stock_filters['visite__medecin__commune__wilaya__pays__id']=request.GET.get("pays")

    if  request.GET.get("wilaya") and request.GET.get("wilaya")!="0" :
        stock_filters['visite__medecin__commune__wilaya__id']=request.GET.get("wilaya")

    if  request.GET.get("commune") and request.GET.get("commune")!="0" :
        stock_filters['visite__medecin__commune__id']=request.GET.get("commune")    


    if  request.GET.get("commercial") and request.GET.get("commercial")!="" :
        stock_filters['visite__medecin__users__username__icontains']=request.GET.get("commercial")

    if  request.GET.get("specialite") and request.GET.get("specialite")!="" :
        if request.GET.get("specialite")=="commerciale":
            stock_filters['visite__medecin__specialite__in']=['Pharmacie','Grossiste','SuperGros']
        else:
            stock_filters['visite__medecin__specialite__in']=request.GET.get("specialite").split(",")



    produitsvisites=ProduitVisite.objects.filter(**stock_filters).values("produit__nom").annotate(total=Sum("qtt"))

    return produitsvisites