from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render,redirect

class FrontView(TemplateView):
    def get(self,request,path=''):
        if request.user.is_authenticated:
            print("path : "+str(path))
            if path=="medecins":
                return render(request,'index.html')
            return render(request,'rapports/home.html')
        else:
            return redirect("login")
