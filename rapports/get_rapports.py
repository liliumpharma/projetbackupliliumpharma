from django.http import JsonResponse
from rapports.models import Rapport, Visite
from django.db.models import Q
from produits.models import Produit, ProduitVisite
from regions.models import *
from medecins.models import *
from django.utils import timezone
from accounts.models import UserProfile

# def rapport_list(request):
#     filters = {}
#     user = request.user

#     if request.GET.get("pays") and request.GET.get("pays") != "0":
#         filters['user__userprofile__commune__wilaya__pays__id'] = request.GET.get("pays")
#     if request.GET.get("wilaya") and request.GET.get("wilaya") != "0":
#         filters['visite__medecin__commune__wilaya__id'] = request.GET.get("wilaya")
#     if request.GET.get("commune") and request.GET.get("commune") != "0":
#         filters['visite__medecin__commune__id'] = request.GET.get("commune")
#     if request.GET.get("medecin") and request.GET.get("medecin") != "":
#         if request.GET.get("medecin").isnumeric():
#             filters['id'] = request.GET.get("medecin")
#         else:
#             filters['visite__medecin__nom__icontains'] = request.GET.get("medecin")
#     if request.GET.get("priority") and request.GET.get("priority") != "0":
#         filters['visite__priority'] = request.GET.get("priority")
#     if request.GET.get("mindate") and request.GET.get("mindate") != "":
#         filters['added__gte'] = request.GET.get("mindate")
#     if request.GET.get("maxdate") and request.GET.get("maxdate") != "":
#         filters['added__lte'] = request.GET.get("maxdate")
#     if request.GET.get("specialite") and request.GET.get("specialite") != "":
#         specialite = request.GET.get("specialite")
#         if specialite == "commerciale":
#             filters['visite__medecin__specialite__in'] = ['Pharmacie', 'Grossiste', 'SuperGros']
#         elif specialite == "medicale":
#             filters['visite__medecin__specialite__in'] = [
#                 'Generaliste', 'Diabetologue', 'Interniste', 'Neurologue', 'Psychologue',
#                 'Gynecologue', 'Rumathologue', 'Allergologue', 'Phtisio', 'Cardiologue',
#                 'Urologue', 'Hematologue', 'Orthopedie', 'Nutritionist', 'Dermatologue'
#             ]
#         else:
#             filters['visite__medecin__specialite__in'] = specialite.split(",")
#     if request.GET.get("classification") and request.GET.get("classification") != "":
#         filters['visite__medecin__classification__in'] = request.GET.get("classification").split(",")
#     if request.GET.get("produit") and request.GET.get("produit") != "":
#         filters['visite__produits__id'] = request.GET.get("produit")
#     if request.GET.get("note") and request.GET.get("note") != "":
#         filters['note'] = request.GET.get("note")
#     if request.GET.get("commercial") and request.GET.get("commercial") != "":
#         filters['user__username__icontains'] = request.GET.get("commercial")
#     if request.GET.get("deal") is not None:
#         filters['visite__medecin__deal__isnull'] = (request.GET.get("deal") == "0")

#     rapports_list = Rapport.objects.filter(**filters).order_by("-added")

#     # Filtrer par rôles et permissions
#     if not user.is_superuser:
#         rapports_list = rapports_list.filter(user__userprofile__commune__wilaya__pays=user.userprofile.commune.wilaya.pays)
#         user_role = user.userprofile.speciality_rolee
#         if user_role == "CountryManager":
#             rapports_list = rapports_list.filter(user__userprofile__company=user.userprofile.company)
#         elif user_role == "Superviseur_national":
#             rapports_list = rapports_list.filter(Q(user__in=user.userprofile.usersunder.all()) | Q(user=user))
#         else:
#             rapports_list = rapports_list.filter(user=user)

#     return rapports_list


from django.db.models import Q
from django.utils import timezone
from datetime import timedelta

# def rapport_list(request):
#     filters = {}
#     q = Q()
#     user = request.user

#     def add_filter(param, db_field, func=None):
#         value = request.GET.get(param)
#         if value and value != "0":
#             filters[db_field] = func(value) if func else value

#     add_filter("pays", 'user__userprofile__commune__wilaya__pays__id')
#     add_filter("wilaya", 'visite__medecin__commune__wilaya__id')
#     add_filter("commune", 'visite__medecin__commune__id')

#     medecin = request.GET.get("medecin")
#     if medecin:
#         if medecin.isnumeric():
#             filters['id'] = medecin
#         else:
#             filters['visite__medecin__nom__icontains'] = medecin

#     add_filter("priority", 'visite__priority')
#     add_filter("mindate", 'added__gte')
#     add_filter("maxdate", 'added__lte')
#     add_filter("produit", 'visite__produits__id')
#     add_filter("note", 'note')
#     add_filter("commercial", 'user__username__icontains')

