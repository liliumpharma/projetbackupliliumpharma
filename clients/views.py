# from django.shortcuts import render, redirect, reverse, get_object_or_404
# from django.contrib.auth.models import User
from django.db.models import Exists, OuterRef
# from produits.models import Produit
# from clients.models import *
from clients.functions import (
    get_order_source_details,
    #get_target_per_user,
    get_target_per_user_id,
    get_target_details_per_user,
    #get_target_details_per_user_use,
    get_target_all_users,
    #get_target_for_supervisor,
    get_target_per_user_per_month,
)
# from accounts.models import UserProfile, UserProduct
# from django.utils import timezone
# from .models import UserTargetMonth, UserTargetMonthProduct
# from datetime import datetime
# from monthly_evaluations.models import Monthly_Evaluation, SupEvaluation

# from rest_framework.views import APIView
# from rest_framework.response import Response
# from datetime import datetime

# from django.views.generic import TemplateView
# from django.contrib.auth.mixins import LoginRequiredMixin
# from orders.models import *
# from liliumpharm.utils import month_number_to_french_name
# from django.db.models import Subquery, OuterRef


# class taruser(LoginRequiredMixin, TemplateView):
    
#     def get(self, request):
#         if UserProfile.objects.get(user=request.user).speciality_rolee == "Commercial":
#             user_sectors = UserProfile.objects.get(user=request.user).sectors.all()
#             #user_sectors = request.User.UserProfile.sectors
#             date_given = "2024-01-01"
#             usermonth_ids = UserTargetMonth.objects.filter(user=request.user, date=date_given)
#             latest_ids = (
#                 UserTargetMonthProduct.objects
#                 .filter(usermonth__in=usermonth_ids, product_id=OuterRef('product_id'))
#                 .order_by('-id')  # ou autre critère temporel
#                 .values('id')[:1]
#             )
#             results = (
#                 UserTargetMonthProduct.objects
#                 .filter(id__in=Subquery(latest_ids))
#                 .filter(usermonth__in=usermonth_ids)
#                 .distinct('product_id')  # PostgreSQL seulement
#                 .values('quantity', 'product_id')
#             )
#             print(results)
#             print("youuuuuuuuuuuuuuuuuuu")
#             for sect in user_sectors:
#                 print(sect.nom)
#                 print(sect.code_name)
#             source_file = Source.objects.get(date=date_given).id
#             source_order = OrderSource.objects.filter(source_file_id=source_file).values_list('id', flat=True)
#             print(list(source_order))
#             source_order_product = OrderSourceProduct.objects.filter(source_id__in=source_order)
#             list_client = []
#             for sect in user_sectors:
#                 ls = Client.objects.filter(wilaya_id=sect.code_name).values_list('id', flat=True)
#                 ls_related = Client.objects.filter(wilaya_id=sect.code_name).values_list('related_client_id', flat=True)
#                 ls_related = list(set(ls_related))
#                 list_client.extend(ls)
#                 list_client.extend(ls_related)
#             list_client = [item for item in list_client if item is not None]
#             list_client = list(set(list_client))
#             print(list(list_client))
#             #order_obj = Order.objects.filter(client__in=list_client, source_id__in=source_order).values_list('id', flat=True)
#             order_obj = Order.objects.filter(
#                 source__in=source_order, client__in=list_client
#             )           
#             for pro in results:
#                 total_order = OrderProduct.objects.filter(order_id__in=order_obj, produit_id=pro.id)
#                 print(total_order)
            
                
#             user_profiles = User.objects.all()
#             return render(request, "clients/taruser.html", {"users":user_profiles})
#         return render(request, "clients/taruser.html")
    
#     def post(self, request):
#         print("BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB")
#         month = int(request.POST.get("months"))
#         year = int(request.POST.get("years"))
#         selected_user_id = request.POST.get('users')
        
