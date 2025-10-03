from django import forms
from django.forms import ModelForm
from .models import *



class RapportForm(ModelForm):
    class Meta:
        model=Rapport
        fields=["image","image2"]

    def set_the_user(self,user):
        self.user=user

    def save(self, commit = True):
        rapport = super(RapportForm, self).save(commit = False)
        rapport.user=self.user
        if commit:
            rapport.save()
        return rapport




class CommentForm(ModelForm):
    class Meta:
        model=Comment
        exclude=["rapport","user"]
        
        

# class VisiteForm(ModelForm):
#     class Meta:
#         model=Visite
#         fields='__all__'
#
#     def set_the_user(self,user):
#         self.user=user
#
#     def save(self, commit = True):
#         rapport = super(RapportForm, self).save(commit = False)
#         rapport.user=self.user
#         if commit:
#             rapport.save()
#         return rapport