#     specialite = request.GET.get("specialite")
#     if specialite:
#         if specialite == "commerciale":
#             filters['visite__medecin__specialite__in'] = ['Pharmacie', 'Grossiste', 'SuperGros']
#         elif specialite == "medicale":
#             filters['visite__medecin__specialite__in'] = [
#                 'Generaliste', 'Diabetologue', 'Interniste', 'Neurologue', 'Psychologue',
#                 'Gynecologue', 'Rumathologue', 'Allergologue', 'Phtisio', 'Cardiologue',
#                 'Urologue', 'Hematologue', 'Orthopedie', 'Nutritionist', 'Dermatologue'
#             ]
#         else:
#             filters['visite__medecin__specialite__in'] = specialite.split(",")

#     classification = request.GET.get("classification")
#     if classification:
#         filters['visite__medecin__classification__in'] = classification.split(",")

#     deal = request.GET.get("deal")
#     if deal == "1":
#         filters['visite__medecin__deal__isnull'] = False
#     elif deal == "0":
#         filters['visite__medecin__deal__isnull'] = True

#     # Filtrer les rapports du jour courant
#     today = timezone.now().date()
#     five_days_ago = today - timedelta(days=10)
#     filters['added__range'] = (five_days_ago, today)

#     rapports_list = Rapport.objects.filter(**filters).order_by("-added").distinct()

#     if not request.user.is_superuser:
#         rapports_list = rapports_list.filter(user__userprofile__commune__wilaya__pays=user.userprofile.commune.wilaya.pays)

#         if user.userprofile.speciality_rolee == "CountryManager":
#             company_field_value = user.userprofile.company
#             rapports_list = rapports_list.filter(user__userprofile__company=company_field_value)
#         elif user.userprofile.speciality_rolee == "Superviseur_national":
#             rapports_list = rapports_list.filter(Q(user__in=user.userprofile.usersunder.all()) | Q(user=user))
#         else:
#             print(f"{request.user} getting repports")
#             rapports_list = rapports_list.filter(user=user)

#     return rapports_list


# ---------- FROM HERE ------------


# def rapport_list(request):
#     filters = {}
#     user = request.user

#     # Extraction des filtres depuis la requête GET
#     mindate = request.GET.get("mindate")
#     maxdate = request.GET.get("maxdate")
#     specialite = request.GET.get("specialite")
#     commercial_input = request.GET.get("commercial", "").strip()

#     # Ajout des filtres de dates
#     if mindate:
#         filters["added__gte"] = mindate
#     if maxdate:
#         filters["added__lte"] = maxdate

#     # Filtrage par spécialité avec mapping simplifié
#     if specialite:
#         specialite_mapping = {
#             "commerciale": ["Pharmacie", "Grossiste", "SuperGros"],
#             "medicale": [
#                 "Generaliste",
#                 "Diabetologue",
#                 "Interniste",
#                 "Neurologue",
#                 "Psychologue",
#                 "Gynecologue",
#                 "Rumathologue",
#                 "Allergologue",
#                 "Phtisio",
#                 "Cardiologue",
#                 "Urologue",
#                 "Hematologue",
#                 "Orthopedie",
#                 "Nutritionist",
#                 "Dermatologue",
#             ],
#         }
#         filters["visite__medecin__specialite__in"] = specialite_mapping.get(
#             specialite, specialite.split(",")
#         )

#     # Filtrage par commercial
#     if commercial_input:
#         filters["user__username__icontains"] = (
#             commercial_input.split(" - ")[0]
#             if " - " in commercial_input
#             else commercial_input
#         )

#     # Récupération initiale des rapports filtrés
#     rapports_list = Rapport.objects.filter(**filters).order_by("-added").distinct()

#     # Filtrage spécifique pour les utilisateurs non superadmin
#     if not user.is_superuser:
#         # Limiter aux rapports du même pays que l'utilisateur
#         rapports_list = rapports_list.filter(
#             user__userprofile__commune__wilaya__pays=user.userprofile.commune.wilaya.pays
#         )

#         # Gestion des rôles de l'utilisateur
#         if user.userprofile.rolee in [
#             "Superviseur",
#             "Superviseur_regional",
#             "Medico_commercial",
#             "Commercial",
#             "Superviseur_national",
#         ]:
#             # L'utilisateur peut voir ses propres rapports et ceux de ses subordonnés
#             rapports_list = rapports_list.filter(
#                 Q(user=user) | Q(user__in=user.userprofile.usersunder.all())
#             )
#         else:
#             # Filtrage par entreprise pour les autres rôles
#             rapports_list = rapports_list.filter(
#                 user__userprofile__company=user.userprofile.company
#             )

#     return rapports_list

# from django.db.models import Q


# def rapport_list(request):
#     filters = {}
#     user = request.user
#     user_profile = user.userprofile  # Fetch the user profile once