#         params = {}
#         if month != 0:
#             params["month"] = month
#         params["year"] = year
#         print("2")
#         french_month = (
#         month_number_to_french_name(int(params["month"]))
#         if "month" in params
#         else "Tous les Mois"
#         )
#         year = params["year"] if "year" in params else "Toutes les Années"
#         print("3")
#         context = {"month": french_month, "year": year}
#         if selected_user_id:
#             if int(selected_user_id)==00:
#                 data = get_target_all_users(**params)
#                 #data = get_target_per_user_id(**params)
#                 context["data"] = data
#                 return render(
#                     request,
#                     template_name="clients/reports/target_report_all_users.html",
#                     context=context,
#                 )
#             else:
#                 params["user_id"] = int(selected_user_id)
#                 data = get_target_per_user_id(**params)
#                 context["data"] = data
#                 return render(
#                     request,
#                     template_name="clients/reports/target_report_all_users.html",
#                     context=context,
#                 )
#         else:
#             params["user_id"] = request.user.id
#             print(params)
#             data = get_target_per_user_id(**params)
#             context["data"] = data
#             return render(
#                 request,
#                 template_name="clients/reports/target_report_all_users.html",
#                 context=context,
#             )
        

        
#         #data = get_target_all_users(**params)
#         data = get_target_per_user_id(**params)
#         context["data"] = data
#         return render(
#             request,
#             template_name="clients/reports/target_report_all_users.html",
#             context=context,
#         )
#         data = get_target_per_user_id(**params)
#         print(data)
#         context["data"] = data
#         return render(
#             request,
#             template_name="clients/reports/target_report_per_user.html",
#             context=context,
#         )
#         return render(requests, "")

# def target(request):

#     context = {}
#     context["wilayas"] = request.user.userprofile.sectors.all()

#     user = request.user
#     if user.is_superuser == True:
#         context["users"] = User.objects.filter(userproduct__isnull=False).distinct()
#     elif user.userprofile.rolee == "CountryManager":
#         context["users"] = User.objects.filter(
#             userprofile__commune__wilaya__pays=request.user.userprofile.commune.wilaya.pays,
#             userproduct__isnull=False,
#         ).distinct()
#     elif user.userprofile.rolee == "Superviseur":
#         context["users"] = request.user.userprofile.usersunder.filter(
#             userproduct__isnull=False
#         ).distinct()

#     all_months_and_years = (
#         OrderSource.objects.all().values_list("date__month", "date__year").distinct()
#     )

#     all_months = set()
#     all_years = set()

#     for month_and_year in all_months_and_years:
#         all_months.add(int(month_and_year[0]))
#         all_years.add(int(month_and_year[1]))

#     if request.method == "POST":

#         params = {}
#         post_data = request.POST

#         user_id = post_data.get("user_id")
#         month = post_data.get("months")
#         year = post_data.get("years")

#         # If a User is selected then set the User's ID
#         if int(user_id) == 0:
#             context["current_user"] = 0
#             params["user_id"] = request.user.id
#             params["include_user"] = True
#             print_target_per_user_url_params = f"&user={request.user.id}"

#         else:
#             params = {"user_id": user_id}
#             print_target_per_user_url_params = f"&user={user_id}"

#         # Check if 0 not in List | 0 means All Months
#         if int(month) != 0:
#             params["month"] = month
#             print_target_per_user_url_params += f"&month={int(month)}"

#         # Check if 0 not in List | 0 means All Years
#         if int(year) != 0:
#             params["year"] = year
#             print_target_per_user_url_params += f"&year={int(year)}"

#         if int(user_id) == 0 and (
#             request.user.is_superuser
#             or request.user.userprofile.rolee in ["Superviseur", "CountryManager"]
#         ):
#             context["target_per_user"] = get_target_for_supervisor(**params)
#         else:
#             context["target_per_user"] = get_target_per_user(**params)

#         # Remove '&' symbol at beginning
#         print_target_per_user_url_params = print_target_per_user_url_params[1:]
#         context["print_target_per_user_url"] = (
#             f"{reverse('target_report')}?{print_target_per_user_url_params}"
#         )

#     context["all_months"] = all_months
#     context["all_years"] = all_years

#     return render(
#         request, template_name="clients/user_profile_target.html", context=context
#     )


# def sales_report(request, id):

#     os = get_object_or_404(OrderSource, pk=id)

#     data = get_order_source_details(os)

#     return render(
#         request,
#         template_name="clients/reports/sales_report.html",
#         context={"data": data},
#     )


# def target_report(request):

#     request_params = request.GET

#     params = {}

#     if "year" in request_params:
#         params["year"] = request_params.get("year")

#     if "month" in request_params:
#         params["month"] = request_params.get("month")

#     if "client_wilaya_id" in request_params:
#         params["wilaya"] = request_params.get("client_wilaya_id")

#     french_month = (
#         month_number_to_french_name(int(params["month"]))
#         if "month" in params
#         else "Tous les Mois"
#     )
#     year = params["year"] if "year" in params else "Toutes les Années"

#     context = {"month": french_month, "year": year}

#     if "user" in request_params:
#         params["user_id"] = request_params.get("user")
#         data = get_target_per_user(**params)
#         context["data"] = data
#         return render(
#             request,
#             template_name="clients/reports/target_report_per_user.html",
#             context=context,
#         )

