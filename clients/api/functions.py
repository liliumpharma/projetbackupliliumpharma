# Django Imports
from django.contrib.auth.models import User
from django.db.models import Sum, F
from django.db.models import Q
from django.shortcuts import reverse
from datetime import date

# App Imports
from accounts.models import UserProfile, UserProduct
from regions.models import Wilaya
from clients.models import *
from produits.models import Produit
from liliumpharm.utils import thousand_separator, date_format
from orders.models import Order as Orders
from orders.models import OrderItem


def get_order_source_details(ordersource):
    products = Produit.objects.all()

    data = {"ordersource": ordersource, "products": products, "orders": []}

    for order in ordersource.order_set.all():
        products_list = []
        for product in products:
            order_product = OrderProduct.objects.filter(order=order, produit=product)
            if order_product.exists():
                # --- NEW CODE START ---
                # Calculate the sum of 'qtt' for all matching lines
                total_qty = order_product.aggregate(total=Sum("qtt"))["total"]
                products_list.append(total_qty)
                # --- NEW CODE END ---
                continue
            products_list.append(0)

        user_profiles = UserProfile.objects.filter(sectors=order.client.wilaya)

        data["orders"].append(
            {
                "order": order,
                "user_profiles": user_profiles,
                "products_list": products_list,
            }
        )

    # Calculating Totals for each Product
    products_list = []
    products_list.extend([order_list["products_list"] for order_list in data["orders"]])
    total_products = [sum(product) for product in zip(*products_list)]
    data["total_products"] = total_products

    # Calculating Global Total
    data["total"] = sum(total_products)

    return data


# FIXME - Fix SOLD QUANTITY

# Parameters are IDs
def get_target_details_per_user(user_id=None, product_id=None, month=None, year=None):
    
    data = {} 

    if user_id and product_id:

        user_profile = UserProfile.objects.get(user__id=user_id)
        data["user"] = f"{user_profile.user.last_name} {user_profile.user.first_name}"

        product = Produit.objects.get(id=product_id)
        data["product"] = product

        user_product = UserTargetMonthProduct.objects.get(usermonth__user=user_profile.user, product=product, usermonth__date__month=month, usermonth__date__year=year)
        data["product_target"] = user_product.quantity * product.price
        data["product_target_quantity"] = user_product.quantity

        wilayas = user_profile.sectors.all()
        data["wilayas"] = wilayas

        # Preparing Query for Order Product
        order_client_query = Q()
        if month:
            order_client_query &= Q(order__source__date__month=month)
        if year:
            order_client_query &= Q(order__source__date__year=year)
        order_client_query &= Q(order__client__wilaya__in=wilayas)
        order_client_query &= Q(produit=product)
        
        order_client = OrderProduct.objects.filter(order_client_query).values("order__source__source__name", "order__source__date", "order__source__attachement_file", "order__client__name", "order__client__wilaya__nom").order_by('-order__source__date').annotate(total=Sum("qtt"))

        data["order_client"] = order_client

        total_quantity = sum(oc["total"] for oc in order_client)
        data["total_quantity"] = total_quantity

        # data["order_client"]=[*order_client, 
        # *[{
        #     "total":0,
        #     "order__client__name":c.name,
        #     "order__client__wilaya__nom":c.wilaya.nom,
        # } for c in Client.objects.filter(wilaya__in=wilayas)]
        # ]
        # for c in Client.objects.filter(wilaya__in=wilayas):
        #     print("**************",c)
        # print("***********yeaaah")    
        return data

from django.shortcuts import render, redirect, reverse, get_object_or_404

def get_target_details_per_user_use(user_id=None, product_id=None, months=None, years=None, gros_super=False):
    
    data = {}

    if user_id and product_id:

        user_profile = UserProfile.objects.get(user__id=user_id)
        data["user"] = f"{user_profile.user.last_name} {user_profile.user.first_name}"

        product = Produit.objects.get(id=product_id)
        data["product"] = product

        order_product_query_by_user = []
        
        if user_profile.rolee == "CountryManager":
            us = User.objects.filter(userprofile__commune__wilaya__pays=user_profile.commune.wilaya.pays, userprofile__speciality_rolee__in=["Commercial", "Medico_commercial"])
            if gros_super:
                order_product_query_by_user = Orders.objects.filter(user__in=us, added__month__in=months, added__year__in=years, super_gros__isnull=False).exclude(pharmacy__isnull=True, gros__isnull=True).exclude(super_gros_id=149) | Orders.objects.filter(user__in=us, added__month__in=months, added__year__in=years, pharmacy__isnull=True, gros__isnull=False).exclude(super_gros_id=149)
            else:
                order_product_query_by_user = Orders.objects.filter(user__in=us, added__month__in=months, added__year__in=years, super_gros__isnull=True).exclude(pharmacy__isnull=True, gros__isnull=True).exclude(super_gros_id=149)
        
        elif user_profile.rolee in ["Superviseur", "Superviseur_national"] and not getattr(user_profile, 'work_as_commercial', False):
            users_under = user_profile.usersunder.all()
            if gros_super:
                order_product_query_by_user = Orders.objects.filter(user__in=users_under, added__month__in=months, added__year__in=years, super_gros__isnull=False).exclude(pharmacy__isnull=True, gros__isnull=True).exclude(super_gros_id=149) | Orders.objects.filter(user__in=users_under, added__month__in=months, added__year__in=years, pharmacy__isnull=True, gros__isnull=False).exclude(super_gros_id=149)
            else:
                order_product_query_by_user = Orders.objects.filter(user__in=users_under, added__month__in=months, added__year__in=years, super_gros__isnull=True).exclude(pharmacy__isnull=True, gros__isnull=True).exclude(super_gros_id=149)
                
        elif user_profile.speciality_rolee == "Medico_commercial":
            if gros_super:
                order_product_query_by_user = Orders.objects.filter(user=user_profile.user, added__month__in=months, added__year__in=years, super_gros__isnull=False).exclude(pharmacy__isnull=True, gros__isnull=True).exclude(super_gros_id=149)
            else:
                order_product_query_by_user = Orders.objects.filter(user=user_profile.user, added__month__in=months, added__year__in=years, super_gros__isnull=True).exclude(pharmacy__isnull=True, gros__isnull=True).exclude(super_gros_id=149)
                
        elif user_profile.speciality_rolee == "Commercial":
            if gros_super:
                order_product_query_by_user = Orders.objects.filter(user=user_profile.user, added__month__in=months, added__year__in=years, pharmacy__isnull=True, gros__isnull=False).exclude(super_gros_id=149)
            else:
                order_product_query_by_user = Orders.objects.filter(user=user_profile.user, added__month__in=months, added__year__in=years, super_gros__isnull=True).exclude(pharmacy__isnull=True, gros__isnull=True).exclude(super_gros_id=149)
                
        elif user_profile.speciality_rolee == "Superviseur_national" and getattr(user_profile, 'work_as_commercial', False):
            if gros_super:
                order_product_query_by_user = Orders.objects.filter(user__in=user_profile.usersunder.all(), added__month__in=months, added__year__in=years, pharmacy__isnull=True, gros__isnull=False).exclude(super_gros_id=149)
            else:
                order_product_query_by_user = Orders.objects.filter(user__in=user_profile.usersunder.all(), added__month__in=months, added__year__in=years, super_gros__isnull=True).exclude(pharmacy__isnull=True, gros__isnull=True).exclude(super_gros_id=149)
        
        if len(months) == 1:
            user_product = UserTargetMonthProduct.objects.get(usermonth__user=user_profile.user, product=product, usermonth__date__month__in=months, usermonth__date__year__in=years)
        else:
            user_product = UserTargetMonthProduct.objects.filter(usermonth__user=user_profile.user, product=product, usermonth__date__month__in=months, usermonth__date__year__in=years)
        #total_quantity = 0
        if len(months) == 1:
            total_quantity = user_product.quantity
        else:
            total_quantity = sum(up.quantity for up in user_product)
        data["product_target"] = total_quantity * product.price
        #total_quantity = sum(up.quantity for up in user_product)
        data["product_target_quantity"] = total_quantity

        wilayas = user_profile.sectors.all()
        data["wilayas"] = wilayas

        # Preparing Query for Order Product
        order_client_query = Q()
        if months:
            order_client_query &= Q(order__source__date__month=months)
        if years:
            order_client_query &= Q(order__source__date__year=years)
        order_client_query &= Q(order__client__wilaya__in=wilayas)
        order_client_query &= Q(produit=product)
        
        #order_client = OrderProduct.objects.filter(order_client_query).values("order__source__source__name", "order__source__date", "order__source__attachement_file", "order__client__name", "order__client__wilaya__nom").order_by('-order__source__date').annotate(total=Sum("qtt"))
        for a in order_product_query_by_user:
            pass
        order_client = OrderItem.objects.filter(order__in=order_product_query_by_user, produit=product)
        #order_item = OrderItem.objects.filter(order=ord, produit=month_product['product'])
        data["order_client"] = order_client

        total_quantity = sum(oc.qtt for oc in order_client)
        data["total_quantity"] = total_quantity

        # data["order_client"]=[*order_client, 
        # *[{
        #     "total":0,
        #     "order__client__name":c.name,
        #     "order__client__wilaya__nom":c.wilaya.nom,
        # } for c in Client.objects.filter(wilaya__in=wilayas)]
        # ]
        # for c in Client.objects.filter(wilaya__in=wilayas):
        #     print("**************",c)
        # print("***********yeaaah")    
        return data


