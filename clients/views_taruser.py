from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from django.db.models import Exists, OuterRef

from rest_framework.views import APIView

from accounts.models import UserProfile
from produits.models import Produit
from .models import UserTargetMonth
from clients.api.functions import (
    get_target_per_user,
    get_target_all_users,
    get_target_for_supervisor,
)
from clients.functions import get_target_per_user_per_month
from liliumpharm.utils import month_number_to_french_name


def add_special_table_data(context):
    """Helper function to calculate special table totals if target products exist"""
    # Ordered list of special product names to display
    SPECIAL_PRODUCTS = ["ADVAGEN", "HAIRVOL", "GOLD MAG", "SLEEP ALAISE"]
    show_special_table = False

    target_data = context.get("data")

    # Helper to force any value (string, None, etc.) into a number safely
    def to_number(val):
        try:
            if isinstance(val, str):
                val = val.replace(',', '').replace(' ', '')
            return float(val) if val else 0
        except (ValueError, TypeError):
            return 0

    # Helper to extract quantity from objects used in the template lists
    def get_qty(item):
        if hasattr(item, 'total'):
            return to_number(item.total)
        elif isinstance(item, dict):
            return to_number(item.get('total', 0))
        return to_number(item)

    special_table_rows = []   # list of dicts, one per special product found
    total_unite = 0
    total_prix = 0
    total_target_unite = 0
    total_target_prix = 0

    if target_data and "products" in target_data:
        for i, product in enumerate(target_data["products"]):
            product_name = product.nom if hasattr(product, 'nom') else str(product)
            product_upper = product_name.upper()

            if product_upper in SPECIAL_PRODUCTS:
                show_special_table = True
                try:
                    # Use the same "Achevé (par unité)" source as the main table
                    acheve_item      = target_data.get("quantities", [])[i]
                    acheve_unite     = get_qty(acheve_item)
                    acheve_link      = acheve_item.get("target_report_details_link", "#") if isinstance(acheve_item, dict) else "#"

                    prix             = to_number(target_data.get("prices", [])[i])
                    objectif_unite   = to_number(target_data.get("targets", [])[i])

                    acheve_prix      = acheve_unite * prix
                    objectif_prix    = objectif_unite * prix

                    total_unite      += acheve_unite
                    total_prix       += acheve_prix
                    total_target_unite += objectif_unite
                    total_target_prix  += objectif_prix

                    special_table_rows.append({
                        "name":           product_name,
                        "target_unite":   int(objectif_unite),
                        "acheve_unite":   int(acheve_unite),
                        "acheve_link":    acheve_link,
                        "prix":           int(prix),
                        "target_prix":    int(objectif_prix),
                        "acheve_prix":    int(acheve_prix),
                    })
                except IndexError:
                    pass

        # Sort special_table_rows by acheve_unite decreasing
        special_table_rows.sort(key=lambda x: x["acheve_unite"], reverse=True)

        # Preserve back-compat fields used elsewhere in the template
        target_data["special_table_rows"]       = special_table_rows
        target_data["special_total_unite"]      = int(total_unite)
        target_data["special_total_prix"]       = int(total_prix)
        target_data["special_target_unite"]     = int(total_target_unite)
        target_data["special_target_prix"]      = int(total_target_prix)
        # Legacy fields (kept in case something else references them)
        target_data["total_unit_ph_gros"]       = 0
        target_data["total_unit_gros_super"]    = 0
        target_data["total_val_ph_gros"]        = 0
        target_data["total_val_gros_super"]     = 0
        target_data["montant_objectif_special"] = int(total_target_prix)

        # Sort Main Table Columns by acheve_unite (quantities) descending
        if "quantities" in target_data:
            quantities = target_data.get("quantities", [])
            products_list = list(target_data.get("products", []))

            if len(quantities) == len(products_list) and len(quantities) > 0:
                indices = list(range(len(quantities)))
                indices.sort(key=lambda i: get_qty(quantities[i]), reverse=True)

                def reorder(lst):
                    if lst is None:
                        return lst
                    lst_as_list = list(lst)
                    if len(lst_as_list) != len(quantities):
                        return lst
                    return [lst_as_list[i] for i in indices]

                keys_to_reorder = [
                    "products", "targets", "total_unite_product",
                    "total_unite_product_gros_super", "prices",
                    "quantities", "total_targets", "total_achievements",
                    "percentage_achievements"
                ]
                for key in keys_to_reorder:
                    if key in target_data:
                        target_data[key] = reorder(target_data[key])

    context["show_special_table"] = show_special_table
    return context


