from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from django.db.models import Exists, OuterRef
from django.db.models import Max

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

        # --- NOUVEAU : Date globale de dernière mise à jour ---
        from .models import BISnapshot
        from django.db.models import Max
        latest_update = BISnapshot.objects.aggregate(max_date=Max('updated_at'))['max_date']
        last_updated_str = latest_update.strftime('%d/%m/%Y à %H:%M') if latest_update else "Non disponible"
        # ------------------------------------------------------

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
        regions = list(
            UserProfile.objects.exclude(region__isnull=True).exclude(region__exact='').exclude(region__iexact='n/a')
            .values_list('region', flat=True).distinct().order_by('region')
        )
        lines = list(Produit.objects.exclude(line__isnull=True).exclude(line__exact='').values_list('line', flat=True).distinct().order_by('line'))

        if UserProfile.objects.get(user=user_id).speciality_rolee in [
            "Medico_commercial",
            "Commercial",
        ]:
            user_profiles = User.objects.filter(id=user_id)
            return render(
                request, template_name, {"users": user_profiles, "num_id": 33, "produits": produits, "regions": regions, "lines": lines, "last_updated": last_updated_str}
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
            return render(request, template_name, {"users": user_profiles, "num_id": 1, "produits": produits, "regions": regions, "lines": lines, "last_updated": last_updated_str})

        elif (
            UserProfile.objects.get(user=user_id).speciality_rolee in [
                "Superviseur_regional", "Superviseur_national", "Superviseur"
            ]
        ):
            user_profile = UserProfile.objects.get(user=user_id)
            user_profiles = user_profile.usersunder.all() | User.objects.filter(id=user_id)
            ur = User.objects.get(id=user_id)
            nam = ur.first_name + " " + ur.last_name
            return render(
                request,
                template_name,
                {"users": user_profiles.distinct(), "num_id": 2, "name": nam, "produits": produits, "regions": regions, "lines": lines, "last_updated": last_updated_str},
            )
        else:
            pass

        return render(request, template_name, {"produits": produits, "regions": regions, "lines": lines, "last_updated": last_updated_str})



    # ════════════════ NOUVELLE FONCTION POST ULTRA-RAPIDE ════════════════
    def post(self, request):
        is_desktop = request.GET.get('view') == 'desktop'

        if request.user.is_authenticated:
            session_user_id = request.user.id
        else:
            session_user_id = request.session.get("user_id")

        # 1. Extraction des paramètres
        selected_user_str = request.POST.get("users")
        years_str = request.POST.getlist("years")
        months_str = request.POST.getlist("months")
        
        # Fallback si l'année est envoyée comme un champ simple
        if not years_str and request.POST.get("years"):
            years_str = [request.POST.get("years")]
            
        years = [int(y) for y in years_str if y]
        months = [int(m) for m in months_str if m]
        
        selected_user = int(selected_user_str) if selected_user_str and selected_user_str.isdigit() else session_user_id

        # ── Rétrocompatibilité : Ancienne App Mobile (users = 0) ──
        if selected_user == 0:
            params = {"years": years, "months": months}
            if "client_wilaya_id" in request.GET:
                params["wilaya"] = request.GET.get("client_wilaya_id")
            context = {
                "month": "Tous les Mois" if len(months) > 1 else (month_number_to_french_name(months[0]) if months else ""),
                "year": years[0] if years else ""
            }
            data = get_target_all_users(**params)
            context["data"] = data
            return render(request, "clients/reports/target_report_all_users.html", context)

        # ── NOUVELLE LOGIQUE SNAPSHOT (Chargement < 50ms) ──
        
        # A. Données globales agrégées (Tous les mois sélectionnés ensemble)
        main_data = self.build_fast_target_data(selected_user, years, months)
        
        # Formatage des mois pour le titre
        if len(months) == 1:
            french_month_str = month_number_to_french_name(months[0])
        else:
            french_month_str = [month_number_to_french_name(m) for m in months]

        context = {
            "month": french_month_str, 
            "year": years,
            "data": main_data
        }
        
        # La table spéciale (ADVAGEN, HAIRVOL, etc.)
        if is_desktop:
            context = add_special_table_data(context)

        # B. Ventilation par mois (si plusieurs mois sélectionnés)
        if len(months) > 1:
            per_month_sections = []
            for m in months:
                single_data = self.build_fast_target_data(selected_user, years, [m])
                single_ctx = {"data": single_data}
                
                if is_desktop:
                    single_ctx = add_special_table_data(single_ctx)
                
                per_month_sections.append({
                    "month": month_number_to_french_name(m),
                    "data": single_ctx["data"],
                    "show_special_table": single_ctx.get("show_special_table", False),
                })
            context["per_month_sections"] = per_month_sections

        return render(request, "clients/reports/target_report_per_user.html", context)


    # ════════════════ FONCTION HELPER (Lecture du Snapshot) ════════════════
    def build_fast_target_data(self, user_id, years, months):
        """
        HYBRID APPROACH:
        - Targets and Mobile Orders (Ph_Gros/Gros_Super) are queried LIVE.
        - Achieved Sales (Achevé) are read instantly from Snapshots.
        """
        from accounts.models import UserProfile
        from clients.models import BISnapshot, SupergrosSalesSnapshot, UserTargetMonth, UserTargetMonthProduct
        from orders.models import OrderItem
        from produits.models import Produit
        from django.db.models import Sum, Q
        from django.urls import reverse
        from liliumpharm.utils import thousand_separator

        try:
            profile = UserProfile.objects.select_related('user', 'commune__wilaya__pays').get(user_id=user_id)
            user = profile.user
            role = profile.speciality_rolee
        except UserProfile.DoesNotExist:
            return {}

        # 1. Scope Definition (Who are we calculating for?)
        target_users = [user]
        order_users = [user]
        supervisor_wilayas = []

        is_supervisor = role in ["Superviseur_national", "Superviseur_regional", "Superviseur"]
        is_cm = role == "CountryManager"

        if is_cm:
            # CountryManager sees all delegates in the country
            team = User.objects.filter(
                userprofile__speciality_rolee__in=["Medico_commercial", "Commercial", "Superviseur", "Superviseur_regional", "Superviseur_national"],
                userprofile__commune__wilaya__pays=profile.commune.wilaya.pays
            )
            # The DB automatically calculates the true CM target (including Commercial special products)
            target_users = User.objects.filter(userprofile__speciality_rolee="CountryManager")
            order_users = team

        elif is_supervisor:
            team = profile.usersunder.all() | User.objects.filter(pk=user.pk)
            # The Supervisor's profile ALREADY contains the aggregated target from the DB signal
            target_users = [user]
            order_users = team
            supervisor_wilayas = list(profile.sectors.values_list('nom', flat=True))

        # 2. LIVE DATA: Targets (Carry-over logic per month) - OPTIMIZED O(1) Queries
        target_map = {}
        product_prices = {}
        product_names = {}
        # Product IDs explicitly present in the user's target (even if qty=0)
        target_product_ids = set()

        # --- PRE-FETCH TARGETS (Fixing N+1) ---
        all_utms = list(UserTargetMonth.objects.filter(user__in=target_users).order_by("-date"))
        utm_ids = [utm.id for utm in all_utms]

        all_tps = UserTargetMonthProduct.objects.filter(usermonth_id__in=utm_ids).select_related('product')

        # Map UTM ID -> List of Products
        tps_by_utm = {}
        for tp in all_tps:
            if tp.usermonth_id not in tps_by_utm:
                tps_by_utm[tp.usermonth_id] = []
            tps_by_utm[tp.usermonth_id].append(tp)

        # Map User ID -> List of UTMs (already sorted by -date descending)
        utms_by_user = {}
        for utm in all_utms:
            if utm.user_id not in utms_by_user:
                utms_by_user[utm.user_id] = []
            utms_by_user[utm.user_id].append(utm)
        # ---------------------------------------

        for y in years:
            for m in months:
                target_year = int(y)
                target_month = int(m)

                for u in target_users:
                    # Scan the pre-fetched list to find the first UTM up to the target month/year
                    user_utms = utms_by_user.get(u.id, [])
                    latest_utm = None
                    for utm in user_utms:
                        # STRICT RULE: Only use the target created EXACTLY in this month/year
                        if utm.date.year == target_year and utm.date.month == target_month:
                            latest_utm = utm
                            break

                    if latest_utm:
                        tps = tps_by_utm.get(latest_utm.id, [])
                        for tp in tps:
                            pid = tp.product.id
                            target_product_ids.add(pid)
                            target_map[pid] = target_map.get(pid, 0) + tp.quantity
                            product_prices[pid] = float(tp.product.price)
                            product_names[pid] = tp.product.nom

        # 3. LIVE DATA: Mobile Orders (Ph_Gros vs Gros_Super)
        ph_gros_q = Q(order__user__in=order_users, order__added__year__in=years, order__added__month__in=months, order__super_gros__isnull=True) & ~Q(order__pharmacy__isnull=True, order__gros__isnull=True) & ~Q(order__super_gros_id=149)
        gros_super_q = Q(order__user__in=order_users, order__added__year__in=years, order__added__month__in=months, order__super_gros__isnull=False) & ~Q(order__pharmacy__isnull=True, order__gros__isnull=True) & ~Q(order__super_gros_id=149)

        comm_gs_q = Q(order__user__in=order_users, order__added__year__in=years, order__added__month__in=months, order__pharmacy__isnull=True, order__gros__isnull=False) & ~Q(order__super_gros_id=149)

        if role == "Commercial" or (is_supervisor and getattr(profile, 'work_as_commercial', False)):
            gros_super_q = comm_gs_q
        elif is_cm or is_supervisor:
            gros_super_q = gros_super_q | comm_gs_q

        ph_gros_sales = OrderItem.objects.filter(ph_gros_q).values('produit_id', 'produit__nom', 'produit__price').annotate(total=Sum('qtt'))
        gros_super_sales = OrderItem.objects.filter(gros_super_q).values('produit_id', 'produit__nom', 'produit__price').annotate(total=Sum('qtt'))

        ph_gros_map = {item['produit_id']: item['total'] for item in ph_gros_sales}
        gros_super_map = {item['produit_id']: item['total'] for item in gros_super_sales}

        for item in list(ph_gros_sales) + list(gros_super_sales):
            pid = item['produit_id']
            if pid not in product_names:
                product_names[pid] = item['produit__nom']
                product_prices[pid] = float(item['produit__price'])

        # 4. SNAPSHOT DATA: Achevé / SuperGros Sales
        sg_achieved_map = {}
        if is_cm:
            sg_sales = SupergrosSalesSnapshot.objects.filter(year__in=years, month__in=months).values('product_id', 'product_name').annotate(total_qty=Sum('qty'))
        elif is_supervisor:
            sg_sales = SupergrosSalesSnapshot.objects.filter(year__in=years, month__in=months, wilaya__in=supervisor_wilayas).values('product_id', 'product_name').annotate(total_qty=Sum('qty'))
        else:
            sg_sales = BISnapshot.objects.filter(year__in=years, month__in=months, user_id=user.id).values('product_id', 'product_name').annotate(total_qty=Sum('qty'))

        for item in sg_sales:
            pid = item['product_id']
            sg_achieved_map[pid] = item['total_qty']
            if pid not in product_names:
                product_names[pid] = item['product_name']

        # Missing prices fallback
        missing_price_pids = [pid for pid in product_names if pid not in product_prices]
        if missing_price_pids:
            for p in Produit.objects.filter(id__in=missing_price_pids):
                product_prices[p.id] = float(p.price)

        # 5. Build HTML Dictionary
        products, targets, prices = [], [], []
        total_unite_product, total_unite_product_gros_super, quantities = [], [], []
        total_targets, total_achievements = [], []

        total_target_val, total_reached_val = 0.0, 0.0
        total_ph_gros_val, total_gros_super_val = 0.0, 0.0

        sorted_pids = sorted(product_names.keys(), key=lambda k: product_names[k])

        for pid in sorted_pids:
            p_name = product_names[pid]
            p_price = product_prices.get(pid, 0.0)

            t_qty = float(target_map.get(pid, 0.0))
            ph_qty = float(ph_gros_map.get(pid, 0.0))
            gs_qty = float(gros_super_map.get(pid, 0.0))
            sg_qty = float(sg_achieved_map.get(pid, 0.0))

            # Delegates only see products explicitly in their target (qty=0 is fine, absent=excluded)
            if role in ["Medico_commercial", "Commercial"] and pid not in target_product_ids:
                continue
            if t_qty == 0 and ph_qty == 0 and gs_qty == 0 and sg_qty == 0:
                continue

            row_target_val = t_qty * p_price
            row_sg_val = sg_qty * p_price
            row_ph_val = ph_qty * p_price
            row_gs_val = gs_qty * p_price

            products.append(p_name)
            targets.append(t_qty)
            prices.append(p_price)

            query_string = f"user={user_id}&product={pid}"
            for y in years: query_string += f"&years={y}"
            for m in months: query_string += f"&months={m}"

            link_mobile = f"{reverse('target_report_details_use')}?{query_string}"
            link_sg     = f"{reverse('target_report_details')}?{query_string}"

            total_unite_product.append({"total": ph_qty, "target_report_details_link": link_mobile})
            total_unite_product_gros_super.append({"total": gs_qty, "target_report_details_link": link_mobile + "&gros_super=1"})
            quantities.append({"total": sg_qty, "target_report_details_link": link_sg})

            total_targets.append(row_target_val)
            total_achievements.append(row_sg_val)

            total_target_val += row_target_val
            total_reached_val += row_sg_val
            total_ph_gros_val += row_ph_val
            total_gros_super_val += row_gs_val

        percentage_reached = round((total_reached_val / total_target_val * 100), 2) if total_target_val > 0 else 0
        wilayas = [w.nom for w in profile.sectors.all()]

        return {
            "user_id": user_id,
            "user": f"{user.last_name} {user.first_name}",
            "wilayas": wilayas,
            "products": products,
            "targets": [thousand_separator(t) for t in targets],
            "prices": [thousand_separator(p) for p in prices],
            "total_unite_product": total_unite_product,
            "total_unite_product_gros_super": total_unite_product_gros_super,
            "quantities": quantities,
            "total_targets": [thousand_separator(t) for t in total_targets],
            "total_achievements": [thousand_separator(t) for t in total_achievements],
            "total_target": thousand_separator(total_target_val),
            "total_reached": thousand_separator(total_reached_val),
            "percentage_reached": percentage_reached,
            "total_ph_gros_value": thousand_separator(total_ph_gros_val),
            "total_gros_super_value": thousand_separator(total_gros_super_val),
            "speciality_rolee": role
        }



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

        if not user_id:
            return JsonResponse({"error": "Non authentifié."}, status=401)
        try:
            profile = UserProfile.objects.select_related(
                'user', 'commune__wilaya__pays'
            ).get(user=user_id)
        except UserProfile.DoesNotExist:
            return JsonResponse({"error": "Profil introuvable."}, status=403)
        if profile.speciality_rolee not in self._ALLOWED_ROLES:
            return JsonResponse({"error": "Accès refusé."}, status=403)

        # --- Parameter parsing ---
        year = request.GET.get("year")
        months = request.GET.getlist("months[]") or request.GET.getlist("months")

        years_filter = [int(year)] if year else []
        months_filter = [int(m) for m in months] if months else list(range(1, 13))

        from .models import SupergrosSalesSnapshot, UserTargetMonthProduct
        from django.db.models import Sum
        import datetime

        role = profile.speciality_rolee
        is_cm = role in ["CountryManager", "Admin", "Office"]
        is_supervisor = role in ["Superviseur_national", "Superviseur_regional", "Superviseur"]

        # --- Scope: which delegate profiles to show ---
        delegate_qs = UserProfile.objects.select_related(
            'user', 'commune__wilaya'
        ).filter(
            speciality_rolee__in=[
                "CountryManager", "Superviseur_national", "Superviseur_regional",
                "Medico_commercial", "Commercial",
            ],
            hidden=False,
        )
        if is_supervisor:
            delegate_qs = delegate_qs.filter(
                user__in=profile.usersunder.all()
            ) | UserProfile.objects.filter(user=profile.user)

        # --- LIVE: Targets per delegate per product ---
        # Build a map: {(user_id, product_id): {"target_value": float, "product_name": str}}
        target_map = {}   # (uid, pid) -> float value
        product_name_map = {}  # pid -> str

        for y in years_filter:
            for m in months_filter:
                for dp in delegate_qs:
                    # STRICT RULE: Only look for targets created EXACTLY in this month/year
                    latest_utm = UserTargetMonth.objects.filter(
                        user=dp.user, date__year=y, date__month=m
                    ).order_by("-date").first()
                    if not latest_utm:
                        continue
                    tps = UserTargetMonthProduct.objects.filter(
                        usermonth=latest_utm
                    ).select_related('product')
                    for tp in tps:
                        pid = tp.product.id
                        key = (dp.user_id, pid)
                        price = float(tp.product.price)
                        target_map[key] = target_map.get(key, 0.0) + tp.quantity * price
                        product_name_map[pid] = tp.product.nom

        # --- SNAPSHOT: Achieved values ---
        # --- SNAPSHOT: Achieved values ---
        achieved_map = {}  # uid -> {"total": float, "by_product": {pid: float}}

        # 1. ALWAYS fetch the allocated BISnapshot sales for all displayed delegates
        delegate_ids = list(delegate_qs.values_list('user_id', flat=True))
        bi_rows = BISnapshot.objects.filter(
            year__in=years_filter, month__in=months_filter,
            user_id__in=delegate_ids,
        ).values('user_id', 'product_id', 'product_name').annotate(total_val=Sum('value'))

        delegate_role_map = {dp.user_id: dp.speciality_rolee for dp in delegate_qs}

        for row in bi_rows:
            uid = row['user_id']
            pid = row['product_id']
            # Medico_commercial and Commercial: only count products present in their target
            if delegate_role_map.get(uid) in ("Medico_commercial", "Commercial"):
                if (uid, pid) not in target_map:
                    continue
            val = float(row['total_val'] or 0)
            if uid not in achieved_map:
                achieved_map[uid] = {"total": 0.0, "by_product": {}}
            achieved_map[uid]["total"] += val
            achieved_map[uid]["by_product"][pid] = achieved_map[uid]["by_product"].get(pid, 0.0) + val
            product_name_map[pid] = row['product_name']

        # 2. OVERRIDE CountryManager cards with pure raw SuperGros data
        cm_profiles_qs = delegate_qs.filter(speciality_rolee="CountryManager")
        if cm_profiles_qs.exists():
            sg_rows = SupergrosSalesSnapshot.objects.filter(
                year__in=years_filter, month__in=months_filter
            ).values('product_id', 'product_name').annotate(total_val=Sum('value'))

            for cm_prof in cm_profiles_qs:
                cm_uid = cm_prof.user_id
                # Reset their specific map to ensure pure raw data
                achieved_map[cm_uid] = {"total": 0.0, "by_product": {}}

                for row in sg_rows:
                    pid = row['product_id']
                    val = float(row['total_val'] or 0)
                    achieved_map[cm_uid]["total"] += val
                    achieved_map[cm_uid]["by_product"][pid] = achieved_map[cm_uid]["by_product"].get(pid, 0.0) + val
                    product_name_map[pid] = row['product_name']

        # 3. OVERRIDE ALL Supervisors cards with pure Regional SuperGros data (ignoring targets)
        sup_profiles_qs = delegate_qs.filter(speciality_rolee__in=["Superviseur_national", "Superviseur_regional", "Superviseur"])
        for sup_prof in sup_profiles_qs:
            sup_uid = sup_prof.user_id
            supervisor_wilayas = list(sup_prof.sectors.values_list('nom', flat=True))

            sg_rows = SupergrosSalesSnapshot.objects.filter(
                year__in=years_filter, month__in=months_filter,
                wilaya__in=supervisor_wilayas,
            ).values('product_id', 'product_name').annotate(total_val=Sum('value'))

            # Reset their specific map to ensure pure raw data
            achieved_map[sup_uid] = {"total": 0.0, "by_product": {}}

            for row in sg_rows:
                pid = row['product_id']
                val = float(row['total_val'] or 0)
                achieved_map[sup_uid]["total"] += val
                achieved_map[sup_uid]["by_product"][pid] = achieved_map[sup_uid]["by_product"].get(pid, 0.0) + val
                product_name_map[pid] = row['product_name']

        # --- Assemble users_map ---
        users_map = {}

        # Seed from delegate profiles so every delegate appears even with zero data
        for dp in delegate_qs:
            uid = dp.user_id
            users_map[uid] = {
                "id": uid,
                "name": f"{dp.user.last_name} {dp.user.first_name}",
                "role": dp.speciality_rolee,
                "lines": getattr(dp, 'lines', '') or "",
                "sector": getattr(dp, 'sector_category', None) or "N/A",
                "region": getattr(dp, 'region', None) or "N/A",
                "work_as_commercial": getattr(dp, 'work_as_commercial', False),
                "target_total": 0.0,
                "achieved_total": 0.0,
                "product_breakdown_map": {},
            }

        # Fill in target values
        for (uid, pid), t_val in target_map.items():
            if uid not in users_map:
                continue
            u = users_map[uid]
            u["target_total"] += t_val
            if pid not in u["product_breakdown_map"]:
                u["product_breakdown_map"][pid] = {
                    "product_id": pid,
                    "product_name": product_name_map.get(pid, ""),
                    "target_value": 0.0,
                    "achieved_value": 0.0,
                }
            u["product_breakdown_map"][pid]["target_value"] += t_val

        # Fill in achieved values
        for uid, ach in achieved_map.items():
            if uid not in users_map:
                continue
            u = users_map[uid]
            u["achieved_total"] += ach["total"]
            for pid, a_val in ach["by_product"].items():
                if pid not in u["product_breakdown_map"]:
                    u["product_breakdown_map"][pid] = {
                        "product_id": pid,
                        "product_name": product_name_map.get(pid, ""),
                        "target_value": 0.0,
                        "achieved_value": 0.0,
                    }
                u["product_breakdown_map"][pid]["achieved_value"] += a_val

        # --- CountryManager totals for global_percentage ---
        cm_profiles = [u for u in users_map.values() if u["role"] == "CountryManager"]
        meriem_total_target = sum(u["target_total"] for u in cm_profiles) or 0.0
        meriem_total_achieved = sum(u["achieved_total"] for u in cm_profiles) or 0.0

        # --- Final Formatting ---
        cards_data = []
        dash_raw = []

        for u in users_map.values():
            u["product_breakdown"] = list(u["product_breakdown_map"].values())
            del u["product_breakdown_map"]

            u["personal_percentage"] = round((u["achieved_total"] / u["target_total"] * 100), 2) if u["target_total"] > 0 else 0.0
            u["global_percentage"] = round((u["achieved_total"] / meriem_total_target * 100), 2) if meriem_total_target > 0 else 0.0
            u["global_achieved_percentage"] = round((u["achieved_total"] / meriem_total_achieved * 100), 2) if meriem_total_achieved > 0 else 0.0

            if u["target_total"] > 0 or u["achieved_total"] > 0 or u["role"] in ["CountryManager", "Superviseur_national", "Superviseur_regional"]:
                cards_data.append(u)
                for pb in u["product_breakdown"]:
                    for m in months_filter:
                        dash_raw.append({
                            "month": m,
                            "user_id": u["id"],
                            "user_name": u["name"],
                            "product_id": pb["product_id"],
                            "lines": u["lines"],
                            "target_value": pb["target_value"],
                        })

        # --- ADD RAW SALES DATA WITH REGIONS FOR FRONTEND CM CALCULATION ---
        wilaya_to_region = {}
        for dp in delegate_qs.prefetch_related('sectors'):
            region = getattr(dp, 'region', 'N/A')
            for w in dp.sectors.all():
                if w.nom not in wilaya_to_region or wilaya_to_region[w.nom] == 'N/A':
                    wilaya_to_region[w.nom] = region

        raw_sales_data = []
        if is_cm or is_supervisor:
            from .models import SupergrosSalesSnapshot
            sales_qs = SupergrosSalesSnapshot.objects.filter(year__in=years_filter, month__in=months_filter)
            if is_supervisor:
                supervisor_wilayas = list(profile.sectors.values_list('nom', flat=True))
                sales_qs = sales_qs.filter(wilaya__in=supervisor_wilayas)

            for row in sales_qs.values('wilaya', 'product_id', 'value'):
                raw_sales_data.append({
                    "wilaya": row['wilaya'],
                    "product_id": row['product_id'],
                    "value": row['value'],
                    "region": wilaya_to_region.get(row['wilaya'], 'N/A')
                })

        return JsonResponse({
            "meriem_total_target": meriem_total_target,
            "users": cards_data,
            "dash_raw": dash_raw,
            "raw_sales_data": raw_sales_data,
            "last_updated": datetime.datetime.now().strftime('%d/%m/%Y à %H:%M'),
        })


class VisualisationVenteView(APIView):
    """
    Renders the Data Visualisation page.
    """
    def get(self, request):
        from .models import BISnapshot
        from django.db.models import Max
        from accounts.models import UserProfile

        # --- Date globale de dernière mise à jour ---
        latest_update = BISnapshot.objects.aggregate(max_date=Max('updated_at'))['max_date']
        last_updated_str = latest_update.strftime('%d/%m/%Y à %H:%M') if latest_update else "Non disponible"

        if request.user.is_authenticated:
            user_id = request.user.id
        else:
            user_id = request.session.get("user_id")

        users_to_display = []
        if user_id:
            try:
                profile = UserProfile.objects.get(user=user_id)
                role = profile.speciality_rolee
                if role in ["CountryManager", "Admin", "Office"]:
                    users_to_display = UserProfile.objects.filter(
                        speciality_rolee__in=["Medico_commercial", "Commercial", "Superviseur", "Superviseur_regional", "Superviseur_national"],
                        hidden=False
                    ).select_related('user')
                elif role in ["Superviseur", "Superviseur_regional", "Superviseur_national"]:
                    users_under_ids = list(profile.usersunder.values_list('id', flat=True))
                    users_to_display = UserProfile.objects.filter(
                        user_id__in=users_under_ids + [user_id],
                        hidden=False
                    ).select_related('user')
                else:
                    users_to_display = [profile]
            except UserProfile.DoesNotExist:
                pass

        # Sort alphabetically by last name, then first name
        users_to_display = sorted(users_to_display, key=lambda p: f"{p.user.last_name or ''} {p.user.first_name or ''}")

        produits = Produit.objects.all()
        regions = list(
            UserProfile.objects.exclude(region__isnull=True).exclude(region__exact='').exclude(region__iexact='n/a')
            .values_list('region', flat=True).distinct().order_by('region')
        )
        lines = list(Produit.objects.exclude(line__isnull=True).exclude(line__exact='').values_list('line', flat=True).distinct().order_by('line'))
        context = {
            "produits": produits,
            "users": users_to_display,
            "regions": regions,
            "lines": lines,
            "query_string": request.GET.urlencode(),
            "last_updated": last_updated_str,
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
            # FIX: Change 'user__id' to 'id'
            users_under_ids = list(profile.usersunder.all().values_list('id', flat=True))
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

        latest_update = snapshots.aggregate(max_date=Max('updated_at'))['max_date']
        last_updated_str = latest_update.strftime('%d/%m/%Y à %H:%M') if latest_update else "Non disponible"

        return JsonResponse({
            "raw_data": raw_data, 
            "raw_sales_data": raw_sales_data, 
            "sector_costs": sector_costs,
            "last_updated": last_updated_str # <-- Nouvelle donnée renvoyée
        })