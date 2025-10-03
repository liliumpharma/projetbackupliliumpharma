from rest_framework import generics
from .models import Fournisseur, Information, Item, Achat, Sortie
from .serializers import FournisseurSerializer, InformationSerializer, ItemSerializer, AchatSerializer, SortieSerializer


# View to retrieve Fournisseur data
class FournisseurListView(generics.ListAPIView):
    queryset = Fournisseur.objects.all()
    serializer_class = FournisseurSerializer
    


# View to retrieve a specific Fournisseur by ID
class FournisseurDetailView(generics.RetrieveAPIView):
    queryset = Fournisseur.objects.all()
    serializer_class = FournisseurSerializer


# View to retrieve Information data related to a specific Fournisseur
class InformationListView(generics.ListAPIView):
    queryset = Information.objects.all()
    serializer_class = InformationSerializer

    def get_queryset(self):
        # Filter information based on the supplier (fournisseur)
        fournisseur_id = self.kwargs.get('fournisseur_id')
        return Information.objects.filter(fournisseur_id=fournisseur_id)


# View to retrieve Item data
class ItemListView(generics.ListAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer


# View to retrieve a specific Item by ID
class ItemDetailView(generics.RetrieveAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer


# View to retrieve Achat data
class AchatListView(generics.ListAPIView):
    queryset = Achat.objects.all()
    serializer_class = AchatSerializer


# View to retrieve Sortie data
class SortieListView(generics.ListAPIView):
    queryset = Sortie.objects.all()
    serializer_class = SortieSerializer


# View to retrieve Sortie data based on destination
class SortieByDestinationView(generics.ListAPIView):
    queryset = Sortie.objects.all()
    serializer_class = SortieSerializer

    def get_queryset(self):
        destination = self.kwargs.get('destination')
        return Sortie.objects.filter(destination=destination)
