from django.urls import path
from .views import *

urlpatterns = [
    path('front/', front_main, name='front_main'),
    path('addfront/', front_add, name='front_add'),
    path('proxy/', proxy_openrouteservice, name='proxy_openrouteservice'),
    path('deplacement/create/', create_deplacement, name='create_deplacement'),
    path('api/', get_deplacements, name='get_deplacements'),
    path('api/<int:deplacement_id>/update_status/', update_status, name='update_status'),
    path('sector-table/', get_sector_table, name='sector_table'),
    path('wilaya-sales/', get_wilaya_real_sales, name='get_wilaya_real_sales'),
    path('communes/', get_communes_by_wilaya, name='get_communes_by_wilaya'),
    # 1. Affichage de la fiche de remboursement (A4)
    path('reimbursement-sheet/<int:user_id>/<str:month>/', reimbursement_sheet_view, name='reimbursement_sheet'),
    # 2. Unified API: supervisor price + direction approval
    path('api/validate-sector/', save_sector_validation, name='save_sector_validation'),


]


