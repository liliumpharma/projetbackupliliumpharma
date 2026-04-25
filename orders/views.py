from .models import *
from .serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import (
    TokenAuthentication,
    SessionAuthentication,
    BasicAuthentication,
)
from django.http import Http404, JsonResponse
from django.core.paginator import Paginator
from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import datetime
from datetime import date
from django.template.loader import render_to_string
from weasyprint import HTML
from django.http import HttpResponse
from django.db.models import Q
from django.shortcuts import render, redirect
from django.utils import timezone
from rest_framework.authtoken.models import Token
import json
from produits.models import Produit


from accounts.models import *
from clients.models import *


# class addorder(TemplateView):
#     def get(self, request):
#         #med = request.user.medecins.all()
#         user_id=request.session.get('user_id')
#         if user_id is None:
#             user_id=request.user.id
#         else:
#             user_id=int(user_id)
#         print("mobile probleme 1 addorder")
#         print(user_id)
#         u = UserProfile.objects.get(user=user_id)
#         if u.speciality_rolee == "Office" or u.speciality_rolee == "Admin" or u.speciality_rolee == "CountryManager":
#             print("yes is super user")

#             pha = Medecin.objects.filter(specialite="Pharmacie")
#             gro = Medecin.objects.filter(specialite="Grossiste")
#             sugro = Client.objects.filter(supergro=True)
#             #pro = Produit.objects.all()
#             #pro = UserProduct.objects.filter(user=request.user)
#             pro = Produit.objects.all()
#             return render(request, "orders/addorder.html", {'pha':pha, 'gro':gro, 'sugro':sugro, 'pro':pro})

#         if u.speciality_rolee == "Superviseur_regional" or u.speciality_rolee == "Superviseur_national":
#             usr = User.objects.get(id=user_id)
#             userpro = UserProfile.objects.get(user=usr)
#             users_under = userpro.usersunder.all()
#             all_sectors = set()
#             for user in users_under:
#                 try:
#                     sectors = user.userprofile.sectors.all()
#                     all_sectors.update(sectors)
#                 except UserProfile.DoesNotExist:
#                     continue  # au cas où un user n'a pas encore de profil

#             meds = Medecin.objects.filter(users=usr)
#             pha = Medecin.objects.filter(users=usr, specialite="Pharmacie")
#             gro = Medecin.objects.filter(specialite="Grossiste", wilaya__in=all_sectors)
#             sugro = Client.objects.filter(supergro=True)
#             pro = Produit.objects.all()
#             #pro = UserProduct.objects.filter(user=request.user)
#             return render(request, "orders/addorder.html", {'pha':pha, 'gro':gro, 'sugro':sugro, 'pro':pro})

#         print("mobile probleme 2 addorder")
#         usr = User.objects.get(id=user_id)
#         userpro = UserProfile.objects.get(user=usr)
#         meds = Medecin.objects.filter(users=usr)
#         pha = Medecin.objects.filter(users=usr, specialite="Pharmacie")
#         gro = Medecin.objects.filter(specialite="Grossiste",wilaya__in=userpro.sectors.all())
#         sugro = Client.objects.filter(supergro=True)
#         pro = Produit.objects.all()
#         #pro = UserProduct.objects.filter(user=request.user)
#         return render(request, "orders/addorder.html", {'pha':pha, 'gro':gro, 'sugro':sugro, 'pro':pro})

#     def post(self, request):
#         user_id=request.session.get('user_id')
#         if user_id is None:
#             user_id=request.user.id
#         else:
#             user_id=int(user_id)
#         u = UserProfile.objects.get(user=user_id)
#         pharmacy_id = request.POST.get("phar")
#         pharmacyy = Medecin.objects.filter(id=pharmacy_id).first() if pharmacy_id else None
#         gros_id = request.POST.get("gros")
#         groo = Medecin.objects.filter(id=gros_id).first() if gros_id else None
#         super_gros_id = request.POST.get("sugros")
#         su_gro = Client.objects.filter(id=super_gros_id).first() if super_gros_id else None
#         if pharmacy_id and gros_id and super_gros_id:
#             m = "Veuillez Choisir que deux parmi Pharmacie, Grossiste et SuperGros ou Bien que SuperGros"
#             if u.speciality_rolee == "Office" or u.speciality_rolee == "Admin" or u.speciality_rolee == "CountryManager":
#                 print("yes is super user")

#                 pha = Medecin.objects.filter(specialite="Pharmacie")
#                 gro = Medecin.objects.filter(specialite="Grossiste")
#                 sugro = Client.objects.filter(supergro=True)
#                 pro = Produit.objects.all()
#                 #pro = UserProduct.objects.filter(user=request.user)
#                 #m = "Bon de Commande ajouter avec succes"
#                 return render(request, "orders/addorder.html", {'pha':pha, 'gro':gro, 'sugro':sugro, 'pro':pro, "m":m})
#             else:
#                 pha = Medecin.objects.filter(users=user_id, specialite="Pharmacie")
#                 usr = User.objects.get(id=user_id)
#                 userpro = UserProfile.objects.get(user=usr)
#                 gro = Medecin.objects.filter(specialite="Grossiste",wilaya__in=userpro.sectors.all())
#                 sugro = Client.objects.filter(supergro=True)
#                 pro = Produit.objects.all()
#                 #m = "Bon de Commande ajouter avec succes"
#                 return render(request, "orders/addorder.html", {'pha':pha, 'gro':gro, 'sugro':sugro, 'pro':pro, "m":m})
#         if not pharmacy_id and not gros_id and super_gros_id:
#             pass
#         elif pharmacy_id and gros_id and not super_gros_id:
#             pass
#         elif pharmacy_id and not gros_id and super_gros_id:
#             pass
#         elif not pharmacy_id and gros_id and super_gros_id:
#             pass
#         elif pharmacy_id and not gros_id and not super_gros_id:
#             m = "Veuillez Choisir que deux parmi Pharmacie, Grossiste et SuperGros ou Bien que SuperGros Seul"
#             if u.speciality_rolee == "Office" or u.speciality_rolee == "Admin" or u.speciality_rolee == "CountryManager":
#                 print("yes is super user")

#                 pha = Medecin.objects.filter(specialite="Pharmacie")
#                 usr = User.objects.get(id=user_id)
#                 userpro = UserProfile.objects.get(user=usr)
#                 gro = Medecin.objects.filter(specialite="Grossiste",wilaya__in=userpro.sectors.all())
#                 sugro = Client.objects.filter(supergro=True)
#                 pro = Produit.objects.all()
#                 #pro = UserProduct.objects.filter(user=request.user)
#                 #m = "Bon de Commande ajouter avec succes"
#                 return render(request, "orders/addorder.html", {'pha':pha, 'gro':gro, 'sugro':sugro, 'pro':pro, "m":m})
#             else:
#                 pha = Medecin.objects.filter(users=user_id, specialite="Pharmacie")
#                 usr = User.objects.get(id=user_id)
#                 userpro = UserProfile.objects.get(user=usr)
#                 gro = Medecin.objects.filter(specialite="Grossiste",wilaya__in=userpro.sectors.all())
#                 sugro = Client.objects.filter(supergro=True)
#                 pro = Produit.objects.all()
#                 #m = "Bon de Commande ajouter avec succes"
#                 return render(request, "orders/addorder.html", {'pha':pha, 'gro':gro, 'sugro':sugro, 'pro':pro, "m":m})
#         elif not pharmacy_id and gros_id and not super_gros_id:
#             m = "Veuillez Choisir que deux parmi Pharmacie, Grossiste et SuperGros ou Bien que SuperGros Seul"
#             if u.speciality_rolee == "Office" or u.speciality_rolee == "Admin" or u.speciality_rolee == "CountryManager":
#                 print("yes is super user")

#                 pha = Medecin.objects.filter(specialite="Pharmacie")
#                 gro = Medecin.objects.filter(specialite="Grossiste")
#                 sugro = Client.objects.filter(supergro=True)
#                 pro = Produit.objects.all()
#                 #pro = UserProduct.objects.filter(user=request.user)
#                 #m = "Bon de Commande ajouter avec succes"
#                 return render(request, "orders/addorder.html", {'pha':pha, 'gro':gro, 'sugro':sugro, 'pro':pro, "m":m})
#             else:
#                 pha = Medecin.objects.filter(users=user_id, specialite="Pharmacie")
#                 usr = User.objects.get(id=user_id)
#                 userpro = UserProfile.objects.get(user=usr)
#                 gro = Medecin.objects.filter(specialite="Grossiste",wilaya__in=userpro.sectors.all())
#                 sugro = Client.objects.filter(supergro=True)
#                 pro = Produit.objects.all()
#                 #m = "Bon de Commande ajouter avec succes"
#                 return render(request, "orders/addorder.html", {'pha':pha, 'gro':gro, 'sugro':sugro, 'pro':pro, "m":m})
#         else:
#             m = "Veuillez Choisir que deux parmi Pharmacie, Grossiste et SuperGros ou Bien que SuperGros Seul, parceque vous avec rien choisir"
#             if u.speciality_rolee == "Office" or u.speciality_rolee == "Admin" or u.speciality_rolee == "CountryManager":
#                 print("yes is super user")

#                 pha = Medecin.objects.filter(specialite="Pharmacie")
#                 gro = Medecin.objects.filter(specialite="Grossiste")
#                 sugro = Client.objects.filter(supergro=True)
#                 pro = Produit.objects.all()
#                 #pro = UserProduct.objects.filter(user=request.user)
#                 #m = "Bon de Commande ajouter avec succes"
#                 return render(request, "orders/addorder.html", {'pha':pha, 'gro':gro, 'sugro':sugro, 'pro':pro, "m":m})
#             else:
#                 pha = Medecin.objects.filter(users=user_id, specialite="Pharmacie")
#                 usr = User.objects.get(id=user_id)
#                 userpro = UserProfile.objects.get(user=usr)
#                 gro = Medecin.objects.filter(specialite="Grossiste",wilaya__in=userpro.sectors.all())
#                 sugro = Client.objects.filter(supergro=True)
#                 pro = Produit.objects.all()
#                 #m = "Bon de Commande ajouter avec succes"
#                 return render(request, "orders/addorder.html", {'pha':pha, 'gro':gro, 'sugro':sugro, 'pro':pro, "m":m})
#         observations = request.POST.get("observations")
#         image = request.FILES.get('image')
#         us = User.objects.get(id=user_id)

#         pro = Produit.objects.all()
#         #pro = UserProduct.objects.filter(user=request.user)
#         h=0
#         for itempro in pro:
#             check_value = request.POST.get(f"check_{itempro.nom}")
#             if check_value == "on":
#                 h=h+1
#                 qtt_value = request.POST.get(f"qtt_{itempro.nom}")
#                 if not qtt_value:
#                     m = f"Veuillez Ajoutez un veleur a le produit cocher {itempro.nom}"
#                     if u.speciality_rolee == "Office" or u.speciality_rolee == "Admin" or u.speciality_rolee == "CountryManager":
#                         print("yes is super user")