def get_target_per_user_commercial(user_id=None, months=None, years=None):
    
    targets = []
    prices = []
    quantities = []
    total_targets = []
    total_achievements = []

    if user_id:

        user_profile = UserProfile.objects.get(user__id=user_id)
        users_under = user_profile.usersunder.all()
        isUserUnderItSelf = user_profile.user in users_under

        wilayas = user_profile.sectors.all()

        if not months:
            months = OrderSource.objects.all().values_list('date__month').distinct()
        if not years:
            years = OrderSource.objects.all().values_list('date__year').distinct()


        products = Produit.objects.all()
        user_target_month_products = UserTargetMonthProduct.objects.filter(usermonth__date__year__in=years, usermonth__date__month__in=months, usermonth__user=user_profile.user).values('product', 'product__nom').distinct()

        for month_product in user_target_month_products:
            
            product = products.get(id=month_product['product'])
            
            # Appending Price
            prices.append(product.price)
            
            total_product_quantity_sold = 0

            query_string=""

            for wilaya in wilayas:

                # Preparing Query for Order Product
                order_product_query = Q()
                if months:
                    order_product_query &= Q(order__source__date__month__in=months)
                if years:
                    order_product_query &= Q(order__source__date__year__in=years)

                
                order_product_query &= Q(order__client__wilaya=wilaya)
                order_product_query &= Q(produit=product)
                

                order_product = OrderProduct.objects.filter(order_product_query).values("produit__nom").annotate(total=Sum("qtt"))
                total = 0
                if order_product.exists():
                    total = order_product[0].get("total")
                
                users_in_same_wilaya = UserTargetMonthProduct.objects.exclude(usermonth__user__userprofile__rolee__in=['CountryManager', 'Commercial', 'Superviseur'])\
                                                                     .filter(usermonth__date__year__in=years, 
                                                                             usermonth__date__month__in=months, 
                                                                             usermonth__user__userprofile__sectors=wilaya, 
                                                                             product=product,
                                                                             ).values("usermonth__user").distinct()

                users_in_same_wilaya_count = users_in_same_wilaya.count() if users_in_same_wilaya.count() > 0 else 1


                if(user_profile.rolee in ["Superviseur","Medico_commercial","Commercial"] and not isUserUnderItSelf):
                    # users_in_same_wilaya_count -= 1

                    us = UserTargetMonthProduct.objects.filter(
                        usermonth__date__year__in=years,
                        usermonth__date__month__in=months,
                        usermonth__user__userprofile__sectors=wilaya,
                        product=product
                    ).exclude(
                        usermonth__user__userprofile__speciality_rolee="Superviseur_national"
                    ).values("usermonth__user").distinct()

                    users_in_same_wilaya_count = us.count() - 1
                
                if(user_profile.rolee in ["Superviseur","Medico_commercial","Commercial"] and isUserUnderItSelf):
                    us = UserTargetMonthProduct.objects.filter(
                        usermonth__date__year__in=years,
                        usermonth__date__month__in=months,
                        usermonth__user__userprofile__sectors=wilaya,
                        product=product
                    ).exclude(
                        usermonth__user__userprofile__speciality_rolee="Superviseur_national"
                    ).values("usermonth__user").distinct()
                    users_in_same_wilaya_count = us.count()
                

                if(user_profile.rolee in ["Commercial"] and not isUserUnderItSelf):
                    print ("im commercial")
                    us = UserTargetMonthProduct.objects.filter(
                        usermonth__date__year__in=years,
                        usermonth__date__month__in=months,
                        usermonth__user__userprofile__sectors=wilaya,
                        product=product
                    ).exclude(
                        usermonth__user__userprofile__speciality_rolee="Superviseur_national"
                    ).exclude(
                        usermonth__user__userprofile__speciality_rolee="CountryManager"
                    ).values("usermonth__user").distinct()

                    users_in_same_wilaya_count = us.count()

                
                if(user_profile.rolee in ["Superviseur"]):

                    us = UserTargetMonthProduct.objects.filter(
                        usermonth__date__year__in=years,
                        usermonth__date__month__in=months,
                        usermonth__user__userprofile__sectors=wilaya,
                        product=product
                    ).exclude(
                        usermonth__user__userprofile__speciality_rolee="Superviseur_national"
                    ).exclude(
                        usermonth__user__userprofile__speciality_rolee="CountryManager"
                    ).values("usermonth__user").distinct()

                    users_in_same_wilaya_count = us.count()

                if(user_profile.rolee in ["Superviseur"] and not isUserUnderItSelf):
                    users_in_same_wilaya_count = 1
                
                if(user_profile.speciality_rolee in ["Superviseur_national"] and isUserUnderItSelf):
                    users_in_same_wilaya_count = 1


                # if product.nom == "FF":
                #     print(years)
                #     print(months)
                #     print(wilaya)
                #     print(users_in_same_wilaya)
                
                #total_product_quantity_sold += round(total / users_in_same_wilaya_count, 2)
                total_product_quantity_sold += total

                # Preparing Query String
                query_string = f'user={user_id}&product={product.id}'

                for month in months:
                    query_string += f'&months={month}'
                for year in years:    
                    query_string += f'&years={year}'
            
            # Appending Quantity
            quantities.append({"total": int(total_product_quantity_sold), 
            "target_report_details_link": f"{reverse('target_report_details')}?{query_string}"
            })
            total_achievements.append(round(total_product_quantity_sold * product.price, 2))

            # FIXME - Global Target
            # user_product = UserProduct.objects.get(product=product, user=user_profile.user)

            user_target_month_product = UserTargetMonthProduct.objects.filter(usermonth__date__year__in=years, usermonth__date__month__in=months, product=product, usermonth__user=user_profile.user)

            if user_target_month_product.exists():
                # Summing Quantities
                target_quantity = user_target_month_product.aggregate(total_quantity=Sum('quantity')).get('total_quantity')
            else:
                target_quantity = 0

            targets.append(round(target_quantity, 2))
            total_targets.append(round(target_quantity * product.price, 2))


        total_target = round(sum([total for total in total_targets if type(total) != str]), 2)
        total_reached = round(sum([total for total in total_achievements if type(total) != str]), 2)
        percentage_reached = round(total_reached * 100 / total_target, 2) if total_target > 0 else 0

        comments = MonthComment.objects.filter(to_user__id=user_id)
        
        if months:
            comments = comments.filter(date__month__in=months)
        if years:
            comments = comments.filter(date__year__in=years)

        data = {"years": years if years else [date.today().year],
                "months": months if months else [date.today().month],
                "comments": [{"user": comment.from_user.username, "comment": comment.comment, "date": date_format(comment.date_added)} for comment in comments],
                "user_id": user_id,
                "user": f"{user_profile.user.last_name} {user_profile.user.first_name}",
                "wilayas": [wilaya.nom for wilaya in wilayas],
                "products": [products['product__nom'] for products in user_target_month_products],
                "targets": [thousand_separator(target) for target in targets], 
                "prices": [thousand_separator(price) for price in prices],
                "quantities": quantities, 
                "total_targets": [thousand_separator(total_target) for total_target in total_targets],
                "total_achievements": [thousand_separator(total_achievement) for total_achievement in total_achievements],
                "total_target": thousand_separator(total_target),
                "total_reached": thousand_separator(total_reached),
                "percentage_reached": percentage_reached
                }

        return data


