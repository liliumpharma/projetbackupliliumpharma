from django.db.models.expressions import Value, When, Case
from django.http import JsonResponse
from medecins.models import Medecin
from rapports.models import Visite
from produits.models import ProduitVisite
from django.db.models import Q, F, Max, Count, ExpressionWrapper
from django.db import models
from django.contrib.auth.models import User
from django.db.models.functions import TruncDate

from itertools import chain
from collections import defaultdict



def get_medecinsss(request):
    from collections import defaultdict
    filters = {}
    visites_filters = {}
    params = request.GET
    print(params)

    q = Q()
    specialite = request.GET.get("specialite")
    visites_value = request.GET.get("visites")

    def _extract_username(raw):
        if not raw:
            return ""
        raw = str(raw).strip()
        if " - " in raw:
            return raw.split(" - ")[0].strip()
        return raw

    def _norm_speciality_rolee(u):
        try:
            return (u.userprofile.speciality_rolee or "").strip().replace(" ", "_")
        except Exception:
            return ""

    commercial_username = _extract_username(request.GET.get("commercial"))
    selected_user = User.objects.filter(username=commercial_username).select_related("userprofile").first() if commercial_username else None
    selected_sr = _norm_speciality_rolee(selected_user) if selected_user else ""
    selected_is_supervisor = selected_sr in ["Superviseur", "Superviseur_regional", "Superviseur_national"]

    # -------------------------
    # Medecin filters (NE PAS filtrer ici par "commercial" => sinon superviseur peut vider la liste)
    # -------------------------
    if request.GET.get("pays") and request.GET.get("pays") != "0":
        filters["commune__wilaya__pays__id"] = request.GET.get("pays")

    if request.GET.get("wilaya") and request.GET.get("wilaya") != "0":
        filters["commune__wilaya__id"] = request.GET.get("wilaya")

    if request.GET.get("commune") and request.GET.get("commune") != "0":
        filters["commune__id"] = request.GET.get("commune")

    if request.GET.get("medecin") and request.GET.get("medecin") != "":
        if request.GET.get("medecin").isdigit():
            filters["id"] = request.GET.get("medecin")
        else:
            filters["nom__icontains"] = request.GET.get("medecin").lower()

    if request.GET.get("specialite") and request.GET.get("specialite") != "":
        if request.GET.get("specialite") == "commerciale":
            filters["specialite__in"] = ["Pharmacie", "Grossiste", "SuperGros"]
        elif request.GET.get("specialite") == "medicale":
            filters["specialite__in"] = [
                "Generaliste", "Généraliste", "Diabetologue", "Neurologue", "Interniste",
                "Psychologue", "Gynecologue", "Gynécologue", "Rumathologue", "Allergologue",
                "Phtisio", "Cardiologue", "Urologue", "Hematologue", "Orthopedie",
                "Nutritionist", "Dermatologue", "Gastrologue", "Endocrinologue", "Dentiste",
                "ORL", "Maxilo facial",
            ]
        else:
            filters["specialite__in"] = request.GET.get("specialite").split(",")

    if request.GET.get("classification"):
        filters["classification__in"] = request.GET.get("classification").split(",")

    if request.GET.get("deal") == "1":
        filters["medecin__isnull"] = False
    if request.GET.get("deal") == "0":
        filters["medecin__isnull"] = True

    if request.GET.get("note") == "2":
        q |= Q(note="")
        q |= Q(note__isnull=True)

    # -------------------------
    # Visites filters (comme avant)
    # -------------------------
    if request.GET.get("mindate"):
        visites_filters["rapport__added__gte"] = request.GET.get("mindate")

    if request.GET.get("maxdate"):
        visites_filters["rapport__added__lte"] = request.GET.get("maxdate")

    if request.GET.get("produit"):
        visites_filters["produits__id"] = request.GET.get("produit")

    # IMPORTANT: "commercial" filtre les visites (pas les medecins assignés)
    if commercial_username:
        visites_filters["rapport__user__username__icontains"] = commercial_username

    # recycle bins
    medecin_recycle_bin_user = User.objects.get(username="Medecin_Recycle_Bin")
    pharmacie_recycle_bin_user = User.objects.get(username="Pharmacie_Recycle_Bin")

    medecins_list = (
        Medecin.objects.filter(**filters)
        .exclude(users__in=[medecin_recycle_bin_user, pharmacie_recycle_bin_user])
        .order_by("nom")
    )

    if q:
        medecins_list = medecins_list.filter(q)

    if request.GET.get("shared") == "2":
        medecins_list = Medecin.objects.annotate(num_users=Count("users")).filter(
            num_users__gt=1, id__in=[medecins_list.values("id")]
        )

    if request.GET.get("shared") == "1":
        medecins_list = Medecin.objects.annotate(num_users=Count("users")).filter(
            num_users=1, id__in=[medecins_list.values("id")]
        )

    medecins_list = medecins_list.distinct()

    # -------------------------
    # Country scoping (utilise selected_user si présent, sinon request.user)
    # -------------------------
    scope_user = selected_user or request.user
    if scope_user is None:
        scope_user = request.user

    if not request.user.is_superuser:
        medecins_list = medecins_list.filter(
            users__userprofile__commune__wilaya__pays=scope_user.userprofile.commune.wilaya.pays
        ).distinct()

    # -------------------------
    # ✅ Assignment scoping "commercial" (ALTERNATIVE DEMANDÉE)
    # - superviseur + visites!=3 => seulement ses medecins
    # - superviseur + visites==3 => ses medecins + underusers (pour duo)
    # - delegué => seulement ses medecins (comme avant)
    # -------------------------
    if selected_user:
        if selected_is_supervisor and visites_value == "3":
            users_scope = selected_user.userprofile.usersunder.all() | User.objects.filter(id=selected_user.id)
            medecins_list = medecins_list.filter(users__in=users_scope).distinct()
        else:
            medecins_list = medecins_list.filter(users=selected_user).distinct()
    else:
        # Comportement normal quand aucun "commercial" sélectionné
        usr = request.user
        if usr and (not usr.is_superuser):
            if usr.userprofile.rolee in ["Superviseur", "Commercial", "CountryManager"] or _norm_speciality_rolee(usr) in [
                "Superviseur", "Superviseur_regional", "Superviseur_national", "Commercial", "Medico_commercial"
            ]:
                users_qs = usr.userprofile.usersunder.all() | User.objects.filter(id=usr.id)
                medecins_list = medecins_list.filter(users__in=users_qs).distinct()
            elif usr.userprofile.rolee != "CountryManager":
                medecins_list = medecins_list.filter(users=usr).distinct()
            elif usr.userprofile.rolee in ["Commercial"] and _norm_speciality_rolee(usr) in ["Commercial"]:
                query = Q(users__in=usr.userprofile.usersunder.all()) | Q(users=usr)
                medecins_list = medecins_list.filter(
                    query and specialite in ["Pharmacie", "Grossiste", "SuperGros"]
                ).distinct()

    # ------------------------------------------------------------------
    # VISITES FILTER LOGIC (0/1/2/3/4)
    # ------------------------------------------------------------------
    scoped_visites = Visite.objects.filter(**visites_filters).distinct()

    if visites_value == "0":
        medecins_list = medecins_list.exclude(visite__in=scoped_visites).distinct()

    elif visites_value == "1":
        medecins_list = medecins_list.filter(visite__in=scoped_visites).distinct()

    elif visites_value == "2":
        visited_multi_day_ids = (
            scoped_visites
            .annotate(day=TruncDate("rapport__added"))
            .values("medecin_id")
            .annotate(day_count=Count("day", distinct=True))
            .filter(day_count__gte=2)
            .values_list("medecin_id", flat=True)
        )
        medecins_list = medecins_list.filter(id__in=visited_multi_day_ids).distinct()

    elif visites_value in ["3", "4"]:
        base_visites_filters = dict(visites_filters)
        base_visites_filters.pop("rapport__user__username__icontains", None)

        base_visites_qs = (
            Visite.objects.filter(**base_visites_filters, medecin_id__in=medecins_list.values("id"))
            .distinct()
        )

        selected_keys = None
        if selected_user:
            selected_keys = set(
                scoped_visites
                .annotate(day=TruncDate("rapport__added"))
                .values_list("medecin_id", "day")
                .distinct()
            )

        agg_qs = (
            base_visites_qs
            .annotate(day=TruncDate("rapport__added"))
            .values("medecin_id", "day")
            .annotate(
                total_visites=Count("id", distinct=True),
                total_users=Count("rapport__user", distinct=True),
            )
        )

        suspect_medecin_ids = set()
        candidate_keys = set()

        for row in agg_qs:
            key = (row["medecin_id"], row["day"])
            if selected_keys is not None and key not in selected_keys:
                continue

            if row["total_visites"] >= 3:
                suspect_medecin_ids.add(row["medecin_id"])
            elif row["total_visites"] == 2 and row["total_users"] == 2:
                candidate_keys.add(key)

        grouped_users = defaultdict(set)
        if candidate_keys:
            for med_id, day, user_id in (
                base_visites_qs
                .annotate(day=TruncDate("rapport__added"))
                .values_list("medecin_id", "day", "rapport__user_id")
                .distinct()
            ):
                k = (med_id, day)
                if k in candidate_keys:
                    grouped_users[k].add(user_id)

        all_user_ids = set()
        for uset in grouped_users.values():
            all_user_ids.update(uset)

        under_map = {}
        role_map = {}

        if all_user_ids:
            users = (
                User.objects.filter(id__in=all_user_ids)
                .select_related("userprofile")
                .prefetch_related("userprofile__usersunder")
            )

            for u in users:
                # role
                try:
                    role_map[u.id] = (u.userprofile.rolee or "").strip()
                except Exception:
                    role_map[u.id] = ""

                # underusers
                try:
                    under_map[u.id] = set(u.userprofile.usersunder.values_list("id", flat=True))
                except Exception:
                    under_map[u.id] = set()

        def _is_valid_duo_pair(u1_id, u2_id):
            # u1 supervises u2 => u1 must REALLY be a Superviseur
            if u2_id in under_map.get(u1_id, set()):
                return role_map.get(u1_id) == "Superviseur"

            # u2 supervises u1 => u2 must REALLY be a Superviseur
            if u1_id in under_map.get(u2_id, set()):
                return role_map.get(u2_id) == "Superviseur"

            return False

        duo_medecin_ids = set()

        for (med_id, day), uset in grouped_users.items():
            if len(uset) != 2:
                continue
            u1, u2 = tuple(uset)

            if selected_user and selected_user.id not in uset:
                continue

            if _is_valid_duo_pair(u1, u2):
                duo_medecin_ids.add(med_id)
            else:
                suspect_medecin_ids.add(med_id)

        if visites_value == "3":
            medecins_list = medecins_list.filter(id__in=duo_medecin_ids).distinct()
        else:
            medecins_list = medecins_list.filter(id__in=suspect_medecin_ids).distinct()

    # -------------------------
    # Remaining filters (as-is)
    # -------------------------
    if request.GET.get("stock") != "":
        product = request.GET.get("stock")
        filter_by_period = False
        stock_filters = {}

        if request.GET.get("mindate"):
            stock_filters["visite__rapport__added__gte"] = request.GET.get("mindate")
            filter_by_period = True

        if request.GET.get("maxdate"):
            stock_filters["visite__rapport__added__lte"] = request.GET.get("maxdate")
            filter_by_period = True

        if filter_by_period:
            stock_filters["produit__id"] = product
            stock_filters["qtt__gte"] = 1
            medecins_availaible_stock = ProduitVisite.objects.filter(**stock_filters).values("medecin__id")
        else:
            medecins_availaible_stock = ProduitVisite.objects.filter(
                medecin__isnull=False, produit__id=product, qtt__gte=1
            ).values("medecin__id")

        medecins_list = medecins_list.filter(id__in=medecins_availaible_stock)

    if request.GET.get("note") == "1":
        medecins_list = medecins_list.exclude(note="").exclude(note__isnull=True)

    if request.GET.get("priority") and request.GET.get("priority") != "":
        with_priority = (
            Medecin.objects.annotate(last_visite=Max("visite__rapport__added"))
            .filter(
                last_visite=F("visite__rapport__added"),
                visite__priority=request.GET.get("priority"),
            )
            .values("id")
            .distinct()
        )
        medecins_list = medecins_list.filter(id__in=with_priority)

    return medecins_list



