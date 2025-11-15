# Django Imports
from django.contrib.auth.models import User
from django.db.models import Sum
from django.db.models import Q
from django.shortcuts import reverse

# App Imports
from accounts.models import UserProfile, UserProduct
from regions.models import Wilaya
from clients.models import *
from produits.models import Produit
from liliumpharm.utils import month_number_to_french_name


def get_order_source_details(ordersource):
    products = Produit.objects.all()

    data = {"ordersource": ordersource, "products": products, "orders": []}

    for order in ordersource.order_set.all():
        products_list = []
        for product in products:
            order_product = OrderProduct.objects.filter(order=order, produit=product)
            if order_product.exists():
                #order_product = order_product.first()
                #products_list.append(order_product.qtt)
                s=0
                for a in order_product:
                    s= s+a.qtt
                products_list.append(s)
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
# def get_target_details_per_user(user_id=None, product_id=None, months=None, years=None):
    
#     data = {}



#     if user_id and product_id:

#         user_profile = UserProfile.objects.get(user__id=user_id)
#         data["user"] = f"{user_profile.user.last_name} {user_profile.user.first_name}"

#         product = Produit.objects.get(id=product_id)
#         data["product"] = product
#         print("aaaaaaaaaa")
#         user_product_target = UserTargetMonthProduct.objects.filter(usermonth__user=user_id, product=product_id, usermonth__date__month=months, usermonth__date__year=years)
#         #user_product_target = Produit.objects.filter(id=product_id, usertargetmonthproduct__usermonth__user=user_id, usertargetmonthproduct__usermonth__date__month=months,usertargetmonthproduct__usermonth__date__year=years)
#         #user_product_target = user_product_target.filter(id=product_id)
#         #user_product_target = UserTargetMonthProduct.objects.filter(product=product_id, usermonth__user=user_id, usermonth__date__month=months, usermonth__date__year=years)
#         print(user_product_target)
#         #user_product_target_quantity = user_product_target.aggregate(total=Sum('quantity'))['total']
#         user_product_target_quantity = 0

#         data["product_target"] = user_product_target_quantity * product.price
#         data["product_target_quantity"] = user_product_target_quantity
#         profile = UserProfile.objects.get(user=user_id)
#         if profile.usersunder.exists() and profile.speciality_rolee != "Medico_commercial":
#             user_under_profiles = UserProfile.objects.filter(user__in=profile.usersunder.all())
#             wilayas = Wilaya.objects.filter(userprofile__in=user_under_profiles).distinct()
#         elif profile.speciality_rolee=="CountryManager":
#             wilayas = Wilaya.objects.all()
#         else:
#             wilayas = profile.sectors.all()
#         #wilayas = user_profile.sectors.all()
#         data["wilayas"] = wilayas

   
#         # Preparing Query for Order Product
#         order_client_query = Q()
#         if months is not None:
#             if isinstance(months, (int, str)):
#                 months = [int(months)]
#             else:
#                 months = list(months)

#         if years is not None:
#             if isinstance(years, (int, str)):
#                 years = [int(years)]
#             else:
#                 years = list(years)

#         if months:
#             order_client_query &= Q(order__source__date__month__in=months)
#         if years:
#             order_client_query &= Q(order__source__date__year__in=years)
#         order_client_query &= Q(order__client__wilaya__in=wilayas)
#         order_client_query &= Q(produit=product)
        
#         order_client = OrderProduct.objects.filter(order_client_query).values("order__source__source__name", "order__source__date", "order__source__attachement_file", "order__client__name", "order__client__wilaya__nom").order_by('-order__source__date').annotate(total=Sum("qtt"))
            
#         data["order_client"] = order_client

#         total_quantity = sum(oc["total"] for oc in order_client)

#         data["total_quantity"] = int(total_quantity)

#         return data