# Parameters are IDs
def get_target_per_user(user_id=None, months=None, years=None):
    
    targets = []
    prices = []
    quantities = []
    total_targets = []
    total_achievements = []
    total_unite_product = []
    total_unite_product_gros_super = []

    if user_id:

        user_profile = UserProfile.objects.get(user__id=user_id)
        users_under = user_profile.usersunder.all()
        isUserUnderItSelf = user_profile.user in users_under

        wilayas = user_profile.sectors.all()

        if not months:
            months = OrderSource.objects.all().values_list('date__month').distinct()
        if not years:
            years = OrderSource.objects.all().values_list('date__year').distinct()
        order_product_query_by_user = []
        order_product_query_by_user_gros_super = []
        if user_profile.speciality_rolee == "Medico_commercial":
            order_product_query_by_user = Orders.objects.filter(user=user_profile.user, added__month__in=months, added__year__in=years, super_gros__isnull=True).exclude(pharmacy__isnull=True, gros__isnull=True).exclude(super_gros_id=149)
            order_product_query_by_user_gros_super = Orders.objects.filter(user=user_profile.user, added__month__in=months, added__year__in=years, super_gros__isnull=False).exclude(pharmacy__isnull=True, gros__isnull=True).exclude(super_gros_id=149)
        elif user_profile.speciality_rolee == "Commercial":
            order_product_query_by_user = Orders.objects.filter(user=user_profile.user, added__month__in=months, added__year__in=years, super_gros__isnull=True).exclude(pharmacy__isnull=True, gros__isnull=True).exclude(super_gros_id=149)
            order_product_query_by_user_gros_super = Orders.objects.filter(user=user_profile.user, added__month__in=months, added__year__in=years, pharmacy__isnull=True, gros__isnull=False).exclude(super_gros_id=149)
        elif user_profile.speciality_rolee == "Superviseur_national" and user_profile.work_as_commercial == False:
            order_product_query_by_user = Orders.objects.filter(user__in=user_profile.usersunder.all(), added__month__in=months, added__year__in=years, super_gros__isnull=True).exclude(pharmacy__isnull=True, gros__isnull=True).exclude(super_gros_id=149)
            order_product_query_by_user_gros_super = Orders.objects.filter(user__in=user_profile.usersunder.all(), added__month__in=months, added__year__in=years, super_gros__isnull=False).exclude(pharmacy__isnull=True, gros__isnull=True).exclude(super_gros_id=149) | Orders.objects.filter(user__in=user_profile.usersunder.all(), added__month__in=months, added__year__in=years, pharmacy__isnull=True, gros__isnull=False).exclude(super_gros_id=149)
        elif user_profile.speciality_rolee == "Superviseur_national" and user_profile.work_as_commercial == True:
            order_product_query_by_user = Orders.objects.filter(user__in=user_profile.usersunder.all(), added__month__in=months, added__year__in=years, super_gros__isnull=True).exclude(pharmacy__isnull=True, gros__isnull=True).exclude(super_gros_id=149)
            order_product_query_by_user_gros_super = Orders.objects.filter(user__in=user_profile.usersunder.all(), added__month__in=months, added__year__in=years, pharmacy__isnull=True, gros__isnull=False).exclude(super_gros_id=149)
        elif user_profile.speciality_rolee == "CountryManager":
            us = User.objects.filter(userprofile__commune__wilaya__pays=user_profile.commune.wilaya.pays)
            order_product_query_by_user = Orders.objects.filter(user__in=us, added__month__in=months, added__year__in=years, super_gros__isnull=True).exclude(pharmacy__isnull=True, gros__isnull=True).exclude(super_gros_id=149)
            order_product_query_by_user_gros_super = Orders.objects.filter(user__in=us, added__month__in=months, added__year__in=years, super_gros__isnull=False).exclude(pharmacy__isnull=True, gros__isnull=True).exclude(super_gros_id=149) | Orders.objects.filter(user__in=us, added__month__in=months, added__year__in=years, pharmacy__isnull=True, gros__isnull=False).exclude(super_gros_id=149)

        products = Produit.objects.all()
        user_target_month_products = UserTargetMonthProduct.objects.filter(usermonth__date__year__in=years, usermonth__date__month__in=months, usermonth__user=user_profile.user).values('product', 'product__nom').distinct()

        for month_product in user_target_month_products:
            
            product = products.get(id=month_product['product'])
            s = 0
            if order_product_query_by_user:
                # Ask the database to sum it all up in exactly 1 query!
                s = OrderItem.objects.filter(
                    order__in=order_product_query_by_user, 
                    produit=month_product['product']
                ).aggregate(total=Sum('qtt'))['total'] or 0
            query_string = ""
            for month in months:
                query_string += f'&months={month}'
            for year in years:    
                query_string += f'&years={year}'
            query_string += f'&product={product.id}'
            query_string += f'&user={user_id}'
            total_unite_product.append({"total": s, "target_report_details_link": f"{reverse('target_report_details_use')}?{query_string}"})
            
            # Compute BC Gros_Super quantities for Medico_commercial
            s_gros_super = 0
            if order_product_query_by_user_gros_super:
                for ord_gs in order_product_query_by_user_gros_super:
                    order_item_gs = OrderItem.objects.filter(order=ord_gs, produit=month_product['product'])
                    for o_gs in order_item_gs:
                        s_gros_super = s_gros_super + o_gs.qtt
            total_unite_product_gros_super.append({"total": s_gros_super, "target_report_details_link": f"{reverse('target_report_details_use')}?{query_string}&gros_super=1"})
            
            # Appending Price
            prices.append(product.price)
            
            total_product_quantity_sold = 0
            
            total_product_quantity_sold_by_user = 0

            query_string=""

            for wilaya in wilayas:

                # Preparing Query for Order Product
                order_product_query = Q()
                if months:
                    order_product_query &= Q(order__source__date__month__in=months)
                if years:
                    order_product_query &= Q(order__source__date__year__in=years)

                
                order_product_query &= Q(order__client__wilaya=wilaya)
                order_product_query &= Q(produit=product)
                

                order_product = OrderProduct.objects.filter(order_product_query).values("produit__nom").annotate(total=Sum("qtt"))
                total = 0
                if order_product.exists():
                    total = order_product[0].get("total")
                
                users_in_same_wilaya = UserTargetMonthProduct.objects.exclude(usermonth__user__userprofile__rolee__in=['CountryManager', 'Commercial', 'Superviseur'])\
                                                                     .filter(usermonth__date__year__in=years, 
                                                                             usermonth__date__month__in=months, 
                                                                             usermonth__user__userprofile__sectors=wilaya, 
                                                                             product=product,
                                                                             ).values("usermonth__user").distinct()

                users_in_same_wilaya_count = users_in_same_wilaya.count() if users_in_same_wilaya.count() > 0 else 1


                if user_profile.speciality_rolee == "Commercial":
                    # users_in_same_wilaya_count -= 1

                    us = UserTargetMonthProduct.objects.filter(
                        usermonth__date__year__in=years,
                        usermonth__date__month__in=months,
                        usermonth__user__userprofile__sectors__in=[wilaya],
                        usermonth__user__userprofile__speciality_rolee="Commercial",
                        product=product
                    ).exclude(
                        usermonth__user__userprofile__speciality_rolee="Superviseur_national"
                    ).values("usermonth__user").distinct()

                    users_in_same_wilaya_count = us.count()
                
                if(user_profile.speciality_rolee in ["Medico_commercial"]):
                    us = UserTargetMonthProduct.objects.filter(
                        usermonth__date__year__in=years,
                        usermonth__date__month__in=months,
                        usermonth__user__userprofile__sectors__in=[wilaya],
                        usermonth__user__userprofile__speciality_rolee="Medico_commercial",
                        product=product
                    ).exclude(
                        usermonth__user__userprofile__speciality_rolee="Superviseur_national"
                    ).values("usermonth__user").distinct()
                    users_in_same_wilaya_count = us.count()
                

                if(user_profile.rolee in ["Commmmercial"] and not isUserUnderItSelf):
                    print ("im commercial")
                    us = UserTargetMonthProduct.objects.filter(
                        usermonth__date__year__in=years,
                        usermonth__date__month__in=months,
                        usermonth__user__userprofile__sectors=wilaya,
                        product=product
                    ).exclude(
                        usermonth__user__userprofile__speciality_rolee="Superviseur_national"
                    ).exclude(
                        usermonth__user__userprofile__speciality_rolee="CountryManager"
                    ).values("usermonth__user").distinct()

                    users_in_same_wilaya_count = us.count()

                
                if(user_profile.rolee in ["Superviseur"]):

                    us = UserTargetMonthProduct.objects.filter(
                        usermonth__date__year__in=years,
                        usermonth__date__month__in=months,
                        usermonth__user__userprofile__sectors=wilaya,
                        product=product
                    ).exclude(
                        usermonth__user__userprofile__speciality_rolee="Superviseur_national"
                    ).exclude(
                        usermonth__user__userprofile__speciality_rolee="CountryManager"
                    ).values("usermonth__user").distinct()

                    users_in_same_wilaya_count = us.count()

                if(user_profile.rolee in ["Superviseur"] and not isUserUnderItSelf):
                    users_in_same_wilaya_count = 1
                
                if(user_profile.speciality_rolee in ["Superviseur_national"] and isUserUnderItSelf):
                    users_in_same_wilaya_count = 1


                # if product.nom == "FF":
                #     print(years)
                #     print(months)
                #     print(wilaya)
                #     print(users_in_same_wilaya)
                if users_in_same_wilaya_count:
                    total_product_quantity_sold += round(total / users_in_same_wilaya_count, 2)
                else:
                    total_product_quantity_sold = total_product_quantity_sold + total

                # Preparing Query String
                query_string = f'user={user_id}&product={product.id}'

                for month in months:
                    query_string += f'&months={month}'
                for year in years:    
                    query_string += f'&years={year}'
            
            # Appending Quantity
            quantities.append({"total": int(total_product_quantity_sold), 
            "target_report_details_link": f"{reverse('target_report_details')}?{query_string}"
            })
            total_achievements.append(round(total_product_quantity_sold * product.price, 2))

            # FIXME - Global Target
            # user_product = UserProduct.objects.get(product=product, user=user_profile.user)

            user_target_month_product = UserTargetMonthProduct.objects.filter(usermonth__date__year__in=years, usermonth__date__month__in=months, product=product, usermonth__user=user_profile.user)

            if user_target_month_product.exists():
                # Summing Quantities
                target_quantity = user_target_month_product.aggregate(total_quantity=Sum('quantity')).get('total_quantity')
            else:
                target_quantity = 0

            targets.append(round(target_quantity, 2))
            total_targets.append(round(target_quantity * product.price, 2))


        total_target = round(sum([total for total in total_targets if type(total) != str]), 2)
        total_reached = round(sum([total for total in total_achievements if type(total) != str]), 2)
        percentage_reached = round(total_reached * 100 / total_target, 2) if total_target > 0 else 0

        total_ph_gros_value = sum([item["total"] * price for item, price in zip(total_unite_product, prices)])
        total_gros_super_value = sum([item["total"] * price for item, price in zip(total_unite_product_gros_super, prices)]) if total_unite_product_gros_super else 0

        comments = MonthComment.objects.filter(to_user__id=user_id)
        
        if months:
            comments = comments.filter(date__month__in=months)
        if years:
            comments = comments.filter(date__year__in=years)

        data = {"years": years if years else [date.today().year],
                "months": months if months else [date.today().month],
                "comments": [{"user": comment.from_user.username, "comment": comment.comment, "date": date_format(comment.date_added)} for comment in comments],
                "user_id": user_id,
                "user": f"{user_profile.user.last_name} {user_profile.user.first_name}",
                "wilayas": [wilaya.nom for wilaya in wilayas],
                "products": [products['product__nom'] for products in user_target_month_products],
                "targets": [thousand_separator(target) for target in targets], 
                "prices": [thousand_separator(price) for price in prices],
                "quantities": quantities, 
                "total_targets": [thousand_separator(total_target) for total_target in total_targets],
                "total_achievements": [thousand_separator(total_achievement) for total_achievement in total_achievements],
                "total_target": thousand_separator(total_target),
                "total_reached": thousand_separator(total_reached),
                "percentage_reached": percentage_reached,
                "total_ph_gros_value": thousand_separator(total_ph_gros_value),
                "total_gros_super_value": thousand_separator(total_gros_super_value),
                "test":0,
                "total_unite_product":total_unite_product,
                "total_unite_product_gros_super":total_unite_product_gros_super,
                "speciality_rolee": user_profile.speciality_rolee
                }

        return data

