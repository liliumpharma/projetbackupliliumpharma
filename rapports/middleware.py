from django.conf import settings
from django.urls import reverse
from django.shortcuts import redirect
from django.db import connection



class ProtectCommercial:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        print(f" path {request.path}")
        # connection.close()
        # if "rapports" in request.path and not "api" in request.path and not "admin" in request.path and not "PDF" in request.path and not "IMAGE" in request.path:
        #     if request.user.is_authenticated and request.user.userprofile.rolee != "Commercial":
        #         return redirect("Home")

        if request.path=='/' or request.path=='/commerciaux' or request.path=='/medecins':
            if request.user.is_authenticated:
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