def get_target_details_per_user(user_id=None, product_id=None, months=None, years=None):
    data = {}

    if user_id and product_id:
        user_profile = UserProfile.objects.get(user__id=user_id)
        data["user"] = f"{user_profile.user.last_name} {user_profile.user.first_name}"

        product = Produit.objects.get(id=product_id)
        data["product"] = product

        # Sécurisation des mois / années en listes
        if months is not None:
            if isinstance(months, (int, str)):
                months = [int(months)]
            else:
                months = list(map(int, months))

        if years is not None:
            if isinstance(years, (int, str)):
                years = [int(years)]
            else:
                years = list(map(int, years))

        # Ciblage du produit utilisateur
        user_product_target = UserTargetMonthProduct.objects.filter(
            usermonth__user=user_id,
            product=product_id
        )

        if months:
            user_product_target = user_product_target.filter(usermonth__date__month__in=months)
        if years:
            user_product_target = user_product_target.filter(usermonth__date__year__in=years)

        print(user_product_target)

        # TODO: calculer la quantité réelle
        user_product_target_quantity = 0
        data["product_target"] = user_product_target_quantity * product.price
        data["product_target_quantity"] = user_product_target_quantity

        # Détermination wilayas
        profile = UserProfile.objects.get(user=user_id)
        if profile.usersunder.exists() and profile.speciality_rolee != "Medico_commercial":
            user_under_profiles = UserProfile.objects.filter(user__in=profile.usersunder.all())
            wilayas = Wilaya.objects.filter(userprofile__in=user_under_profiles).distinct()
        elif profile.speciality_rolee == "CountryManager":
            wilayas = Wilaya.objects.all()
        else:
            wilayas = profile.sectors.all()

        data["wilayas"] = wilayas

        # Commandes clients
        order_client_query = Q()
        if months:
            order_client_query &= Q(order__source__date__month__in=months)
        if years:
            order_client_query &= Q(order__source__date__year__in=years)
        order_client_query &= Q(order__client__wilaya__in=wilayas)
        order_client_query &= Q(produit=product)

        order_client = (
            OrderProduct.objects.filter(order_client_query)
            .values(
                "order__source__source__name",
                "order__source__date",
                "order__source__attachement_file",
                "order__client__name",
                "order__client__wilaya__nom"
            )
            .order_by('-order__source__date')
            .annotate(total=Sum("qtt"))
        )

        data["order_client"] = order_client
        data["total_quantity"] = sum(oc["total"] for oc in order_client)

        return data


# Parameters are IDs
def get_target_per_userrrr(user_id=None, month=None, year=None):
    
    targets = []
    prices = []
    quantities = []
    total_targets = []
    total_achievements = []
    percentage_achievements = []

    if user_id:
        print(f"user _ id {user_id}")
        user_profile = UserProfile.objects.get(user=user_id)

        #products = Produit.objects.filter(userproduct__user=user_profile.user)
        products = Produit.objects.filter(usertargetmonthproduct__usermonth__user=user_id, usertargetmonthproduct__usermonth__date__month=month,usertargetmonthproduct__usermonth__date__year=year)
        #products = UserTargetMonthProduct.objects.filter(usermonth__user=user_id)
        print("test")
        print("test for product")
        print(products)
        
        
        #if month and year:
        #    products = products.filter(
        #        usertargetmonthproduct__usermonth__date__month=month,
        #        usertargetmonthproduct__usermonth__date__year=year
        #    )
        #elif month:  # Si seul 'month' est donné
        #    products = products.filter(usertargetmonthproduct__usermonth__date__month=month)
        #elif year:  # Si seul 'year' est donné
        #    products = products.filter(usertargetmonthproduct__usermonth__date__year=year)

        print("test22222")
        print(products)
        
        wilayas = user_profile.sectors.all()

        for product in products:
            
            # Appending Price
            prices.append(product.price)
            
            total_product_quantity_sold = 0

            query_string=""

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
                
                #users_in_same_wilaya = UserTargetMonthProduct.objects.filter(usermonth__date__year__in=str(year), usermonth__date__month__in=str(month), usermonth__user__userprofile__sectors=wilaya, product=product).values("usermonth__user").distinct()
                users_in_same_wilaya = UserTargetMonthProduct.objects.filter(usermonth__date__year=year, usermonth__date__month=month, usermonth__user__userprofile__sectors=wilaya, usermonth__user__userprofile__speciality_rolee="Medico_commercial",product=product).values("usermonth__user").distinct()

                if users_in_same_wilaya.count() != 0:
                    print(f"il ya users {users_in_same_wilaya.count()}")
                    for usr in users_in_same_wilaya:
                        print(usr["usermonth__user"])
                    total_product_quantity_sold += round(total / users_in_same_wilaya.count(), 2)
                else:
                    total_product_quantity_sold = 0

                # Preparing Query String
                query_string = f'user={user_id}&product={product.id}'

                if month:
                    query_string += f'&month={month}'
                if year: 
                    query_string += f'&year={year}'
                
            # Appending Quantity
            quantities.append({"total": total_product_quantity_sold, 
            "target_report_details_link": f"{reverse('target_report_details')}?{query_string}"
            })
            total_achievements.append(round(total_product_quantity_sold * product.price, 2))


            #user_product = UserProduct.objects.get(product=product, user=user_profile.user)
            user_product = UserTargetMonthProduct.objects.filter(product_id=product.id, usermonth__user=user_id, usermonth__date__month=month, usermonth__date__year=year)
            #user_product = products.filter(product__id=product.id)
            t=0
            for p in user_product:
                t=p.quantity
            
            # Appending Quantity
            targets.append(t)
            total_targets.append(round(t * product.price, 2))
            if total_product_quantity_sold != 0 and t!=0:
                percentage_achievements.append((total_product_quantity_sold*100)/t)
            else:
                percentage_achievements.append(0)


        total_target = round(sum([total for total in total_targets if type(total) != str]), 2)
        total_reached = round(sum([total for total in total_achievements if type(total) != str]), 2)
        percentage_reached = round(total_reached * 100 / total_target, 2) if total_target > 0 else 0

        data = {"year": year,
                "month": month_number_to_french_name(month),
                "user_id": user_id,
                "user": f"{user_profile.user.last_name} {user_profile.user.first_name}",
                "wilayas": wilayas,
                "products": products,
                "targets": targets, 
                "prices": prices, 
                "quantities": quantities, 
                "total_targets": total_targets,
                "total_achievements": total_achievements,
                "percentage_achievements":percentage_achievements,
                "total_target": total_target,
                "total_reached": total_reached,
                "percentage_reached": percentage_reached
                }
        print(data)
        return data


