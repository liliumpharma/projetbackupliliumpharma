from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from django.db.models import Exists, OuterRef

from rest_framework.views import APIView

from accounts.models import UserProfile
from produits.models import Produit
from .models import UserTargetMonth, BISnapshot
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
        # --- Authentication & Role Checks ---
        if request.user.is_authenticated:
            user_id = request.user.id
        else:
            user_id = request.session.get("user_id")

        if not user_id: return JsonResponse({"error": "Non authentifié."}, status=401)
        try:
            profile = UserProfile.objects.get(user=user_id)
        except UserProfile.DoesNotExist:
            return JsonResponse({"error": "Profil introuvable."}, status=403)
        if profile.speciality_rolee not in self._ALLOWED_ROLES:
            return JsonResponse({"error": "Accès refusé."}, status=403)

        # --- Parameter parsing ---
        year = request.GET.get("year")
        months = request.GET.getlist("months[]") or request.GET.getlist("months")

        years_filter = [int(year)] if year else []
        months_filter = [int(m) for m in months] if months else list(range(1, 13))

        # --- 0ms Database Read ---
        from .models import DashboardSnapshot
        snapshots = DashboardSnapshot.objects.filter(year__in=years_filter, month__in=months_filter)

        # Apply visibility rules for Supervisors
        if profile.speciality_rolee in ["Superviseur_regional", "Superviseur_national", "Superviseur"]:
            users_under_ids = list(profile.usersunder.all().values_list('user__id', flat=True))
            snapshots = snapshots.filter(user_id__in=users_under_ids)

        # --- Instant Python Aggregation ---
        users_map = {}
        meriem_total_target = 0.0
        meriem_total_achieved = 0.0

        for s in snapshots:
            uid = s.user_id
            if uid not in users_map:
                users_map[uid] = {
                    "id": uid, "name": s.user_name, "role": s.role,
                    "lines": s.lines or "",
                    "sector": s.sector_category or "N/A",
                    "region": s.region or "N/A",
                    "work_as_commercial": s.work_as_commercial,
                    "target_total": 0.0, "achieved_total": 0.0,
                    "product_breakdown_map": {}
                }
            
            u = users_map[uid]
            u["target_total"] += s.target_value
            u["achieved_total"] += s.achieved_value
            
            pid = s.product_id
            if pid != 0:
                if pid not in u["product_breakdown_map"]:
                    u["product_breakdown_map"][pid] = {
                        "product_id": pid, "product_name": s.product_name,
                        "target_value": 0.0, "achieved_value": 0.0
                    }
                u["product_breakdown_map"][pid]["target_value"] += s.target_value
                u["product_breakdown_map"][pid]["achieved_value"] += s.achieved_value

            if s.role == "CountryManager":
                meriem_total_target += s.target_value
                meriem_total_achieved += s.achieved_value

        # --- Final Formatting ---
        cards_data = []
        for u in users_map.values():
            u["product_breakdown"] = list(u["product_breakdown_map"].values())
            del u["product_breakdown_map"]
            
            # Percentages
            u["personal_percentage"] = round((u["achieved_total"] / u["target_total"] * 100), 2) if u["target_total"] > 0 else 0.0
            u["global_percentage"] = round((u["achieved_total"] / meriem_total_target * 100), 2) if meriem_total_target > 0 else 0.0
            u["global_achieved_percentage"] = round((u["achieved_total"] / meriem_total_achieved * 100), 2) if meriem_total_achieved > 0 else 0.0
            
            if u["target_total"] > 0 or u["achieved_total"] > 0 or u["role"] in ["CountryManager", "Superviseur_national", "Superviseur_regional"]:
                cards_data.append(u)

        # Also return raw targets so frontend can calculate per-month percentages
        dash_raw = list(snapshots.values("month", "user_id", "user_name", "product_id", "lines", "target_value"))

        return JsonResponse({
            "meriem_total_target": meriem_total_target,
            "users": cards_data,
            "dash_raw": dash_raw
        })


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
    JSON endpoint that returns the FLAT raw data for the Visualisation page.
    This now reads directly from the lightning-fast BISnapshot table.
    """

    _ALLOWED_ROLES = {
        "CountryManager",
        "Admin",
        "Office",
        "Superviseur_national",
        "Superviseur_regional",
    }

    def get(self, request):
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

        years_filter = [int(year)] if year else []
        months_filter = [int(m) for m in months] if months else list(range(1, 13))

        # ── Fetch from Flat Snapshot Table (0.05ms load time) ──────────────────
        snapshots = BISnapshot.objects.all()
        
        if years_filter:
            snapshots = snapshots.filter(year__in=years_filter)
        if months_filter:
            snapshots = snapshots.filter(month__in=months_filter)

        # Apply visibility rules for Supervisors
        users_under_ids = None
        if profile.speciality_rolee in ["Superviseur_regional", "Superviseur_national", "Superviseur"]:
            users_under_ids = list(profile.usersunder.all().values_list('user__id', flat=True))
            snapshots = snapshots.filter(user_id__in=users_under_ids)

        # Instantly dump the flat data to a list of dicts
        raw_data = list(snapshots.values(
            'month', 'user_id', 'user_name', 'role', 'lines',
            'sector_category',
            'region', 'wilaya', 'supergros_name',
            'product_id', 'product_name', 'qty', 'value'
        ))

        # Normalise key name so the frontend always reads 'sector'
        for row in raw_data:
            row['sector'] = row.pop('sector_category', 'IN')

        from .models import SupergrosSalesSnapshot
        sales_snaps = SupergrosSalesSnapshot.objects.all()
        if years_filter:
            sales_snaps = sales_snaps.filter(year__in=years_filter)
        if months_filter:
            sales_snaps = sales_snaps.filter(month__in=months_filter)

        raw_sales_data = list(sales_snaps.values(
            'month', 'wilaya', 'supergros_name', 'product_id', 'product_name', 'lines', 'qty', 'value'
        ))

        # ── Calculate Sector Costs (SEMI/DEP) dynamically ──
        from accounts.models import UserSectorDetail
        sector_costs = {}

        usd_qs = UserSectorDetail.objects.exclude(category='IN').prefetch_related('wilayas')

        if users_under_ids is not None:
            usd_qs = usd_qs.filter(user_profile__user__id__in=users_under_ids)

        for usd in usd_qs:
            cost = float(usd.value or 0)
            if usd.category == 'DEP':
                cost += float(usd.hotel_cost or 0)

            if cost <= 0:
                continue

            for w in usd.wilayas.all():
                w_name = w.nom
                if w_name not in sector_costs:
                    sector_costs[w_name] = {'DEP': {}, 'SEMI': {}}

                for m in range(1, 13):
                    if usd.month_frequency == 'EVEN' and m % 2 != 0:
                        continue
                    if usd.month_frequency == 'ODD' and m % 2 == 0:
                        continue

                    m_str = str(m)
                    sector_costs[w_name][usd.category][m_str] = (
                        sector_costs[w_name][usd.category].get(m_str, 0) + cost
                    )

        return JsonResponse({"raw_data": raw_data, "raw_sales_data": raw_sales_data, "sector_costs": sector_costs})