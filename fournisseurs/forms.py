from django.forms import ModelForm
from .models import *

class SpendModelForm(ModelForm):
    class Meta:
        model=Spend
        exclude = ['status']

class SpendCommentModelForm(ModelForm):
    class Meta:
        model=SpendComment
        exclude = ['status']