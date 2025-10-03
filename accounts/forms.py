from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm,UserChangeForm
from .models import *
import re

class RegistrationForm(UserCreationForm):
    email=forms.EmailField( required='True');
    is_active=False
    prefix='user'
    class Meta:
        model=User
        fields=['email','username','password1','password2','first_name','last_name','is_active']

    def is_valid(self):
        valid = super(RegistrationForm, self).is_valid()
        if not valid:
            return valid
        try:
            User.objects.get(email=self.cleaned_data.get('email'))
            self.add_error('email', 'compte existant')
        except:
            pass
        if not self.errors:
            return True
        return False

class UserProfileRgistrationForm(forms.ModelForm):
    prefix='profile'
    class Meta:
        model=UserProfile
        exclude=['user','solde','activate','rolee']

    def is_valid(self):
        valid = super(UserProfileRgistrationForm, self).is_valid()
        if not valid:
            return valid

        mobile = re.compile(r'^0[5-9][0-9]{8}')
        fix=re.compile(r'^0[2-9][0-9]{7}')
        phone=self.cleaned_data.get('telephone')
        if (not mobile.search(phone)) and (not fix.search(phone)):
            self.add_error('telephone', 'Numero de Telephone Invalide')


        if not self.errors:
            return True
        return False

class EditProfileForm(forms.ModelForm):
    prefix='profile'
    class Meta:
        model=UserProfile
        exclude=['activate','user','solde']

class EditUserForm(UserChangeForm):
    prefix='user'
    class Meta:
        model=User
        fields=['first_name','last_name','email',]

class activateAccountForm(forms.Form):
    email=forms.EmailField( required='True');