#     data = get_target_all_users(**params)
#     context["data"] = data
#     return render(
#         request,
#         template_name="clients/reports/target_report_all_users.html",
#         context=context,
#     )


# def target_report_details(request):

#     request_params = request.GET

#     params = {}

#     if "year" in request_params:
#         params["years"] = int(request_params.get("year"))

#     if "month" in request_params:
#         params["months"] = int(request_params.get("month"))

#     if "user" in request_params:
#         params["user_id"] = request_params.get("user")

#     if "product" in request_params:
#         params["product_id"] = request_params.get("product")

#     french_month = (
#         month_number_to_french_name(int(params["months"]))
#         if "month" in params
#         else "Tous les Mois"
#     )
    
#     #french_month = (
#     #    ", ".join(month_number_to_french_name(int(month)) for month in params["months"])
#     #    if "months" in params
#     #    else "Tout les Mois"
#     #)
    
#     data = get_target_details_per_user(**params)

#     #french_month = (
#     #    ", ".join(month_number_to_french_name(int(month)) for month in params["months"])
#     #    if "months" in params
#     #    else "Tout les Mois"
#     #)
#     french_month = (
#         ", ".join(month_number_to_french_name(int(month)) for month in ([params["months"]] if isinstance(params["months"], (int, str)) else params["months"]))
#         if "months" in params
#         else "Tous les Mois"
#     )

#     #year = (
#     #    ", ".join(str(year) for year in params["years"])
#     #    if "years" in params
#     #    else "Toutes les Années"
#     #)
    
#     year = (
#         ", ".join(str(year) for year in ([params["years"]] if isinstance(params["years"], (int, str)) else params["years"]))
#         if "years" in params
#         else "Toutes les Années"
#     )