#     # Extraction des filtres depuis la requête GET
#     mindate = request.GET.get("mindate")
#     maxdate = request.GET.get("maxdate")
#     specialite = request.GET.get("specialite")
#     commercial_input = request.GET.get("commercial", "").strip()

#     # Ajout des filtres de dates
#     if mindate:
#         filters["added__gte"] = mindate
#     if maxdate:
#         filters["added__lte"] = maxdate

#     print("min date " + str(mindate))
#     print("max date " + str(maxdate))

#     # Filtrage par spécialité
#     if specialite:
#         specialite_mapping = {
#             "commerciale": ["Pharmacie", "Grossiste", "SuperGros"],
#             "medicale": [
#                 "Generaliste",
#                 "Diabetologue",
#                 "Interniste",
#                 "Neurologue",
#                 "Psychologue",
#                 "Gynecologue",
#                 "Rumathologue",
#                 "Allergologue",
#                 "Phtisio",
#                 "Cardiologue",
#                 "Urologue",
#                 "Hematologue",
#                 "Orthopedie",
#                 "Nutritionist",
#                 "Dermatologue",
#             ],
#         }
#         filters["visite__medecin__specialite__in"] = specialite_mapping.get(
#             specialite, specialite.split(",")
#         )

#     # Filtrage par commercial
#     if commercial_input:
#         filters["user__username__icontains"] = (
#             commercial_input.split(" - ")[0]
#             if " - " in commercial_input
#             else commercial_input
#         )

#     # Récupération initiale des rapports filtrés
#     rapports_list = Rapport.objects.filter(**filters).order_by("-added").distinct()

#     # Filtrage spécifique pour les utilisateurs non superadmin
#     if not user.is_superuser:
#         pays = user_profile.commune.wilaya.pays
#         rapports_list = rapports_list.filter(
#             user__userprofile__commune__wilaya__pays=pays
#         )

#         # Gestion des rôles de l'utilisateur
#         if user_profile.rolee in [
#             "Superviseur",
#             "Superviseur_regional",
#             "Medico_commercial",
#             "Commercial",
#             "Superviseur_national",
#         ]:
#             rapports_list = rapports_list.filter(
#                 Q(user=user) | Q(user__in=user_profile.usersunder.all())
#             )
#         else:
#             rapports_list = rapports_list.filter(
#                 user__userprofile__company=user_profile.company
#             )

#     return rapports_list


def add_date_filters(request, filters):
    mindate = request.GET.get("mindate")
    maxdate = request.GET.get("maxdate")

    # Check if both mindate and maxdate are empty
    if not mindate and not maxdate:
        return (
            filters,
            None,
        )  # Return an empty filters dictionary and indicate no date filter applied

    if mindate:
        filters["added__gte"] = mindate
    if maxdate:
        filters["added__lte"] = maxdate

    return filters, (mindate, maxdate)


def add_speciality_filter(request, filters):
    specialite = request.GET.get("specialite")
    if specialite:
        specialite_mapping = {
            "commerciale": ["Pharmacie", "Grossiste", "SuperGros"],
            "medicale": [
                "Generaliste",
                "Diabetologue",
                "Interniste",
                "Neurologue",
                "Psychologue",
                "Gynecologue",
                "Rumathologue",
                "Allergologue",
                "Phtisio",
                "Cardiologue",
                "Urologue",
                "Hematologue",
                "Orthopedie",
                "Nutritionist",
                "Dermatologue",
            ],
        }
        filters["visite__medecin__specialite__in"] = specialite_mapping.get(
            specialite, specialite.split(",")
        )
    return filters


def add_commercial_filter(request, filters):
    commercial_input = request.GET.get("commercial", "").strip()
    profile = UserProfile.objects.get(user=request.user.id)
    if commercial_input!= '' and commercial_input.isdigit() and int(commercial_input) == 1000000:
        print("il veux tous les rapports de users")
        if request.user.is_superuser or profile.speciality_rolee == "Superviseur_national" or profile.speciality_rolee == "CountryManager":
            authorized_users = User.objects.filter(userprofile__family__in=["lilium Pharma", "Lilium1", "Lilium2", "orient Bio", "Aniya_Pharm", "production", "Administration"])
            filters["user__id__in"] = [u.id for u in authorized_users]
            return filters
        elif profile.speciality_rolee == "Superviseur_regional":
            authorized_users = profile.usersunder.all()
            filters["user__id__in"] = [u.id for u in authorized_users]
            return filters
    # Vérifier si commercial_input est un entier
    if commercial_input.isdigit():
        filters["user__id"] = int(commercial_input)
    else:
        # Si ce n'est pas un entier, effectuer la recherche par username
        filters["user__username__icontains"] = (
            commercial_input.split(" - ")[0]
            if " - " in commercial_input
            else commercial_input
        )

    return filters