#                         pha = Medecin.objects.filter(specialite="Pharmacie")
#                         gro = Medecin.objects.filter(specialite="Grossiste")
#                         sugro = Client.objects.filter(supergro=True)
#                         pro = Produit.objects.all()
#                         #pro = UserProduct.objects.filter(user=request.user)
#                         #m = "Bon de Commande ajouter avec succes"
#                         return render(request, "orders/addorder.html", {'pha':pha, 'gro':gro, 'sugro':sugro, 'pro':pro, "m":m})
#                     else:
#                         pha = Medecin.objects.filter(users=request.user, specialite="Pharmacie")
#                         gro = Medecin.objects.filter(users=request.user, specialite="Grossiste")
#                         sugro = Client.objects.filter(supergro=True)
#                         pro = Produit.objects.all()
#                         #m = "Bon de Commande ajouter avec succes"
#                         return render(request, "orders/addorder.html", {'pha':pha, 'gro':gro, 'sugro':sugro, 'pro':pro, "m":m})
#         if h==0:
#             m="Veuillez ajouter en moin un produit"
#             if u.speciality_rolee == "Office" or u.speciality_rolee == "Admin" or u.speciality_rolee == "CountryManager":
#                 print("yes is super user")

#                 pha = Medecin.objects.filter(specialite="Pharmacie")
#                 gro = Medecin.objects.filter(specialite="Grossiste")
#                 sugro = Client.objects.filter(supergro=True)
#                 pro = Produit.objects.all()
#                 #pro = UserProduct.objects.filter(user=request.user)
#                 #m = "Bon de Commande ajouter avec succes"
#                 return render(request, "orders/addorder.html", {'pha':pha, 'gro':gro, 'sugro':sugro, 'pro':pro, "m":m})
#             else:
#                 pha = Medecin.objects.filter(users=request.user, specialite="Pharmacie")
#                 gro = Medecin.objects.filter(users=request.user, specialite="Grossiste")
#                 sugro = Client.objects.filter(supergro=True)
#                 pro = Produit.objects.all()
#                 #m = "Bon de Commande ajouter avec succes"
#                 return render(request, "orders/addorder.html", {'pha':pha, 'gro':gro, 'sugro':sugro, 'pro':pro, "m":m})
#         else:
#             createorder = Order.objects.create(pharmacy=pharmacyy, gros=groo, super_gros=su_gro, user=us, observation=observations, image=image, status="initial")
#             for itempro in pro:
#                 check_value = request.POST.get(f"check_{itempro.nom}")
#                 if check_value == "on":
#                     qtt_value = request.POST.get(f"qtt_{itempro.nom}")
#                     createitemorder = OrderItem.objects.create(order=createorder,produit=itempro, qtt=qtt_value)
#         if u.speciality_rolee == "Office" or u.speciality_rolee == "Admin" or u.speciality_rolee == "CountryManager":
#             print("yes is super user")

#             pha = Medecin.objects.filter(specialite="Pharmacie")
#             gro = Medecin.objects.filter(specialite="Grossiste")
#             sugro = Client.objects.filter(supergro=True)
#             pro = Produit.objects.all()
#             #pro = UserProduct.objects.filter(user=request.user)
#             m = "Bon de Commande ajouter avec succes"
#             #return redirect('MsOrders')
#             return render(request, "orders/ord.html", {"m":m})
#             return redirect(f"{reverse('MsOrders')}?ttl=1")
#             #return render(request, "orders/addorder.html", {'pha':pha, 'gro':gro, 'sugro':sugro, 'pro':pro, "m":m})
#         pha = Medecin.objects.filter(users=user_id, specialite="Pharmacie")
#         gro = Medecin.objects.filter(users=user_id, specialite="Grossiste")
#         sugro = Client.objects.filter(supergro=True)
#         m = "Bon de Commande ajouter avec succes"
#         #return redirect('MsOrders')
#         return render(request, "orders/ord.html", {"m":m})
#         return redirect(f"{reverse('MsOrders')}?ttl=1")
#         #return render(request, "orders/addorder.html", {'pha':pha, 'gro':gro, 'sugro':sugro, 'pro':pro, "m":m})

class addorder(TemplateView):
    @staticmethod
    def _grossistes_scoped_by_superviseur_or_self(user_obj, user_profile):
        """
        For Commercials:
        - If user has one or more superviseur profiles (Superviseur / regional / national),
          scope grossistes by the union of superviseurs' sectors.
        - Else fallback to user's own sectors.
        """
        superviseur_profiles = UserProfile.objects.filter(
            usersunder=user_obj,
            speciality_rolee__in=["Superviseur", "Superviseur_regional", "Superviseur_national"],
        ).distinct()

        sectors = set()
        for sp in superviseur_profiles:
            sectors.update(sp.sectors.all())

        if not sectors:
            sectors.update(user_profile.sectors.all())

        return Medecin.objects.filter(specialite="Grossiste", wilaya__in=sectors)

    @staticmethod
    def _safe_upload_name(original_name: str) -> str:
        """
        Make uploaded filenames filesystem-safe (ASCII only) to avoid UnicodeEncodeError
        on servers running under ASCII locales.
        Example: "capture_décran.png" -> "capture_decran_a1b2c3d4.png"
        """
        import os
        import uuid
        import unicodedata
        from django.utils.text import get_valid_filename

        base, ext = os.path.splitext(original_name or "")

        # Remove accents (é -> e), drop non-ascii
        base = unicodedata.normalize("NFKD", base).encode("ascii", "ignore").decode("ascii")

        # Django-safe filename + small hardening
        base = get_valid_filename(base).replace(" ", "_").strip("._")
        if not base:
            base = "file"

        ext = (ext or "").lower()
        return f"{base}_{uuid.uuid4().hex[:8]}{ext}"

    def get(self, request):
        user_id = request.session.get("user_id")
        if user_id is None:
            user_id = request.user.id
        else:
            user_id = int(user_id)

        u = UserProfile.objects.get(user=user_id)

        # Office/Admin/CountryManager => see everything
        if u.speciality_rolee in ["Office", "Admin", "CountryManager"]:
            pha = Medecin.objects.filter(specialite="Pharmacie")
            gro = Medecin.objects.filter(specialite="Grossiste")
            sugro = Client.objects.filter(supergro=True)
            pro = Produit.objects.all()
            return render(
                request,
                "orders/addorder.html",
                {"pha": pha, "gro": gro, "sugro": sugro, "pro": pro},
            )

        # Superviseurs => keep your existing logic (grossistes by union of underusers sectors)
        if u.speciality_rolee in ["Superviseur", "Superviseur_regional", "Superviseur_national"]:
            usr = User.objects.get(id=user_id)
            userpro = UserProfile.objects.get(user=usr)
            users_under = userpro.usersunder.all()

            all_sectors = set()
            for user in users_under:
                try:
                    sectors = user.userprofile.sectors.all()
                    all_sectors.update(sectors)
                except UserProfile.DoesNotExist:
                    continue

            pha = Medecin.objects.filter(users=usr, specialite="Pharmacie")
            gro = Medecin.objects.filter(specialite="Grossiste", wilaya__in=all_sectors)
            sugro = Client.objects.filter(supergro=True)
            pro = Produit.objects.all()
            return render(
                request,
                "orders/addorder.html",
                {"pha": pha, "gro": gro, "sugro": sugro, "pro": pro},
            )

        # Default (Commercial / other)
        usr = User.objects.get(id=user_id)
        userpro = UserProfile.objects.get(user=usr)

        pha = Medecin.objects.filter(users=usr, specialite="Pharmacie")
        gro = self._grossistes_scoped_by_superviseur_or_self(usr, userpro)
        sugro = Client.objects.filter(supergro=True)
        pro = Produit.objects.all()
        return render(
            request,
            "orders/addorder.html",
            {"pha": pha, "gro": gro, "sugro": sugro, "pro": pro},
        )

    def post(self, request):
        user_id = request.session.get("user_id")
        if user_id is None:
            user_id = request.user.id
        else:
            user_id = int(user_id)

        u = UserProfile.objects.get(user=user_id)

        pharmacy_id = request.POST.get("phar")
        pharmacyy = Medecin.objects.filter(id=pharmacy_id).first() if pharmacy_id else None

        gros_id = request.POST.get("gros")
        groo = Medecin.objects.filter(id=gros_id).first() if gros_id else None

        super_gros_id = request.POST.get("sugros")
        su_gro = Client.objects.filter(id=super_gros_id).first() if super_gros_id else None

        # Helper to re-render the form with consistent scoping
        def _render_form_with_message(msg):
            if u.speciality_rolee in ["Office", "Admin", "CountryManager"]:
                pha = Medecin.objects.filter(specialite="Pharmacie")
                gro = Medecin.objects.filter(specialite="Grossiste")
                sugro = Client.objects.filter(supergro=True)
                pro = Produit.objects.all()
                return render(
                    request,
                    "orders/addorder.html",
                    {"pha": pha, "gro": gro, "sugro": sugro, "pro": pro, "m": msg},
                )

            usr = User.objects.get(id=user_id)
            userpro = UserProfile.objects.get(user=usr)

            # Keep your current behavior: pharmacies linked to user
            pha = Medecin.objects.filter(users=user_id, specialite="Pharmacie")
            gro = self._grossistes_scoped_by_superviseur_or_self(usr, userpro)

            sugro = Client.objects.filter(supergro=True)
            pro = Produit.objects.all()
            return render(
                request,
                "orders/addorder.html",
                {"pha": pha, "gro": gro, "sugro": sugro, "pro": pro, "m": msg},
            )

        # --- Validate selection rules (kept identical to your existing logic) ---
        if pharmacy_id and gros_id and super_gros_id:
            return _render_form_with_message(
                "Veuillez Choisir que deux parmi Pharmacie, Grossiste et SuperGros ou Bien que SuperGros"
            )

        if not pharmacy_id and not gros_id and super_gros_id:
            pass
        elif pharmacy_id and gros_id and not super_gros_id:
            pass
        elif pharmacy_id and not gros_id and not super_gros_id:
            return _render_form_with_message(
                "Veuillez Choisir que deux parmi Pharmacie, Grossiste et SuperGros ou Bien que SuperGros Seul"
            )
        elif not pharmacy_id and gros_id and not super_gros_id:
            return _render_form_with_message(
                "Veuillez Choisir que deux parmi Pharmacie, Grossiste et SuperGros ou Bien que SuperGros Seul"
            )
        else:
            return _render_form_with_message(
                "Veuillez Choisir que deux parmi Pharmacie, Grossiste et SuperGros ou Bien que SuperGros Seul, parceque vous avec rien choisir"
            )

        # --- Validate products BEFORE creating the Order (prevents empty orders) ---
        pro = Produit.objects.all()

        selected_lines = []
        for itempro in pro:
            check_value = request.POST.get(f"check_{itempro.nom}")
            if check_value == "on":
                qtt_value = request.POST.get(f"qtt_{itempro.nom}")
                if not qtt_value:
                    return _render_form_with_message(
                        f"Veuillez Ajoutez un veleur a le produit cocher {itempro.nom}"
                    )
                try:
                    qtt_int = int(qtt_value)
                except ValueError:
                    return _render_form_with_message(f"Quantité invalide pour {itempro.nom}")

                if qtt_int <= 0:
                    return _render_form_with_message(f"Quantité invalide pour {itempro.nom}")

                selected_lines.append((itempro, qtt_int))

        if not selected_lines:
            return _render_form_with_message("Veuillez ajouter en moin un produit")

        # --- Create the Order + its OrderItems ---
        observations = request.POST.get("observations")
        image = request.FILES.get("image")

        # ✅ FIX: sanitize upload filename to prevent UnicodeEncodeError (é, à, …)
        if image and getattr(image, "name", None):
            image.name = self._safe_upload_name(image.name)

        us = User.objects.get(id=user_id)

        order = Order.objects.create(
            pharmacy=pharmacyy,
            gros=groo,
            super_gros=su_gro,
            user=us,
            observation=observations,
            image=image,
            status="initial",
        )

        for produit_obj, qtt_int in selected_lines:
            OrderItem.objects.create(order=order, produit=produit_obj, qtt=qtt_int)

        m = "Bon de Commande ajouter avec succes"
        return render(request, "orders/ord.html", {"m": m})