def get_target_per_user_none(user_id=None, months=None, years=None):
    
    targets = []
    prices = []
    quantities = []
    total_targets = []
    total_achievements = []

    if user_id:
        print(f"user _ id {user_id}")
        user_profile = UserProfile.objects.get(user=user_id)

        #products = Produit.objects.filter(userproduct__user=user_profile.user)
        products = Produit.objects.filter(usertargetmonthproduct__usermonth__user=user_id, usertargetmonthproduct__usermonth__date__month__in=months,usertargetmonthproduct__usermonth__date__year__in=years)
        #products = UserTargetMonthProduct.objects.filter(usermonth__user=user_id)
        print("test")
        print("test for product")
        print(products)
        
        
        #if month and year:
        #    products = products.filter(
        #        usertargetmonthproduct__usermonth__date__month=month,
        #        usertargetmonthproduct__usermonth__date__year=year
        #    )
        #elif month:  # Si seul 'month' est donné
        #    products = products.filter(usertargetmonthproduct__usermonth__date__month=month)
        #elif year:  # Si seul 'year' est donné
        #    products = products.filter(usertargetmonthproduct__usermonth__date__year=year)

        print("test22222")
        print(products)
        
        wilayas = user_profile.sectors.all()

        for product in products:
            
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
                
                #users_in_same_wilaya = UserTargetMonthProduct.objects.filter(usermonth__date__year__in=str(year), usermonth__date__month__in=str(month), usermonth__user__userprofile__sectors=wilaya, product=product).values("usermonth__user").distinct()
                users_in_same_wilaya = UserTargetMonthProduct.objects.filter(usermonth__date__year__in=years, usermonth__date__month__in=months, usermonth__user__userprofile__sectors=wilaya, usermonth__user__userprofile__speciality_rolee="Medico_commercial",product=product).values("usermonth__user").distinct()

                if users_in_same_wilaya.count() != 0:
                    print(f"il ya users {users_in_same_wilaya.count()}")
                    for usr in users_in_same_wilaya:
                        print(usr["usermonth__user"])
                    total_product_quantity_sold += round(total / 1, 2)
                else:
                    total_product_quantity_sold = 0
                
                

                # Preparing Query String
                query_string = f'user={user_id}&product={product.id}'

                if months:
                    query_string += f'&month={months}'
                if years:
                    query_string += f'&year={years}'
                
            # Appending Quantity
            quantities.append({"total": total_product_quantity_sold, 
            "target_report_details_link": f"{reverse('target_report_details')}?{query_string}"
            })
            total_achievements.append(round(total_product_quantity_sold * product.price, 2))


            #user_product = UserProduct.objects.get(product=product, user=user_profile.user)
            user_product = UserTargetMonthProduct.objects.filter(product_id=product.id, usermonth__user=user_id, usermonth__date__month__in=months, usermonth__date__year__in=years)
            #user_product = products.filter(product__id=product.id)
            t=0
            for p in user_product:
                t=p.quantity
            
            # Appending Quantity
            targets.append(t)
            total_targets.append(round(t * product.price, 2))


        total_target = round(sum([total for total in total_targets if type(total) != str]), 2)
        total_reached = round(sum([total for total in total_achievements if type(total) != str]), 2)
        percentage_reached = round(total_reached * 100 / total_target, 2) if total_target > 0 else 0

        data = {"year": years,
                "month": month_number_to_french_name(months),
                "user_id": user_id,
                "user": f"{user_profile.user.last_name} {user_profile.user.first_name}",
                "wilayas": wilayas,
                "products": products,
                "targets": targets, 
                "prices": prices, 
                "quantities": quantities, 
                "total_targets": total_targets,
                "total_achievements": total_achievements,
                "total_target": total_target,
                "total_reached": total_reached,
                "percentage_reached": percentage_reached
                }

        return data