def add_note_filter(request, filters):
    note = request.GET.get("note")
    if note:

        print("----- note :"+str(note))
        filters["note"] = note

    return filters



def apply_user_specific_filters(user, user_profile, rapports_list):
    if not user.is_superuser:
        pays = user_profile.commune.wilaya.pays
        rapports_list = rapports_list.filter(
            user__userprofile__commune__wilaya__pays=pays
        )

        # Manage user roles
        if user_profile.rolee in [
            "Superviseur",
            "Superviseur_regional",
            "Medico_commercial",
            "Commercial",
            "Superviseur_national",
        ]:
            rapports_list = rapports_list.filter(
                Q(user=user) | Q(user__in=user_profile.usersunder.all())
            )
        else:
            rapports_list = rapports_list.filter(
                user__userprofile__company=user_profile.company
            )

    return rapports_list


def rapport_list(request, imp=0):
    if imp == 1:
        print("imp est 1")
    else:
        print("imp n'est pas 1")
    filters = {}
    user = request.user
    user_profile = user.userprofile  # Fetch the user profile once
    commercial_input = request.GET.get("commercial", "").strip()
    print(str(request))
    if imp==1 and int(commercial_input) == 1000000:
        if user_profile.speciality_rolee == "Superviseur_regional":
            print("tous user under")
            filters["user__in"] = user_profile.usersunder.all()
        if user.is_superuser or user_profile.speciality_rolee == "CountryManager" or user_profile.speciality_rolee == "Superviseur_national":
            print(" tous user medico commercial")
            filters["user__in"] = User.objects.filter(userprofile__speciality_rolee__in=["Medico_commercial", "Commercial"])
    # Add date filters
    filters, dates = add_date_filters(request, filters)
    if dates is None:
        print("dates is None")
        return JsonResponse(
            [], safe=False
        )  # Return an empty response if no date filters are applied
    
    print("ls rapport ")

    # Add speciality filters
    filters = add_speciality_filter(request, filters)

    # Add Note filters
    filters = add_note_filter(request, filters)

    # Add commercial filters
    filters = add_commercial_filter(request, filters)
    
    # Retrieve the filtered rapports
    rapports_list = Rapport.objects.filter(**filters).order_by("-added").distinct()
    print("je suis la 1111111111111111")
    # Apply user-specific filtering
    rapports_list = apply_user_specific_filters(user, user_profile, rapports_list)
    print(str(rapports_list.count()))

    # Append the visit count to each rapport
    rapport_visit_counts = []
    for rapport in rapports_list:
        visit_count = Visite.objects.filter(rapport=rapport).count()  # Count the number of visits for each rapport
        rapport_visit_counts.append({
            "rapport_id": rapport.id,
            "visit_count": visit_count
        })
        # print(f"Rapport ID: {rapport.id}, Visit Count: {visit_count}")

    # You can return both rapports and the visit counts if needed
    return rapports_list  # Return the queryset of rapports and visit counts



# def rapport_list(request):
#     filters = {}
#     q = Q()
#     user = request.user
#     com = request.GET.get("commercial")
#     print("############################################################")
#     print(str(com))
#     # filters['user__username__icontains']=user.username
#     # if  request.GET.get("pays") and request.GET.get("pays")!="0" :
#     #     filters['user__userprofile__commune__wilaya__pays__id']=request.GET.get("pays")
#     # if  request.GET.get("wilaya") and request.GET.get("wilaya")!="0" :
#     #     filters['visite__medecin__commune__wilaya__id']=request.GET.get("wilaya")
#     # if  request.GET.get("commune") and request.GET.get("commune")!="0" :
#     #     filters['visite__medecin__commune__id']=request.GET.get("commune")
#     # if  request.GET.get("medecin") and request.GET.get("medecin")!="" :
#     #     if request.GET.get("medecin").isnumeric():
#     #         filters['id']=request.GET.get("medecin")
#     #     else:
#     #         filters['visite__medecin__nom__icontains']=request.GET.get("medecin")
#     # if  request.GET.get("priority") and request.GET.get("priority")!="0" :
#     #     filters['visite__priority']=request.GET.get("priority")
#     if request.GET.get("mindate") and request.GET.get("mindate") != "":
#         filters["added__gte"] = request.GET.get("mindate")
#     if request.GET.get("maxdate") and request.GET.get("maxdate") != "":
#         filters["added__lte"] = request.GET.get("maxdate")
#     if request.GET.get("specialite") and request.GET.get("specialite") != "":
#         if request.GET.get("specialite") == "commerciale":
#             filters["visite__medecin__specialite__in"] = [
#                 "Pharmacie",
#                 "Grossiste",
#                 "SuperGros",
#             ]
#         elif request.GET.get("specialite") == "medicale":
#             filters["visite__medecin__specialite__in"] = [
#                 "Generaliste",
#                 "Diabetologue",
#                 "Interniste",
#                 "Neurologue",
#                 "Psychologue",
#                 "Gynecologue",
#                 "Rumathologue",
#                 "Allergologue",
#                 "Phtisio",
#                 "Cardiologue",
#                 "Urologue",
#                 "Hematologue",
#                 "Orthopedie",
#                 "Nutritionist",
#                 "Dermatologue",
#             ]
#         else:
#             filters["visite__medecin__specialite__in"] = request.GET.get(
#                 "specialite"
#             ).split(",")
#     # if  request.GET.get("classification") and request.GET.get("classification")!="" :
#     #     filters['visite__medecin__classification__in']=request.GET.get("classification").split(",")
#     # if  request.GET.get("produit") and request.GET.get("produit")!="" :
#     #     filters['visite__produits__id']=request.GET.get("produit")
#     # if  request.GET.get("note") and request.GET.get("note")!="" :
#     #     filters['note']=request.GET.get("note")