def get_medecins(request):
    filters = {}
    visites_filters = {}
    params = request.GET
    print(params)  # Affiche un QueryDict

    q = Q()
    specialite = request.GET.get("specialite")

    if request.GET.get("pays") and request.GET.get("pays") != "0":
        filters["commune__wilaya__pays__id"] = request.GET.get("pays")

    if request.GET.get("wilaya") and request.GET.get("wilaya") != "0":
        filters["commune__wilaya__id"] = request.GET.get("wilaya")

    if request.GET.get("commune") and request.GET.get("commune") != "0":
        filters["commune__id"] = request.GET.get("commune")

    if request.GET.get("medecin") and request.GET.get("medecin") != "":
        if request.GET.get("medecin").isdigit():
            filters["id"] = request.GET.get("medecin")
        else:
            filters["nom__icontains"] = request.GET.get("medecin").lower()

    if request.GET.get("commercial") and request.GET.get("commercial") != "":
        commercial_input = request.GET.get("commercial").strip()
        # Extraire le username de la chaîne formatée
        if " - " in commercial_input:
            # Prendre la partie après le " - "
            username_filter = commercial_input.split(" - ")[0]
            filters["users__username__icontains"] = username_filter
        else:
            filters["users__username__icontains"] = commercial_input
    # filters['users__username__icontains']=request.GET.get("commercial")
    # q |= Q(users__first_name__icontains=request.GET.get("commercial"))
    # q |= Q(users__last_name__icontains=request.GET.get("commercial"))

    if request.GET.get("specialite") and request.GET.get("specialite") != "":
        if request.GET.get("specialite") == "commerciale":
            filters["specialite__in"] = ["Pharmacie", "Grossiste", "SuperGros"]
        elif request.GET.get("specialite") == "medicale":
            filters["specialite__in"] = [
                "Generaliste",
                "Généraliste",
                "Diabetologue",
                "Neurologue",
                "Interniste",
                "Psychologue",
                "Gynecologue",
                "Gynécologue",
                "Rumathologue",
                "Allergologue",
                "Phtisio",
                "Cardiologue",
                "Urologue",
                "Hematologue",
                "Orthopedie",
                "Nutritionist",
                "Dermatologue",
                "Gastrologue",
                "Endocrinologue",
                "Dentiste",
                "ORL",
                "Maxilo facial",
            ]
        else:
            filters["specialite__in"] = request.GET.get("specialite").split(",")

    if request.GET.get("classification"):
        filters["classification__in"] = request.GET.get("classification").split(",")

    if request.GET.get("deal") == "1":
        filters["medecin__isnull"] = False

    if request.GET.get("deal") == "0":
        filters["medecin__isnull"] = True

    if request.GET.get("note") == "2":
        q |= Q(note="")
        q |= Q(note__isnull=True)

    if request.GET.get("mindate"):
        visites_filters["rapport__added__gte"] = request.GET.get("mindate")

    if request.GET.get("maxdate"):
        visites_filters["rapport__added__lte"] = request.GET.get("maxdate")

    if request.GET.get("produit"):
        visites_filters["produits__id"] = request.GET.get("produit")

    # medecins_list = Medecin.objects.filter(**filters).order_by("nom")
    # Assuming you have references to the Medecin_recycle_bin and pharmacie_recycle_bin users
    medecin_recycle_bin_user = User.objects.get(username="Medecin_Recycle_Bin")
    pharmacie_recycle_bin_user = User.objects.get(username="Pharmacie_Recycle_Bin")

    medecins_list = (
        Medecin.objects.filter(**filters)
        .exclude(users__in=[medecin_recycle_bin_user, pharmacie_recycle_bin_user])
        .order_by("nom")
    )

    if q:
        medecins_list = medecins_list.filter(q)

    if request.GET.get("shared") == "2":
        medecins_list = Medecin.objects.annotate(num_users=Count("users")).filter(
            num_users__gt=1, id__in=[medecins_list.values("id")]
        )

    if request.GET.get("shared") == "1":
        medecins_list = Medecin.objects.annotate(num_users=Count("users")).filter(
            num_users=1, id__in=[medecins_list.values("id")]
        )

    medecins_list = medecins_list.distinct()

    if not request.user.is_superuser:
        medecins_list = medecins_list.filter(
            users__userprofile__commune__wilaya__pays=request.user.userprofile.commune.wilaya.pays
        )
        if request.user.userprofile.rolee in [
            "Superviseur",
            "Superviseur_regional",
            "Commercial",
            "Medico_commercial",
            "Superviseur_national",
        ]:
            query = Q()
            query = Q(users__in=request.user.userprofile.usersunder.all())
            query |= Q(users=request.user)
            medecins_list = medecins_list.filter(query)
            # medecins_list=medecins_list.filter(users__in=request.user.userprofile.usersunder.all())

        elif request.user.userprofile.rolee != "CountryManager":
            medecins_list = medecins_list.filter(users=request.user)
        elif request.user.userprofile.rolee in [
            "Commercial"
        ] and request.user.userprofile.speciality_rolee in ["Commercial"]:
            query = Q()
            query = Q(users__in=request.user.userprofile.usersunder.all())
            query |= Q(users=request.user)
            medecins_list = medecins_list.filter(
                query and specialite in ["Pharmacie", "Grossiste", "SuperGros"]
            )

    visites = Visite.objects.filter(**visites_filters).distinct()

    if request.GET.get("visites") == "0":
        medecins_list = medecins_list.exclude(visite__in=visites).distinct()

    if request.GET.get("visites") == "1" or request.GET.get("visites") == "2":
        medecins_list = medecins_list.filter(visite__in=visites).distinct()

    if request.GET.get("visites") == "2":
        visites_count_medcin = (
            Visite.objects.filter(**visites_filters)
            .distinct()
            .values("medecin__id")
            .annotate(dcount=Count("medecin__id"))
        )
        visited_more_one = [
            v["medecin__id"] for v in visites_count_medcin if v["dcount"] > 2
        ]
        medecins_list = medecins_list.filter(id__in=visited_more_one)
    if request.GET.get("visites") == "3":
        print("visites egal a 3")
        visites_count_medcin = (
            Visite.objects.filter(**visites_filters)
            .annotate(jour=TruncDate("rapport__added"))  # 👈 regroupe par jour
            .values("medecin__id", "jour")               # 👈 groupement par médecin et par jour
            .annotate(
                total_visites=Count("id", distinct=True),
                total_users=Count("rapport__user", distinct=True),
            )
            )

        # On garde les médecins avec 2 visites et 2 utilisateurs différents le même jour
        visited_more_one = [
            v["medecin__id"]
            for v in visites_count_medcin
            if v["total_visites"] == 2 and v["total_users"] == 2
        ]

        medecins_list = medecins_list.filter(id__in=visited_more_one)
    if request.GET.get("stock") != "":
        product = request.GET.get("stock")
        filter_by_period = False
        stock_filters = {}

        if request.GET.get("mindate"):
            stock_filters["visite__rapport__added__gte"] = request.GET.get("mindate")
            filter_by_period = True

        if request.GET.get("maxdate"):
            stock_filters["visite__rapport__added__lte"] = request.GET.get("maxdate")
            filter_by_period = True

        if filter_by_period:
            stock_filters["produit__id"] = product
            stock_filters["qtt__gte"] = 1
            medecins_availaible_stock = ProduitVisite.objects.filter(
                **stock_filters
            ).values("medecin__id")
        else:
            medecins_availaible_stock = ProduitVisite.objects.filter(
                medecin__isnull=False, produit__id=product, qtt__gte=1
            ).values("medecin__id")

        medecins_list = medecins_list.filter(id__in=medecins_availaible_stock)

    if request.GET.get("note") == "1":
        medecins_list = medecins_list.exclude(note="").exclude(note__isnull=True)

    if request.GET.get("priority") and request.GET.get("priority") != "":
        # visites=Visite.objects.filter(medecin__id__in=medecins_list.values("id"))
        with_priority = (
            Medecin.objects.annotate(last_visite=Max("visite__rapport__added"))
            .filter(
                last_visite=F("visite__rapport__added"),
                visite__priority=request.GET.get("priority"),
            )
            .values("id")
            .distinct()
        )
        medecins_list = medecins_list.filter(id__in=with_priority)
    # print(f"\n\n\n{medecins_list}\n\n\n")

    return medecins_list