class OrderAPI(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, id=""):
        if id == "":
            if (
                request.user.userprofile.rolee not in ["Superviseur", "CountryManager"]
                and request.user.is_superuser != True
                and request.user.username not in ["ibtissemdz", "liliumdz"]
            ):
                orders_list = Order.objects.filter(
                    user=request.user,
                    added__month=datetime.now().month,
                    added__year=datetime.now().year,
                ).order_by("-added")
            else:
                if (
                    request.user.is_superuser
                    or request.user.username
                    in ["ibtissemdz", "RABTIDZ", "a.lounis@liliumpharma.com"]
                    or request.user.username == "liliumdz"
                    or request.user.userprofile.speciality_rolee in ["Office"]
                ):
                    filters = {}

                    if request.GET.get("pays") and request.GET.get("pays") != "0":
                        filters["user__userprofile__commune__wilaya__pays__id"] = (
                            request.GET.get("pays")
                        )

                    if request.GET.get("wilaya") and request.GET.get("wilaya") != "0":
                        filters["client__commune__wilaya__id"] = request.GET.get(
                            "wilaya"
                        )

                    if request.GET.get("commune") and request.GET.get("commune") != "0":
                        filters["client__commune__id"] = request.GET.get("commune")

                    if request.GET.get("client") and request.GET.get("client") != "":
                        filters["client__nom__icontains"] = request.GET.get("client")

                    if request.GET.get("mindate") and request.GET.get("mindate") != "":
                        filters["added__gte"] = request.GET.get("mindate")

                    if request.GET.get("maxdate") and request.GET.get("maxdate") != "":
                        filters["added__lte"] = request.GET.get("maxdate")

                    if request.GET.get("produit") and request.GET.get("produit") != "":
                        filters["orderitem__produit__id"] = request.GET.get("produit")

                    if request.GET.get("status") and request.GET.get("status") != "":
                        filters["status"] = request.GET.get("status")

                    if (
                        request.GET.get("commercial")
                        and request.GET.get("commercial") != ""
                    ):
                        filters["user__username__icontains"] = request.GET.get(
                            "commercial"
                        )

                    orders_list = Order.objects.filter(**filters).order_by("-added")
                else:
                    q = Q(
                        user=request.user,
                        added__month=datetime.now().month,
                        added__year=datetime.now().year,
                    )
                    q |= Q(user__in=request.user.userprofile.usersunder.all())
                    orders_list = Order.objects.filter(q).distinct().order_by("-added")

            serializer = OrderSerializer(orders_list, many=True)

            return Response(serializer.data, status=200)
        else:
            order = Order.objects.get(id=id)
            if order.status == "en cours":
                order.status = "traite"
                order.done_date = datetime.today().date()

            if order.status == "confirmed":
                order.status = "en cours"

            if order.status == "initial":
                order.status = "confirmed"
                order.validation_date = datetime.today().date()

            order.save()

            return Response(OrderSerializer(order).data, status=200)

import json
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

