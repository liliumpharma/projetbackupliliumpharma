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
        from .models import DashboardSnapshot
        from django.db.models import Max
        latest_update = DashboardSnapshot.objects.aggregate(max_date=Max('updated_at'))['max_date']
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

        if UserProfile.objects.get(user=user_id).speciality_rolee in [
            "Medico_commercial",
            "Commercial",
        ]:
            user_profiles = User.objects.filter(id=user_id)
            return render(
                request, template_name, {"users": user_profiles, "num_id": 33, "produits": produits, "last_updated": last_updated_str}
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
            return render(request, template_name, {"users": user_profiles, "num_id": 1, "produits": produits, "last_updated": last_updated_str})

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
            return render(
                request,
                template_name,
                {"users": user_profiles, "num_id": 2, "name": nam, "produits": produits, "last_updated": last_updated_str},
            )
        else:
            pass

        return render(request, template_name, {"produits": produits, "last_updated": last_updated_str})



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
        Génère exactement le dictionnaire attendu par le template HTML,
        mais en lisant instantanément notre table précalculée UserReportSnapshot.
        """
        from .models import UserReportSnapshot
        from accounts.models import UserProfile
        from django.db.models import Sum
        from django.urls import reverse
        from liliumpharm.utils import thousand_separator

        try:
            profile = UserProfile.objects.select_related('user').get(user_id=user_id)
        except UserProfile.DoesNotExist:
            return {}

        # 1. Agrégation instantanée depuis la BDD (Sans boucles complexes)
        qs = UserReportSnapshot.objects.filter(
            user_id=user_id,
            year__in=years,
            month__in=months
        ).values('product_id', 'product_name', 'product_price').annotate(
            t_target=Sum('target_qty'),
            t_ph_gros=Sum('mobile_ph_gros_qty'),
            t_gros_super=Sum('mobile_gros_super_qty'),
            t_supergros=Sum('supergros_achieved_qty')
        ).order_by('product_name')

        wilayas = [w.nom for w in profile.sectors.all()]
        
        products, targets, prices = [], [], []
        total_unite_product = []
        total_unite_product_gros_super = []
        quantities = []
        total_targets, total_achievements = [], []

        total_target = 0.0
        total_reached = 0.0
        total_ph_gros_value = 0.0
        total_gros_super_value = 0.0

        for row in qs:
            p_name = row['product_name']
            p_price = float(row['product_price'])
            
            t_qty = float(row['t_target'] or 0)
            ph_qty = float(row['t_ph_gros'] or 0)
            gs_qty = float(row['t_gros_super'] or 0)
            sg_qty = float(row['t_supergros'] or 0)

            # --- CORRECTION ICI ---
            # On ignore les colonnes 100% vides. 
            # Si un produit n'a pas d'objectif (t_qty=0) mais a été vendu (sg_qty>0), il s'affichera !
            if t_qty == 0 and ph_qty == 0 and gs_qty == 0 and sg_qty == 0:
                continue

            row_target_val = t_qty * p_price
            row_sg_val = sg_qty * p_price
            row_ph_val = ph_qty * p_price
            row_gs_val = gs_qty * p_price

            products.append(p_name)
            targets.append(t_qty)
            prices.append(p_price)
            
            # Reconstruction des liens pour voir le détail des ventes
            query_string = f"user={user_id}&product={row['product_id']}"
            for y in years: query_string += f"&years={y}"
            for m in months: query_string += f"&months={m}"
            
            link_mobile = f"{reverse('target_report_details_use')}?{query_string}"
            link_sg     = f"{reverse('target_report_details')}?{query_string}"

            total_unite_product.append({"total": ph_qty, "target_report_details_link": link_mobile})
            total_unite_product_gros_super.append({"total": gs_qty, "target_report_details_link": link_mobile + "&gros_super=1"})
            quantities.append({"total": sg_qty, "target_report_details_link": link_sg})

            total_targets.append(row_target_val)
            total_achievements.append(row_sg_val)

            total_target += row_target_val
            total_reached += row_sg_val
            total_ph_gros_value += row_ph_val
            total_gros_super_value += row_gs_val

        percentage_reached = round((total_reached / total_target * 100), 2) if total_target > 0 else 0

        # On retourne le dictionnaire exact attendu par target_report_per_user.html
        return {
            "user_id": user_id,
            "user": f"{profile.user.last_name} {profile.user.first_name}",
            "wilayas": wilayas,
            "products": products,
            "targets": [thousand_separator(t) for t in targets],
            "prices": [thousand_separator(p) for p in prices],
            "total_unite_product": total_unite_product,
            "total_unite_product_gros_super": total_unite_product_gros_super,
            "quantities": quantities,
            "total_targets": [thousand_separator(t) for t in total_targets],
            "total_achievements": [thousand_separator(t) for t in total_achievements],
            "total_target": thousand_separator(total_target),
            "total_reached": thousand_separator(total_reached),
            "percentage_reached": percentage_reached,
            "total_ph_gros_value": thousand_separator(total_ph_gros_value),
            "total_gros_super_value": thousand_separator(total_gros_super_value),
            "speciality_rolee": profile.speciality_rolee
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

        # --- Find Latest Update ---
        latest_update = snapshots.aggregate(max_date=Max('updated_at'))['max_date']
        last_updated_str = latest_update.strftime('%d/%m/%Y à %H:%M') if latest_update else "Non disponible"

        return JsonResponse({
            "meriem_total_target": meriem_total_target,
            "users": cards_data,
            "dash_raw": dash_raw,
            "last_updated": last_updated_str # <-- Nouvelle donnée renvoyée
        })


class VisualisationVenteView(APIView):
    """
    Renders the Data Visualisation page.
    """
    def get(self, request):
        from .models import BISnapshot
        from django.db.models import Max
        
        # --- Date globale de dernière mise à jour ---
        latest_update = BISnapshot.objects.aggregate(max_date=Max('updated_at'))['max_date']
        last_updated_str = latest_update.strftime('%d/%m/%Y à %H:%M') if latest_update else "Non disponible"

        produits = Produit.objects.all()
        context = {
            "produits": produits,
            "query_string": request.GET.urlencode(),
            "last_updated": last_updated_str, # Injection de la date
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

        latest_update = snapshots.aggregate(max_date=Max('updated_at'))['max_date']
        last_updated_str = latest_update.strftime('%d/%m/%Y à %H:%M') if latest_update else "Non disponible"

        return JsonResponse({
            "raw_data": raw_data, 
            "raw_sales_data": raw_sales_data, 
            "sector_costs": sector_costs,
            "last_updated": last_updated_str # <-- Nouvelle donnée renvoyée
        })