#     return render(
#         request,
#         template_name="clients/reports/target_report_details_per_user_details.html",
#         context={"data": data, "month": french_month, "year": year, "m":int(request_params.get("month"))},
#     )
# from rest_framework.authentication import (
#     SessionAuthentication,
#     TokenAuthentication,
#     BasicAuthentication,
# )
# from django.db.models import Q
# from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

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
    #authentication_classes = [SessionAuthentication]
    #permission_classes = [IsAuthenticated]
    def get(selt, request):
        print(str(request))
        print("sesssionnnnnnnnnnnn")
        print(request.session.items())
        print("user_id dans sessionnnnnnnnn")
        user_id = request.session.get('user_id')
        is_mobile = request.session.get('is_mobile')
        print(user_id)
        # Afficher tous les en-têtes
        
        if request.user.is_authenticated:
            user_id = request.user.id
            print("dans request web")
            print(user_id)
        else:
            user_id = request.session.get('user_id')
            print("dans la session")
            print(user_id)
        if UserProfile.objects.get(user=user_id).speciality_rolee in ["Medico_commercial", "Commercial"]:
            user_profiles = User.objects.filter(id=user_id)
            return render(request, "clients/taruser.html", {"users":user_profiles, "num_id":33})
        elif UserProfile.objects.get(user=user_id).speciality_rolee == "CountryManager" or UserProfile.objects.get(user=user_id).speciality_rolee == "Admin" or UserProfile.objects.get(user=user_id).speciality_rolee == "Office":
            user_profiles = User.objects.filter(userprofile__speciality_rolee__in=["Medico_commercial", "Superviseur_national", "Superviseur_regional", "CountryManager", "Commercial"], userprofile__hidden=False).filter(Exists(UserTargetMonth.objects.filter(user=OuterRef('pk'))))
            return render(request, "clients/taruser.html", {"users":user_profiles, "num_id":1})
        elif UserProfile.objects.get(user=user_id).speciality_rolee == "Superviseur_regional" or UserProfile.objects.get(user=user_id).speciality_rolee == "Superviseur_national":
            user_profiles = UserProfile.objects.get(user=user_id)
            user_profiles = user_profiles.usersunder.all()
            ur = User.objects.get(id=user_id)
            nam = ur.first_name + " " + ur.last_name
            return render(request, "clients/taruser.html", {"users":user_profiles, "num_id":2, "name":nam})
            #return render(request, "clients/taruser.html")
        else:
            pass
        return render(request, "clients/taruser.html")
    def post(self, request):
        if request.user.is_authenticated:
            user_id = request.user.id
            print("dans request web")
        else:
            user_id = request.session.get('user_id')
            print("dans la session")
        request_params = request.GET
        e = request.POST.get('users')
        if e:
            selected_user = int(request.POST.get('users'))
        else:
            selected_user = "passssssss"
        if selected_user == 0 and UserProfile.objects.get(user=user_id).speciality_rolee in  ["Superviseur_regional"]:
            print("SuperViseur Regional")
            year = int(request.POST.get('years'))
            month = int(request.POST.get('months'))
            mo = month_number_to_french_name(month)
            year = int(request.POST.get('years'))
            months = request.POST.getlist('months')
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
            #data = get_target_per_user_id(**params)
            context["data"] = data
            return render(
                request,
                template_name="clients/reports/target_report_per_user.html",
                context=context,
            )
        elif selected_user != 0 and selected_user != "passssssss" and UserProfile.objects.get(user=selected_user).speciality_rolee in ["Superviseur_regional","CountryManager"]:
            t = UserProfile.objects.get(user=selected_user)
            
            print("SuperViseur Regional or CountryManager")
            year = int(request.POST.get('years'))
            months = request.POST.getlist('months')
            m = []
            for i in months:
                mo = month_number_to_french_name(int(i))
                #q.append(int(i))
                m.append(mo)
            #month = q
            year = [int(request.POST.get('years'))]
            month = months = request.POST.getlist('months')

            params = {}
            if year:
                params["years"] = year
            if month:
                params["months"] = months
            params["user_id"] = selected_user
            context = {"month": m, "year": year}
            data = get_target_for_supervisor(**params)
            #data = get_target_per_user_id(**params)
            context["data"] = data
            context = add_special_table_data(context)
            return render(
                request,
                template_name="clients/reports/target_report_per_user.html",
                context=context,
            )
        
        
       
        
        
        year = int(request.POST.get('years'))
        months = request.POST.getlist('months')
        year = request.POST.getlist('years')
        #month=0000000
        q = []
        m =[]
        if len(months) == 1:
            month = int(months[0])
        else:
            
            for i in months:
                mo = month_number_to_french_name(int(i))
                q.append(int(i))
                m.append(mo)
            month = q
        print(month)
        user = request.POST.get('users')
        if user:
            user = int(user)
        print(request_params)
        print(year)
        print(month)

        params = {}
        year = [int(request.POST.get('years'))]
        month = [int(request.POST.get('months'))]
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
        
        if user==0:
            data = get_target_all_users(**params)
            #data = get_target_per_user_id(**params)
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
            context = add_special_table_data(context)
            return render(
                request,
                template_name="clients/reports/target_report_per_user.html",
                context=context,
                )
        else:
            french_month = q
            months = request.POST.getlist('months')
            params["months"] = months
            context = {"month": m, "year": year}
            data = get_target_per_user_per_month(**params)
            context["data"] = data
            context = add_special_table_data(context)

            # Build per-month individual sections
            per_month_sections = []
            for single_month in months:
                single_params = dict(params)
                single_params["months"] = [single_month]
                single_data = get_target_per_user(**single_params)
                single_french_month = month_number_to_french_name(int(single_month))
                single_ctx = {"data": single_data}
                single_ctx = add_special_table_data(single_ctx)
                per_month_sections.append({
                    "month": single_french_month,
                    "data": single_ctx["data"],
                    "show_special_table": single_ctx.get("show_special_table", False),
                })
            context["per_month_sections"] = per_month_sections

            return render(
                request,
                template_name="clients/reports/target_report_per_user.html",
                context=context,
            )
        
        data = get_target_all_users(**params)
        context["data"] = data
        return render(
            request,
            template_name="clients/reports/target_report_all_users.html",
            context=context,
        )
        return render(request, "clients/taruser.html")
        





# class UsersWithTargetMonth(APIView):
#     authentication_classes = (
#         TokenAuthentication,
#         SessionAuthentication,
#     )

#     def get(self, request):

#         current_year = datetime.now().year
#         print("yeaaar " + str(current_year))
#         month = request.GET.get("month")
#         if month == "null":
#             month = datetime.now().month - 1
#         user = request.user
#         response = []

#         if (
#             user.userprofile.speciality_rolee in ["admin", "CountryManager"]
#             or user.is_superuser
#         ):
#             users = User.objects.all()
#             users = users.exclude(
#                 userprofile__speciality_rolee__in=["Superviseur_national"]
#             )
#             excluded_families = ["lilium Pharma", "orient Bio", "Aniya_Pharm"]
#             users = users.exclude(userprofile__family__in=excluded_families)

#             for u in users:
#                 has_eval = False
#                 has_sup_eval = False
#                 has_direction_eval = False
#                 pourcentage = 0
#                 own_perc = 0

#                 if UserTargetMonth.objects.filter(user=u, date__month=month).exists():
#                     print("added year " + str(current_year))
#                     print("added month " + str(month))
#                     print("user " + str(u))