#     if request.GET.get("commercial") and request.GET.get("commercial") != "":
#         commercial_input = request.GET.get("commercial").strip()
#         # Extraire le username de la chaîne formatée
#         if " - " in commercial_input:
#             # Prendre la partie après le " - "
#             username_filter = commercial_input.split(" - ")[0]
#             print("################# " + str(username_filter))
#             filters["user__username__icontains"] = username_filter
#         else:
#             filters["user__username__icontains"] = commercial_input
#     # if  request.GET.get("commercial") and request.GET.get("commercial")!="" :
#     #     filters['user__username__icontains']=request.GET.get("commercial")
#     # q |= Q(user__first_name__icontains=request.GET.get("commercial"))
#     # q |= Q(user__last_name__icontains=request.GET.get("commercial"))
#     # if  request.GET.get("deal")=="1" :
#     #     filters['visite__medecin__deal__isnull']=False
#     # if  request.GET.get("deal")=="0" :
#     #     filters['visite__medecin__deal__isnull']=True
#     rapports_list = Rapport.objects.filter(**filters).order_by("-added")
#     # rapports_list = Rapport.objects.filter(added__month=mois_courant, **filters).order_by("-added")
#     if q:
#         rapports_list = rapports_list.filter(q)
#     rapports_list = rapports_list.distinct()

#     if request.user.is_superuser:
#         query = Q()
#         # company_field_value = request.user.userprofile.company
#         # query |= Q(user__userprofile__company=company_field_value)
#         # rapports_list = rapports_list.filter(query)
#         print("######" + str(rapports_list))

#     else:
#         rapports_list = rapports_list.filter(
#             user__userprofile__commune__wilaya__pays=request.user.userprofile.commune.wilaya.pays
#         )
#         if request.user.userprofile.rolee in [
#             "Superviseur",
#             "Superviseur_regional",
#             "Medico_commercial",
#             "Commercial",
#             "Superviseur_national",
#         ]:
#             query = Q()
#             query = Q(user=request.user)
#             query |= Q(user__in=request.user.userprofile.usersunder.all())
#             rapports_list = rapports_list.filter(query)
#         else:
#             company_field_value = request.user.userprofile.company
#             query = Q()
#             query = Q(user__userprofile__company=company_field_value)
#             rapports_list = rapports_list.filter(query)

#     return rapports_list

# else:
#     print("hereeeeeee")