class OrderAppAPI(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            raise Http404

    def pagination_response(self, orders, json, result_length):
        response = {
            "pages": orders.paginator.num_pages,
            "result": {"orders": json.data},
            "length": result_length,
        }
        try:
            response["previous"] = orders.previous_page_number()
        except:
            pass
        try:
            response["next"] = orders.next_page_number()
        except:
            pass
        return response

    def get(self, request, id=""):
        if id == "":
            if request.user.username in ["RABTIDZ", "a.lounis@liliumpharma.com"]:
                orders_list = Order.objects.all().order_by("-added")
            else:
                if (
                    request.user.userprofile.rolee
                    not in ["Superviseur", "CountryManager"]
                    and request.user.is_superuser != True
                    and request.user.username not in ["ibtissemdz", "liliumdz"]
                ):
                    q = Q(
                        user=request.user,
                        added__month=datetime.now().month,
                        added__year=datetime.now().year,
                    )
                    q |= Q(
                        touser=request.user,
                        added__month=datetime.now().month,
                        added__year=datetime.now().year,
                    )
                    orders_list = Order.objects.filter().order_by("-added")
                else:
                    if (
                        request.user.is_superuser
                        or request.user.username == "ibtissemdz"
                        or request.user.username == "liliumdz"
                        or request.user.userprofile.speciality_rolee in ["Office"]
                    ):
                        orders_list = Order.objects.all().order_by("-added")
                    else:
                        q = Q(
                            user=request.user,
                            added__month=datetime.now().month,
                            added__year=datetime.now().year,
                        )
                        q |= Q(user__in=request.user.userprofile.usersunder.all())
                        orders_list = (
                            Order.objects.filter(q).distinct().order_by("-added")
                        )

            if request.GET.get("status") and request.GET.get("status") != "":
                orders_list = orders_list.filter(status=request.GET.get("status"))

            paginator = Paginator(orders_list, 3)
            page = (
                request.GET.get("page")
                if request.GET.get("page") and request.GET.get("page") != "0"
                else None
            )
            orders = paginator.get_page(page)

            serializer = OrderSerializer(orders, many=True)

            return Response(
                self.pagination_response(orders, serializer, len(orders_list)),
                status=200,
            )
        else:
            order = Order.objects.get(id=id)
            if order.status == "en cours":
                order.status = "traite"
                order.done_date = datetime.today().date()

            if order.status == "confirmed":
                order.status = "en cours"

            if order.status == "initial":
                order.status = "confirmed"
                order.validation_date = datetime.today().date()

            order.save()

            return Response(OrderSerializer(order).data, status=200)

    def put(self, request, id="", format=None):
        if id == "":
            print(request.data)
            items_raw = request.data.get("items")
            ph = request.data.get("pharmacy")
            gro = request.data.get("gros")
            supgro = request.data.get("super_gros")
            print(items_raw)
            #print(date())
            print(date.today())
            try:
                ord = Order.objects.get(added__date=date.today(),user=request.user, pharmacy=ph,gros=gro,super_gros=supgro)
                print("exist deja un bon de commande avec les meme ph, supgro, gro")
                message = {"error": "Un bon de commande existe déjà pour cette pharmacie, ce grossiste et ce super grossiste aujourd’hui."}
                return Response(
                    message["error"],
                    status=status.HTTP_400_BAD_REQUEST)
            except ObjectDoesNotExist:
                print("pas de bon de commande ")
            except MultipleObjectsReturned:
                # Plusieurs bons trouvés → renvoyer un message clair
                message = {"error": "Un bon de commande existe déjà pour cette pharmacie, ce grossiste et ce super grossiste aujourd’hui."}
                return Response(
                    message["error"],
                    status=status.HTTP_400_BAD_REQUEST)
            if not items_raw:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            # Convertir la chaîne JSON en liste Python
            items = json.loads(items_raw) if items_raw else []
            # Vérifier s’il existe un item avec qtt == "0"
            has_zero_qtt = any(str(item.get("qtt")) == "0" for item in items)
            if has_zero_qtt:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            serializer = OrderSerializer(
                data=request.data, instance=Order(user=request.user), partial=True
            )
            if serializer.is_valid():
                produits_data = json.loads(request.data.get("items"))
                order = serializer.save()
                # for p in produits_data:
                #     p['order']=order.id

                produits_data = list(
                    map(lambda p: {**p, "order": order.id}, produits_data)
                )
                pserializer = OrderItemSerializer(data=produits_data, many=True)
                if pserializer.is_valid():
                    pserializer.save()
                    return Response(
                        OrderSerializer(order, many=False).data,
                        status=status.HTTP_201_CREATED,
                    )
                else:
                    print(pserializer.errors)
                    return Response(
                        pserializer.errors, status=status.HTTP_400_BAD_REQUEST
                    )
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            print("######### IM HERE UPDATING BC")
            # order_obj = self.get_object(id)
            # serializer = OrderSerializer(
            #     data=request.data, instance=order_obj, partial=True
            # )
            # if serializer.is_valid():
            #     OrderItem.objects.filter(order=order_obj).delete()
            #     produits_data = json.loads(request.data.get("items"))
            #     order = serializer.save()
            #     produits_data = list(
            #         map(lambda p: {**p, "order": order.id}, produits_data)
            #     )
            #     pserializer = OrderItemSerializer(data=produits_data, many=True)
            #     if pserializer.is_valid():
            #         pserializer.save()
            #         return Response(
            #             OrderSerializer(order, many=False).data,
            #             status=status.HTTP_201_CREATED,
            #         )
            #     else:
            #         print(pserializer.errors)
            #         return Response(
            #             pserializer.errors, status=status.HTTP_400_BAD_REQUEST
            #         )
            # print(serializer.errors)
            # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response(status=status.HTTP_400_BAD_REQUEST)


class OrderFrontWebAPI(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            raise Http404

    def post(self, request, id):
        order_obj = self.get_object(id)
        serializer = OrderSerializer(
            data=request.data, instance=order_obj, partial=True
        )
        if serializer.is_valid():
            OrderItem.objects.filter(order=order_obj).delete()
            produits_data = request.data.get("items")
            order = serializer.save()
            produits_data = list(map(lambda p: {**p, "order": order.id}, produits_data))
            pserializer = OrderItemSerializer(data=produits_data, many=True)
            if pserializer.is_valid():
                pserializer.save()
                return Response(
                    OrderSerializer(order, many=False).data,
                    status=status.HTTP_201_CREATED,
                )
            else:
                print(pserializer.errors)
                return Response(pserializer.errors, status=status.HTTP_400_BAD_REQUEST)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderHTML(TemplateView):
    def get(self, request, id):
        return render(request, "orders/pdf.html", {"order": Order.objects.get(id=id)})


class OrderPDF(LoginRequiredMixin, TemplateView):
    template_name = "orders/pdf"

    def get(self, request, id):
        rendered = render_to_string(
            "orders/pdf.html", {"order": Order.objects.get(id=id)}
        )
        htmldoc = HTML(string=rendered, base_url="http://app.liliumpharma.com")
        return HttpResponse(htmldoc.write_pdf(), content_type="application/pdf")


class ExitOrderAppAPI(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return ExitOrder.objects.get(pk=pk)
        except ExitOrder.DoesNotExist:
            raise Http404

    def pagination_response(self, exit_orders, json, result_length):
        response = {
            "pages": exit_orders.paginator.num_pages,
            "result": {"orders": json.data},
            "length": result_length,
        }
        try:
            response["previous"] = exit_orders.previous_page_number()
        except:
            pass
        try:
            response["next"] = exit_orders.next_page_number()
        except:
            pass
        return response

    def get(self, request, id=""):
        if id == "":
            exit_orders_list = ExitOrder.objects.filter(
                user=request.user,
                added__month=datetime.now().month,
                added__year=datetime.now().year,
            ).order_by("-added")

            if (
                request.user.userprofile.rolee not in ["Superviseur", "CountryManager"]
                and request.user.is_superuser != True
                and request.user.username not in ["ibtissemdz", "liliumdz"]
            ):
                exit_orders_list = ExitOrder.objects.filter(
                    user=request.user,
                    added__month=datetime.now().month,
                    added__year=datetime.now().year,
                ).order_by("-added")
            else:
                if (
                    request.user.is_superuser
                    or request.user.username
                    in [
                        "ibtissemdz",
                        "liliumdz",
                    ]
                    or request.user.userprofile.speciality_rolee in ["Office"]
                ):
                    exit_orders_list = ExitOrder.objects.all().order_by("-added")
                else:
                    q = Q(
                        user=request.user,
                        added__month=datetime.now().month,
                        added__year=datetime.now().year,
                    )
                    q |= Q(user__in=request.user.userprofile.usersunder.all())
                    exit_orders_list = (
                        ExitOrder.objects.filter(q).distinct().order_by("-added")
                    )

            paginator = Paginator(exit_orders_list, 3)
            page = (
                request.GET.get("page")
                if request.GET.get("page") and request.GET.get("page") != "0"
                else None
            )
            exit_orders = paginator.get_page(page)

            serializer = ExitOrderSerializer(exit_orders, many=True)

            return Response(
                self.pagination_response(
                    exit_orders, serializer, len(exit_orders_list)
                ),
                status=200,
            )
        else:
            order = ExitOrder.objects.get(id=id)
            order.status = "initial" if order.status == "traite" else "traite"
            order.save()
            return Response(ExitOrderSerializer(order).data, status=200)

    def post(self, request, id="", format=None):
        if id == "":
            serializer = ExitOrderSerializer(
                data=request.data, instance=ExitOrder(user=request.user), partial=True
            )
            if serializer.is_valid():
                produits_data = request.data.get("items")
                exit_order = serializer.save()
                # for p in produits_data:
                #     p['order']=order.id
                produits_data = list(
                    map(lambda p: {**p, "order": exit_order.id}, produits_data)
                )
                pserializer = ExitOrderItemSerializer(data=produits_data, many=True)
                if pserializer.is_valid():
                    pserializer.save()
                    return Response(
                        {
                            "id": exit_order.id,
                            "observation": exit_order.observation,
                            "items": produits_data,
                        },
                        status=status.HTTP_201_CREATED,
                    )
                else:
                    return Response(
                        pserializer.errors, status=status.HTTP_400_BAD_REQUEST
                    )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            exit_order_obj = self.get_object(id)
            serializer = ExitOrderSerializer(
                data=request.data, instance=exit_order_obj, partial=True
            )
            if serializer.is_valid():
                ExitOrderItem.objects.filter(order=exit_order_obj).delete()
                produits_data = request.data.get("items")
                exit_order = serializer.save()
                produits_data = list(
                    map(lambda p: {**p, "order": exit_order.id}, produits_data)
                )
                pserializer = ExitOrderItemSerializer(data=produits_data, many=True)
                if pserializer.is_valid():
                    pserializer.save()
                    return Response(
                        {
                            "id": exit_order.id,
                            "observation": exit_order.observation,
                            "items": produits_data,
                        },
                        status=status.HTTP_201_CREATED,
                    )
                else:
                    return Response(
                        pserializer.errors, status=status.HTTP_400_BAD_REQUEST
                    )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ExitOrderPDF(TemplateView):
    template_name = "orders/pdf"

    def get(self, request, id):
        rendered = render_to_string(
            "orders/exit_pdf.html", {"order": ExitOrder.objects.get(id=id)}
        )
        # htmldoc = HTML(string=rendered, base_url="http://app.liliumpharma.com")
        # return HttpResponse(htmldoc.write_pdf(), content_type='application/pdf')
        return render(
            request, "orders/exit_pdf.html", {"order": ExitOrder.objects.get(id=id)}
        )


from datetime import date, datetime
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated


class OrderSupervisor(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def apply_filters(self, request):
        """Apply filters based on query parameters."""
        filters = {}

        if request.GET.get("min_date"):
            filters["added__date__gte"] = request.GET.get("min_date")

        if request.GET.get("max_date"):
            filters["added__date__lte"] = request.GET.get("max_date")

        if request.GET.get("produit"):
            filters["orderitem__produit__id"] = request.GET.get("produit")

        if request.GET.get("status"):
            filters["status__in"] = request.GET.get("status").split(",")

        if request.GET.get("user"):
            filters["user__username__in"] = request.GET.get("user").split(",")

        if request.GET.get("source"):
            sources = {
                "Pharmacie": "pharmacy__isnull",
                "Gros": "gros__isnull",
                "Supergros": "super_gros__isnull",
            }
            filters[sources[request.GET.get("source")]] = False

        if request.GET.get("client"):
            clients = {
                "Pharmacie": "pharmacy__isnull",
                "Gros": "gros__isnull",
                "Supergros": "super_gros__isnull",
            }
            filters[clients[request.GET.get("client")]] = False

        return filters

    def apply_keyword_filter(self, request):
        """Apply keyword search filters."""
        q = Q()
        keyword = request.GET.get("keyword")

        if keyword:
            q |= Q(pharmacy__nom__icontains=keyword)
            q |= Q(gros__nom__icontains=keyword)
            q |= Q(super_gros__name__icontains=keyword)

        return q

    def get_filtered_orders(self, request, filters, q):
        """Return filtered and sorted order list based on user roles and conditions."""
        orders = Order.objects.filter(**filters).filter(q).order_by("-added")

        # Additional filters
        if request.GET.get("office") == "1":
            orders = orders.filter(from_company=True)

        if request.GET.get("attente") == "1":
            orders = orders.filter(flag=True)

        if request.GET.get("flag") == "1":
            orders = orders.exclude(status="traite")

        # Apply role-based filtering
        if (
            request.user.userprofile.rolee not in ["Superviseur", "CountryManager"]
            and not request.user.is_superuser
            and request.user.username not in ["liliumdz"]
            and request.user.userprofile.speciality_rolee not in ["Office"]
        ):
            orders = orders.filter(
                Q(user=request.user)
                | Q(touser=request.user)
                | Q(user__username__in=["MeriemDZ", "ibtissemdz"])
            ).distinct()

        elif (
            request.user.userprofile.rolee == "Superviseur"
            and request.user.userprofile.speciality_rolee
            not in ["Superviseur_national"]
        ):
            orders = orders.filter(
                Q(user=request.user)
                | Q(user__in=request.user.userprofile.usersunder.all())
                | Q(touser=request.user)
                | Q(touser__in=request.user.userprofile.usersunder.all())
                | Q(user__username__in=["MeriemDZ", "ibtissemdz"])
            ).distinct()

        elif request.user.userprofile.speciality_rolee in [
            "Office"
        ] or request.user.username in [
            "ibtissemdz",
            "RABTIDZ",
            "a.lounis@liliumpharma.com",
        ]:
            orders = orders.all()

        if request.user.userprofile.speciality_rolee in ["Superviseur_national"]:
            users = User.objects.filter(userprofile__work_as_commercial=True)
            orders = orders.filter(
                Q(user=request.user)
                | Q(user__in=users)
                | Q(touser=request.user)
                | Q(touser__in=users)
                | Q(user__in=request.user.userprofile.usersunder.all())
                | Q(user__username__in=["MeriemDZ", "ibtissemdz"])
            ).distinct()

        return orders

    def get(self, request, id=""):
        if id == "":
            filters = self.apply_filters(request)
            q = self.apply_keyword_filter(request)

            orders_list = self.get_filtered_orders(request, filters, q)
            serializer = OrderSerializer(orders_list, many=True)

            return Response(serializer.data, status=200)
        else:
            order = Order.objects.get(id=id)

            if order.status == "en cours":
                order.status = "traite"
                order.done_date = date.today()

            if order.status == "confirme":
                if request.GET.get("bl"):
                    order.bl = request.GET.get("bl")
                order.status = "en cours"

            if order.status == "initial":
                order.status = "confirme"
                order.validation_date = date.today()

            order.save()
            return Response(OrderSerializer(order).data, status=200)

    def post(self, request, id="", format=None):
        order_obj = self.get_object(id)

        # Serialize and validate the order data
        serializer = OrderSerializer(
            data=request.data, instance=order_obj, partial=True
        )

        if serializer.is_valid():
            # Delete existing order items linked to this order
            OrderItem.objects.filter(order=order_obj).delete()

            # Prepare and serialize order items data
            produits_data = request.data.get("items", [])
            for produit in produits_data:
                produit["order"] = order_obj.id  # Attach the order ID to each product

            order = serializer.save()
            pserializer = OrderItemSerializer(data=produits_data, many=True)

            if pserializer.is_valid():
                pserializer.save()

                # Construct the response data
                response_data = {
                    "id": order.id,
                    "observation": order.observation,
                    "items": produits_data,
                    "medecin": {
                        "id": order.client.id,
                        "nom": order.client.nom,
                        "specialite": order.client.specialite,
                        "classification": order.client.classification,
                        "telephone": order.client.telephone,
                    },
                    "commune": order.client.commune.nom,
                }

                return Response(response_data, status=status.HTTP_201_CREATED)
            else:
                # Handle product serializer errors
                return Response(pserializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Handle order serializer errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def MsOrders(request):

    if request.user.is_authenticated:
        token = Token.objects.filter(user=request.user)

        if token.exists():
            token = token.first().key
        else:
            Token.objects.create(user=request.user)
            token = Token.objects.filter(user=request.user)
            token = token.first().key

    return render(
        request,
        "micro_frontends/orders_front/index.html",
        {"token": token if request.user.is_authenticated else ""},
    )


class ExitOrderSupervisor(APIView):

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, id=""):

        filters = {}
        if request.GET.get("min_date") and request.GET.get("min_date") != "":
            filters["added__date__gte"] = request.GET.get("min_date")

        if request.GET.get("max_date") and request.GET.get("max_date") != "":
            filters["added__date__lte"] = request.GET.get("max_date")
        if request.GET.get("produit") and request.GET.get("produit") != "":
            filters["exit_orderitem__produit__id"] = request.GET.get("produit")

        if request.GET.get("status") and request.GET.get("status") != "":
            filters["status__in"] = request.GET.get("status").split(",")
        if request.GET.get("depot") and request.GET.get("depot") != "":
            filters["depot__in"] = request.GET.get("depot").split(",")
        if request.GET.get("user") and request.GET.get("user") != "":
            filters["user__username__in"] = request.GET.get("user").split(",")

        if id == "":
            if (
                request.user.userprofile.rolee not in ["Superviseur", "CountryManager"]
                and request.user.is_superuser != True
                and request.user.username not in ["liliumdz"]
                and request.user.userprofile.speciality_rolee not in ["Office"]
            ):
                exit_orders_list = ExitOrder.objects.filter(
                    user=request.user,
                    added__month=datetime.now().month,
                    added__year=datetime.now().year,
                ).order_by("-added")
            else:
                if (
                    request.user.is_superuser
                    or request.user.userprofile.speciality_rolee
                    in ["Office", "CountryManager"]
                    or request.user.username
                    in ["ibtissemdz", "RABTIDZ", "a.lounis@liliumpharma.com"]
                ):
                    print("im superuser")
                    q = Q()

                    if q:
                        exit_orders_list = (
                            ExitOrder.objects.filter(**filters)
                            .filter(q)
                            .order_by("-added")
                        )
                    else:
                        exit_orders_list = ExitOrder.objects.filter(**filters).order_by(
                            "-added"
                        )

                else:
                    q = Q(
                        user=request.user,
                        added__month=datetime.now().month,
                        added__year=datetime.now().year,
                    )
                    q |= Q(user__in=request.user.userprofile.usersunder.all())
                    exit_orders_list = (
                        ExitOrder.objects.filter(q, **filters)
                        .distinct()
                        .order_by("-added")
                    )

            serializer = ExitOrderSerializer(exit_orders_list, many=True)

            return Response(serializer.data, status=200)
        else:
            exit_order = ExitOrder.objects.get(id=id)

            if exit_order.status == "confirme":
                exit_order.status = "traite"
                exit_order.done_date = datetime.today().date()

            if exit_order.status == "initial":
                exit_order.status = "confirme"
                exit_order.user_confirmed = request.user
                exit_order.validation_date = datetime.today().date()

            exit_order.save()

            return Response(ExitOrderSerializer(exit_order).data, status=200)

    def post(self, request, id="", format=None):

        exit_order_obj = self.get_object(id)
        serializer = ExitOrderSerializer(
            data=request.data, instance=exit_order_obj, partial=True
        )
        if serializer.is_valid():
            ExitOrderItem.objects.filter(exit_order=exit_order_obj).delete()
            produits_data = request.data.get("items")
            exit_order = serializer.save()
            produits_data = list(
                map(lambda p: {**p, "exit_order": exit_order.id}, produits_data)
            )
            pserializer = ExitOrderItemSerializer(data=produits_data, many=True)
            if pserializer.is_valid():
                pserializer.save()
                return Response(
                    {
                        "id": exit_order.id,
                        "observation": exit_order.observation,
                        "items": produits_data,
                        "commune": exit_order.client.commune.nom,
                    },
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response(pserializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def MsExitOrders(request):

    if request.user.is_authenticated:
        token = Token.objects.filter(user=request.user)

        if token.exists():
            token = token.first().key
        else:
            Token.objects.create(user=request.user)
            token = Token.objects.filter(user=request.user)
            token = token.first().key

    return render(
        request,
        "micro_frontends/exit_orders_front/index.html",
        {"token": token if request.user.is_authenticated else ""},
    )


class ShareUser(APIView):

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            raise Http404

    def get_user(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404

    def get(self, request, id):
        touser = self.get_user(request.GET.get("user"))
        Order.objects.filter(id=id).update(
            transfer_date=date.today(), touser=touser, status="en cours"
        )
        instance = self.get_object(id)
        notification = Notification.objects.create(
            title=f"Transfert Bon de commande  {instance.user.username}",
            description=f"{str(instance.added)}",
            data={
                "name": "Orders",
                "title": "Bon de commande",
                "message": f"Transfert Bon de commande de {instance.user.username} a {touser.username}",
                "confirm_text": "voir le bon",
                "cancel_text": "plus tard",
                "StackName": "Orders",
                "url": f"https://app.liliumpharma.com/orders/front/?user={instance.user.username}&date={instance.added.date()}",
                "navigate_to": json.dumps(
                    {
                        "screen": "List",
                        "params": {
                            "user": instance.user.username,
                            "date": str(instance.added.date()),
                        },
                    },
                    ensure_ascii=False,
                ),
            },
        )
        notification.users.set(
            [
                touser,
            ]
        )
        # notification.send()
        return Response(status=200)


from datetime import *
from django.db.models import Q


class ordersPerUserPerMonth(APIView):

    authentication_classes = (
        TokenAuthentication,
        SessionAuthentication,
    )
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user_param = request.GET.get("user")
        if user_param:
            user = User.objects.filter(username=user_param).first()
        else:
            user = request.user
        # user=request.user

        #year = date.today().year
        year = int(request.GET.get("year"))
        month_param = request.GET.get("month")
        try:
            month = int(month_param)
            tz = datetime.now().tzinfo  # Get the current time zone

            if 1 <= month <= 12:
                date_debut_mois = datetime(
                    year, month, 1, 0, 0, 0, 0, tzinfo=tz
                )
                if month == 12:
                    date_fin_mois = datetime(
                        year + 1, 1, 1, 0, 0, 0, 0, tzinfo=tz
                    )
                else:
                    date_fin_mois = datetime(
                        year, month + 1, 1, 0, 0, 0, 0, tzinfo=tz
                    )
            else:
                return Response(
                    {"error": "Mois invalide. Utilisez une valeur entre 1 et 12."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except (ValueError, TypeError):
            return Response(
                {
                    "error": "Mois invalide. Utilisez une valeur numérique entre 1 et 12."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        orders = Order.objects.filter(
            user=user, added__range=[date_debut_mois, date_fin_mois], added__year=year
        )

        data = {
            "total_orders": orders.count(),
            "orders": [],
            "transfered_orders": [],
            "transfered_orders_2": [],
            "product_summary": {},  # Ajout d'un dictionnaire pour stocker le résumé des quantités de produits
        }
        transfered_orders = Order.objects.filter(
            touser=user, added__range=[date_debut_mois, date_fin_mois], added__year=year
        )
        transfered_orders_2 = Order.objects.filter(
            Q(user=user)
            & Q(added__range=[date_debut_mois, date_fin_mois])
            & ~Q(touser=None)
        )
        for order in orders:
            order_data = {
                "order_id": order.id,
                "status": order.status,
                "date": order.added.strftime("%Y-%m-%d"),
                "products": [],
                "pharmacy": order.pharmacy.nom if order.pharmacy else "-",
                "gros": order.gros.nom if order.gros else "-",
                "super_gros": order.super_gros.name if order.super_gros else "-",
            }

            order_items = OrderItem.objects.filter(order=order)

            for item in order_items:
                product_data = {
                    "product_name": item.produit.nom,
                    "quantity": item.qtt,
                }
                order_data["products"].append(product_data)

                # Mise à jour du résumé des quantités de produits
                product_name = item.produit.nom
                if product_name in data["product_summary"]:
                    data["product_summary"][product_name] += item.qtt

            data["orders"].append(order_data)

        for order in transfered_orders:
            order_data_transfered = {
                "user": str(order.user),
                "order_id": order.id,
                "status": order.status,
                "date": order.added.strftime("%Y-%m-%d"),
                "products": [],
                "pharmacy": order.pharmacy.nom if order.pharmacy else "-",
                "gros": order.gros.nom if order.gros else "-",
                "super_gros": order.super_gros.name if order.super_gros else "-",
            }

            order_items = OrderItem.objects.filter(order=order)
            for item in order_items:
                product_data = {
                    "product_name": item.produit.nom,
                    "quantity": item.qtt,
                }
                order_data_transfered["products"].append(product_data)

                # Mise à jour du résumé des quantités de produits
                product_name = item.produit.nom
                if product_name in data["product_summary"]:
                    data["product_summary"][product_name] += item.qtt
                else:
                    data["product_summary"][product_name] = item.qtt

            data["transfered_orders"].append(order_data_transfered)

        for order in transfered_orders_2:
            order_data_transfered_2 = {
                "user": str(order.user),
                "order_id": order.id,
                "status": order.status,
                "date": order.added.strftime("%Y-%m-%d"),
                "products": [],
                "to_user": order.touser.username,
                "pharmacy": order.pharmacy.nom if order.pharmacy else "-",
                "gros": order.gros.nom if order.gros else "-",
                "super_gros": order.super_gros.name if order.super_gros else "-",
            }

            order_items = OrderItem.objects.filter(order=order)
            for item in order_items:
                product_data = {
                    "product_name": item.produit.nom,
                    "quantity": item.qtt,
                }
                order_data_transfered_2["products"].append(product_data)

                # Mise à jour du résumé des quantités de produits
                product_name = item.produit.nom
                if product_name in data["product_summary"]:
                    data["product_summary"][product_name] += item.qtt
                else:
                    data["product_summary"][product_name] = item.qtt

            data["transfered_orders_2"].append(order_data_transfered_2)

        return Response(data)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from .models import Order, OrderItem  # Assurez-vous d'importer vos modèles
from datetime import datetime
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import User, Order, OrderItem
from .serializers import OrderSerializer
from datetime import datetime

class OrdersByUserAndDateView(APIView):

    def get(self, request, username, order_date):
        try:
            # Vérification du format du nom d'utilisateur
            name_parts = username.split()
            if len(name_parts) != 2:
                return Response({"error": "Invalid username format"}, status=400)
            first_name, last_name = name_parts

            # Filtrer l'utilisateur basé sur le prénom et nom de famille
            user = User.objects.get(first_name=first_name, last_name=last_name)

            # Convertir la date fournie dans l'URL au format de date Python
            try:
                order_date = datetime.strptime(order_date, '%Y-%m-%d').date()
            except ValueError:
                return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

            # Filtrer les commandes de cet utilisateur dans la plage de dates donnée
            orders = Order.objects.filter(user=user, added__date=order_date)

            # Utiliser le serializer pour convertir les commandes en JSON
            orders_data = OrderSerializer(orders, many=True).data

            # Comptage des commandes pour pharmacie et gros
            orders_with_pharmacy_and_gros = orders.filter(pharmacy__isnull=False, gros__isnull=False)
            count_orders_with_pharmacy_and_gros = orders_with_pharmacy_and_gros.count()

            product_qty_pharmacy_and_gros = {}
            for order in orders_with_pharmacy_and_gros:
                order_items = OrderItem.objects.filter(order=order)
                for item in order_items:
                    product_name = item.produit.nom
                    qty = item.qtt

                    if product_name in product_qty_pharmacy_and_gros:
                        product_qty_pharmacy_and_gros[product_name] += qty
                    else:
                        product_qty_pharmacy_and_gros[product_name] = qty

            # Comptage des commandes pour gros et super gros
            orders_with_gros_and_super_gros = orders.filter(gros__isnull=False, super_gros__isnull=False)
            count_orders_with_gros_and_super_gros = orders_with_gros_and_super_gros.count()

            product_qty_gros_and_super_gros = {}
            for order in orders_with_gros_and_super_gros:
                order_items = OrderItem.objects.filter(order=order)
                for item in order_items:
                    product_name = item.produit.nom
                    qty = item.qtt

                    if product_name in product_qty_gros_and_super_gros:
                        product_qty_gros_and_super_gros[product_name] += qty
                    else:
                        product_qty_gros_and_super_gros[product_name] = qty

            # Création d'un ensemble de produits uniques
            all_products = set(product_qty_pharmacy_and_gros.keys()).union(product_qty_gros_and_super_gros.keys())
            unique_products = list(all_products)

            # Préparation des données à envoyer dans la réponse
            context = {
                "orders_with_pharmacy_and_gros": orders_data,
                "orders_with_gros_and_super_gros": orders_data,
                "product_qty_pharmacy_and_gros": product_qty_pharmacy_and_gros,
                "product_qty_gros_and_super_gros": product_qty_gros_and_super_gros,
                "unique_products": unique_products,
                "count_orders_with_pharmacy_and_gros": count_orders_with_pharmacy_and_gros,
                "count_orders_with_gros_and_super_gros": count_orders_with_gros_and_super_gros,
            }
            print(str(context))

            return Response(context, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=404)

from collections import defaultdict
from datetime import datetime, date, timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from django.db.models import Q

import calendar as _calendar
from clients.models import (
    Client,
    OrderSource as _OrderSource,
    Order as _ClientOrder,
    OrderProduct as _ClientOrderProduct,
)
from medecins.models import Medecin
from .models import Order, OrderItem


class TransactionTrackerAPI(APIView):
    """
    API Endpoint for the Visual Organigram Dashboard, Tables & User Charts.
    """

    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        entity_type = request.GET.get("type", "").lower()
        entity_id = request.GET.get("id")
        min_date = request.GET.get("min_date")
        max_date = request.GET.get("max_date")

        if not entity_type or not entity_id:
            return Response({"error": "Paramètres 'type' et 'id' requis."}, status=400)

        def parse_date(d_str, default_date):
            if d_str:
                try:
                    return datetime.strptime(d_str, "%Y-%m-%d").date()
                except Exception:
                    pass
            return default_date

        today = date.today()
        d_max = parse_date(max_date, today)
        d_min = parse_date(min_date, today - timedelta(days=30))

        if d_min > d_max:
            d_min, d_max = d_max, d_min

        clients_agg = defaultdict(
            lambda: {
                "bons": set(),
                "unites": 0,
                "valeur": 0.0,
                "produits": defaultdict(int),
                "orders_details": [],
            }
        )
        fournisseurs_agg = defaultdict(
            lambda: {
                "bons": set(),
                "unites": 0,
                "valeur": 0.0,
                "produits": defaultdict(int),
                "orders_details": [],
            }
        )

        # New dicts for the User Charts
        user_stats_ventes = defaultdict(
            lambda: {"bons": set(), "unites": 0, "valeur": 0.0}
        )
        user_stats_achats = defaultdict(
            lambda: {"bons": set(), "unites": 0, "valeur": 0.0}
        )

        root_stats = {"bons": set(), "unites": 0, "valeur": 0.0, "valeur_brute": 0.0}
        root_name = ""

        region = request.GET.get("region")

        orders_qs = Order.objects.filter(added__date__gte=d_min, added__date__lte=d_max)

        # ── User scoping ──
        try:
            _req_up = request.user.userprofile
            _req_spec = getattr(_req_up, "speciality_rolee", "")
        except Exception:
            _req_up = None
            _req_spec = ""

        _TRACKER_RESTRICTED = {"Commercial", "Medico_commercial"}
        _TRACKER_FULL = {"CountryManager", "Admin"}

        if not request.user.is_superuser and _req_spec not in _TRACKER_FULL:
            if _req_spec in _TRACKER_RESTRICTED:
                orders_qs = orders_qs.filter(
                    Q(user=request.user) | Q(touser=request.user)
                ).distinct()
            elif _req_spec == "Superviseur_national" and _req_up is not None:
                orders_qs = orders_qs.filter(
                    Q(user=request.user)
                    | Q(touser=request.user)
                    | Q(user__in=_req_up.usersunder.all())
                    | Q(touser__in=_req_up.usersunder.all())
                ).distinct()
        # ────────────────────────────────────────────────────────────────────────────

        # ── ALL SUPERGROS RANKING BLOCK (before region filter — sees all regions) ──
        if entity_type == "supergros" and entity_id == "ALL":
            orders = orders_qs.filter(super_gros__isnull=False).filter(Q(gros__isnull=False) | Q(pharmacy__isnull=False)).select_related("super_gros", "user", "user__userprofile")

            order_map = {o.id: o for o in orders}
            order_ids = list(order_map.keys())
            items = OrderItem.objects.filter(order_id__in=order_ids).select_related("produit")

            sg_stats = {}
            for it in items:
                o = order_map[it.order_id]
                sg_id = o.super_gros_id

                if sg_id not in sg_stats:
                    sg_stats[sg_id] = {
                        "name": o.super_gros.name if o.super_gros else "Inconnu",
                        "total_val": 0.0,
                        "regions": {"Ouest": 0.0, "Centre": 0.0, "Est": 0.0, "Sud": 0.0, "Vide": 0.0},
                        "regions_bons": {"Ouest": set(), "Centre": set(), "Est": set(), "Sud": set(), "Vide": set()},
                        "regions_unites": {"Ouest": 0, "Centre": 0, "Est": 0, "Sud": 0, "Vide": 0},
                    }

                val = float(it.qtt or 0) * float(it.produit.price or 0)
                qtt = int(it.qtt or 0)

                try:
                    reg = o.user.userprofile.region if getattr(o, "user", None) and hasattr(o.user, "userprofile") else None
                except Exception:
                    reg = None

                reg_key = reg if reg in ["Ouest", "Centre", "Est", "Sud"] else "Vide"
                sg_stats[sg_id]["total_val"] += val
                sg_stats[sg_id]["regions"][reg_key] += val
                sg_stats[sg_id]["regions_bons"][reg_key].add(o.id)
                sg_stats[sg_id]["regions_unites"][reg_key] += qtt

            for s in sg_stats.values():
                s["regions_bons"] = {k: len(v) for k, v in s["regions_bons"].items()}

            if region:
                target_reg = region if region in ["Ouest", "Centre", "Est", "Sud"] else "Vide"
                sorted_sg = sorted(
                    [s for s in sg_stats.values() if s["regions"].get(target_reg, 0) > 0],
                    key=lambda x: x["regions"].get(target_reg, 0),
                    reverse=True
                )
            else:
                sorted_sg = sorted(
                    [s for s in sg_stats.values() if s["total_val"] > 0],
                    key=lambda x: x["total_val"],
                    reverse=True
                )

            return Response({"type": "ALL_SUPERGROS", "data": sorted_sg})
        # ────────────────────────────────────────────────────────────────────────────

        # ── ALL GROSSISTES RANKING BLOCK ──
        elif entity_type == "grossiste" and entity_id == "ALL":
            # Grossiste is the fournisseur when there is a Pharmacy attached
            orders = orders_qs.filter(
                gros__isnull=False, pharmacy__isnull=False
            ).select_related("gros", "user", "user__userprofile")

            order_map = {o.id: o for o in orders}
            order_ids = list(order_map.keys())
            items = OrderItem.objects.filter(order_id__in=order_ids).select_related(
                "produit"
            )

            g_stats = {}
            for it in items:
                o = order_map[it.order_id]
                g_id = o.gros_id

                if g_id not in g_stats:
                    g_stats[g_id] = {
                        "name": o.gros.nom if o.gros else "Inconnu",
                        "total_val": 0.0,
                        "regions": {"Ouest": 0.0, "Centre": 0.0, "Est": 0.0, "Sud": 0.0, "Vide": 0.0},
                        "regions_bons": {"Ouest": set(), "Centre": set(), "Est": set(), "Sud": set(), "Vide": set()},
                        "regions_unites": {"Ouest": 0, "Centre": 0, "Est": 0, "Sud": 0, "Vide": 0},
                    }

                val = float(it.qtt or 0) * float(it.produit.price or 0)
                qtt = int(it.qtt or 0)

                try:
                    reg = (
                        o.user.userprofile.region
                        if getattr(o, "user", None) and hasattr(o.user, "userprofile")
                        else None
                    )
                except Exception:
                    reg = None

                reg_key = reg if reg in ["Ouest", "Centre", "Est", "Sud"] else "Vide"
                g_stats[g_id]["total_val"] += val
                g_stats[g_id]["regions"][reg_key] += val
                g_stats[g_id]["regions_bons"][reg_key].add(o.id)
                g_stats[g_id]["regions_unites"][reg_key] += qtt

            for s in g_stats.values():
                s["regions_bons"] = {k: len(v) for k, v in s["regions_bons"].items()}

            if region:
                target_reg = (
                    region if region in ["Ouest", "Centre", "Est", "Sud"] else "Vide"
                )
                sorted_g = sorted(
                    [
                        s
                        for s in g_stats.values()
                        if s["regions"].get(target_reg, 0) > 0
                    ],
                    key=lambda x: x["regions"].get(target_reg, 0),
                    reverse=True,
                )
            else:
                sorted_g = sorted(
                    [s for s in g_stats.values() if s["total_val"] > 0],
                    key=lambda x: x["total_val"],
                    reverse=True,
                )

            return Response({"type": "ALL_GROSSISTES", "data": sorted_g})
        # ─────────────────────────────────────────────────────────

        if region:
            orders_qs = orders_qs.filter(user__userprofile__region=region)

        regional_stats = {
            "Centre": {"bons": set(), "unites": 0, "valeur": 0.0},
            "Est": {"bons": set(), "unites": 0, "valeur": 0.0},
            "Ouest": {"bons": set(), "unites": 0, "valeur": 0.0},
            "Sud": {"bons": set(), "unites": 0, "valeur": 0.0},
        }

        if entity_type == "supergros":
            try:
                sg = Client.objects.get(id=entity_id, supergro=True)
                root_name = sg.name
            except Client.DoesNotExist:
                return Response({"error": "SuperGros introuvable."}, status=404)

            orders = (
                orders_qs.filter(super_gros_id=entity_id)
                .filter(Q(gros__isnull=False) | Q(pharmacy__isnull=False))
                .select_related("pharmacy", "gros", "user", "super_gros", "user__userprofile")
            )

            order_map = {o.id: o for o in orders}
            order_ids = list(order_map.keys())
            items = OrderItem.objects.filter(order_id__in=order_ids).select_related(
                "produit"
            )

            order_stats = defaultdict(lambda: {"qty": 0, "val": 0.0})
            order_items_map = defaultdict(list)
            order_brute_map = defaultdict(float)

            for it in items:
                it.order = order_map[it.order_id]
                qty = it.qtt or 0
                val = float(qty) * float(it.produit.price or 0)

                order_stats[it.order_id]["qty"] += qty
                order_stats[it.order_id]["val"] += val
                order_items_map[it.order_id].append(it)
                order_brute_map[it.order_id] += float(it.line_total_ttc)

            for o in orders:
                qty = order_stats[o.id]["qty"]
                val = order_stats[o.id]["val"]
                val_brute = order_brute_map[o.id]

                root_stats["bons"].add(o.id)
                root_stats["unites"] += qty
                root_stats["valeur"] += val
                root_stats["valeur_brute"] += val_brute

                try:
                    reg = o.user.userprofile.region if getattr(o, "user", None) and hasattr(o.user, "userprofile") else None
                except Exception:
                    reg = None

                if reg in regional_stats:
                    regional_stats[reg]["bons"].add(o.id)
                    regional_stats[reg]["unites"] += qty
                    regional_stats[reg]["valeur"] += val

                # Track User Ventes (SuperGros selling outwards)
                uname = (
                    getattr(o.user, "username", "Inconnu")
                    if getattr(o, "user", None)
                    else "Inconnu"
                )
                user_stats_ventes[uname]["bons"].add(o.id)
                user_stats_ventes[uname]["unites"] += qty
                user_stats_ventes[uname]["valeur"] += val_brute

                if o.gros_id and o.gros:
                    key = (o.gros_id, "Grossiste", getattr(o.gros, "nom", "Inconnu"))
                elif o.pharmacy_id and o.pharmacy:
                    key = (
                        o.pharmacy_id,
                        "Pharmacie",
                        getattr(o.pharmacy, "nom", "Inconnu"),
                    )
                else:
                    continue

                clients_agg[key]["bons"].add(o.id)
                clients_agg[key]["unites"] += qty
                clients_agg[key]["valeur"] += val

                o_prods = []
                for it in order_items_map[o.id]:
                    clients_agg[key]["produits"][it.produit.nom] += it.qtt or 0
                    if it.qtt and it.qtt > 0:
                        o_prods.append(f"{it.qtt} {it.produit.nom}")

                clients_agg[key]["orders_details"].append(
                    {
                        "id": o.id,
                        "date": o.added.strftime("%Y-%m-%d"),
                        "user": uname,
                        "valeur_brute": round(val_brute, 2),
                        "produits_str": " , ".join(o_prods) if o_prods else "-",
                    }
                )

        elif entity_type == "grossiste":
            try:
                gr = Medecin.objects.get(id=entity_id, specialite="Grossiste")
                root_name = gr.nom
            except Medecin.DoesNotExist:
                return Response({"error": "Grossiste introuvable."}, status=404)

            orders = orders_qs.filter(gros_id=entity_id).select_related(
                "pharmacy", "super_gros", "user", "gros", "user__userprofile"
            )

            order_map = {o.id: o for o in orders}
            order_ids = list(order_map.keys())
            items = OrderItem.objects.filter(order_id__in=order_ids).select_related(
                "produit"
            )

            order_stats = defaultdict(lambda: {"qty": 0, "val": 0.0})
            order_items_map = defaultdict(list)
            order_brute_map = defaultdict(float)
            root_stats_in = {"bons": set(), "unites": 0, "valeur": 0.0}
            root_stats_out = {"bons": set(), "unites": 0, "valeur": 0.0}

            for it in items:
                it.order = order_map[it.order_id]
                qty = it.qtt or 0
                val = float(qty) * float(it.produit.price or 0)

                order_stats[it.order_id]["qty"] += qty
                order_stats[it.order_id]["val"] += val
                order_items_map[it.order_id].append(it)
                order_brute_map[it.order_id] += float(it.line_total_ttc)

            for o in orders:
                qty = order_stats[o.id]["qty"]
                val = order_stats[o.id]["val"]
                val_brute = order_brute_map[o.id]

                root_stats["bons"].add(o.id)
                root_stats["unites"] += qty
                root_stats["valeur"] += val

                try:
                    reg = o.user.userprofile.region if getattr(o, "user", None) and hasattr(o.user, "userprofile") else None
                except Exception:
                    reg = None

                if reg in regional_stats:
                    regional_stats[reg]["bons"].add(o.id)
                    regional_stats[reg]["unites"] += qty
                    regional_stats[reg]["valeur"] += val

                uname = (
                    getattr(o.user, "username", "Inconnu")
                    if getattr(o, "user", None)
                    else "Inconnu"
                )

                if o.super_gros_id and o.super_gros:
                    # Track incoming stats
                    root_stats_in["bons"].add(o.id)
                    root_stats_in["unites"] += qty
                    root_stats_in["valeur"] += val
                    # User Achats (Grossiste buying from SuperGros)
                    user_stats_achats[uname]["bons"].add(o.id)
                    user_stats_achats[uname]["unites"] += qty
                    user_stats_achats[uname]["valeur"] += val_brute

                    key = (
                        o.super_gros_id,
                        "SuperGros",
                        getattr(o.super_gros, "name", "Inconnu"),
                    )
                    fournisseurs_agg[key]["bons"].add(o.id)
                    fournisseurs_agg[key]["unites"] += qty
                    fournisseurs_agg[key]["valeur"] += val

                    o_prods = []
                    for it in order_items_map[o.id]:
                        fournisseurs_agg[key]["produits"][it.produit.nom] += it.qtt or 0
                        if it.qtt and it.qtt > 0:
                            o_prods.append(f"{it.qtt} {it.produit.nom}")

                    fournisseurs_agg[key]["orders_details"].append(
                        {
                            "id": o.id,
                            "date": o.added.strftime("%Y-%m-%d"),
                            "user": uname,
                            "valeur_brute": round(val_brute, 2),
                            "produits_str": " , ".join(o_prods) if o_prods else "-",
                        }
                    )

                if o.pharmacy_id and o.pharmacy:
                    # Track outgoing stats
                    root_stats_out["bons"].add(o.id)
                    root_stats_out["unites"] += qty
                    root_stats_out["valeur"] += val
                    # User Ventes (Grossiste selling to Pharmacie)
                    user_stats_ventes[uname]["bons"].add(o.id)
                    user_stats_ventes[uname]["unites"] += qty
                    user_stats_ventes[uname]["valeur"] += val_brute

                    key = (
                        o.pharmacy_id,
                        "Pharmacie",
                        getattr(o.pharmacy, "nom", "Inconnu"),
                    )
                    clients_agg[key]["bons"].add(o.id)
                    clients_agg[key]["unites"] += qty
                    clients_agg[key]["valeur"] += val

                    o_prods = []
                    for it in order_items_map[o.id]:
                        clients_agg[key]["produits"][it.produit.nom] += it.qtt or 0
                        if it.qtt and it.qtt > 0:
                            o_prods.append(f"{it.qtt} {it.produit.nom}")

                    clients_agg[key]["orders_details"].append(
                        {
                            "id": o.id,
                            "date": o.added.strftime("%Y-%m-%d"),
                            "user": uname,
                            "valeur_brute": round(val_brute, 2),
                            "produits_str": " , ".join(o_prods) if o_prods else "-",
                        }
                    )

        else:
            return Response({"error": "Type invalide."}, status=400)

        def format_nodes(agg_dict):
            res = []
            for (nid, ntype, nname), stats in agg_dict.items():
                prod_list = [f"{q} {n}" for n, q in stats["produits"].items() if q > 0]
                prod_str = " , ".join(prod_list) if prod_list else "-"
                sorted_orders = sorted(
                    stats["orders_details"], key=lambda x: x["id"], reverse=True
                )
                res.append(
                    {
                        "id": nid,
                        "name": nname,
                        "type": ntype,
                        "stats": {
                            "bons": len(stats["bons"]),
                            "unites": stats["unites"],
                            "valeur": round(stats["valeur"], 2),
                            "produits_str": prod_str,
                            "orders_details": sorted_orders,
                        },
                    }
                )
            res.sort(
                key=lambda x: (
                    (
                        1
                        if x["type"] == "SuperGros"
                        else (2 if x["type"] == "Grossiste" else 3)
                    ),
                    -x["stats"]["valeur"],
                )
            )
            return res

        def format_user_stats(stats_dict):
            res = [
                {
                    "username": u,
                    "bons": len(s["bons"]),
                    "unites": s["unites"],
                    "valeur": round(s["valeur"], 2),
                }
                for u, s in stats_dict.items()
            ]
            res.sort(key=lambda x: x["valeur"], reverse=True)
            return res

        payload = {
            "period": {
                "min_date": d_min.strftime("%Y-%m-%d"),
                "max_date": d_max.strftime("%Y-%m-%d"),
            },
            "root": {
                "id": int(entity_id),
                "name": root_name,
                "type": "SuperGros" if entity_type == "supergros" else "Grossiste",
                "stats": {
                    "bons": len(root_stats["bons"]),
                    "unites": root_stats["unites"],
                    "valeur": round(root_stats["valeur"], 2),
                },
            },
            "fournisseurs": format_nodes(fournisseurs_agg),
            "clients": format_nodes(clients_agg),
            "user_stats_ventes": format_user_stats(user_stats_ventes),
            "user_stats_achats": format_user_stats(user_stats_achats),
        }

        payload["regional_stats"] = {
            r: {
                "bons": len(d["bons"]),
                "unites": d["unites"],
                "valeur": round(d["valeur"], 2)
            } for r, d in regional_stats.items()
        }

        if entity_type == "grossiste":
            payload["root"]["stats_in"] = {
                "bons": len(root_stats_in["bons"]),
                "unites": root_stats_in["unites"],
                "valeur": round(root_stats_in["valeur"], 2),
            }
            payload["root"]["stats_out"] = {
                "bons": len(root_stats_out["bons"]),
                "unites": root_stats_out["unites"],
                "valeur": round(root_stats_out["valeur"], 2),
            }

        # ── Real Sales Coverage (SuperGros + full calendar month only) ──
        payload["real_sales_data"] = None
        if entity_type == "supergros":
            if (
                d_min.day == 1
                and d_min.year == d_max.year
                and d_min.month == d_max.month
            ):
                last_day = _calendar.monthrange(d_min.year, d_min.month)[1]
                if d_max.day == last_day:
                    # Note: Added .order_by('-id') here just in case of multiple uploads!
                    os_obj = (
                        _OrderSource.objects.filter(
                            source_id=entity_id,
                            date__year=d_min.year,
                            date__month=d_min.month,
                        )
                        .order_by("-id")
                        .first()
                    )

                    if os_obj is not None:
                        # 1. Grab the Client's Wilaya and Region
                        ops = _ClientOrderProduct.objects.filter(
                            order__source=os_obj
                        ).select_related("produit", "order__client__wilaya__region")

                        real_units = 0
                        real_val = 0

                        regions_data = {
                            "Centre": {"units": 0, "val": 0, "coverage": 0},
                            "Est": {"units": 0, "val": 0, "coverage": 0},
                            "Ouest": {"units": 0, "val": 0, "coverage": 0},
                            "Sud": {"units": 0, "val": 0, "coverage": 0},
                        }

                        for op in ops:
                            qty = op.qtt or 0
                            val = (
                                float(qty) * float(op.produit.price or 0) * 1.19 * 1.15
                            )

                            real_units += qty
                            real_val += val

                            # 2. Extract Region from the Client's Wilaya!
                            # 2. Extract Region directly from Wilaya Name (Bypassing DB Region Table)
                            try:
                                wilaya_obj = op.order.client.wilaya

                                if wilaya_obj and wilaya_obj.nom:
                                    # Force lowercase, remove dashes, and strip spaces
                                    w_nom = (
                                        str(wilaya_obj.nom)
                                        .lower()
                                        .replace("-", " ")
                                        .strip()
                                    )

                                    # --- MASTER MAPPING DICTIONARY ---
                                    centre = [
                                        "alger",
                                        "blida",
                                        "boumerdes",
                                        "tipaza",
                                        "tizi ouzou",
                                        "bejaia",
                                        "bouira",
                                        "medea",
                                        "chlef",
                                        "ain defla",
                                    ]

                                    est = [
                                        "setif",
                                        "constantine",
                                        "batna",
                                        "annaba",
                                        "skikda",
                                        "jijel",
                                        "mila",
                                        "oum el bouaghi",
                                        "tebessa",
                                        "guelma",
                                        "khenchela",
                                        "souk ahras",
                                        "bordj bou arreridj",
                                        "el tarf",
                                        "msila",
                                        "m'sila",
                                    ]

                                    ouest = [
                                        "oran",
                                        "tlemcen",
                                        "sidi bel abbes",
                                        "mostaganem",
                                        "mascara",
                                        "relizane",
                                        "tiaret",
                                        "saida",
                                        "ain temouchent",
                                        "tissemsilt",
                                    ]

                                    sud = [
                                        "ouargla",
                                        "biskra",
                                        "el oued",
                                        "ghardaia",
                                        "laghouat",
                                        "djelfa",
                                        "bechar",
                                        "adrar",
                                        "tamanrasset",
                                        "illizi",
                                        "tindouf",
                                        "el bayadh",
                                        "naama",
                                        "touggourt",
                                        "el meniaa",
                                        "ouled djellal",
                                        "beni abbes",
                                        "in salah",
                                        "in guezzam",
                                        "djanet",
                                        "bordj badji mokhtar",
                                    ]

                                    # Match the wilaya to its region
                                    if w_nom in centre:
                                        reg = "Centre"
                                    elif w_nom in est:
                                        reg = "Est"
                                    elif w_nom in ouest:
                                        reg = "Ouest"
                                    elif w_nom in sud:
                                        reg = "Sud"
                                    else:
                                        reg = None
                                else:
                                    reg = None
                            except Exception:
                                reg = None
                            if reg in regions_data:
                                regions_data[reg]["units"] += qty
                                regions_data[reg]["val"] += val

                        # Calculate National Coverage
                        total_order_brute = root_stats.get("valeur_brute", 0)
                        coverage_pct = (
                            round((total_order_brute / real_val) * 100, 1)
                            if real_val > 0
                            else 0
                        )

                        # 3. Calculate Regional Coverage
                        for reg in regions_data:
                            # regional_stats['valeur'] is HT. We must multiply by taxes to match the SuperGros TTC!
                            lilium_reg_val_ht = regional_stats.get(reg, {}).get(
                                "valeur", 0
                            )
                            lilium_reg_val_ttc = lilium_reg_val_ht * 1.19 * 1.15

                            reg_real_val = regions_data[reg]["val"]

                            if reg_real_val > 0:
                                regions_data[reg]["coverage"] = round(
                                    (lilium_reg_val_ttc / reg_real_val) * 100, 1
                                )

                        # Attach to payload
                        payload["real_sales_data"] = {
                            "real_sales_val": round(real_val, 2),
                            "real_sales_units": real_units,
                            "coverage_percentage": coverage_pct,
                            "sg_name": root_name,
                            "regions": regions_data,
                        }
        # ────────────────────────────────────────────────────────────────

        return Response(payload)


import json as _json
from django.contrib.auth.decorators import login_required as _login_required


@_login_required
def transaction_tracker_front(request):
    """
    Renders the supply-chain transaction tracker organigram page.

    Passes pre-loaded entity lists as JSON so the template avoids
    an extra authenticated round-trip for the filter dropdowns.

    Context variables:
      super_gros_json  – JSON array of {id, name} for SuperGros entities
      grossistes_json  – JSON array of {id, name} for Grossiste entities
    """
    from clients.models import Client
    from medecins.models import Medecin

    super_gros_list = list(
        Client.objects.filter(supergro=True).values("id", "name").order_by("name")
    )
    grossiste_list = list(
        Medecin.objects.filter(specialite="Grossiste")
        .values("id", "nom")
        .order_by("nom")
    )
    # Normalise field name to "name" for the template
    grossiste_list = [{"id": g["id"], "name": g["nom"]} for g in grossiste_list]

    return render(
        request,
        "orders/tracking.html",
        {
            "super_gros_json": _json.dumps(super_gros_list),
            "grossistes_json": _json.dumps(grossiste_list),
        },
    )


@_login_required
def orders_stats_view(request):
    import json as _json2
    from clients.models import Client as _Client

    try:
        _up = request.user.userprofile
        _spec = getattr(_up, "speciality_rolee", "")
    except Exception:
        _up = None
        _spec = ""

    _RESTRICTED = {"Commercial", "Medico_commercial"}
    _FULL_ACCESS = {"CountryManager", "Admin"}

    _ALLOWED_ROLES = {"Commercial", "Medico_commercial", "Superviseur_national", "Superviseur", "Superviseur_regional", "CountryManager"}

    if request.user.is_superuser or _spec in _FULL_ACCESS:
        users = UserProfile.objects.filter(is_human=True, user__is_active=True, speciality_rolee__in=_ALLOWED_ROLES).select_related("user").order_by("user__username")
        is_restricted = False
    elif _spec == "Superviseur_national" and _up is not None:
        users = UserProfile.objects.filter(
            Q(user=request.user) | Q(user__in=_up.usersunder.all()),
            is_human=True, user__is_active=True, speciality_rolee__in=_ALLOWED_ROLES,
        ).select_related("user").order_by("user__username")
        is_restricted = False
    elif _spec in _RESTRICTED and _up is not None:
        users = UserProfile.objects.filter(user=request.user, is_human=True, user__is_active=True, speciality_rolee__in=_ALLOWED_ROLES).select_related("user")
        is_restricted = True
    else:
        users = UserProfile.objects.filter(is_human=True, user__is_active=True, speciality_rolee__in=_ALLOWED_ROLES).select_related("user").order_by("user__username")
        is_restricted = False

    from medecins.models import Medecin as _Medecin
    super_gros = list(_Client.objects.filter(supergro=True).values("id", "name").order_by("name"))
    grossistes = [
        {"id": g["id"], "name": g["nom"]}
        for g in _Medecin.objects.filter(specialite="Grossiste").values("id", "nom").order_by("nom")
    ]
    users_list = [{"value": up.user.username, "label": up.user.username, "region": up.region or "", "role": up.speciality_rolee or ""} for up in users]
    restricted_user = users_list[0] if is_restricted and users_list else None

    produits = list(Produit.objects.values('id', 'nom', 'line').order_by('nom'))
    lignes = list(Produit.objects.exclude(line__isnull=True).exclude(line__exact='').values_list('line', flat=True).distinct().order_by('line'))

    return render(request, "orders/stats_dashboard.html", {
        "users_json": _json2.dumps(users_list),
        "restricted_user": _json2.dumps(restricted_user),
        "super_gros_json": _json2.dumps(super_gros),
        "grossistes_json": _json2.dumps(grossistes),
        "produits_json": _json2.dumps(produits),
        "lignes_json": _json2.dumps(lignes),
        "is_restricted": is_restricted,
    })


class ProductStatsView(TemplateView):
    template_name = "orders/product_stats.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query_string'] = self.request.GET.urlencode()
        return context

class ProductStatsDataAPI(APIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        min_date = request.GET.get('min_date')
        max_date = request.GET.get('max_date')
        produit_id = request.GET.get('produit')
        ligne = request.GET.get('ligne')
        region = request.GET.get('region')

        # select_related profond pour la Wilaya
        # NOTE: The hardcoded order__status__in filter was removed to match the 
        # export_excel.py behavior which pulls all orders in the date range.
        items = OrderItem.objects.select_related(
            'order',
            'order__user',
            'order__user__userprofile',
            'produit',
            'order__pharmacy__commune__wilaya',
            'order__gros__commune__wilaya',
            'order__super_gros'
        )

        if min_date:
            items = items.filter(order__added__date__gte=min_date)
        if max_date:
            items = items.filter(order__added__date__lte=max_date)
        if produit_id:
            items = items.filter(produit_id=produit_id)
        if ligne:
            items = items.filter(produit__line=ligne)
        if region:
            items = items.filter(order__user__userprofile__region=region)

        raw_data = []
        for item in items:
            o = item.order
            p = item.produit

            # 1. EXACT FIELD-BASED LOGIC FROM export_excel.py
            ph  = o.pharmacy_id is not None
            gro = o.gros_id is not None
            sg  = o.super_gros_id is not None

            if ph and gro:
                order_type = "PH_GROS"
            elif (ph and not gro and sg) or (not ph and gro and sg):
                order_type = "GROS_SUPER"
            else:
                # Skips OFFICE (not ph and not gro and sg) and anomalie
                continue

            # Mirror preview.html exclusion: skip LILIUM PHARMA ALG super-gros orders
            if o.super_gros and getattr(o.super_gros, 'name', None) == "LILIUM PHARMA ALG":
                continue

            # 2. DETERMINER LA WILAYA (Via le client direct)
            wilaya_nom = "Inconnue"
            if o.pharmacy and o.pharmacy.commune and o.pharmacy.commune.wilaya:
                wilaya_nom = o.pharmacy.commune.wilaya.nom
            elif o.gros and o.gros.commune and o.gros.commune.wilaya:
                wilaya_nom = o.gros.commune.wilaya.nom

            # 3. IDENTIFIER LE ROLE ET LA REGION
            try:
                role = o.user.userprofile.speciality_rolee
                user_region = o.user.userprofile.region
            except Exception:
                role = ""
                user_region = ""

            qty = item.qtt or 0
            val = float(qty) * float(p.price or 0)

            raw_data.append({
                "order_id": o.id,
                "month": "1", # Force single month for global period aggregation
                "user_id": o.user.id,
                "user_name": f"{o.user.first_name} {o.user.last_name}".strip() or o.user.username,
                "role": role,
                "region": user_region,
                "wilaya": wilaya_nom,
                "order_type": order_type,
                "product_id": p.id,
                "product_name": p.nom,
                "qty": qty,
                "value": val,
                "gros_name": o.gros.nom if o.gros else None,
                "gros_wilaya": (o.gros.commune.wilaya.nom if o.gros and o.gros.commune and o.gros.commune.wilaya else None),
                "super_gros_name": o.super_gros.name if o.super_gros else None,
                "from_company": o.from_company,
            })

        # Determine the target line for zero-order user detection
        target_line = None
        if produit_id:
            try:
                from produits.models import Produit as ProduitModel
                target_line = ProduitModel.objects.get(id=produit_id).line
            except Exception:
                pass
        elif ligne:
            target_line = ligne

        all_line_users = []
        if target_line:
            profiles = UserProfile.objects.select_related('user').filter(
                speciality_rolee__in=['Medico_commercial', 'Commercial', 'Superviseur_national']
            )
            for profile in profiles:
                user_lines = [l.strip() for l in (profile.lines or '').split(',') if l.strip()]
                if target_line in user_lines:
                    full_name = f"{profile.user.first_name} {profile.user.last_name}".strip() or profile.user.username
                    all_line_users.append({
                        'user_id': profile.user.id,
                        'user_name': full_name,
                        'role': profile.speciality_rolee,
                    })

        return JsonResponse({"raw_data": raw_data, "all_line_users": all_line_users})