#                     me = Monthly_Evaluation.objects.filter(
#                         Q(added__year=current_year) & Q(added__month=month) & Q(user=u)
#                     ).first()

#                     if Monthly_Evaluation.objects.filter(
#                         user=u, added__month=month, added__year=current_year
#                     ).exists():
#                         has_eval = True
#                         has_direction_eval = me.user_direction_evaluation
#                         own_perc = me.own_perc

#                     if SupEvaluation.objects.filter(
#                         user=u, added__month=month, added__year=current_year
#                     ).exists():
#                         se = SupEvaluation.objects.filter(
#                             user=u, added__month=month
#                         ).first()
#                         has_sup_eval = True
#                         pourcentage = se.perc

#                     response.append(
#                         {
#                             "user": u.username,
#                             "has_eval": has_eval,
#                             "has_sup_eval": has_sup_eval,
#                             "family": u.userprofile.family,
#                             "has_direction_eval": has_direction_eval,
#                             "pourcentage": pourcentage,
#                             "own_perc": own_perc,
#                         }
#                     )
#         else:
#             if user.userprofile.speciality_rolee == "Superviseur_national":
#                 users_under_supervisor = user.userprofile.usersunder.all()
#                 users_under_supervisor = users_under_supervisor.exclude(
#                     username=request.user.username
#                 )
#                 for u in users_under_supervisor:
#                     has_eval = False
#                     has_sup_eval = False
#                     has_direction_eval = False
#                     pourcentage = 0
#                     own_perc = 0
#                     if UserTargetMonth.objects.filter(
#                         user=u, date__month=month, date__year=current_year
#                     ).exists():
#                         me = Monthly_Evaluation.objects.filter(
#                             user=u, added__month=month, added__year=current_year
#                         ).first()
#                         if Monthly_Evaluation.objects.filter(
#                             user=u, added__month=month, added__year=current_year
#                         ).exists():
#                             has_eval = True
#                             has_direction_eval = me.user_direction_evaluation
#                             own_perc = me.own_perc

#                         if SupEvaluation.objects.filter(
#                             user=u, added__month=month, added__year=current_year
#                         ).exists():
#                             se = SupEvaluation.objects.filter(
#                                 user=u, added__month=month, added__year=current_year
#                             ).first()
#                             has_sup_eval = True
#                             pourcentage = se.perc

#                         response.append(
#                             {
#                                 "user": u.username,
#                                 "has_eval": has_eval,
#                                 "has_sup_eval": has_sup_eval,
#                                 "has_direction_eval": has_direction_eval,
#                                 "pourcentage": pourcentage,
#                                 "own_perc": own_perc,
#                             }
#                         )
#             else:
#                 user = request.user
#                 has_eval = False
#                 has_sup_eval = False
#                 has_direction_eval = False
#                 pourcentage = 0
#                 own_perc = 0
#                 me = Monthly_Evaluation.objects.filter(
#                     user__username=user, added__month=month, added__year=current_year
#                 ).first()
#                 if Monthly_Evaluation.objects.filter(
#                     user=user, added__month=month, added__year=current_year
#                 ).exists():
#                     has_eval = True
#                     has_direction_eval = me.user_direction_evaluation
#                     own_perc = me.own_perc
#                 if SupEvaluation.objects.filter(
#                     user__username=request.user,
#                     added__month=month,
#                     added__year=current_year,
#                 ).exists():
#                     se = SupEvaluation.objects.filter(
#                         user__username=user,
#                         added__month=month,
#                         added__year=current_year,
#                     ).first()
#                     has_sup_eval = True
#                     pourcentage = se.perc

#                 response.append(
#                     {
#                         "user": user.username,
#                         "has_eval": has_eval,
#                         "has_sup_eval": has_sup_eval,
#                         "has_direction_eval": has_direction_eval,
#                         "pourcentage": pourcentage,
#                         "own_perc": own_perc,
#                     }
#                 )

#         return Response(response)


# from django.shortcuts import render, get_object_or_404
# from .models import UserTargetMonth


# def user_target_month_print(request, id):
#     user_target_month = get_object_or_404(UserTargetMonth, id=id)
#     context = {
#         "user_target_month": user_target_month,
#         "products": user_target_month.usertargetmonthproduct_set.all(),
#     }
#     return render(
#         request, "../templates/print/target_month.html", context
#     )  # Remplacez par votre template

from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib.auth.models import User

from produits.models import Produit
from clients.models import OrderSource
from clients.api.functions import (
    get_order_source_details,
    get_target_per_user,
    #get_target_details_per_user,
    get_target_details_per_user_use,
    get_target_all_users,
    get_target_for_supervisor,
)
from accounts.models import UserProfile, UserProduct
from django.utils import timezone
from .models import UserTargetMonth
from datetime import datetime
from monthly_evaluations.models import Monthly_Evaluation, SupEvaluation, Commercial_Monthly_Evaluation