# if  request.GET.get("pays") and request.GET.get("pays")!="0" :
#     filters['user__userprofile__commune__wilaya__pays__id']=request.GET.get("pays")
# if  request.GET.get("wilaya") and request.GET.get("wilaya")!="0" :
#     filters['visite__medecin__commune__wilaya__id']=request.GET.get("wilaya")
# if  request.GET.get("commune") and request.GET.get("commune")!="0" :
#     filters['visite__medecin__commune__id']=request.GET.get("commune")
# if  request.GET.get("medecin") and request.GET.get("medecin")!="" :
#     if request.GET.get("medecin").isnumeric():
#         filters['id']=request.GET.get("medecin")
#     else:
#         filters['visite__medecin__nom__icontains']=request.GET.get("medecin")
# if  request.GET.get("priority") and request.GET.get("priority")!="0" :
#     filters['visite__priority']=request.GET.get("priority")
# if  request.GET.get("mindate") and request.GET.get("mindate")!="" :
#     filters['added__gte']=request.GET.get("mindate")
# if  request.GET.get("maxdate") and request.GET.get("maxdate")!="" :
#     filters['added__lte']=request.GET.get("maxdate")
# if  request.GET.get("specialite") and request.GET.get("specialite")!="" :
#     if request.GET.get("specialite")=="commerciale":
#         filters['visite__medecin__specialite__in']=['Pharmacie','Grossiste','SuperGros']
#     elif request.GET.get("specialite")=="medicale":
#         filters['visite__medecin__specialite__in']=['Generaliste','Diabetologue','Interniste','Neurologue','Psychologue','Gynecologue','Rumathologue','Allergologue','Phtisio','Cardiologue','Urologue','Hematologue','Orthopedie','Nutritionist','Dermatologue']
#     else:
#         filters['visite__medecin__specialite__in']=request.GET.get("specialite").split(",")
# if  request.GET.get("classification") and request.GET.get("classification")!="" :
#     filters['visite__medecin__classification__in']=request.GET.get("classification").split(",")
# if  request.GET.get("produit") and request.GET.get("produit")!="" :
#     filters['visite__produits__id']=request.GET.get("produit")
# if  request.GET.get("note") and request.GET.get("note")!="" :
#     filters['note']=request.GET.get("note")
# if  request.GET.get("commercial") and request.GET.get("commercial")!="" :
#     filters['user__username__icontains']=request.GET.get("commercial")
#     # q |= Q(user__first_name__icontains=request.GET.get("commercial"))
#     # q |= Q(user__last_name__icontains=request.GET.get("commercial"))
# if  request.GET.get("deal")=="1" :
#     filters['visite__medecin__deal__isnull']=False
# if  request.GET.get("deal")=="0" :
#     filters['visite__medecin__deal__isnull']=True
# rapports_list=Rapport.objects.filter(**filters).order_by("-added")
# if q:
#     rapports_list=rapports_list.filter(q)
# rapports_list=rapports_list.distinct()
# if not request.user.is_superuser:
#     rapports_list=rapports_list.filter(user__userprofile__commune__wilaya__pays=request.user.userprofile.commune.wilaya.pays)
#     if request.user.userprofile.speciality_rolee in ["CountryManager"]:
#         print("im country manager getting repports")
#         query = Q()
#         company_field_value = request.user.userprofile.company
#         query |= Q(user__userprofile__company=company_field_value)
#         rapports_list=rapports_list.filter(query)
#     else:
#         if request.user.userprofile.speciality_rolee in ["Superviseur_national"]:
#             print("im supervisor national getting repports")
#             query = Q()
#             query = Q(user__in=request.user.userprofile.usersunder.all())
#             query |= Q(user=request.user)
#             rapports_list=rapports_list.filter(query)
#         else:
#             user=request.user.username
#             print(f'im {user} simple delegate getting repports')
#             query = Q(user=request.user)
#             query |= Q(user__in=request.user.userprofile.usersunder.all())
#             rapports_list=rapports_list.filter(query)

# return rapports_list


# ---------- TO HERE ------------


# def rapport_list(request):
#     filters={}
#     q = Q()
#     user = request.user
#     print()
#     if user.userprofile.rolee == "Commercial":
#         print("hereeeeeee3")

#         mois_courant = timezone.now().month


#         filters['user__username__icontains']=user.username

#         if  request.GET.get("pays") and request.GET.get("pays")!="0" :
#             filters['user__userprofile__commune__wilaya__pays__id']=request.GET.get("pays")

#         if  request.GET.get("wilaya") and request.GET.get("wilaya")!="0" :
#             filters['visite__medecin__commune__wilaya__id']=request.GET.get("wilaya")

#         if  request.GET.get("commune") and request.GET.get("commune")!="0" :
#             filters['visite__medecin__commune__id']=request.GET.get("commune")

#         if  request.GET.get("medecin") and request.GET.get("medecin")!="" :
#             if request.GET.get("medecin").isnumeric():
#                 filters['id']=request.GET.get("medecin")
#             else:
#                 filters['visite__medecin__nom__icontains']=request.GET.get("medecin")

#         if  request.GET.get("priority") and request.GET.get("priority")!="0" :
#             filters['visite__priority']=request.GET.get("priority")

#         if  request.GET.get("mindate") and request.GET.get("mindate")!="" :
#             filters['added__gte']=request.GET.get("mindate")

#         if  request.GET.get("maxdate") and request.GET.get("maxdate")!="" :
#             filters['added__lte']=request.GET.get("maxdate")

#         if  request.GET.get("specialite") and request.GET.get("specialite")!="" :
#             if request.GET.get("specialite")=="commerciale":
#                 filters['visite__medecin__specialite__in']=['Pharmacie','Grossiste','SuperGros']
#             elif request.GET.get("specialite")=="medicale":
#                 filters['visite__medecin__specialite__in']=['Generaliste','Diabetologue','Interniste','Neurologue','Psychologue','Gynecologue','Rumathologue','Allergologue','Phtisio','Cardiologue','Urologue','Hematologue','Orthopedie','Nutritionist','Dermatologue']
#             else:
#                 filters['visite__medecin__specialite__in']=request.GET.get("specialite").split(",")


#         if  request.GET.get("classification") and request.GET.get("classification")!="" :
#             filters['visite__medecin__classification__in']=request.GET.get("classification").split(",")

