from django import forms
from django.forms import ModelForm
from .models import Medecin
from regions.models import Wilaya, Commune



class MedecinForm(forms.ModelForm):
    class Meta:
        model = Medecin
        exclude = ['users', 'updatable']
        widgets = {
            'wilaya': forms.Select(attrs={'id': 'id_wilaya'}),
            'commune': forms.Select(attrs={'id': 'id_commune'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['wilaya'].queryset = Wilaya.objects.all()

        if 'wilaya' in self.data:
            try:
                wilaya_id = int(self.data.get('wilaya'))
                self.fields['commune'].queryset = Commune.objects.filter(wilaya_id=wilaya_id).order_by('nom')
            except (ValueError, TypeError):
                self.fields['commune'].queryset = Commune.objects.none()
        elif self.instance.pk:
            self.fields['commune'].queryset = Commune.objects.filter(wilaya=self.instance.wilaya).order_by('nom')
        else:
            self.fields['commune'].queryset = Commune.objects.none()


    # def set_the_user(self,user):
    #     self.user=user
    #
    # def save(self, commit = True):
    #     rapport = super(RapportForm, self).save(commit = False)
    #     rapport.user=self.user
    #     if commit:
    #         rapport.save()
    #     return rapport

class UploadExcelForm(forms.Form):
    fichier_excel = forms.FileField()