from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime


from liliumpharm.utils import month_number_to_french_name


def target(request):

    context = {}
    context["wilayas"] = request.user.userprofile.sectors.all()

    user = request.user
    if user.is_superuser == True:
        context["users"] = User.objects.filter(userproduct__isnull=False).distinct()
    elif user.userprofile.rolee == "CountryManager":
        context["users"] = User.objects.filter(
            userprofile__commune__wilaya__pays=request.user.userprofile.commune.wilaya.pays,
            userproduct__isnull=False,
        ).distinct()
    elif user.userprofile.rolee == "Superviseur":
        context["users"] = request.user.userprofile.usersunder.filter(
            userproduct__isnull=False
        ).distinct()

    all_months_and_years = (
        OrderSource.objects.all().values_list("date__month", "date__year").distinct()
    )

    all_months = set()
    all_years = set()

    for month_and_year in all_months_and_years:
        all_months.add(int(month_and_year[0]))
        all_years.add(int(month_and_year[1]))

    if request.method == "POST":

        params = {}
        post_data = request.POST

        user_id = post_data.get("user_id")
        month = post_data.get("months")
        year = post_data.get("years")

        # If a User is selected then set the User's ID
        if int(user_id) == 0:
            context["current_user"] = 0
            params["user_id"] = request.user.id
            params["include_user"] = True
            print_target_per_user_url_params = f"&user={request.user.id}"

        else:
            params = {"user_id": user_id}
            print_target_per_user_url_params = f"&user={user_id}"

        # Check if 0 not in List | 0 means All Months
        if int(month) != 0:
            params["month"] = month
            print_target_per_user_url_params += f"&month={int(month)}"

        # Check if 0 not in List | 0 means All Years
        if int(year) != 0:
            params["year"] = year
            print_target_per_user_url_params += f"&year={int(year)}"

        if int(user_id) == 0 and (
            request.user.is_superuser
            or request.user.userprofile.rolee in ["Superviseur", "CountryManager"]
        ):
            context["target_per_user"] = get_target_for_supervisor(**params)
        else:
            context["target_per_user"] = get_target_per_user(**params)

        # Remove '&' symbol at beginning
        print_target_per_user_url_params = print_target_per_user_url_params[1:]
        context["print_target_per_user_url"] = (
            f"{reverse('target_report')}?{print_target_per_user_url_params}"
        )

    context["all_months"] = all_months
    context["all_years"] = all_years

    return render(
        request, template_name="clients/user_profile_target.html", context=context
    )


def sales_report(request, id):

    os = get_object_or_404(OrderSource, pk=id)

    data = get_order_source_details(os)

    return render(
        request,
        template_name="clients/reports/sales_report.html",
        context={"data": data},
    )


def target_report(request):

    request_params = request.GET

    params = {}

    if "year" in request_params:
        params["year"] = request_params.get("year")

    if "month" in request_params:
        params["month"] = request_params.get("month")

    if "client_wilaya_id" in request_params:
        params["wilaya"] = request_params.get("client_wilaya_id")

    french_month = (
        month_number_to_french_name(int(params["month"]))
        if "month" in params
        else "Tous les Mois"
    )
    year = params["year"] if "year" in params else "Toutes les Années"

    context = {"month": french_month, "year": year}

    if "user" in request_params:
        params["user_id"] = request_params.get("user")
        data = get_target_per_user(**params)
        context["data"] = data
        return render(
            request,
            template_name="clients/reports/target_report_per_user.html",
            context=context,
        )

    data = get_target_all_users(**params)
    context["data"] = data
    return render(
        request,
        template_name="clients/reports/target_report_all_users.html",
        context=context,
    )


# def target_report_details(request):

#     request_params = request.GET

#     params = {}

#     if "months" in request_params:
#         params["months"] = [int(m) for m in request_params.getlist("months")]

#     if "years" in request_params:
#         params["years"] = [int(y) for y in request_params.getlist("years")]


#     if "user" in request_params:
#         params["user_id"] = request_params.get("user")

#     if "product" in request_params:
#         params["product_id"] = request_params.get("product")

#     data = get_target_details_per_user(**params)

#     french_month = (
#         ", ".join(month_number_to_french_name(int(month)) for month in params["months"])
#         if "months" in params
#         else "Tout les Mois"
#     )
#     year = (
#         ", ".join(str(year) for year in params["years"])
#         if "years" in params
#         else "Toutes les Années"
#     )