from clients.api.functions import get_target_per_user
def get_target_per_user_per_month(user_id=None, months=None, years=None):
    
    targets = []
    prices = []
    quantities = []
    total_targets = []
    total_achievements = []
    data = []

    if user_id:

        user_profile = UserProfile.objects.get(user__id=user_id)

        #products = Produit.objects.filter(userproduct__user=user_profile.user)
        for i in months:
            mo = month_number_to_french_name(int(i))
        dt = get_target_per_user(user_id=user_id, months=months, years=years)
        return dt
        print(dt)
        data.append(dt)
        print(data)
        data2 = []
        products = []
        targets = []
        total_achievements = []
        total_targets = []
        quantities =[]
        prices = []
        perc_ach = []
        for dat in data:
            on = dat['months']
            for pro_dat in dat['products']:
                tar = 0
                q = 0
                tt = 0
                ta = 0
                if data.index(dat) == 0 or pro_dat not in products:
                    products.append(pro_dat)
                    for dat1 in data:
                        for p in dat1['products']:
                            if p == pro_dat:
                                ind = list(dat1['products']).index(p)
                                tar = tar + int(dat1['targets'][ind])
                                q = q + dat1['quantities'][ind]['total']
                                pri = dat1['prices'][ind]
                                tt = tt + float(dat1['total_targets'][ind].replace(",", "."))
                                value = dat1["total_achievements"][ind]
                                value = str(value).replace(",", "")  # Supprime toutes les virgules
                                ta = ta + float(value)

                        if tar != 0:
                            pa = (q * 100) / tar
                        elif tar ==0:
                            pa = 0
                    targets.append(tar)
                    total_targets.append(tt)
                    total_achievements.append(ta)
                    prices.append(pri)
                    perc_ach.append(pa)
                    r ={
                            'total': q,
                            'target_report_details_link': '#'
                        }
                    quantities.append(r)
        stt =0
        sta = 0
        spo = 0
        for d in data:
            #stt = stt + sum(d['total_targets'])
            for x in d['total_targets']:
                # Supprimer les virgules utilisées pour les milliers
                x_clean = str(x).replace(",", "")
                stt += float(x_clean)
            #sta = sta + sum(d['total_achievements'])
            for x in d['total_achievements']:
                # Supprime les virgules de milliers et convertit en float
                x_clean = str(x).replace(",", "")
                sta += float(x_clean)
            spo = spo + d['percentage_reached']
        spo = round(spo / len(data), 2)
        m = []
        for i in months:
                mo = month_number_to_french_name(int(i))
                
                m.append(mo)
        t = {"year": years,
                "month": m,
                "user_id": user_id,
                "user": f"{user_profile.user.last_name} {user_profile.user.first_name}",
                "wilayas": data[0]['wilayas'],
                "products": products,
                "targets": targets, 
                "prices": prices, 
                "quantities": quantities, 
                "total_targets": total_targets,
                "total_achievements": total_achievements,
                "total_target": stt,
                "total_reached": sta,
                "percentage_reached": spo,
                "percentage_achievements": [float(ta) for ta in perc_ach],
                }
        data.insert(0, t)
        
        return(data)
        for i in month:
            print(f"MONTH {i}")
            mo = month_number_to_french_name(int(i))
            products = Produit.objects.filter(usertargetmonthproduct__usermonth__user=user_id, usertargetmonthproduct__usermonth__date__month=i,usertargetmonthproduct__usermonth__date__year=year).distinct()
            #products = UserTargetMonthProduct.objects.filter(usermonth__user=user_id)
            print("test")
            print("")
            print(products)
            prices.clear()
            quantities.clear()
            targets.clear()
            total_targets.clear()
            total_achievements.clear()
        
        

            print("test22222")
            print(products)
        
            wilayas = user_profile.sectors.all()

            for product in products:
            
                # Appending Price
                prices.append(product.price)
            
                total_product_quantity_sold = 0

                query_string=""

                for wilaya in wilayas:

                    # Preparing Query for Order Product
                    order_product_query = Q()
                    if month:
                        order_product_query &= Q(order__source__date__month=i)
                    if year:
                        order_product_query &= Q(order__source__date__year=year)

                
                    order_product_query &= Q(order__client__wilaya=wilaya)
                    order_product_query &= Q(produit=product)
                

                    order_product = OrderProduct.objects.filter(order_product_query).values("produit__nom").annotate(total=Sum("qtt"))
                    total = 0
                    if order_product.exists():
                        total = order_product[0].get("total")
                
                    #users_in_same_wilaya = UserTargetMonthProduct.objects.filter(usermonth__date__year__in=str(year), usermonth__date__month__in=str(month), usermonth__user__userprofile__sectors=wilaya, product=product).values("usermonth__user").distinct()
                    users_in_same_wilaya = UserTargetMonthProduct.objects.filter(usermonth__date__year=year, usermonth__date__month=i, usermonth__user__userprofile__sectors=wilaya, product=product).values("usermonth__user").distinct()

                    if users_in_same_wilaya.count() != 0:
                        print(f"il ya users {users_in_same_wilaya.count()}")
                        for usr in users_in_same_wilaya:
                            print(usr["usermonth__user"])
                        total_product_quantity_sold += round(total / users_in_same_wilaya.count(), 2)
                    else:
                        total_product_quantity_sold = 0

                    # Preparing Query String
                    query_string = f'user={user_id}&product={product.id}'

                    if month:
                        query_string += f'&month={i}'
                    if year: 
                        query_string += f'&year={year}'
                
                # Appending Quantity
                quantities.append({"total": total_product_quantity_sold, 
                "target_report_details_link": f"{reverse('target_report_details')}?{query_string}"
                })
                total_achievements.append(round(total_product_quantity_sold * product.price, 2))


                #user_product = UserProduct.objects.get(product=product, user=user_profile.user)
                user_product = UserTargetMonthProduct.objects.filter(product_id=product.id, usermonth__user=user_id, usermonth__date__month=i, usermonth__date__year=year)
                #user_product = products.filter(product__id=product.id)
                t=0
                for p in user_product:
                    t=p.quantity
            
                # Appending Quantity
                targets.append(t)
                total_targets.append(round(t * product.price, 2))


            total_target = round(sum([total for total in total_targets if type(total) != str]), 2)
            total_reached = round(sum([total for total in total_achievements if type(total) != str]), 2)
            percentage_reached = round(total_reached * 100 / total_target, 2) if total_target > 0 else 0

            data.append({#"year": year,
                    #"month": i,
                    #"user_id": user_id,
                    "user": f"{user_profile.user.last_name} {user_profile.user.first_name}",
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
            print(data)
            
        print(data)
        return data


def get_target_for_supervisor(user_id=None, include_user=False, month=None, year=None):

    if user_id:
        user_profile = UserProfile.objects.get(user__id=user_id)
        user = user_profile.user

        #if user.is_superuser == True:
            #users_under = User.objects.exclude(id=user.id)
        if user.userprofile.rolee == "CountryManager":
            print(user_profile.commune.wilaya.pays)
            print("je suis laaaaaaaaaaaaa")
            #users_under = User.objects.filter(userprofile__commune__wilaya__pays=user_profile.commune.wilaya.pays)
            #users_under = User.objects.all()
            users_under = User.objects.filter(userprofile__speciality_rolee__in=["Medico_commercial","Commercial"],userprofile__commune__wilaya__pays=user.userprofile.commune.wilaya.pays)

        elif user.userprofile.rolee == "Superviseur":
            users_under = user_profile.usersunder.all()

        
        if not include_user:
            # If the User is under itself, then consider him like a simple User
            if user in users_under:
                print(f"The User {user} is Under It Self, Returning Single Data")
                return get_target_per_userrrr(user_id, month, year)

        print(month)
        print("hiiiii je suis dans functions.py dans clients")
        target_months = UserTargetMonth.objects.filter(user__in=users_under,date__year=year, date__month=month)
        if user.userprofile.rolee == "CountryManager":
            target_months = UserTargetMonth.objects.filter(user__in=users_under, date__year=year, date__month=month)
        
        productss = UserTargetMonthProduct.objects.filter(usermonth__user=user_id).values('product').distinct()
        productss = UserTargetMonthProduct.objects.filter(usermonth__in=target_months).values('product').distinct()
        #productss = UserTargetMonthProduct.objects.filter(usermonth__user=user_id, usermonth__date__month=month, usermonth__date__year=year).values('product').distinct()
        products = Produit.objects.filter(id__in=[p['product'] for p in productss])
            #products = Produit.objects.all()
        wilayas = []

        # Init Lists with Zeroes for Summing
        targets = [0] * products.count()
        prices = [*products.values_list('price', flat=True)]

        # Init List With Objects
        quantities = []
        for i in range(products.count()):
            quantities.append({"total": 0})

        total_targets = [0] * products.count()
        total_achievements = [0] * products.count()
        percentage_achievements = [0] * products.count()

        for user_under in users_under:
            user_under_target = get_target_per_userrrr(user_under.id, month, year)

            wilayas.extend(list(user_under_target["wilayas"]))

            for index, product in enumerate(products):
                if product in user_under_target["products"]:
                    # Getting Product index in User Target Data
                    user_under_product_index = list(user_under_target["products"]).index(product)

                    # Adding Values to Supervisor's List
                    targets[index] += user_under_target["targets"][user_under_product_index]
                    quantities[index]["total"] += user_under_target["quantities"][user_under_product_index]["total"]
                    query_string = f'user={user_id}&product={product.id}'

                    if month:
                        query_string += f'&month={month}'
                    if year: 
                        query_string += f'&year={year}'
                
                    quantities[index]["target_report_details_link"] = f"{reverse('target_report_details')}?{query_string}"
                    
                    total_targets[index] += user_under_target["total_targets"][user_under_product_index]
                    total_achievements[index] += user_under_target["total_achievements"][user_under_product_index]
                    if total_achievements[index] != 0 and total_targets[index] != 0:
                        percentage_achievements[index] = (total_achievements[index] * 100)/total_targets[index]

        products = list(products)
        # Removing Product with No Target
        for index, target in enumerate(targets):
            if target == 0:
                del products[index]
                del targets[index]
                del prices[index]
                del quantities[index]
                del total_targets[index]
                del total_achievements[index]
                if percentage_achievements[index] == 0:
                    del percentage_achievements[index]


        total_target = round(sum([total for total in total_targets if type(total) != str]), 2)
        total_reached = round(sum([total for total in total_achievements if type(total) != str]), 2)
        percentage_reached = round(total_reached * 100 / total_target, 2)
        
        # Removing Wilayas Duplicates
        wilayas = set(wilayas)


        print('Returning >>> ',wilayas)

        data = {"year": year,
                "month": month,
                "user_id": user_id,
                "user": f"{user_profile.user.last_name} {user_profile.user.first_name}",
                "wilayas": wilayas,
                "products": products,
                "targets": targets, 
                "prices": prices, 
                "quantities": quantities, 
                "total_targets": total_targets,
                "total_achievements": total_achievements,
                "percentage_achievements":percentage_achievements,
                "total_target": total_target,
                "total_reached": total_reached,
                "percentage_reached": percentage_reached
                }
        return data

# Parameters are IDs

def get_target_all_users(month=None, year=None, user_id=None):
    
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

                    users_in_same_wilaya = UserProduct.objects.filter(user__userprofile__sectors=wilaya, product=product).values("user").distinct()

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





def get_target_per_user_id(month=None, year=None, user_id=None):
    
    data = []
    print("youuuuuuuuuuuuu boumerdes")
    print(user_id)
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

                    users_in_same_wilaya = UserProduct.objects.filter(user__userprofile__sectors=wilaya, product=product).values("user").distinct()

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
            print("youuuuuuuuuuuuu Alger")
            print(user_profile.user.id)
            if user_profile.user.id == user_id:
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