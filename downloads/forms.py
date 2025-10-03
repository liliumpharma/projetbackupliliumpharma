# forms.py
from django import forms

class UploadFolderForm(forms.Form):
    folder = forms.FileField(label='Selectionner le fichier ZIP')