#     return render(
#         request,
#         template_name="clients/reports/target_report_details_per_user_details.html",
#         context={"data": data, "month": french_month, "year": year},
#     )

def target_report_details(request):
    request_params = request.GET
    params = {}

    # Mois
    if "months" in request_params:
        params["months"] = [int(m) for m in request_params.getlist("months")]

    # Années
    if "years" in request_params:
        params["years"] = [int(y) for y in request_params.getlist("years")]

    # User
    if "user" in request_params:
        params["user_id"] = int(request_params.get("user"))

    # Product
    if "product" in request_params:
        params["product_id"] = int(request_params.get("product"))

    # Récupération données
    data = get_target_details_per_user(**params)

    # Mois en français
    french_month = (
        ", ".join(month_number_to_french_name(m) for m in params.get("months", []))
        if "months" in params else "Tous les Mois"
    )

    # Années
    year = (
        ", ".join(str(y) for y in params.get("years", []))
        if "years" in params else "Toutes les Années"
    )

    return render(
        request,
        "clients/reports/target_report_details_per_user_details.html",
        {"data": data, "month": french_month, "year": year},
    )


def target_report_details_use(request):
    request_params = request.GET
    params = {}

    # Mois
    if "months" in request_params:
        params["months"] = [int(m) for m in request_params.getlist("months")]

    # Années
    if "years" in request_params:
        params["years"] = [int(y) for y in request_params.getlist("years")]

    # User
    if "user" in request_params:
        params["user_id"] = int(request_params.get("user"))
        #print(f"le user esttttttttt {params["user_id"]}")

    # Product
    if "product" in request_params:
        params["product_id"] = int(request_params.get("product"))
        
    if "gros_super" in request_params:
        params["gros_super"] = request_params.get("gros_super") == "1"

    # Récupération données
    data = get_target_details_per_user_use(**params)

    # Mois en français
    french_month = (
        ", ".join(month_number_to_french_name(m) for m in params.get("months", []))
        if "months" in params else "Tous les Mois"
    )

    # Années
    year = (
        ", ".join(str(y) for y in params.get("years", []))
        if "years" in params else "Toutes les Années"
    )

    return render(
        request,
        "clients/reports/use.html",
        {"data": data, "month": french_month, "year": year},
    )


def target_front(request):
    print(str(request))
    return render(request, "micro_frontends/target/index.html")

#def target_front_2(request):
#    print(str(request))
#    return render(request, "micro_frontends/target/index.html")


from rest_framework.authentication import (
    SessionAuthentication,
    TokenAuthentication,
    BasicAuthentication,
)
from django.db.models import Q