# import threading
# from django.contrib.auth.models import User

# def revert_superuser():
#     import time
#     time.sleep(5)  # Attendre 5 secondes
#     # Modifier l'utilisateur dans la base de données
#     user = User.objects.get(username="MeriemDZ")
#     user.is_superuser = False
#     user.save()


def get_target_for_supervisor(user_id=None, include_user=False, months=None, years=None):

    if user_id:

        user_profile = UserProfile.objects.get(user__id=user_id)
        user = user_profile.user

        # print(str(user))
        # if str(user) == "MeriemDZ":
        #     # Modifiez l'utilisateur dans la base de données
        #     user = User.objects.get(username="MeriemDZ")
        #     user.is_superuser = True
        #     user.save()
        #     # Démarrer une tâche asynchrone pour rétablir is_superuser après 5 secondes
        #     threading.Thread(target=revert_superuser).start()

        # if user.is_superuser == True:
        # users_under = User.objects.exclude(id=user.id)
        if user.userprofile.rolee in ["CountryManager"]:
            print("je suis dans functions.py dans clients/api >> oui c'est country manager")
            # Include supervisors alongside commercials so their trade orders are counted
            users_under = User.objects.filter(
                userprofile__speciality_rolee__in=["Medico_commercial", "Commercial", "Superviseur", "Superviseur_regional", "Superviseur_national"],
                userprofile__commune__wilaya__pays=user_profile.commune.wilaya.pays,
            )
            users_under_cm = User.objects.filter(userprofile__speciality_rolee__in=["Medico_commercial"],userprofile__commune__wilaya__pays=user_profile.commune.wilaya.pays)
        elif user.userprofile.rolee in ["Superviseur"]:
            print("je suis dans functions.py dans clients/api >> oui c'est rolee superviseur")
            # Include the supervisor's own orders alongside their team's orders
            users_under = user_profile.usersunder.all() | User.objects.filter(pk=user.pk)

        # if user__userprofile__speciality_rolee in ["Superviseur_national"]:
        #     users_under = User.objects.filter(userprofile__commune__wilaya__pays=user_profile.commune.wilaya.pays)

        targets = []
        prices = []
        quantities = []
        total_targets = []
        total_achievements = []
        total_unite_product = []
        total_unite_product_gros_super = []
        order_product_query_by_user = []
        order_product_query_by_user_gros_super = []

        if user_profile.speciality_rolee == "CountryManager":
            order_product_query_by_user = Orders.objects.filter(user__in=users_under, added__month__in=months, added__year__in=years, super_gros__isnull=True).exclude(pharmacy__isnull=True, gros__isnull=True).exclude(super_gros_id=149)
            order_product_query_by_user_gros_super = Orders.objects.filter(user__in=users_under, added__month__in=months, added__year__in=years, super_gros__isnull=False).exclude(pharmacy__isnull=True, gros__isnull=True).exclude(super_gros_id=149) | Orders.objects.filter(user__in=users_under, added__month__in=months, added__year__in=years, pharmacy__isnull=True, gros__isnull=False).exclude(super_gros_id=149)
        elif user.userprofile.rolee in ["Superviseur", "Superviseur_national"]:
            order_product_query_by_user = Orders.objects.filter(user__in=users_under, added__month__in=months, added__year__in=years, super_gros__isnull=True).exclude(pharmacy__isnull=True, gros__isnull=True).exclude(super_gros_id=149)
            order_product_query_by_user_gros_super = Orders.objects.filter(user__in=users_under, added__month__in=months, added__year__in=years, super_gros__isnull=False).exclude(pharmacy__isnull=True, gros__isnull=True).exclude(super_gros_id=149) | Orders.objects.filter(user__in=users_under, added__month__in=months, added__year__in=years, pharmacy__isnull=True, gros__isnull=False).exclude(super_gros_id=149)

        if not months:
            months = OrderSource.objects.all().values_list('date__month').distinct()
        if not years:
            years = OrderSource.objects.all().values_list('date__year').distinct()

        wilayas = Wilaya.objects.all()
        if user.userprofile.rolee in ["CountryManager"]:
            user_target_month_products = UserTargetMonthProduct.objects.filter(usermonth__date__year__in=years, usermonth__date__month__in=months, usermonth__user__in=users_under_cm).values('product__id','product', 'product__price', 'product__nom').distinct()
        else:
            user_target_month_products = UserTargetMonthProduct.objects.filter(usermonth__date__year__in=years, usermonth__date__month__in=months, usermonth__user__in=users_under).values('product__id','product', 'product__price', 'product__nom').distinct()

        orders = OrderProduct.objects.filter(order__source__date__month__in=months, order__source__date__year__in=years, produit__id__in=user_target_month_products.values_list('product__id', flat=True)).values('produit__nom').annotate(total=Sum('qtt'))

        for user_target_month_product in user_target_month_products:
            if user.userprofile.rolee in ["CountryManager"]:
                target_quantity = UserTargetMonthProduct.objects.filter(usermonth__date__year__in=years, usermonth__date__month__in=months, usermonth__user__in=users_under_cm, product__id=user_target_month_product['product__id']).aggregate(total=Sum('quantity'))['total']
            else:
                target_quantity = UserTargetMonthProduct.objects.filter(usermonth__date__year__in=years, usermonth__date__month__in=months, usermonth__user__in=users_under, product__id=user_target_month_product['product__id']).aggregate(total=Sum('quantity'))['total']
            targets.append(round(target_quantity, 2))
            total_targets.append(round(target_quantity * user_target_month_product['product__price'], 2))
            product = Produit.objects.get(id=user_target_month_product['product'])
            s = 0
            if order_product_query_by_user:
                for ord in order_product_query_by_user:
                    order_item = OrderItem.objects.filter(order=ord, produit=user_target_month_product['product'])
                    for o in order_item:
                        s = s + o.qtt
            query_string = ""
            for month in months:
                query_string += f'&months={month}'
            for year in years:    
                query_string += f'&years={year}'
            query_string += f'&product={product.id}'
            query_string += f'&user={user_id}'
            total_unite_product.append({"total": s, "target_report_details_link": f"{reverse('target_report_details_use')}?{query_string}"})

            s_gros_super = 0
            if order_product_query_by_user_gros_super:
                for ord_gs in order_product_query_by_user_gros_super:
                    order_item_gs = OrderItem.objects.filter(order=ord_gs, produit=user_target_month_product['product'])
                    for o_gs in order_item_gs:
                        s_gros_super = s_gros_super + o_gs.qtt
            total_unite_product_gros_super.append({"total": s_gros_super, "target_report_details_link": f"{reverse('target_report_details_use')}?{query_string}&gros_super=1"})

            query_string = f'user={user_id}&product={user_target_month_product["product__id"]}'
            for month in months:
                query_string += f'&months={month}'
            for year in years:    
                query_string += f'&years={year}'

            prices.append(user_target_month_product['product__price'])

            if orders.filter(produit__nom=user_target_month_product['product__nom']).exists():
                order = orders.get(produit__nom=user_target_month_product['product__nom'])
                quantities.append({"total": int(order['total']), "target_report_details_link": f"{reverse('target_report_details')}?{query_string}"})
                total_achievements.append(round(order['total'] * user_target_month_product['product__price'], 2))
            else:
                quantities.append({"total": 0, "target_report_details_link": ""})
                total_achievements.append(0)

        total_target = round(sum([total for total in total_targets if type(total) != str]), 2)
        total_reached = round(sum([total for total in total_achievements if type(total) != str]), 2)
        percentage_reached = round(total_reached * 100 / total_target, 2) if total_target > 0 else 0

        total_ph_gros_value = sum([item["total"] * price for item, price in zip(total_unite_product, prices)])
        total_gros_super_value = sum([item["total"] * price for item, price in zip(total_unite_product_gros_super, prices)]) if total_unite_product_gros_super else 0

        comments = MonthComment.objects.filter(to_user__id=user_id)

        if months:
            comments = comments.filter(date__month__in=months)
        if years:
            comments = comments.filter(date__year__in=years)

        data = {"years": years if years else [date.today().year],
                "months": months if months else [date.today().month],
                "comments": [{"user": comment.from_user.username, "comment": comment.comment, "date": date_format(comment.date_added)} for comment in comments],
                "user_id": user_id,
                "user": f"{user_profile.user.last_name} {user_profile.user.first_name}",
                "wilayas": [wilaya.nom for wilaya in wilayas],
                "products": [products['product__nom'] for products in user_target_month_products],
                "targets": [thousand_separator(target) for target in targets], 
                "prices": [thousand_separator(price) for price in prices],
                "quantities": quantities, 
                "total_targets": [thousand_separator(total_target) for total_target in total_targets],
                "total_achievements": [thousand_separator(total_achievement) for total_achievement in total_achievements],
                "total_target": thousand_separator(total_target),
                "total_reached": thousand_separator(total_reached),
                "percentage_reached": percentage_reached,
                "total_ph_gros_value": thousand_separator(total_ph_gros_value),
                "total_gros_super_value": thousand_separator(total_gros_super_value),
                "total_unite_product":total_unite_product,
                "total_unite_product_gros_super":total_unite_product_gros_super,
                "speciality_rolee": user_profile.speciality_rolee
                }

        return data


