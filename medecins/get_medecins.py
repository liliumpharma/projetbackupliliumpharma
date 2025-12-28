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
    
    if request.GET.get("commercial"):
        visites_filters["rapport__user__username__icontains"] = request.GET.get("commercial").split(" - ")[0]

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
    uu = request.GET.get("commercial").split(" - ")[0]
    if uu:
        try:
            usr = User.objects.filter(username=uu).first()
        except:
            usr = request.user
    else:
        usr = request.user
    if usr is None:
        usr = request.user

    if not usr.is_superuser:
        medecins_list = medecins_list.filter(
            users__userprofile__commune__wilaya__pays=usr.userprofile.commune.wilaya.pays
        )
        print(f"medecins list dans 147 est : {medecins_list}")
        if usr.userprofile.rolee in [
            "Superviseur",
            "Superviseur_regional",
            "Commercial",
            "Medico_commercial",
            "Superviseur_national",
        ]:
            query = Q()
            users_qs = usr.userprofile.usersunder.all() | User.objects.filter(id=usr.id)
            query = Q(users__in=users_qs)
            #query |= Q(users=usr)
            medecins_list = medecins_list.filter(query)
            print(f"medecins list dans 160 est : {medecins_list}")
            # medecins_list=medecins_list.filter(users__in=request.user.userprofile.usersunder.all())

        elif usr.userprofile.rolee != "CountryManager":
            medecins_list = medecins_list.filter(users=usr)
        elif usr.userprofile.rolee in [
            "Commercial"
        ] and usr.userprofile.speciality_rolee in ["Commercial"]:
            query = Q()
            query = Q(users__in=usr.userprofile.usersunder.all())
            query |= Q(users=usr)
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
        ff = request.GET.get("commercial")
        fff = ff.split(" - ")[0]
        us = User.objects.filter(username=fff).first()
        print(f"le user selectionne est {us}")
        user_under = User.objects.none()
        sup_user = User.objects.none()
        if us.userprofile.speciality_rolee in ["Superviseur_regional","Superviseur_national"]:
            print("le user selection est superviseur")
            user_under = us.userprofile.usersunder.exclude(id=us.id)
            print(f"les users under sont {user_under}")
        elif us.userprofile.speciality_rolee in ["Medico_commercial","Commercial"]:
            print("le user selection est delegue")
            sup_user = User.objects.filter(userprofile_usersunder=us)
        all_visites = Visite.objects.filter(**visites_filters)
        print(f"all visites apres les filtres {all_visites}")
        visites_commun = Visite.objects.none()
        visites_commun_list = []
        for v in all_visites:
            if us.userprofile.speciality_rolee in ["Superviseur_regional","Superviseur_national"]:
                visites_under = Visite.objects.filter(rapport__added=v.rapport.added, rapport__user__in=user_under,medecin=v.medecin)
                if all_visites.exists():
                    print("ouiiii une vistes commun")
                    visites_commun_list.extend(chain([v], visites_under))
                    v_qs = Visite.objects.filter(id=v.id).annotate(jour=TruncDate("rapport__added"))
                    visites_under = visites_under.annotate(jour=TruncDate("rapport__added"))
                    visites_commun = visites_commun.union(v_qs, visites_under)
                    #visites_commun = visites_commun.union(visites_under)
            elif us.userprofile.speciality_rolee in ["Medico_commercial","Commercial"]:
                visites_super = Visite.objects.filter(rapport__added=v.rapport.added, rapport__user__in=sup_user,medecin=v.medecin)
                if visites_super.exists():
                    visites_commun_list.extend(chain([v], visites_super ))
                    v_qs = Visite.objects.filter(id=v.id).annotate(jour=TruncDate("rapport__added"))
                    visites_super = visites_super.annotate(jour=TruncDate("rapport__added"))
                    visites_commun = visites_commun.union(v_qs, visites_super)
                    #visites_commun = visites_commun.union(visites_super)
        grouped = defaultdict(lambda: {"total_visites": 0, "total_users": set()})
        for visite in visites_commun_list:
            jour = visite.rapport.added
            medecin_id = visite.medecin.id
            key = (medecin_id, jour)
            grouped[key]["total_visites"] += 1
            grouped[key]["total_users"].add(visite.rapport.user.id)
        print(f"visites commun est {visites_commun}")
        print(f"visites commun list est {visites_commun_list}")
        #visites_count_medcin = visites_commun
        #(
         #   visites_commun
         #   .annotate(jour=TruncDate("rapport__added"))  # 👈 regroupe par jour
         #   #.values("medecin__id", "jour")               # 👈 groupement par médecin et par jour
         #   .annotate(
         #       total_visites=Count("id", distinct=True),
         #       total_users=Count("rapport__user", distinct=True),
         #   )
         #   )

        # On garde les médecins avec 2 visites et 2 utilisateurs différents le même jour
        #visited_more_one = [
        #    v["medecin__id"]
        #    for v in visites_count_medcin
        #    if v["total_visites"] == 2 and v["total_users"] == 2
        #]
        
        visited_more_one = [
            medecin_id
            for (medecin_id, jour), data in grouped.items()
            if data["total_visites"] == 2 and len(data["total_users"]) == 2
        ]
        print(f"visites more than one {visited_more_one}")
        #medecins_list = medecins_list.filter(id__in=visited_more_one)
        medecins_list = Medecin.objects.filter(id__in=visited_more_one)
        print(f"medecins_list est ::: {medecins_list}")
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

