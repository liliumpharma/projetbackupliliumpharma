from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from .forms import *
import os
import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import *
from django.contrib.auth.models import User
from django.core.mail import send_mail
from .models import family, Region
from rest_framework.views import APIView
from rest_framework.response import Response


from django.contrib.auth import authenticate, login

# Create your views here.


class HomeAccount(LoginRequiredMixin, TemplateView):
    def get(self, request):
        # return render(request,'accounts/profile.html')
        return render(request, "accounts/home.html")


class Login(TemplateView):
    def get(self, request):
        return render(request, "accounts/login.html")


class Register(TemplateView):
    def get(self, request):
        form = RegistrationForm()
        profile_form = UserProfileRgistrationForm()
        return render(
            request,
            "accounts/register.html",
            {"form": form, "profile_form": profile_form},
        )

    def post(self, request):
        form = RegistrationForm(request.POST or None, prefix="user")
        if form.is_valid():
            form.save()
            user = User.objects.get(email=form.cleaned_data["email"])
            account = UserProfile.objects.get(user=user)
            profile_form = UserProfileRgistrationForm(
                request.POST or None, prefix="profile", instance=account
            )
            if profile_form.is_valid():
                profile_form.save()
                send_mail(
                    "activation du compte",
                    "http://app.liliumpharma.com/account/activate/"
                    + user.username
                    + "/"
                    + account.activate,
                    "aaaa@mailmail.com",
                    [user.email],
                )
            else:
                user.delete()
                return render(
                    request,
                    "accounts/register.html",
                    {"form": form, "profile_form": profile_form},
                )

            return redirect("login")
        else:
            return render(
                request,
                "accounts/register.html",
                {
                    "form": form,
                    "profile_form": UserProfileRgistrationForm(request.POST),
                },
            )


class Profile(LoginRequiredMixin, TemplateView):
    def get(self, request):
        return render(request, "accounts/profile.html")


class EditProfile(LoginRequiredMixin, TemplateView):
    def get(self, request):
        form = EditProfileForm(instance=request.user.userprofile)
        userForm = EditUserForm(instance=request.user)
        return render(
            request, "accounts/edit_profile.html", {"form": form, "userForm": userForm}
        )

    def post(self, request):
        form = EditProfileForm(
            request.POST, prefix="profile", instance=request.user.userprofile
        )
        userForm = EditUserForm(request.POST, prefix="user", instance=request.user)

        if userForm.is_valid():
            print("saved user")
            userForm.save()
        else:
            return render(
                request,
                "accounts/edit_profile.html",
                {"form": form, "userForm": userForm},
            )

        if form.is_valid():
            print("saved profile")
            form.save()
            return redirect("edit_profile")
        else:
            print(form.errors)
            return render(
                request,
                "accounts/edit_profile.html",
                {"form": form, "userForm": userForm, "message": "profile"},
            )


class ChangePassword(LoginRequiredMixin, TemplateView):
    def get(self, request):
        form = PasswordChangeForm(user=request.user)
        return render(request, "accounts/change_password.html", {"form": form})

    def post(self, request):
        form = PasswordChangeForm(data=request.POST, user=request.user)
        if form.is_valid():
            form.save()
            return redirect("profile")
        else:
            return render(request, "accounts/change_password.html", {"form": form})


def ActivateAccount(request, username, activate):
    user = User.objects.get(username=username)
    account = UserProfile.objects.get(user=user)
    if activate == account.activate:
        user.is_active = True
        user.save()
        new_user = authenticate(
            username=user.email,
            password=user.password,
        )
        login(request, user)
        return redirect("edit_profile")
    else:
        return redirect("activate_account_form")


class ActivateAccountForm(TemplateView):
    def get(self, request):
        form = activateAccountForm()
        return render(request, "accounts/activate_account_form.html", {"form": form})

    def post(self, request):
        form = activateAccountForm(request.POST or None)
        if form.is_valid():
            try:
                user = User.objects.get(email=form.cleaned_data["email"])
                account = UserProfile.objects.get(user=user)
                send_mail(
                    "activation du compte",
                    "/account/activate/" + user.username + "/" + account.activate,
                    "webmaster@liliumpharma.com",
                    [user.email],
                )
                return render(
                    request,
                    "accounts/activate_account_form.html",
                    {"message": "un e-mail de confirmation e bien été envoyé"},
                )
            except User.DoesNotExist:
                return render(
                    request, "accounts/activate_account_form.html", {"form": form}
                )

        return render(request, "accounts/activate_account_form.html", {"form": form})


def check_list_new_delegate(request):
    # produits_lilium = list(
    #     Produit.objects.filter(productcompany__family="lilium pharma")
    # )
    # context = {"produits_lilium": produits_lilium}
    # print(str(context))
    context = {"range_list": range(1, 15)}  # Pour générer les pharmacies de 1 à 14
    return render(request, "accounts/check_list_new_delegate.html", context)


from django.http import JsonResponse


from django.http import JsonResponse