#         if  request.GET.get("produit") and request.GET.get("produit")!="" :
#             filters['visite__produits__id']=request.GET.get("produit")

#         if  request.GET.get("note") and request.GET.get("note")!="" :
#             filters['note']=request.GET.get("note")

#             # q |= Q(user__first_name__icontains=request.GET.get("commercial"))
#             # q |= Q(user__last_name__icontains=request.GET.get("commercial"))

#         if  request.GET.get("deal")=="1" :
#             filters['visite__medecin__deal__isnull']=False

#         if  request.GET.get("deal")=="0" :
#             filters['visite__medecin__deal__isnull']=True

#         # rapports_list=Rapport.objects.filter(**filters).order_by("-added")
#         rapports_list = Rapport.objects.filter(added__month=mois_courant, **filters).order_by("-added")

#         if q:
#             rapports_list=rapports_list.filter(q)

#         rapports_list=rapports_list.distinct()


#         if not request.user.is_superuser:
#             rapports_list=rapports_list.filter(user__userprofile__commune__wilaya__pays=request.user.userprofile.commune.wilaya.pays)
#             if request.user.userprofile.rolee in ["Superviseur","Superviseur_regional","Medico_commercial","Commercial","Superviseur_national"]:
#                 query = Q()
#                 query |= Q(user=request.user)
#                 rapports_list=rapports_list.filter(query)


#         return rapports_list

#     else:
#         print("hereeeeeee")

#         if  request.GET.get("pays") and request.GET.get("pays")!="0" :
#             filters['user__userprofile__commune__wilaya__pays__id']=request.GET.get("pays")

#         if  request.GET.get("wilaya") and request.GET.get("wilaya")!="0" :
#             filters['visite__medecin__commune__wilaya__id']=request.GET.get("wilaya")

#         if  request.GET.get("commune") and request.GET.get("commune")!="0" :
#             filters['visite__medecin__commune__id']=request.GET.get("commune")

#         if  request.GET.get("medecin") and request.GET.get("medecin")!="" :
#             if request.GET.get("medecin").isnumeric():
#                 filters['id']=request.GET.get("medecin")
#             else:
#                 filters['visite__medecin__nom__icontains']=request.GET.get("medecin")

#         if  request.GET.get("priority") and request.GET.get("priority")!="0" :
#             filters['visite__priority']=request.GET.get("priority")

#         if  request.GET.get("mindate") and request.GET.get("mindate")!="" :
#             filters['added__gte']=request.GET.get("mindate")

#         if  request.GET.get("maxdate") and request.GET.get("maxdate")!="" :
#             filters['added__lte']=request.GET.get("maxdate")

#         if  request.GET.get("specialite") and request.GET.get("specialite")!="" :
#             if request.GET.get("specialite")=="commerciale":
#                 filters['visite__medecin__specialite__in']=['Pharmacie','Grossiste','SuperGros']
#             elif request.GET.get("specialite")=="medicale":
#                 filters['visite__medecin__specialite__in']=['Generaliste','Diabetologue','Interniste','Neurologue','Psychologue','Gynecologue','Rumathologue','Allergologue','Phtisio','Cardiologue','Urologue','Hematologue','Orthopedie','Nutritionist','Dermatologue']
#             else:
#                 filters['visite__medecin__specialite__in']=request.GET.get("specialite").split(",")


#         if  request.GET.get("classification") and request.GET.get("classification")!="" :
#             filters['visite__medecin__classification__in']=request.GET.get("classification").split(",")

#         if  request.GET.get("produit") and request.GET.get("produit")!="" :
#             filters['visite__produits__id']=request.GET.get("produit")

#         if  request.GET.get("note") and request.GET.get("note")!="" :
#             filters['note']=request.GET.get("note")

#         if  request.GET.get("commercial") and request.GET.get("commercial")!="" :
#             filters['user__username__icontains']=request.GET.get("commercial")
#             # q |= Q(user__first_name__icontains=request.GET.get("commercial"))
#             # q |= Q(user__last_name__icontains=request.GET.get("commercial"))

#         if  request.GET.get("deal")=="1" :
#             filters['visite__medecin__deal__isnull']=False

#         if  request.GET.get("deal")=="0" :
#             filters['visite__medecin__deal__isnull']=True

#         rapports_list=Rapport.objects.filter(**filters).order_by("-added")
#         if q:
#             rapports_list=rapports_list.filter(q)

#         rapports_list=rapports_list.distinct()


#         if not request.user.is_superuser:
#             rapports_list=rapports_list.filter(user__userprofile__commune__wilaya__pays=request.user.userprofile.commune.wilaya.pays)
#             if request.user.userprofile.rolee in ["Superviseur","Superviseur_regional","Medico_commercial","Commercial","Superviseur_national"]:
#                 query = Q()
#                 query = Q(user__in=request.user.userprofile.usersunder.all())
#                 query |= Q(user=request.user)
#                 rapports_list=rapports_list.filter(query)