# def add_filters(request, filters):
#     if request.GET.get("pays") and request.GET.get("pays") != "0":
#         filters["commune__wilaya__pays__id"] = request.GET.get("pays")
#     if request.GET.get("wilaya") and request.GET.get("wilaya") != "0":
#         filters["commune__wilaya__id"] = request.GET.get("wilaya")
#     if request.GET.get("commune") and request.GET.get("commune") != "0":
#         filters["commune__id"] = request.GET.get("commune")
#     return filters


# def apply_medecin_filter(medecin):
#     filter_dict = {}
#     if medecin.isdigit():
#         filter_dict["id"] = medecin
#     elif len(medecin) > 4:
#         filter_dict["nom__icontains"] = medecin.lower()
#     return filter_dict


# def apply_commercial_filter(commercial_input):
#     filter_dict = {}
#     commercial_input = commercial_input.strip()
#     if " - " in commercial_input:
#         username_filter = commercial_input.split(" - ")[0]
#         filter_dict["users__username__icontains"] = username_filter
#     else:
#         filter_dict["users__username__icontains"] = commercial_input
#     return filter_dict


# def apply_speciality_and_classification_filters(request, filters):
#     if request.GET.get("specialite"):
#         specialite = request.GET.get("specialite")
#         if specialite == "commerciale":
#             filters["specialite__in"] = ["Pharmacie", "Grossiste", "SuperGros"]
#         elif specialite == "medicale":
#             filters["specialite__in"] = [
#                 "Generaliste",
#                 "Généraliste",
#                 "Diabetologue",
#                 "Neurologue",
#                 "Interniste",
#                 "Psychologue",
#                 "Gynecologue",
#                 "Gynécologue",
#                 "Rumathologue",
#                 "Allergologue",
#                 "Phtisio",
#                 "Cardiologue",
#                 "Urologue",
#                 "Hematologue",
#                 "Orthopedie",
#                 "Nutritionist",
#                 "Dermatologue",
#                 "Gastrologue",
#                 "Endocrinologue",
#                 "Dentiste",
#                 "ORL",
#                 "Maxilo facial",
#             ]
#         else:
#             filters["specialite__in"] = specialite.split(",")

