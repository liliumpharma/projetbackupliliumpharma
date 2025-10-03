from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.core.exceptions import ValidationError


class EmailBackend:
    def authenticate(self, request, username=None, password=None,**kwargs):
        try:
            user = User.objects.get(email=username)
        except User.DoesNotExist:
            raise ValidationError('Identifiants Invalides ')

        if user.check_password(password):
            if user.is_active:
                return user
            else:
                raise ValidationError('Vous devez activer votre compte ')

        return None








    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