def get_monthly_report_details(request):
    print("yyouuupiiiiiiiiiii")
    if request.method == "GET":
        user = request.user
        current_month = datetime.datetime.now().month
        current_year = datetime.datetime.now().year

        rapports = Rapport.objects.filter(
            user=user,
            added__month=current_month,
            added__year=current_year,
        )

        visites = Visite.objects.filter(rapport__in=rapports)
        medecins = Medecin.objects.filter(visite__in=visites)

        # Compte des médecins
        medecin_nbr = len(medecins)

        # Comptage des commerciaux - vous devez définir votre propre logique ici
        commercial_nbr = len(
            medecins.filter(specialite__in=["Pharmacie", "Grossiste", "SuperGros"])
        )

        # Calcul de la similarité moyenne
        total_similarity_percentage = 0  # Implémentez la logique nécessaire pour cela
        plan_count = 0  # Nombre de plans - à définir selon votre logique

        # Préparez la réponse JSON
        response_data = {
            "rapports_count": len(rapports),
            "working_days": sum(
                1
                for day in range(
                    1, calendar.monthrange(current_year, current_month)[1] + 1
                )
                if (
                    datetime.datetime(current_year, current_month, day).weekday()
                    not in [4, 5]
                )
            ),
            "similarity_percentage": (
                total_similarity_percentage / plan_count if plan_count else 0
            ),
            "medecin_nbr": medecin_nbr,
            "commercial_nbr": commercial_nbr,
        }

        return JsonResponse(response_data)


def get_families(request):
    #families = [family.value for family in family]
    families = [Region.value for Region in Region]
    print("#####")
    print(str(families))
    return JsonResponse({"families": families})


class UsersByFamilyAPIView(APIView):

    def get(self, request):
        # Getting the 'family' parameter from the request
        family = request.GET.get("family")
        profile = UserProfile.objects.get(user=request.user.id)
        if family=="1":
            # Fetch users associated with the family
            if request.user.is_superuser:
                users = User.objects.filter(userprofile__family__in=["lilium Pharma", "Lilium1", "Lilium2", "orient Bio", "Aniya_Pharm", "production", "Administration"])
                user_data = [
                {
                    "id": user.id,
                    "username": user.username,
                    # Add other fields as necessary
                }
                for user in users
                ]
                t={
                    "id": request.user.id,
                    "username": request.user.username,
                }
                user_data.insert(0,t)
                t={
                    "id": 1000000,
                    "username": "TOUS",
                }
                user_data.insert(0,t)
            elif profile.speciality_rolee == "Superviseur_regional":
                users = profile.usersunder.all()
                user_data = [
                {
                    "id": user.id,
                    "username": user.username,
                    # Add other fields as necessary
                }
                for user in users
                ]
                t={
                    "id": request.user.id,
                    "username": request.user.username,
                }
                user_data.insert(0,t)
                t={
                    "id": 1000000,
                    "username": "TOUS",
                }
                user_data.insert(0,t)
            elif profile.speciality_rolee == "Superviseur_national" or profile.speciality_rolee == "CountryManager":
                users = User.objects.filter(
                    userprofile__family=family
                )  # Adjust this if necessary based on your models
                users = User.objects.filter(userprofile__family__in=["lilium Pharma", "Lilium1", "Lilium2", "orient Bio", "Aniya_Pharm", "production", "Administration"])
                user_data = [
                {
                    "id": user.id,
                    "username": user.username,
                    # Add other fields as necessary
                }
                for user in users
                ]
                t={
                    "id": request.user.id,
                    "username": request.user.username,
                }
                user_data.insert(0,t)
                t={
                    "id": 1000000,
                    "username": "TOUS",
                }
                user_data.insert(0,t)
            else:
                users = request.user

                # Serialize the users - replace 'UserSerializer' with your actual serializer
                user_data = [
                    {
                        "id": user.id,
                        "username": user.username,
                        # Add other fields as necessary
                    }
                    for user in users
                ]
            print(str(user_data))

            return Response(user_data, status=200)
        else:
            if request.user.is_superuser:
                users = User.objects.filter(userprofile__region=family, userprofile__family__in=["lilium Pharma", "Lilium1", "Lilium2", "orient Bio", "Aniya_Pharm", "production", "Administration"])
                user_data = [
                {
                    "id": user.id,
                    "username": user.username,
                    # Add other fields as necessary
                }
                for user in users
                ]
                t={
                    "id": request.user.id,
                    "username": request.user.username,
                }
                user_data.insert(0,t)
                t={
                    "id": 1000000,
                    "username": "TOUS",
                }
                user_data.insert(0,t)
            elif profile.speciality_rolee == "Superviseur_regional":
                users = profile.usersunder.all()
                users = users.filter(userprofile__region=family)
                user_data = [
                {
                    "id": user.id,
                    "username": user.username,
                    # Add other fields as necessary
                }
                for user in users
                ]
                t={
                    "id": request.user.id,
                    "username": request.user.username,
                }
                user_data.insert(0,t)
                t={
                    "id": 1000000,
                    "username": "TOUS",
                }
                user_data.insert(0,t)
            elif profile.speciality_rolee == "Superviseur_national" or profile.speciality_rolee == "CountryManager":
                users = User.objects.filter(
                    userprofile__family=family
                )  # Adjust this if necessary based on your models
                users = User.objects.filter(userprofile__region=family, userprofile__family__in=["lilium Pharma", "Lilium1", "Lilium2", "orient Bio", "Aniya_Pharm", "production", "Administration"])
                user_data = [
                {
                    "id": user.id,
                    "username": user.username,
                    # Add other fields as necessary
                }
                for user in users
                ]
                t={
                    "id": request.user.id,
                    "username": request.user.username,
                }
                user_data.insert(0,t)
                t={
                    "id": 1000000,
                    "username": "TOUS",
                }
                user_data.insert(0,t)
            else:
                users = request.user

                # Serialize the users - replace 'UserSerializer' with your actual serializer
                user_data = [
                    {
                        "id": user.id,
                        "username": user.username,
                        # Add other fields as necessary
                    }
                    for user in users
                ]
                t={
                    "id": 1000000,
                    "username": "TOUS",
                }
                user_data.insert(0,t)
            print(str(user_data))

            return Response(user_data, status=200)
            return Response({"error": "Family parameter is required."}, status=400)

