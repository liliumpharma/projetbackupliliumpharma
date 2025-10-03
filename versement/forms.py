# forms.py
from django import forms
from .models import Versement

class VersementModelForm(forms.ModelForm):
    class Meta:
        model = Versement
        fields = '__all__'  # Include all fields from the model