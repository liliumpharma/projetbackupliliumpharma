from django import forms
from .models import Entree

class EntreeForm(forms.ModelForm):
    class Meta:
        model = Entree
        fields = ['fournisseur', 'number', 'e_type', 'subtype', 'produit', 'quantity', 'unite', 'price', 'devise', 'attachement']
        # You can customize widgets or field attributes if necessary
