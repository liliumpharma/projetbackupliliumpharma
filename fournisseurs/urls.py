from django.urls import path
from .views import (
    FournisseurListView,
    FournisseurDetailView,
    InformationListView,
    ItemListView,
    ItemDetailView,
    AchatListView,
    SortieListView,
    SortieByDestinationView
)

urlpatterns = [
    path('fournisseurs/', FournisseurListView.as_view(), name='fournisseur-list'),
    path('fournisseurs/<int:pk>/', FournisseurDetailView.as_view(), name='fournisseur-detail'),
    path('fournisseurs/<int:fournisseur_id>/informations/', InformationListView.as_view(), name='information-list'),
    path('items/', ItemListView.as_view(), name='item-list'),
    path('items/<int:pk>/', ItemDetailView.as_view(), name='item-detail'),
    path('achats/', AchatListView.as_view(), name='achat-list'),
    path('sorties/', SortieListView.as_view(), name='sortie-list'),
    path('sorties/destination/<str:destination>/', SortieByDestinationView.as_view(), name='sortie-by-destination'),
]