#     if request.GET.get("classification"):
#         filters["classification__in"] = request.GET.get("classification").split(",")

#     if request.GET.get("deal") == "1":
#         filters["deal__isnull"] = False
#     elif request.GET.get("deal") == "0":
#         filters["deal__isnull"] = True


# def filter_by_user_profile(request, medecins_list):
#     if not request.user.is_superuser:
#         medecins_list = medecins_list.filter(
#             users__userprofile__commune__wilaya__pays=request.user.userprofile.commune.wilaya.pays
#         )
#         if request.user.userprofile.rolee in [
#             "Superviseur",
#             "Superviseur_regional",
#             "Commercial",
#             "Medico_commercial",
#             "Superviseur_national",
#         ]:
#             query = Q(users__in=request.user.userprofile.usersunder.all()) | Q(
#                 users=request.user
#             )
#             medecins_list = medecins_list.filter(query)
#         elif request.user.userprofile.rolee != "CountryManager":
#             medecins_list = medecins_list.filter(users=request.user)
#         elif (
#             request.user.userprofile.rolee == "Commercial"
#             and request.user.userprofile.speciality_rolee == "Commercial"
#         ):
#             query = Q(users__in=request.user.userprofile.usersunder.all()) | Q(
#                 users=request.user
#             )
#             medecins_list = medecins_list.filter(
#                 query, specialite__in=["Pharmacie", "Grossiste", "SuperGros"]
#             )
#     return medecins_list


# def get_medecins(request):
#     filters = {}
#     q = Q()

#     commercial_input = request.GET.get("commercial")
#     medecin = request.GET.get("medecin")

#     if commercial_input or (medecin and len(medecin) > 4):
#         filters = add_filters(request, filters)
#         filters.update(apply_medecin_filter(medecin))
#         filters.update(apply_commercial_filter(commercial_input))

#         apply_speciality_and_classification_filters(request, filters)

#         recycled_users = [
#             User.objects.get(username="Medecin_Recycle_Bin"),
#             User.objects.get(username="Pharmacie_Recycle_Bin"),
#         ]
#         medecins_list = Medecin.objects.exclude(users__in=recycled_users).filter(
#             **filters
#         )

#         medecins_list = filter_by_user_profile(request, medecins_list)

#         return medecins_list  # Renvoie le queryset de médecins

#     return Medecin.objects.none()