#         return rapports_list


def get_visites(request):
    filters = {}
    produit = ""
    region = "/"
    specialite = "/"
    classification = "/"

    q = Q()
    commercial_input = request.GET.get("commercial", "").strip()


    # if request.GET.get("pays") and request.GET.get("pays") != "0":
    #     filters["medecin__commune__wilaya__pays__id"] = request.GET.get("pays")
    #     region = f'{Pays.objects.get(id=request.GET.get("pays"))}'

    # if request.GET.get("wilaya") and request.GET.get("wilaya") != "0":
    #     filters["medecin__commune__wilaya__id"] = request.GET.get("wilaya")
    #     wilaya = Wilaya.objects.get(id=request.GET.get("wilaya"))
    #     region = f"{wilaya.pays} {wilaya}"

    # if request.GET.get("commune") and request.GET.get("commune") != "0":
    #     filters["medecin__commune__id"] = request.GET.get("commune")
    #     commune = Commune.objects.get(id=request.GET.get("commune"))
    #     region = f"{commune.wilaya.pays} {commune.wilaya} {commune}"

    # if request.GET.get("medecin") and request.GET.get("medecin") != "":
    #     filters["medecin__nom__icontains"] = request.GET.get("medecin")

    if commercial_input:
        filters["medecin__users__username__icontains"] = commercial_input.split(" - ")[0]
        # q |= Q(medecin__users__first_name__icontains=request.GET.get("commercial"))
        # q |= Q(medecin__users__last_name__icontains=request.GET.get("commercial"))

    if request.GET.get("specialite") and request.GET.get("specialite") != "":
        if request.GET.get("specialite") == "commerciale":
            filters["medecin__specialite__in"] = ["Pharmacie", "Grossiste", "SuperGros"]
        elif request.GET.get("specialite") == "medicale":
            filters["medecin__specialite__in"] = [
                "Généraliste",
                "Diabetologue",
                "Neurologue",
                "Interniste",
                "Psychologue",
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
            ]
        else:
            filters["medecin__specialite__in"] = request.GET.get("specialite").split(
                ","
            )
        specialite = request.GET.get("specialite")

        print("********* specislite " + str(request.GET.get("specialite")))

    if request.GET.get("classification"):
        filters["medecin__classification__in"] = request.GET.get("classification")
        classification = request.GET.get("classification").split(",")

    if request.GET.get("mindate"):
        filters["rapport__added__gte"] = request.GET.get("mindate")

    if request.GET.get("maxdate"):
        filters["rapport__added__lte"] = request.GET.get("maxdate")

    if request.GET.get("priority") and request.GET.get("priority") != "0":
        filters["priority"] = request.GET.get("priority")

    if request.GET.get("produit"):
        filters["produits__id"] = request.GET.get("produit")
        produit += f'{Produit.objects.get(id=request.GET.get("produit")).nom} '

    # If visites=0, find doctors without visits between mindate and maxdate
    if request.GET.get("visites") == "0":
        # Filtrer les médecins déjà visités dans la plage de dates
        medecins_visited = Visite.objects.filter(
            rapport__added__gte=request.GET.get("mindate"),
            rapport__added__lte=request.GET.get("maxdate"),
            rapport__user__username__icontains=commercial_input.split(" - ")[0],
        ).values_list('medecin_id', flat=True)
        
        # Filtrer les médecins non visités en excluant ceux qui sont déjà visités
        medecins_non_visites = Medecin.objects.filter(
            users__username__icontains=commercial_input.split(" - ")[0],
        ).exclude(
            id__in=medecins_visited
        ).exclude(
            specialite__in=['Grossiste', 'Pharmacie', 'SuperGros']
        ).distinct()

        visites = Visite.objects.filter(medecin__in=medecins_non_visites).order_by('medecin').distinct('medecin')
        print("--> "+str(visites))
    else:
        visites = Visite.objects.filter(**filters).distinct()
        


    # if q:
    #     visites = visites.filter(q).distinct()

    # if request.GET.get("stock"):
    #     visites = visites.filter(
    #         produitvisite__produit=request.GET.get("stock"), produitvisite__qtt__gte=1
    #     )

    # if not request.user.is_superuser:
    #     visites = visites.filter(
    #         rapport__user__userprofile__commune__wilaya__pays=request.user.userprofile.commune.wilaya.pays
    #     )
    #     if request.user.userprofile.rolee in [
    #         "Superviseur",
    #         "Superviseur_regional",
    #         "Medico_commercial",
    #         "Commercial",
    #         "Superviseur_national",
    #     ]:
    #         visites = visites.filter(
    #             rapport__user__in=request.user.userprofile.usersunder.all()
    #         )


    return produit, region, specialite, classification, visites
