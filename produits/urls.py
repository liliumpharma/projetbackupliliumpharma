from django.urls import path,include,re_path
from .api.api import  ProduitApi,ProduitAppApi,GetProduitAppApi,GetUserProducts,ProductDetailApi
from .views import * 


urlpatterns = [
        #------------------API ROUTES-----------------------------------#
        path('api/',  ProduitApi.as_view(),name=' ProduitApi'),
        path('prolist/',  Prolist.as_view(),name=' Prolist'),
        path('api/app/',  ProduitAppApi.as_view(),name=' ProduitAppApi'),
        path('knowledge/api/app/',  ProductsKnowledgeList.as_view(),name='ProductsKnowledgeList'),
        path('api/GetProduitAppApi/',  GetProduitAppApi.as_view(),name=' GetProduitAppApi'),
        path('api/get_user_products/', GetUserProducts.as_view(), name='get_user_products'),
        path('api/product/<int:product_id>/', ProductDetailApi.as_view(), name='product_detail_api'),
        path('QualiquantityInformations/', QualiquantityInformations, name='QualiquantityInformations'),

        # VISITE PAR PRODUIT
        path('api/visites-produit/', VisiteProduitAPIView.as_view(), name='visites_produit_api'),
        path('visites-produit', visitesProduitFront.as_view(), name='visitesProduitFront'),

        
        
        #CERTIFICATE PRINTITNG 
        path('qualiquantity/<int:id>/', QualiquantityPDF.as_view(), name='QualiquantityPDF'),
        path('datasheet/<int:id>/', DataSheet.as_view(), name='datasheet'),
        path('product_data/<int:id>/', ProductData.as_view(), name='ProductData'),


        #PRODUCTION
        path('product_infos/', ProductDetailView.as_view(), name='product-detail'),


]