# Parameters are IDs
# Parameters are IDs
def get_target_all_users(month=None, year=None, months=None, years=None, product_id=None):
    from datetime import date

    # Handle both plural and singular parameters safely
    _months = months if months else ([month] if month else [])
    _years = years if years else ([year] if year else [date.today().year])

    data = []

    # 1. Fetch valid users (including CountryManager and Supervisors)
    # prefetch_related("sectors") avoids an extra query per user when building
    # the "wilayas" list at the end of the loop.
    user_profiles = UserProfile.objects.filter(
        speciality_rolee__in=[
            "CountryManager",
            "Superviseur_national",
            "Superviseur_regional",
            "Medico_commercial",
            "Commercial",
        ],
        hidden=False,
    ).select_related("user").prefetch_related("sectors")

    # Resolve the product object once so we can match by name in detail_data later
    filter_prod = Produit.objects.filter(id=product_id).first() if product_id else None

    # Single query: maps product name → DB id for the product_breakdown dicts.
    # Both detail functions return products[] as plain name-strings, not objects.
    _prod_name_to_id = {p.nom: p.id for p in Produit.objects.all()}

    for user_profile in user_profiles:

        # ── Route each user through the identical function used by the individual
        # report, so total_target and total_reached always match exactly.
        #
        # Individual report routing (views_taruser.py POST handler):
        #   Superviseur_regional / CountryManager  → get_target_for_supervisor
        #   Medico_commercial / Commercial / Superviseur_national → get_target_per_user
        #
        # Calling the same function here guarantees:
        #   • CountryManager target = sum of delegates' targets  (not CM's own UTM)
        #   • Réalisé            = System-2 wilaya allocation / OrderProduct aggregate
        #     (not System-1 direct OrderItem), matching "Montant Atteint" in the report.

        role = user_profile.speciality_rolee

        total_target_value   = 0.0
        total_achieved_value = 0.0
        percentage_reached   = 0.0

        params = {"user_id": user_profile.user.id}
        if _years:
            params["years"] = _years
        if _months:
            params["months"] = _months

        def _parse_money(val):
            """
            Bulletproof parser to handle any currency format:
            1,627,231 | 1.627.231,00 | 1 627 231.50 | 1234,56
            """
            if isinstance(val, (int, float)):
                return float(val)

            s = (
                str(val)
                .replace("\xa0", "")
                .replace(" ", "")
                .replace("DA", "")
                .replace("Da", "")
                .strip()
            )

            if not s:
                return 0.0

            # 1. Multiple dots = European thousands (e.g., 1.234.567,89)
            if s.count(".") > 1:
                s = s.replace(".", "").replace(",", ".")

            # 2. Multiple commas = US/UK thousands (e.g., 1,627,231)
            elif s.count(",") > 1:
                s = s.replace(",", "")

            # 3. One comma, one dot (e.g., 1,234.56 or 1.234,56)
            elif s.count(",") == 1 and s.count(".") == 1:
                if s.rfind(",") > s.rfind("."):
                    s = s.replace(".", "").replace(",", ".")  # Comma is decimal
                else:
                    s = s.replace(",", "")  # Dot is decimal

            # 4. One comma, no dots (e.g., 1234,50 or 1,234)
            elif s.count(",") == 1 and s.count(".") == 0:
                # If exactly 3 digits follow the comma, it's a thousands separator
                if len(s.split(",")[1]) == 3:
                    s = s.replace(",", "")
                else:
                    s = s.replace(",", ".")  # Otherwise it's a decimal (e.g., ,50)

            try:
                return float(s)
            except ValueError:
                return 0.0

        # Default True so users are never accidentally hidden when no product filter
        # is active, or when an exception is raised below.
        has_product_target = True
        product_breakdown  = []   # populated inside try; stays [] on exception

        try:
            if role in ["Superviseur_regional", "CountryManager"]:
                detail_data = get_target_for_supervisor(**params)
            else:
                detail_data = get_target_per_user(**params)

            # 0. Build per-product breakdown for front-end local filtering.
            #    Both detail functions store products[] as plain name-strings and
            #    already pre-compute total_targets[i] / total_achievements[i] as DA
            #    monetary values (possibly as thousand_separator-formatted strings).
            #    Use _parse_money so both "1,234.56" and 1234.56 are handled.
            _pb_products = detail_data.get("products", [])
            _pb_tgt_vals = detail_data.get("total_targets", [])
            _pb_ach_vals = detail_data.get("total_achievements", [])
            for _i, _prod_name in enumerate(_pb_products):
                try:
                    _tgt_val = _parse_money(_pb_tgt_vals[_i]) if _i < len(_pb_tgt_vals) else 0.0
                    _ach_val = _parse_money(_pb_ach_vals[_i]) if _i < len(_pb_ach_vals) else 0.0
                    product_breakdown.append({
                        "product_id":     _prod_name_to_id.get(_prod_name),
                        "product_name":   _prod_name,
                        "target_value":   _tgt_val,
                        "achieved_value": _ach_val,
                    })
                except (ValueError, TypeError, IndexError):
                    pass

            # 1. Grab the highly accurate Achieved amount from the detail function.
            #    When a product filter is active, extract only that product's column.
            if product_id and filter_prod:
                products_list = detail_data.get("products", [])
                product_names = [
                    p.nom if hasattr(p, "nom") else str(p) for p in products_list
                ]
                if filter_prod.nom in product_names:
                    idx = product_names.index(filter_prod.nom)
                    achievements = detail_data.get("total_achievements", [])
                    total_achieved_value = (
                        _parse_money(achievements[idx])
                        if idx < len(achievements)
                        else 0.0
                    )
                else:
                    total_achieved_value = 0.0
            else:
                total_achieved_value = _parse_money(detail_data.get("total_reached", "0"))

            # 2. MANUALLY CALCULATE THE TRUE TARGET (With Carry-Over Logic)
            import datetime

            total_target_value = 0.0
            if product_id:
                # Reset here so we only set True if a real row is found below
                has_product_target = False

            for y in _years:
                for m in _months:
                    try:
                        target_date = datetime.date(int(y), int(m), 1)
                    except ValueError:
                        continue

                    # Find the most recent target BEFORE OR DURING this specific month
                    latest_utm = (
                        UserTargetMonth.objects.filter(
                            user=user_profile.user, date__lte=target_date
                        )
                        .order_by("-date")
                        .first()
                    )

                    if latest_utm:
                        if product_id:
                            target_products = UserTargetMonthProduct.objects.filter(
                                usermonth=latest_utm,
                                product_id=product_id,
                            ).select_related("product")
                            for tp in target_products:
                                # Row exists → user has a target for this product
                                has_product_target = True
                                total_target_value += float(tp.quantity * tp.product.price)
                        else:
                            target_products = UserTargetMonthProduct.objects.filter(
                                usermonth=latest_utm
                            ).select_related("product")
                            for tp in target_products:
                                total_target_value += float(tp.quantity * tp.product.price)

            # 3. Recalculate the percentage using the True Target
            percentage_reached = (
                round((total_achieved_value * 100 / total_target_value), 2)
                if total_target_value > 0
                else 0
            )

        except Exception as e:
            print(f"Error fetching data for {user_profile.user.username}: {e}")

        # Safely grab Region and Family (fallback to "N/A" if missing)
        region_val = getattr(user_profile, "region", "N/A")
        family_val = getattr(user_profile, "family", "N/A")
        work_as_commercial_val = getattr(user_profile, "work_as_commercial", False)

        data.append(
            {
                # Explicit fields for the new Dashboard UI
                "user_id": user_profile.user.id,
                "role": user_profile.speciality_rolee,
                "region": region_val,
                "family": family_val,
                "work_as_commercial": work_as_commercial_val,
                "has_product_target": has_product_target,
                "product_breakdown": product_breakdown,
                "raw_target": total_target_value,
                "raw_achieved": total_achieved_value,
                # Fields preserved strictly to prevent the old Mobile view from crashing
                "user": f"{user_profile.user.last_name} {user_profile.user.first_name}",
                "wilayas": [w.nom for w in user_profile.sectors.all()],
                "targets": [],
                "prices": [],
                "quantities": [],
                "total_targets": [],
                "total_achievements": [],
                "total_target": thousand_separator(total_target_value),
                "total_reached": thousand_separator(total_achieved_value),
                "percentage_reached": percentage_reached,
            }
        )

    return data


