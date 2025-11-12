# Django Imports
from django.contrib.auth.models import User
from django.db.models import Sum
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
                order_product = order_product.first()
                products_list.append(order_product.qtt)
                continue
            products_list.append(0)

        user_profiles = UserProfile.objects.filter(sectors=order.client.wilaya)
        
        data["orders"].append({"order": order, "user_profiles": user_profiles, "products_list": products_list })


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
        if user_profile.speciality_rolee == "Medico_commercial":
            order_product_query_by_user = Orders.objects.filter(user=user_profile.user, added__month__in=months, added__year__in=years, super_gros__isnull=True, from_company=False)
        elif user_profile.speciality_rolee == "Commercial":
            order_product_query_by_user = Orders.objects.filter(user=user_profile.user, added__month__in=months, added__year__in=years, pharmacy__isnull=True, from_company=False)

        products = Produit.objects.all()
        user_target_month_products = UserTargetMonthProduct.objects.filter(usermonth__date__year__in=years, usermonth__date__month__in=months, usermonth__user=user_profile.user).values('product', 'product__nom').distinct()

        for month_product in user_target_month_products:
            
            product = products.get(id=month_product['product'])
            s = 0
            if order_product_query_by_user:
                for ord in order_product_query_by_user:
                    order_item = OrderItem.objects.filter(order=ord, produit=month_product['product'])
                    for o in order_item:
                        s = s + o.qtt
            
            total_unite_product.append(s)
            
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
                "test":0,
                "total_unite_product":total_unite_product
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
            users_under = User.objects.filter(userprofile__speciality_rolee__in=["Medico_commercial","Commercial"],userprofile__commune__wilaya__pays=user_profile.commune.wilaya.pays)
            users_under_cm = User.objects.filter(userprofile__speciality_rolee__in=["Medico_commercial"],userprofile__commune__wilaya__pays=user_profile.commune.wilaya.pays)
        elif user.userprofile.rolee in ["Superviseur"]:
            print("je suis dans functions.py dans clients/api >> oui c'est rolee superviseur")
            users_under = user_profile.usersunder.all()
        
        # if user__userprofile__speciality_rolee in ["Superviseur_national"]:
        #     users_under = User.objects.filter(userprofile__commune__wilaya__pays=user_profile.commune.wilaya.pays)



        targets = []
        prices = []
        quantities = []
        total_targets = []
        total_achievements = []

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
def get_target_all_users(month=None, year=None):
    
    data = []

    user_profiles = UserProfile.objects.all()

    for user_profile in user_profiles:
        
        # Check if the user has at least one target
        if UserProduct.objects.filter(user=user_profile.user).exists():

            targets = []
            prices = []
            quantities = []
            total_targets = []
            total_achievements = []

            products = Produit.objects.filter(userproduct__user=user_profile.user)

            wilayas = user_profile.sectors.all()

            for product in products:
                # Appending Price
                prices.append(product.price)
                
                total_product_quantity_sold = 0

                for wilaya in wilayas:

                    # Preparing Query for Order Product
                    order_product_query = Q()
                    if month:
                        order_product_query &= Q(order__source__date__month=month)
                    if year:
                        order_product_query &= Q(order__source__date__year=year)
                    order_product_query &= Q(order__client__wilaya=wilaya)
                    order_product_query &= Q(produit=product)

                    
                    order_product = OrderProduct.objects.filter(order_product_query).values("produit__nom").annotate(total=Sum("qtt"))
                    total = 0
                    if order_product.exists():
                        total = order_product[0].get("total")

                    users_in_same_wilaya = UserProduct.objects.filter(user__userprofile__sectors=wilaya, product=product)

                    total_product_quantity_sold += round(total / users_in_same_wilaya.count(), 2)

                # Preparing Query String
                query_string = f'user={user_profile.user.id}&product={product.id}'

                if month:
                    query_string += f'&month={month}'
                if year: 
                    query_string += f'&year={year}'
                    
                # Appending Quantity
                quantities.append({"total": total_product_quantity_sold, 
                "target_report_details_link": f"{reverse('target_report_details')}?{query_string}"
                })
                total_achievements.append(round(total_product_quantity_sold * product.price, 2))

                user_product = UserProduct.objects.get(product=product, user=user_profile.user)

                # Appending Quantity
                targets.append(user_product.quantity)
                total_targets.append(round(user_product.quantity * product.price, 2))


            total_target = round(sum([total for total in total_targets if type(total) != str]), 2)
            total_reached = round(sum([total for total in total_achievements if type(total) != str]), 2)
            percentage_reached = round(total_reached * 100 / total_target, 2) if total_target > 0 else 0

            data.append({"user": f"{user_profile.user.last_name} {user_profile.user.first_name}",
                        "wilayas": wilayas,
                        "products": products,
                        "targets": targets, 
                        "prices": prices, 
                        "quantities": quantities, 
                        "total_targets": total_targets,
                        "total_achievements": total_achievements,
                        "total_target": total_target,
                        "total_reached": total_reached,
                        "percentage_reached": percentage_reached})


    
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