class UsersWithTargetMonth(APIView):
    authentication_classes = (
        TokenAuthentication,
        SessionAuthentication,
    )

    def get(self, request):

        #current_year = datetime.now().year
        a = request.GET.get("year")
        if a:
            current_year = int(a)
        else:
            current_year = datetime.now().year
        print("yeaaar " + str(current_year))
        print(request.GET.get("user"))
        fml = request.GET.get("family")
        uuuu = request.GET.get("usr")
        uu = request.GET.get("user")
        if uu is not None:
            user = User.objects.filter(username=uu).first()
            print(user)
        else:
            user = request.user
        month = int(request.GET.get("month"))
        if month == "null":
            month = datetime.now().month - 1
        #user = request.user
        response = []

        if (
            user.userprofile.speciality_rolee in ["Admin", "CountryManager"]
            or user.is_superuser
        ):
            if fml:
                users = User.objects.filter(userprofile__speciality_rolee=fml)
                print(f"oui avec family {fml}")
                print(f"les users {users}")
            elif uuuu:
                users = User.objects.filter(username=uuuu)
            else:
                users = User.objects.all()
                users = users.exclude(
                    userprofile__speciality_rolee__in=["Superviseur_national"]
                )
            #excluded_families = ["lilium Pharma", "orient Bio", "Aniya_Pharm"]
            excluded_families = ["orient Bio", "production", "Administration"]
            users = users.exclude(userprofile__family__in=excluded_families)
            print(f"les users apres exclude {users}")

            for u in users:
                has_eval = False
                has_sup_eval = False
                has_direction_eval = False
                pourcentage = 0
                own_perc = 0

                #if UserTargetMonth.objects.filter(user=u, date__month=month).exists():
                if 1:
                    print("added year " + str(current_year))
                    print("added month " + str(month))
                    print("user " + str(u))
                    try:
                        if u.userprofile.speciality_rolee == "Commercial":
                            me = Commercial_Monthly_Evaluation.objects.filter(
                            user=u, added__month=month, added__year=current_year
                            ).first()
                        else:
                            me = Monthly_Evaluation.objects.filter(
                            Q(added__year=current_year) & Q(added__month=month) & Q(user=u)
                            ).first()
                    except:
                        print("pas de monthly target month")
                    d = 0
                    if u.userprofile.speciality_rolee == "Commercial":
                        d = Commercial_Monthly_Evaluation.objects.filter(
                        user=u, added__month=month, added__year=current_year
                    )
                    else:
                        d = Monthly_Evaluation.objects.filter(
                        user=u, added__month=month, added__year=current_year
                        )
                    if d.exists():
                        has_eval = True
                        has_direction_eval = me.user_direction_evaluation
                        own_perc = me.own_perc

                    if SupEvaluation.objects.filter(
                        user=u, added__month=month, added__year=current_year
                    ).exists():
                        se = SupEvaluation.objects.filter(
                            user=u, added__month=month
                        ).first()
                        has_sup_eval = True
                        pourcentage = se.perc

                    response.append(
                        {
                            "user": u.username,
                            "has_eval": has_eval,
                            "has_sup_eval": has_sup_eval,
                            "family": u.userprofile.family,
                            "has_direction_eval": has_direction_eval,
                            "pourcentage": pourcentage,
                            "own_perc": own_perc,
                        }
                    )
        else:
            if user.userprofile.speciality_rolee == "Superviseur_national":
                if fml:
                    users_under_supervisor = user.userprofile.usersunder.filter(
                        userprofile__speciality_rolee=fml
                        )
                elif uuuu:
                    users_under_supervisor = User.objects.filter(username=uuuu)
                else:
                    users_under_supervisor = user.userprofile.usersunder.all()
                users_under_supervisor = users_under_supervisor.exclude(
                    username=user.username
                )
                for u in users_under_supervisor:
                    has_eval = False
                    has_sup_eval = False
                    has_direction_eval = False
                    pourcentage = 0
                    own_perc = 0
                    #if UserTargetMonth.objects.filter(
                    #    user=u, date__month=month, date__year=current_year
                    #).exists():
                    if 1:
                        me = Monthly_Evaluation.objects.filter(
                            user=u, added__month=month, added__year=current_year
                        ).first()
                        if Monthly_Evaluation.objects.filter(
                            user=u, added__month=month, added__year=current_year
                        ).exists():
                            has_eval = True
                            has_direction_eval = me.user_direction_evaluation
                            own_perc = me.own_perc

                        if SupEvaluation.objects.filter(
                            user=u, added__month=month, added__year=current_year
                        ).exists():
                            se = SupEvaluation.objects.filter(
                                user=u, added__month=month, added__year=current_year
                            ).first()
                            has_sup_eval = True
                            pourcentage = se.perc

                        response.append(
                            {
                                "user": u.username,
                                "has_eval": has_eval,
                                "has_sup_eval": has_sup_eval,
                                "has_direction_eval": has_direction_eval,
                                "pourcentage": pourcentage,
                                "own_perc": own_perc,
                            }
                        )
            else:
                #user = request.user
                has_eval = False
                has_sup_eval = False
                has_direction_eval = False
                pourcentage = 0
                own_perc = 0
                me = Monthly_Evaluation.objects.filter(
                    user__username=user, added__month=month, added__year=current_year
                ).first()
                if Monthly_Evaluation.objects.filter(
                    user=user, added__month=month, added__year=current_year
                ).exists():
                    has_eval = True
                    has_direction_eval = me.user_direction_evaluation
                    own_perc = me.own_perc
                if SupEvaluation.objects.filter(
                    user__username=user,
                    added__month=month,
                    added__year=current_year,
                ).exists():
                    se = SupEvaluation.objects.filter(
                        user__username=user,
                        added__month=month,
                        added__year=current_year,
                    ).first()
                    has_sup_eval = True
                    pourcentage = se.perc

                response.append(
                    {
                        "user": user.username,
                        "has_eval": has_eval,
                        "has_sup_eval": has_sup_eval,
                        "has_direction_eval": has_direction_eval,
                        "pourcentage": pourcentage,
                        "own_perc": own_perc,
                    }
                )
        print(f"les reponse sont {response}")
        return Response(response)


from django.shortcuts import render, get_object_or_404
from .models import UserTargetMonth


def user_target_month_print(request, id):
    user_target_month = get_object_or_404(UserTargetMonth, id=id)
    context = {
        "user_target_month": user_target_month,
        "products": user_target_month.usertargetmonthproduct_set.all(),
    }
    return render(
        request, "../templates/print/target_month.html", context
    )  # Remplacez par votre template