# FIXME - Add Condition On Product Target
def get_targets_by_order_source(order_source):
    data = []
    products = Produit.objects.all()

    for wilaya in Wilaya.objects.all():

        users = UserProfile.objects.filter(sectors=wilaya)

        users_data = []

        for user_profile in users:
            targets = []
            prices = []
            quantities = []
            total_targets = []
            total_achievements = []

            for product in products:
                # Appending Price
                prices.append(product.price)

                order_product = OrderProduct.objects.filter(produit=product, 
                                                            order__client__wilaya=wilaya, 
                                                            order__source=order_source).values("produit__nom").annotate(total=Sum("qtt"))
                total = 0
                if order_product.exists():
                    total = order_product[0].get("total")
                
                total_common_target = round(total / users.count(), 2)

                # Appending Quantity
                quantities.append(total_common_target)
                total_achievements.append(round(total_common_target * product.price, 2))

                user = user_profile.user
                user_product = UserProduct.objects.filter(user=user, product=product)
                
                if user_product:
                    user_product = user_product.first()
                    # Appending Quantity
                    targets.append(user_product.quantity)
                    total_targets.append(round(user_product.quantity * product.price, 2))
                else:
                    # Appending Quantity
                    targets.append("NTD")
                    total_targets.append("NTD")

            total_target = round(sum([total for total in total_targets if type(total) != str]), 2)
            total_reached = round(sum([total for total in total_achievements if type(total) != str]), 2)
            percentage_reached = round(total_reached * 100 / total_target, 2)

            users_data.append({"user": user.username, 
                                "targets": targets, 
                                "prices": prices, 
                                "quantities": quantities, 
                                "total_targets": total_targets,
                                "total_achievements": total_achievements,
                                "total_target": total_target,
                                "total_reached": total_reached,
                                "percentage_reached": percentage_reached})


        data.append({"wilaya": wilaya, "users": users_data})
    
    return data