class taruser(APIView):

    def get(self, request):
        is_desktop = request.GET.get('view') == 'desktop'
        template_name = (
            "clients/taruser_desktop.html" if is_desktop else "clients/taruser.html"
        )

        print(str(request))
        print("sesssionnnnnnnnnnnn")
        print(request.session.items())
        print("user_id dans sessionnnnnnnnn")

        if request.user.is_authenticated:
            user_id = request.user.id
            print("dans request web")
            print(user_id)
        else:
            user_id = request.session.get("user_id")
            print("dans la session")
            print(user_id)

        produits = Produit.objects.all()

        if UserProfile.objects.get(user=user_id).speciality_rolee in [
            "Medico_commercial",
            "Commercial",
        ]:
            user_profiles = User.objects.filter(id=user_id)
            # 3. UPDATED: Render the dynamic template_name
            return render(
                request, template_name, {"users": user_profiles, "num_id": 33, "produits": produits}
            )

        elif (
            UserProfile.objects.get(user=user_id).speciality_rolee == "CountryManager"
            or UserProfile.objects.get(user=user_id).speciality_rolee == "Admin"
            or UserProfile.objects.get(user=user_id).speciality_rolee == "Office"
        ):
            user_profiles = User.objects.filter(
                userprofile__speciality_rolee__in=[
                    "Medico_commercial",
                    "Superviseur_national",
                    "Superviseur_regional",
                    "CountryManager",
                    "Commercial",
                ],
                userprofile__hidden=False,
            ).filter(Exists(UserTargetMonth.objects.filter(user=OuterRef("pk"))))
            # 3. UPDATED: Render the dynamic template_name
            return render(request, template_name, {"users": user_profiles, "num_id": 1, "produits": produits})

        elif (
            UserProfile.objects.get(user=user_id).speciality_rolee
            == "Superviseur_regional"
            or UserProfile.objects.get(user=user_id).speciality_rolee
            == "Superviseur_national"
        ):
            user_profiles = UserProfile.objects.get(user=user_id)
            user_profiles = user_profiles.usersunder.all()
            ur = User.objects.get(id=user_id)
            nam = ur.first_name + " " + ur.last_name
            # 3. UPDATED: Render the dynamic template_name
            return render(
                request,
                template_name,
                {"users": user_profiles, "num_id": 2, "name": nam, "produits": produits},
            )
        else:
            pass

        # 3. UPDATED: Render the dynamic template_name
        return render(request, template_name, {"produits": produits})

    def post(self, request):
        is_desktop = request.GET.get('view') == 'desktop'

        if request.user.is_authenticated:
            user_id = request.user.id
            print("dans request web")
        else:
            user_id = request.session.get("user_id")
            print("dans la session")

        request_params = request.GET
        e = request.POST.get("users")
        if e:
            selected_user = int(request.POST.get("users"))
        else:
            selected_user = "passssssss"

        if selected_user == 0 and UserProfile.objects.get(
            user=user_id
        ).speciality_rolee in ["Superviseur_regional"]:
            print("SuperViseur Regional")
            year = int(request.POST.get("years"))
            month = int(request.POST.get("months"))
            mo = month_number_to_french_name(month)
            year = int(request.POST.get("years"))
            months = request.POST.getlist("months")
            for i in months:
                mo = month_number_to_french_name(int(i))
            params = {}
            if year:
                params["years"] = year
            if month:
                params["months"] = months
            params["user_id"] = user_id
            context = {"month": mo, "year": year}
            data = get_target_for_supervisor(**params)
            context["data"] = data
            return render(
                request,
                template_name="clients/reports/target_report_per_user.html",
                context=context,
            )

        elif (
            selected_user != 0
            and selected_user != "passssssss"
            and UserProfile.objects.get(user=selected_user).speciality_rolee
            in ["Superviseur_regional", "CountryManager"]
        ):
            t = UserProfile.objects.get(user=selected_user)
            print("SuperViseur Regional or CountryManager")
            year = int(request.POST.get("years"))
            months = request.POST.getlist("months")
            m = []
            for i in months:
                mo = month_number_to_french_name(int(i))
                m.append(mo)

            year = [int(request.POST.get("years"))]
            month = months = request.POST.getlist("months")

            params = {}
            if year:
                params["years"] = year
            if month:
                params["months"] = months
            params["user_id"] = selected_user
            context = {"month": m, "year": year}
            data = get_target_for_supervisor(**params)
            context["data"] = data

            # 5. NEW LOGIC: Only run heavy special table processing if it's a desktop
            if is_desktop:
                context = add_special_table_data(context)

            return render(
                request,
                template_name="clients/reports/target_report_per_user.html",
                context=context,
            )

        year = int(request.POST.get("years"))
        months = request.POST.getlist("months")
        year = request.POST.getlist("years")
        q = []
        m = []
        if len(months) == 1:
            month = int(months[0])
        else:
            for i in months:
                mo = month_number_to_french_name(int(i))
                q.append(int(i))
                m.append(mo)
            month = q

        user = request.POST.get("users")
        if user:
            user = int(user)

        params = {}
        year = [int(request.POST.get("years"))]
        month = [int(request.POST.get("months"))]
        if year:
            params["years"] = year

        if month:
            params["months"] = month
        french_month = ()
        if "client_wilaya_id" in request_params:
            params["wilaya"] = request_params.get("client_wilaya_id")
        if len(months) == 1:
            french_month = (
                month_number_to_french_name(params["months"][0])
                if "months" in params
                else "Tous les Mois"
            )

        year = params["years"] if "years" in params else "Toutes les Années"
        context = {"month": french_month, "year": year}

        if user == 0:
            data = get_target_all_users(**params)
            context["data"] = data
            return render(
                request,
                template_name="clients/reports/target_report_all_users.html",
                context=context,
            )

        if user:
            params["user_id"] = user
        else:
            params["user_id"] = user_id

        if len(months) == 1:
            data = get_target_per_user(**params)
            context["data"] = data

            # 5. NEW LOGIC: Only run heavy special table processing if it's a desktop
            if is_desktop:
                context = add_special_table_data(context)

            return render(
                request,
                template_name="clients/reports/target_report_per_user.html",
                context=context,
            )
        else:
            french_month = q
            months = request.POST.getlist("months")
            params["months"] = months
            context = {"month": m, "year": year}
            data = get_target_per_user_per_month(**params)
            context["data"] = data

            # 5. NEW LOGIC: Only run heavy special table processing if it's a desktop
            if is_desktop:
                context = add_special_table_data(context)

            per_month_sections = []
            for single_month in months:
                single_params = dict(params)
                single_params["months"] = [single_month]
                single_data = get_target_per_user(**single_params)
                single_french_month = month_number_to_french_name(int(single_month))
                single_ctx = {"data": single_data}

                # 5. NEW LOGIC: Only run heavy special table processing if it's a desktop
                if is_desktop:
                    single_ctx = add_special_table_data(single_ctx)

                per_month_sections.append(
                    {
                        "month": single_french_month,
                        "data": single_ctx["data"],
                        "show_special_table": single_ctx.get(
                            "show_special_table", False
                        ),
                    }
                )
            context["per_month_sections"] = per_month_sections

            return render(
                request,
                template_name="clients/reports/target_report_per_user.html",
                context=context,
            )


