from django.urls import path
from .views import *

urlpatterns = [
    path('front-main/', front_main, name='front_main1'),
    path('mp/', mp_front, name='mp'),
    path('mp-index/', mp_front_index, name='mp'),
    path('mp_approvisonnement_front/', mp_approvisonnement_front, name='mp'),
    path('op_front/', op_front, name='op_front'),
    path('add_op_front/', add_op_front, name='add_op_front'),
    path('mp_op_front/', mp_op_front, name='op_front'),
    path('mp_pesee_front/', mp_pesee_front, name='op_front'),
    path('pesee_front/', pesee_front, name='op_front'),
    path('tableting_front/', tableting_front, name='op_front'),
    path('mp_premix_front/', mp_premix_front, name='premix'),
    path('mp_coating_front/', mp_coating_front, name='coating'),
    path('mp_active_ingredients_front/', mp_active_ingredients_front, name='active_ingredients'),
    path('mp_excipient_front/', mp_excipient_front, name='excipient'),
    path('mp_mp_front/', mp_mp_front, name='matiere premiere'),
    path('mp_retour_front/', mp_retour_front, name='mp'),
    path('mp_sortie_front/', mp_sortie_front, name='mp'),
    path('pesee/', pesee_front, name='pesee'),


    path('entree/add/', AddEntree.as_view(), name='add_entree'),
    path('entree/list/', entree_list, name='entree_list'),  # Vue fonction
    path('all/list/', all_list, name='all_list'),  # Vue fonction

    path('sortie/add/', AddSortie.as_view(), name='add_entree'),
    path('sortie/list/', sortie_list, name='entree_list'),  # Vue fonction


    path('retour/add/', AddRetour.as_view(), name='add_entree'),
    path('retour/list/', retour_list, name='entree_list'),  # Vue fonction


    #OP
    # path('entree/op/calculation/', entree_op_calculation, name='entree_list'),  # Vue fonction
    path('entree/list/op/', entree_list_op, name='entree_list_op'),  # Vue fonction 
    path('entree/op/product_ingredients/', product_ingredients, name='product_ingredients'),  # Vue fonction product_ingredients

    path('item-order-productions/', ItemOrderProductionListCreateView.as_view(), name='item-order-production-list-create'),
    path('item-order-productions/<int:pk>/', ItemOrderProductionDetailView.as_view(), name='item-order-production-detail'),
    path('order-productions/<int:order_production_id>/items/', ItemOrderProductionsListView.as_view(), name='order-production-items'),


    path('order-productions/', OrderProductionListCreateView.as_view(), name='order-production-list-create'),
    path('order-productions/<int:pk>/', OrderProductionDetailView.as_view(), name='order-production-detail'),
    path('order-productions/<int:order_id>/receptionner/', ReceptionnerOrderProductionView.as_view(), name='receptionner-order-production'),
    path('order-productions/<int:order_id>/transfert_pesee/', TransfertPeseeOrderProductionView.as_view(), name='receptionner-order-production'),


    path('order-productions/pesee/', OrderProductionPeseeDetailView.as_view(), name='OrderProductionPeseeDetailView'),
    path('order-productions-bashes/tablette/', OrderProductionsBashesTablette.as_view(), name='orderProductionsBashesTablette'),
    path('order-productions/MpPesee/', OrderProductionMPPeseeDetailView.as_view(), name='OrderProductionMPPeseeDetailView'),
    path('order-productions/pesee/<int:order_id>/receptionner/', ReceptionnerOrderProductionPeseeView.as_view(), name='receptionner-order-production'),
    path('order-productions/MpPesee/<int:order_id>/receptionner/', ReceptionnerOrderProductionMpPeseeView.as_view(), name='ReceptionnerOrderProductionMpPeseeView'),
    path('item-order-productions-pesee/', ItemOrderProductionListPeseeCreateView.as_view(), name='item-order-production-list-create'),
    path('order-productions/<int:order_id>/transfert_tablette/', TransfertOrderProductionPeseeView.as_view(), name='receptionner-order-production'),
    path('order-productions/<int:order_id>/transfert_mp_pesee/', TransfertOrderProductionMpPeseeView.as_view(), name='receptionner-order-production'),
    path('order-productions/<int:item_id>/transfert_production/', TransfertProductionOrderProductionMpPeseeView.as_view(), name='receptionner-order-production'),

    path('order-productions/tablette/<int:order_id>/receptionner/', ReceptionnerOrderProductionTabletteView.as_view(), name='receptionner-order-production'),
    path('create-order-production/', create_order_production, name='create_order_production'),
    path('create-item-bash/', create_item_order_production_bash, name='create_item_bash'),
    path('get_bash_items/', get_bash_items, name='get_bash_items'),
    path("send__bash_group/", send__bash_group, name="send__bash_group"),



]

