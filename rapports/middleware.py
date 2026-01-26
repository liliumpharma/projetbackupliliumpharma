from django.conf import settings
from django.urls import reverse
from django.shortcuts import redirect
#from django.db import connection



class ProtectCommercial:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        from django.shortcuts import redirect  # lazy import

        if request.path in ['/', '/commerciaux', '/medecins']:
            if request.user.is_authenticated:
                if hasattr(request.user, 'userprofile'):
                    if request.user.userprofile.rolee == "Commercial":
                        return redirect("HomeRapport")





# class BDDCON:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         response = self.get_response(request)
#         return response

#     def process_view(self, request, view_func, view_args, view_kwargs):
#         connection.close()