class DashboardDataAPI(APIView):
    """
    Invisible JSON endpoint strictly for the Desktop AJAX dashboard.
    Mobile app never sees or uses this.
    """

    # Roles that are allowed to see the full dashboard
    _ALLOWED_ROLES = {
        "CountryManager",
        "Admin",
        "Office",
        "Superviseur_national",
        "Superviseur_regional",
    }

    def get(self, request):
        # --- Access control ---
        if request.user.is_authenticated:
            user_id = request.user.id
        else:
            user_id = request.session.get("user_id")

        if not user_id:
            return JsonResponse({"error": "Non authentifié."}, status=401)

        try:
            profile = UserProfile.objects.get(user=user_id)
        except UserProfile.DoesNotExist:
            return JsonResponse({"error": "Profil introuvable."}, status=403)

        if profile.speciality_rolee not in self._ALLOWED_ROLES:
            return JsonResponse(
                {"error": "Accès refusé. Rôle insuffisant."}, status=403
            )

        # --- Parameter parsing ---
        year = request.GET.get("year")
        months = request.GET.getlist("months[]")
        if not months:
            months = request.GET.getlist("months")

        params = {}
        if year:
            params["years"] = [int(year)]

        if months:
            params["months"] = [int(m) for m in months]
        else:
            # "No months selected" means "Tous les mois" — pass all 12 explicitly
            # so the backend never silently defaults to the current month only.
            params["months"] = list(range(1, 13))

        # Product filtering is now handled client-side using product_breakdown;
        # the server always returns the full dataset so the cache stays generic.
        # (Keep parsing product_id so old bookmarked URLs don't 400.)
        product_id = request.GET.get("product") or None  # noqa – client-side only

        # --- Cache key: year + sorted months (product is filtered in JS) ---
        _year_key   = params.get("years",  [0])[0]
        _months_key = sorted(params.get("months", []))
        cache_key   = "dashboard_v2_{}_{}".format(
            _year_key, "_".join(str(m) for m in _months_key)
        )

        cached_data = cache.get(cache_key)
        if cached_data:
            return JsonResponse(cached_data)

        # Cache miss → run the heavy computation
        raw_data = get_target_all_users(**params)

        cards_data = []
        meriem_total_target = 0
        meriem_total_achieved = 0

        # 2. Loop directly through the clean list
        for item in raw_data:
            role = item.get("role", "")
            target_val = item.get("raw_target", 0.0)
            achieved_val = item.get("raw_achieved", 0.0)
            personal_perc = item.get("percentage_reached", 0.0)

            # Capture BOTH the target and the achieved values for the Boss
            if role == "CountryManager":
                meriem_total_target = target_val
                meriem_total_achieved = achieved_val

            # Skip fully empty cards (0 target, 0 achieved) unless they are supervisors/boss
            if (
                target_val > 0
                or achieved_val > 0
                or role
                in ["CountryManager", "Superviseur_national", "Superviseur_regional"]
            ):
                cards_data.append(
                    {
                        "id": item.get("user_id"),
                        "name": item.get("user"),
                        "role": role,
                        "family": item.get("family", "N/A"),
                        "region": item.get("region", "N/A"),
                        "work_as_commercial": item.get("work_as_commercial", False),
                        "product_breakdown": item.get("product_breakdown", []),
                        "target_total": target_val,
                        "achieved_total": achieved_val,
                        "personal_percentage": personal_perc,
                    }
                )

        # 3. Calculate % of Global Target AND % of Global Achieved
        for card in cards_data:
            # Existing: % of the Global Target
            global_perc = (
                (card["achieved_total"] / meriem_total_target * 100)
                if meriem_total_target > 0
                else 0
            )
            card["global_percentage"] = round(global_perc, 2)

            # NEW: % of the Global Achieved (Company CA Poids)
            global_achieved_perc = (
                (card["achieved_total"] / meriem_total_achieved * 100)
                if meriem_total_achieved > 0
                else 0
            )
            card["global_achieved_percentage"] = round(global_achieved_perc, 2)

        final_dict = {"meriem_total_target": meriem_total_target, "users": cards_data}
        cache.set(cache_key, final_dict, 600)   # 10-minute TTL
        return JsonResponse(final_dict)