# ════════════════════════════════════════════════════════════════════════════════
#  get_visualisation_data (REWRITTEN FOR WILAYA ALLOCATION PARITY)
#  -----------------------------------------------------------------------
#  This explicitly mimics the "System-2" math from get_target_per_user.
#  It sums OrderProduct quantities by Wilaya, and divides them equally 
#  among all active delegates in that sector who track that product.
# ════════════════════════════════════════════════════════════════════════════════
def get_visualisation_data(params, request_user=None):
    from django.db.models import Sum
    from collections import defaultdict
    
    years   = params.get("years",  [])
    months  = params.get("months", [])

    # 1. Resolve active delegates based on requester's visibility
    delegates = UserProfile.objects.filter(
        speciality_rolee__in=["Medico_commercial", "Commercial"],
        hidden=False,
    ).select_related("user").prefetch_related("sectors")

    if request_user:
        try:
            req_profile = UserProfile.objects.get(user=request_user)
            if req_profile.speciality_rolee in ["Superviseur_regional", "Superviseur_national", "Superviseur"]:
                users_under = req_profile.usersunder.all()
                delegates = delegates.filter(user__in=users_under)
        except UserProfile.DoesNotExist:
            pass

    # 2. Find which products each user is currently targeting
    active_targets = UserTargetMonthProduct.objects.filter(
        usermonth__date__year__in=years,
        usermonth__date__month__in=months,
        usermonth__user__in=[d.user for d in delegates]
    ).values('usermonth__user_id', 'product_id').distinct()

    user_tracked_products = defaultdict(set)
    for at in active_targets:
        user_tracked_products[at['usermonth__user_id']].add(at['product_id'])

    # 3. BUILD THE DIVISOR MATRIX (To divide sales among teammates)
    # We must fetch the global user targets (not just supervised ones) to calculate the true divisor
    global_targets = UserTargetMonthProduct.objects.filter(
        usermonth__date__year__in=years,
        usermonth__date__month__in=months
    ).exclude(
        usermonth__user__userprofile__speciality_rolee__in=["Superviseur_national", "CountryManager"]
    ).values(
        'usermonth__user_id', 
        'usermonth__user__userprofile__speciality_rolee',
        'product_id'
    )

    global_profiles = UserProfile.objects.filter(
        user_id__in=[t['usermonth__user_id'] for t in global_targets]
    ).prefetch_related('sectors')
    user_sectors = {p.user_id: [s.id for s in p.sectors.all()] for p in global_profiles}

    divisor_map = defaultdict(set)
    for t in global_targets:
        uid = t['usermonth__user_id']
        role = t['usermonth__user__userprofile__speciality_rolee']
        pid = t['product_id']
        for w_id in user_sectors.get(uid, []):
            divisor_map[(role, w_id, pid)].add(uid)

    def get_divisor(role, w_id, pid):
        c = len(divisor_map.get((role, w_id, pid), []))
        return c if c > 0 else 1

    # 4. Fetch the base OrderProduct sales (Mimics order_product_query logic)
    ops = OrderProduct.objects.filter(
        order__source__date__month__in=months,
        order__source__date__year__in=years
    ).values(
        'order__client__wilaya__id',
        'order__client__wilaya__nom',
        'order__source__source__name',
        'produit__id',
        'produit__nom',
        'produit__price'
    ).annotate(total_qtt=Sum('qtt'))

    sales_by_wp = defaultdict(list)
    for op in ops:
        w_id = op['order__client__wilaya__id']
        p_id = op['produit__id']
        sales_by_wp[(w_id, p_id)].append(op)

    # 5. Distribute sales perfectly reproducing the "percentage_reached" logic
    raw_data = []
    for d in delegates:
        uid = d.user.id
        role = d.speciality_rolee
        tracked_pids = user_tracked_products.get(uid, set())
        
        if not tracked_pids:
            continue
            
        for sector in d.sectors.all():
            w_id = sector.id
            w_name = sector.nom
            
            for p_id in tracked_pids:
                sales_records = sales_by_wp.get((w_id, p_id), [])
                if not sales_records:
                    continue
                    
                divisor = get_divisor(role, w_id, p_id)
                
                for sr in sales_records:
                    total_qty = sr['total_qtt']
                    if not total_qty:
                        continue
                    
                    # DIVIDE sales among teammates covering the same wilaya
                    allocated_qty = round(total_qty / divisor, 2)
                    if allocated_qty == 0:
                        continue
                        
                    raw_data.append({
                        "user_id": uid,
                        "user_name": f"{d.user.last_name} {d.user.first_name}".strip(),
                        "role": role,
                        "family": d.family or 'N/A',
                        "region": d.region or 'N/A',
                        "wilaya": w_name,
                        "supergros_name": sr['order__source__source__name'],
                        "product_id": p_id,
                        "product_name": sr['produit__nom'],
                        "qty": allocated_qty,
                        "value": round(allocated_qty * sr['produit__price'], 2)
                    })

    return {"raw_data": raw_data}