class VisualisationVenteView(APIView):
    """
    Renders the Data Visualisation page.
    The query-string parameters (?year=…&months[]=…&user=…&…) are passed
    through to the template so the JS initFilters() function can hydrate
    the filter bar on page load without an extra round-trip.
    """

    def get(self, request):
        produits = Produit.objects.all()
        context = {
            "produits": produits,
            # Pass raw query string so the template can embed it in a JS variable
            "query_string": request.GET.urlencode(),
        }
        return render(request, "clients/visualisation_vente.html", context)


class VisualisationDataAPI(APIView):
    """
    JSON endpoint that returns all 5 chart datasets for the Visualisation page.

    GET params (mirrors DashboardDataAPI):
        year        – int
        months[]    – list[int]
        user        – str  (user full-name filter, maps to UserProfile lookup)
        family      – str
        region      – str
        role        – str
        perf        – str  (ignored at data level; kept for cache key parity)
        produit     – int  (Produit.id)

    Response (cached 10 min):
        {
          "graph_medical":    [...],
          "graph_commercial": [...],
          "graph_wilayas":    [...],
          "graph_products":   [...],
          "graph_supergros":  [...],
        }
    """

    # Same role guard as DashboardDataAPI
    _ALLOWED_ROLES = {
        "CountryManager",
        "Admin",
        "Office",
        "Superviseur_national",
        "Superviseur_regional",
    }

    def get(self, request):
        from clients.api.functions import get_visualisation_data

        # ── Auth ──────────────────────────────────────────────────────────────
        if request.user.is_authenticated:
            user_id = request.user.id
        else:
            user_id = request.session.get("user_id")

        if not user_id:
            return JsonResponse({"error": "Non authentifié."}, status=401)

        try:
            profile = UserProfile.objects.get(user=user_id)
        except UserProfile.DoesNotExist:
            return JsonResponse({"error": "Profil introuvable."}, status=403)

        if profile.speciality_rolee not in self._ALLOWED_ROLES:
            return JsonResponse(
                {"error": "Accès refusé. Rôle insuffisant."}, status=403
            )

        # ── Parameter parsing ──────────────────────────────────────────────────
        year   = request.GET.get("year")
        months = request.GET.getlist("months[]") or request.GET.getlist("months")

        params = {}
        if year:
            params["years"] = [int(year)]
        if months:
            params["months"] = [int(m) for m in months]
        else:
            params["months"] = list(range(1, 13))

        # ── Cache ──────────────────────────────────────────────────────────────
        _year_key   = params.get("years",  [0])[0]
        _months_key = sorted(params.get("months", []))
        
        cache_key = "vis_raw_v1_{}_{}_usr{}".format(
            _year_key,
            "_".join(str(m) for m in _months_key),
            user_id
        )

        cached = cache.get(cache_key)
        if cached:
            return JsonResponse(cached)

        # ── Compute ────────────────────────────────────────────────────────────
        try:
            data = get_visualisation_data(params, request_user=user_id)
        except Exception as exc:
            return JsonResponse({"error": str(exc)}, status=500)

        cache.set(cache_key, data, 600)   # 10-minute TTL (matches DashboardDataAPI)
        return JsonResponse(data)
