from .models import *
from .serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import (
    TokenAuthentication,
    SessionAuthentication,
    BasicAuthentication,
)
from django.http import Http404
from django.core.paginator import Paginator
from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import datetime
from datetime import date
from django.template.loader import render_to_string
from weasyprint import HTML
from django.http import HttpResponse
from django.db.models import Q
from django.shortcuts import render, redirect
from django.utils import timezone
from rest_framework.authtoken.models import Token
import json


from accounts.models import *
from clients.models import *


class addorder(TemplateView):
    def get(self, request):
        #med = request.user.medecins.all()
        user_id=request.session.get('user_id')
        if user_id is None:
            user_id=request.user.id
        else:
            user_id=int(user_id)
        print("mobile probleme 1 addorder")
        print(user_id)
        u = UserProfile.objects.get(user=user_id)
        if u.speciality_rolee == "Office" or u.speciality_rolee == "Admin" or u.speciality_rolee == "CountryManager":
            print("yes is super user")
            
            pha = Medecin.objects.filter(specialite="Pharmacie")
            gro = Medecin.objects.filter(specialite="Grossiste")
            sugro = Client.objects.filter(supergro=True)
            #pro = Produit.objects.all()
            #pro = UserProduct.objects.filter(user=request.user)
            pro = Produit.objects.all()
            return render(request, "orders/addorder.html", {'pha':pha, 'gro':gro, 'sugro':sugro, 'pro':pro})
        
        if u.speciality_rolee == "Superviseur_regional" or u.speciality_rolee == "Superviseur_national":
            usr = User.objects.get(id=user_id)
            userpro = UserProfile.objects.get(user=usr)
            users_under = userpro.usersunder.all()
            all_sectors = set()
            for user in users_under:
                try:
                    sectors = user.userprofile.sectors.all()
                    all_sectors.update(sectors)
                except UserProfile.DoesNotExist:
                    continue  # au cas où un user n'a pas encore de profil
            
            meds = Medecin.objects.filter(users=usr)
            pha = Medecin.objects.filter(users=usr, specialite="Pharmacie")
            gro = Medecin.objects.filter(specialite="Grossiste", wilaya__in=all_sectors)
            sugro = Client.objects.filter(supergro=True)
            pro = Produit.objects.all()
            #pro = UserProduct.objects.filter(user=request.user)
            return render(request, "orders/addorder.html", {'pha':pha, 'gro':gro, 'sugro':sugro, 'pro':pro})
        
        print("mobile probleme 2 addorder")
        usr = User.objects.get(id=user_id)
        userpro = UserProfile.objects.get(user=usr)
        meds = Medecin.objects.filter(users=usr)
        pha = Medecin.objects.filter(users=usr, specialite="Pharmacie")
        gro = Medecin.objects.filter(specialite="Grossiste",wilaya__in=userpro.sectors.all())
        sugro = Client.objects.filter(supergro=True)
        pro = Produit.objects.all()
        #pro = UserProduct.objects.filter(user=request.user)
        return render(request, "orders/addorder.html", {'pha':pha, 'gro':gro, 'sugro':sugro, 'pro':pro})
    
    def post(self, request):
        user_id=request.session.get('user_id')
        if user_id is None:
            user_id=request.user.id
        else:
            user_id=int(user_id)
        u = UserProfile.objects.get(user=user_id)
        pharmacy_id = request.POST.get("phar")
        pharmacyy = Medecin.objects.filter(id=pharmacy_id).first() if pharmacy_id else None
        gros_id = request.POST.get("gros")
        groo = Medecin.objects.filter(id=gros_id).first() if gros_id else None
        super_gros_id = request.POST.get("sugros")
        su_gro = Client.objects.filter(id=super_gros_id).first() if super_gros_id else None
        if pharmacy_id and gros_id and super_gros_id:
            m = "Veuillez Choisir que deux parmi Pharmacie, Grossiste et SuperGros ou Bien que SuperGros"
            if u.speciality_rolee == "Office" or u.speciality_rolee == "Admin" or u.speciality_rolee == "CountryManager":
                print("yes is super user")
                
                pha = Medecin.objects.filter(specialite="Pharmacie")
                gro = Medecin.objects.filter(specialite="Grossiste")
                sugro = Client.objects.filter(supergro=True)
                pro = Produit.objects.all()
                #pro = UserProduct.objects.filter(user=request.user)
                #m = "Bon de Commande ajouter avec succes"
                return render(request, "orders/addorder.html", {'pha':pha, 'gro':gro, 'sugro':sugro, 'pro':pro, "m":m})
            else:
                pha = Medecin.objects.filter(users=user_id, specialite="Pharmacie")
                usr = User.objects.get(id=user_id)
                userpro = UserProfile.objects.get(user=usr)
                gro = Medecin.objects.filter(specialite="Grossiste",wilaya__in=userpro.sectors.all())
                sugro = Client.objects.filter(supergro=True)
                pro = Produit.objects.all()
                #m = "Bon de Commande ajouter avec succes"
                return render(request, "orders/addorder.html", {'pha':pha, 'gro':gro, 'sugro':sugro, 'pro':pro, "m":m})
        if not pharmacy_id and not gros_id and super_gros_id:
            pass
        elif pharmacy_id and gros_id and not super_gros_id:
            pass
        elif pharmacy_id and not gros_id and not super_gros_id:
            m = "Veuillez Choisir que deux parmi Pharmacie, Grossiste et SuperGros ou Bien que SuperGros Seul"
            if u.speciality_rolee == "Office" or u.speciality_rolee == "Admin" or u.speciality_rolee == "CountryManager":
                print("yes is super user")
                
                pha = Medecin.objects.filter(specialite="Pharmacie")
                usr = User.objects.get(id=user_id)
                userpro = UserProfile.objects.get(user=usr)
                gro = Medecin.objects.filter(specialite="Grossiste",wilaya__in=userpro.sectors.all())
                sugro = Client.objects.filter(supergro=True)
                pro = Produit.objects.all()
                #pro = UserProduct.objects.filter(user=request.user)
                #m = "Bon de Commande ajouter avec succes"
                return render(request, "orders/addorder.html", {'pha':pha, 'gro':gro, 'sugro':sugro, 'pro':pro, "m":m})
            else:
                pha = Medecin.objects.filter(users=user_id, specialite="Pharmacie")
                usr = User.objects.get(id=user_id)
                userpro = UserProfile.objects.get(user=usr)
                gro = Medecin.objects.filter(specialite="Grossiste",wilaya__in=userpro.sectors.all())
                sugro = Client.objects.filter(supergro=True)
                pro = Produit.objects.all()
                #m = "Bon de Commande ajouter avec succes"
                return render(request, "orders/addorder.html", {'pha':pha, 'gro':gro, 'sugro':sugro, 'pro':pro, "m":m})
        elif not pharmacy_id and gros_id and not super_gros_id:
            m = "Veuillez Choisir que deux parmi Pharmacie, Grossiste et SuperGros ou Bien que SuperGros Seul"
            if u.speciality_rolee == "Office" or u.speciality_rolee == "Admin" or u.speciality_rolee == "CountryManager":
                print("yes is super user")
                
                pha = Medecin.objects.filter(specialite="Pharmacie")
                gro = Medecin.objects.filter(specialite="Grossiste")
                sugro = Client.objects.filter(supergro=True)
                pro = Produit.objects.all()
                #pro = UserProduct.objects.filter(user=request.user)
                #m = "Bon de Commande ajouter avec succes"
                return render(request, "orders/addorder.html", {'pha':pha, 'gro':gro, 'sugro':sugro, 'pro':pro, "m":m})
            else:
                pha = Medecin.objects.filter(users=user_id, specialite="Pharmacie")
                usr = User.objects.get(id=user_id)
                userpro = UserProfile.objects.get(user=usr)
                gro = Medecin.objects.filter(specialite="Grossiste",wilaya__in=userpro.sectors.all())
                sugro = Client.objects.filter(supergro=True)
                pro = Produit.objects.all()
                #m = "Bon de Commande ajouter avec succes"
                return render(request, "orders/addorder.html", {'pha':pha, 'gro':gro, 'sugro':sugro, 'pro':pro, "m":m})
        else:
            m = "Veuillez Choisir que deux parmi Pharmacie, Grossiste et SuperGros ou Bien que SuperGros Seul, parceque vous avec rien choisir"
            if u.speciality_rolee == "Office" or u.speciality_rolee == "Admin" or u.speciality_rolee == "CountryManager":
                print("yes is super user")
                
                pha = Medecin.objects.filter(specialite="Pharmacie")
                gro = Medecin.objects.filter(specialite="Grossiste")
                sugro = Client.objects.filter(supergro=True)
                pro = Produit.objects.all()
                #pro = UserProduct.objects.filter(user=request.user)
                #m = "Bon de Commande ajouter avec succes"
                return render(request, "orders/addorder.html", {'pha':pha, 'gro':gro, 'sugro':sugro, 'pro':pro, "m":m})
            else:
                pha = Medecin.objects.filter(users=user_id, specialite="Pharmacie")
                usr = User.objects.get(id=user_id)
                userpro = UserProfile.objects.get(user=usr)
                gro = Medecin.objects.filter(specialite="Grossiste",wilaya__in=userpro.sectors.all())
                sugro = Client.objects.filter(supergro=True)
                pro = Produit.objects.all()
                #m = "Bon de Commande ajouter avec succes"
                return render(request, "orders/addorder.html", {'pha':pha, 'gro':gro, 'sugro':sugro, 'pro':pro, "m":m})
        observations = request.POST.get("observations")
        image = request.FILES.get('image')
        us = User.objects.get(id=user_id)
        createorder = Order.objects.create(pharmacy=pharmacyy, gros=groo, super_gros=su_gro, user=us, observation=observations, image=image, status="initial")
        pro = Produit.objects.all()
        #pro = UserProduct.objects.filter(user=request.user)
        h=0
        for itempro in pro:
            check_value = request.POST.get(f"check_{itempro.nom}")
            if check_value == "on":
                h=h+1
                qtt_value = request.POST.get(f"qtt_{itempro.nom}")
                if not qtt_value:
                    m = f"Veuillez Ajoutez un veleur a le produit cocher {itempro.nom}"
                    if u.speciality_rolee == "Office" or u.speciality_rolee == "Admin" or u.speciality_rolee == "CountryManager":
                        print("yes is super user")
                        
                        pha = Medecin.objects.filter(specialite="Pharmacie")
                        gro = Medecin.objects.filter(specialite="Grossiste")
                        sugro = Client.objects.filter(supergro=True)
                        pro = Produit.objects.all()
                        #pro = UserProduct.objects.filter(user=request.user)
                        #m = "Bon de Commande ajouter avec succes"
                        return render(request, "orders/addorder.html", {'pha':pha, 'gro':gro, 'sugro':sugro, 'pro':pro, "m":m})
                    else:
                        pha = Medecin.objects.filter(users=request.user, specialite="Pharmacie")
                        gro = Medecin.objects.filter(users=request.user, specialite="Grossiste")
                        sugro = Client.objects.filter(supergro=True)
                        pro = Produit.objects.all()
                        #m = "Bon de Commande ajouter avec succes"
                        return render(request, "orders/addorder.html", {'pha':pha, 'gro':gro, 'sugro':sugro, 'pro':pro, "m":m})
        if h==0:
            m="Veuillez ajouter en moin un produit"
            if u.speciality_rolee == "Office" or u.speciality_rolee == "Admin" or u.speciality_rolee == "CountryManager":
                print("yes is super user")
                        
                pha = Medecin.objects.filter(specialite="Pharmacie")
                gro = Medecin.objects.filter(specialite="Grossiste")
                sugro = Client.objects.filter(supergro=True)
                pro = Produit.objects.all()
                #pro = UserProduct.objects.filter(user=request.user)
                #m = "Bon de Commande ajouter avec succes"
                return render(request, "orders/addorder.html", {'pha':pha, 'gro':gro, 'sugro':sugro, 'pro':pro, "m":m})
            else:
                pha = Medecin.objects.filter(users=request.user, specialite="Pharmacie")
                gro = Medecin.objects.filter(users=request.user, specialite="Grossiste")
                sugro = Client.objects.filter(supergro=True)
                pro = Produit.objects.all()
                #m = "Bon de Commande ajouter avec succes"
                return render(request, "orders/addorder.html", {'pha':pha, 'gro':gro, 'sugro':sugro, 'pro':pro, "m":m})
        if u.speciality_rolee == "Office" or u.speciality_rolee == "Admin" or u.speciality_rolee == "CountryManager":
            print("yes is super user")
            
            pha = Medecin.objects.filter(specialite="Pharmacie")
            gro = Medecin.objects.filter(specialite="Grossiste")
            sugro = Client.objects.filter(supergro=True)
            pro = Produit.objects.all()
            #pro = UserProduct.objects.filter(user=request.user)
            m = "Bon de Commande ajouter avec succes"
            #return redirect('MsOrders')
            return render(request, "orders/ord.html", {"m":m})
            return redirect(f"{reverse('MsOrders')}?ttl=1")
            #return render(request, "orders/addorder.html", {'pha':pha, 'gro':gro, 'sugro':sugro, 'pro':pro, "m":m})
        pha = Medecin.objects.filter(users=user_id, specialite="Pharmacie")
        gro = Medecin.objects.filter(users=user_id, specialite="Grossiste")
        sugro = Client.objects.filter(supergro=True)
        m = "Bon de Commande ajouter avec succes"
        #return redirect('MsOrders')
        return render(request, "orders/ord.html", {"m":m})
        return redirect(f"{reverse('MsOrders')}?ttl=1")
        #return render(request, "orders/addorder.html", {'pha':pha, 'gro':gro, 'sugro':sugro, 'pro':pro, "m":m})

class OrderAPI(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, id=""):
        if id == "":
            if (
                request.user.userprofile.rolee not in ["Superviseur", "CountryManager"]
                and request.user.is_superuser != True
                and request.user.username not in ["ibtissemdz", "liliumdz"]
            ):
                orders_list = Order.objects.filter(
                    user=request.user,
                    added__month=datetime.now().month,
                    added__year=datetime.now().year,
                ).order_by("-added")
            else:
                if (
                    request.user.is_superuser
                    or request.user.username
                    in ["ibtissemdz", "RABTIDZ", "a.lounis@liliumpharma.com"]
                    or request.user.username == "liliumdz"
                    or request.user.userprofile.speciality_rolee in ["Office"]
                ):
                    filters = {}

                    if request.GET.get("pays") and request.GET.get("pays") != "0":
                        filters["user__userprofile__commune__wilaya__pays__id"] = (
                            request.GET.get("pays")
                        )

                    if request.GET.get("wilaya") and request.GET.get("wilaya") != "0":
                        filters["client__commune__wilaya__id"] = request.GET.get(
                            "wilaya"
                        )

                    if request.GET.get("commune") and request.GET.get("commune") != "0":
                        filters["client__commune__id"] = request.GET.get("commune")

                    if request.GET.get("client") and request.GET.get("client") != "":
                        filters["client__nom__icontains"] = request.GET.get("client")

                    if request.GET.get("mindate") and request.GET.get("mindate") != "":
                        filters["added__gte"] = request.GET.get("mindate")

                    if request.GET.get("maxdate") and request.GET.get("maxdate") != "":
                        filters["added__lte"] = request.GET.get("maxdate")

                    if request.GET.get("produit") and request.GET.get("produit") != "":
                        filters["orderitem__produit__id"] = request.GET.get("produit")

                    if request.GET.get("status") and request.GET.get("status") != "":
                        filters["status"] = request.GET.get("status")

                    if (
                        request.GET.get("commercial")
                        and request.GET.get("commercial") != ""
                    ):
                        filters["user__username__icontains"] = request.GET.get(
                            "commercial"
                        )

                    orders_list = Order.objects.filter(**filters).order_by("-added")
                else:
                    q = Q(
                        user=request.user,
                        added__month=datetime.now().month,
                        added__year=datetime.now().year,
                    )
                    q |= Q(user__in=request.user.userprofile.usersunder.all())
                    orders_list = Order.objects.filter(q).distinct().order_by("-added")

            serializer = OrderSerializer(orders_list, many=True)

            return Response(serializer.data, status=200)
        else:
            order = Order.objects.get(id=id)
            if order.status == "en cours":
                order.status = "traite"
                order.done_date = datetime.today().date()

            if order.status == "confirmed":
                order.status = "en cours"

            if order.status == "initial":
                order.status = "confirmed"
                order.validation_date = datetime.today().date()

            order.save()

            return Response(OrderSerializer(order).data, status=200)

import json
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

class OrderAppAPI(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            raise Http404

    def pagination_response(self, orders, json, result_length):
        response = {
            "pages": orders.paginator.num_pages,
            "result": {"orders": json.data},
            "length": result_length,
        }
        try:
            response["previous"] = orders.previous_page_number()
        except:
            pass
        try:
            response["next"] = orders.next_page_number()
        except:
            pass
        return response

    def get(self, request, id=""):
        if id == "":
            if request.user.username in ["RABTIDZ", "a.lounis@liliumpharma.com"]:
                orders_list = Order.objects.all().order_by("-added")
            else:
                if (
                    request.user.userprofile.rolee
                    not in ["Superviseur", "CountryManager"]
                    and request.user.is_superuser != True
                    and request.user.username not in ["ibtissemdz", "liliumdz"]
                ):
                    q = Q(
                        user=request.user,
                        added__month=datetime.now().month,
                        added__year=datetime.now().year,
                    )
                    q |= Q(
                        touser=request.user,
                        added__month=datetime.now().month,
                        added__year=datetime.now().year,
                    )
                    orders_list = Order.objects.filter().order_by("-added")
                else:
                    if (
                        request.user.is_superuser
                        or request.user.username == "ibtissemdz"
                        or request.user.username == "liliumdz"
                        or request.user.userprofile.speciality_rolee in ["Office"]
                    ):
                        orders_list = Order.objects.all().order_by("-added")
                    else:
                        q = Q(
                            user=request.user,
                            added__month=datetime.now().month,
                            added__year=datetime.now().year,
                        )
                        q |= Q(user__in=request.user.userprofile.usersunder.all())
                        orders_list = (
                            Order.objects.filter(q).distinct().order_by("-added")
                        )

            if request.GET.get("status") and request.GET.get("status") != "":
                orders_list = orders_list.filter(status=request.GET.get("status"))

            paginator = Paginator(orders_list, 3)
            page = (
                request.GET.get("page")
                if request.GET.get("page") and request.GET.get("page") != "0"
                else None
            )
            orders = paginator.get_page(page)

            serializer = OrderSerializer(orders, many=True)

            return Response(
                self.pagination_response(orders, serializer, len(orders_list)),
                status=200,
            )
        else:
            order = Order.objects.get(id=id)
            if order.status == "en cours":
                order.status = "traite"
                order.done_date = datetime.today().date()

            if order.status == "confirmed":
                order.status = "en cours"

            if order.status == "initial":
                order.status = "confirmed"
                order.validation_date = datetime.today().date()

            order.save()

            return Response(OrderSerializer(order).data, status=200)

    def put(self, request, id="", format=None):
        if id == "":
            print(request.data)
            items_raw = request.data.get("items")
            ph = request.data.get("pharmacy")
            gro = request.data.get("gros")
            supgro = request.data.get("super_gros")
            print(items_raw)
            #print(date())
            print(date.today())
            try:
                ord = Order.objects.get(added__date=date.today(),user=request.user, pharmacy=ph,gros=gro,super_gros=supgro)
                print("exist deja un bon de commande avec les meme ph, supgro, gro")
                message = {"error": "Un bon de commande existe déjà pour cette pharmacie, ce grossiste et ce super grossiste aujourd’hui."}
                return Response(
                    message["error"],
                    status=status.HTTP_400_BAD_REQUEST)
            except ObjectDoesNotExist:
                print("pas de bon de commande ")
            except MultipleObjectsReturned:
                # Plusieurs bons trouvés → renvoyer un message clair
                message = {"error": "Un bon de commande existe déjà pour cette pharmacie, ce grossiste et ce super grossiste aujourd’hui."}
                return Response(
                    message["error"],
                    status=status.HTTP_400_BAD_REQUEST)
            if not items_raw:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            # Convertir la chaîne JSON en liste Python
            items = json.loads(items_raw) if items_raw else []
            # Vérifier s’il existe un item avec qtt == "0"
            has_zero_qtt = any(str(item.get("qtt")) == "0" for item in items)
            if has_zero_qtt:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            serializer = OrderSerializer(
                data=request.data, instance=Order(user=request.user), partial=True
            )
            if serializer.is_valid():
                produits_data = json.loads(request.data.get("items"))
                order = serializer.save()
                # for p in produits_data:
                #     p['order']=order.id

                produits_data = list(
                    map(lambda p: {**p, "order": order.id}, produits_data)
                )
                pserializer = OrderItemSerializer(data=produits_data, many=True)
                if pserializer.is_valid():
                    pserializer.save()
                    return Response(
                        OrderSerializer(order, many=False).data,
                        status=status.HTTP_201_CREATED,
                    )
                else:
                    print(pserializer.errors)
                    return Response(
                        pserializer.errors, status=status.HTTP_400_BAD_REQUEST
                    )
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            print("######### IM HERE UPDATING BC")
            # order_obj = self.get_object(id)
            # serializer = OrderSerializer(
            #     data=request.data, instance=order_obj, partial=True
            # )
            # if serializer.is_valid():
            #     OrderItem.objects.filter(order=order_obj).delete()
            #     produits_data = json.loads(request.data.get("items"))
            #     order = serializer.save()
            #     produits_data = list(
            #         map(lambda p: {**p, "order": order.id}, produits_data)
            #     )
            #     pserializer = OrderItemSerializer(data=produits_data, many=True)
            #     if pserializer.is_valid():
            #         pserializer.save()
            #         return Response(
            #             OrderSerializer(order, many=False).data,
            #             status=status.HTTP_201_CREATED,
            #         )
            #     else:
            #         print(pserializer.errors)
            #         return Response(
            #             pserializer.errors, status=status.HTTP_400_BAD_REQUEST
            #         )
            # print(serializer.errors)
            # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response(status=status.HTTP_400_BAD_REQUEST)


class OrderFrontWebAPI(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            raise Http404

    def post(self, request, id):
        order_obj = self.get_object(id)
        serializer = OrderSerializer(
            data=request.data, instance=order_obj, partial=True
        )
        if serializer.is_valid():
            OrderItem.objects.filter(order=order_obj).delete()
            produits_data = request.data.get("items")
            order = serializer.save()
            produits_data = list(map(lambda p: {**p, "order": order.id}, produits_data))
            pserializer = OrderItemSerializer(data=produits_data, many=True)
            if pserializer.is_valid():
                pserializer.save()
                return Response(
                    OrderSerializer(order, many=False).data,
                    status=status.HTTP_201_CREATED,
                )
            else:
                print(pserializer.errors)
                return Response(pserializer.errors, status=status.HTTP_400_BAD_REQUEST)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderHTML(TemplateView):
    def get(self, request, id):
        return render(request, "orders/pdf.html", {"order": Order.objects.get(id=id)})


class OrderPDF(LoginRequiredMixin, TemplateView):
    template_name = "orders/pdf"

    def get(self, request, id):
        rendered = render_to_string(
            "orders/pdf.html", {"order": Order.objects.get(id=id)}
        )
        htmldoc = HTML(string=rendered, base_url="http://app.liliumpharma.com")
        return HttpResponse(htmldoc.write_pdf(), content_type="application/pdf")


class ExitOrderAppAPI(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return ExitOrder.objects.get(pk=pk)
        except ExitOrder.DoesNotExist:
            raise Http404

    def pagination_response(self, exit_orders, json, result_length):
        response = {
            "pages": exit_orders.paginator.num_pages,
            "result": {"orders": json.data},
            "length": result_length,
        }
        try:
            response["previous"] = exit_orders.previous_page_number()
        except:
            pass
        try:
            response["next"] = exit_orders.next_page_number()
        except:
            pass
        return response

    def get(self, request, id=""):
        if id == "":
            exit_orders_list = ExitOrder.objects.filter(
                user=request.user,
                added__month=datetime.now().month,
                added__year=datetime.now().year,
            ).order_by("-added")

            if (
                request.user.userprofile.rolee not in ["Superviseur", "CountryManager"]
                and request.user.is_superuser != True
                and request.user.username not in ["ibtissemdz", "liliumdz"]
            ):
                exit_orders_list = ExitOrder.objects.filter(
                    user=request.user,
                    added__month=datetime.now().month,
                    added__year=datetime.now().year,
                ).order_by("-added")
            else:
                if (
                    request.user.is_superuser
                    or request.user.username
                    in [
                        "ibtissemdz",
                        "liliumdz",
                    ]
                    or request.user.userprofile.speciality_rolee in ["Office"]
                ):
                    exit_orders_list = ExitOrder.objects.all().order_by("-added")
                else:
                    q = Q(
                        user=request.user,
                        added__month=datetime.now().month,
                        added__year=datetime.now().year,
                    )
                    q |= Q(user__in=request.user.userprofile.usersunder.all())
                    exit_orders_list = (
                        ExitOrder.objects.filter(q).distinct().order_by("-added")
                    )

            paginator = Paginator(exit_orders_list, 3)
            page = (
                request.GET.get("page")
                if request.GET.get("page") and request.GET.get("page") != "0"
                else None
            )
            exit_orders = paginator.get_page(page)

            serializer = ExitOrderSerializer(exit_orders, many=True)

            return Response(
                self.pagination_response(
                    exit_orders, serializer, len(exit_orders_list)
                ),
                status=200,
            )
        else:
            order = ExitOrder.objects.get(id=id)
            order.status = "initial" if order.status == "traite" else "traite"
            order.save()
            return Response(ExitOrderSerializer(order).data, status=200)

    def post(self, request, id="", format=None):
        if id == "":
            serializer = ExitOrderSerializer(
                data=request.data, instance=ExitOrder(user=request.user), partial=True
            )
            if serializer.is_valid():
                produits_data = request.data.get("items")
                exit_order = serializer.save()
                # for p in produits_data:
                #     p['order']=order.id
                produits_data = list(
                    map(lambda p: {**p, "order": exit_order.id}, produits_data)
                )
                pserializer = ExitOrderItemSerializer(data=produits_data, many=True)
                if pserializer.is_valid():
                    pserializer.save()
                    return Response(
                        {
                            "id": exit_order.id,
                            "observation": exit_order.observation,
                            "items": produits_data,
                        },
                        status=status.HTTP_201_CREATED,
                    )
                else:
                    return Response(
                        pserializer.errors, status=status.HTTP_400_BAD_REQUEST
                    )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            exit_order_obj = self.get_object(id)
            serializer = ExitOrderSerializer(
                data=request.data, instance=exit_order_obj, partial=True
            )
            if serializer.is_valid():
                ExitOrderItem.objects.filter(order=exit_order_obj).delete()
                produits_data = request.data.get("items")
                exit_order = serializer.save()
                produits_data = list(
                    map(lambda p: {**p, "order": exit_order.id}, produits_data)
                )
                pserializer = ExitOrderItemSerializer(data=produits_data, many=True)
                if pserializer.is_valid():
                    pserializer.save()
                    return Response(
                        {
                            "id": exit_order.id,
                            "observation": exit_order.observation,
                            "items": produits_data,
                        },
                        status=status.HTTP_201_CREATED,
                    )
                else:
                    return Response(
                        pserializer.errors, status=status.HTTP_400_BAD_REQUEST
                    )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ExitOrderPDF(TemplateView):
    template_name = "orders/pdf"

    def get(self, request, id):
        rendered = render_to_string(
            "orders/exit_pdf.html", {"order": ExitOrder.objects.get(id=id)}
        )
        # htmldoc = HTML(string=rendered, base_url="http://app.liliumpharma.com")
        # return HttpResponse(htmldoc.write_pdf(), content_type='application/pdf')
        return render(
            request, "orders/exit_pdf.html", {"order": ExitOrder.objects.get(id=id)}
        )


from datetime import date, datetime
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated


class OrderSupervisor(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def apply_filters(self, request):
        """Apply filters based on query parameters."""
        filters = {}

        if request.GET.get("min_date"):
            filters["added__date__gte"] = request.GET.get("min_date")

        if request.GET.get("max_date"):
            filters["added__date__lte"] = request.GET.get("max_date")

        if request.GET.get("produit"):
            filters["orderitem__produit__id"] = request.GET.get("produit")

        if request.GET.get("status"):
            filters["status__in"] = request.GET.get("status").split(",")

        if request.GET.get("user"):
            filters["user__username__in"] = request.GET.get("user").split(",")

        if request.GET.get("source"):
            sources = {
                "Pharmacie": "pharmacy__isnull",
                "Gros": "gros__isnull",
                "Supergros": "super_gros__isnull",
            }
            filters[sources[request.GET.get("source")]] = False

        if request.GET.get("client"):
            clients = {
                "Pharmacie": "pharmacy__isnull",
                "Gros": "gros__isnull",
                "Supergros": "super_gros__isnull",
            }
            filters[clients[request.GET.get("client")]] = False

        return filters

    def apply_keyword_filter(self, request):
        """Apply keyword search filters."""
        q = Q()
        keyword = request.GET.get("keyword")

        if keyword:
            q |= Q(pharmacy__nom__icontains=keyword)
            q |= Q(gros__nom__icontains=keyword)
            q |= Q(super_gros__name__icontains=keyword)

        return q

    def get_filtered_orders(self, request, filters, q):
        """Return filtered and sorted order list based on user roles and conditions."""
        orders = Order.objects.filter(**filters).filter(q).order_by("-added")

        # Additional filters
        if request.GET.get("office") == "1":
            orders = orders.filter(from_company=True)

        if request.GET.get("attente") == "1":
            orders = orders.filter(flag=True)

        if request.GET.get("flag") == "1":
            orders = orders.exclude(status="traite")

        # Apply role-based filtering
        if (
            request.user.userprofile.rolee not in ["Superviseur", "CountryManager"]
            and not request.user.is_superuser
            and request.user.username not in ["liliumdz"]
            and request.user.userprofile.speciality_rolee not in ["Office"]
        ):
            orders = orders.filter(
                Q(user=request.user)
                | Q(touser=request.user)
                | Q(user__username__in=["MeriemDZ", "ibtissemdz"])
            ).distinct()

        elif (
            request.user.userprofile.rolee == "Superviseur"
            and request.user.userprofile.speciality_rolee
            not in ["Superviseur_national"]
        ):
            orders = orders.filter(
                Q(user=request.user)
                | Q(user__in=request.user.userprofile.usersunder.all())
                | Q(touser=request.user)
                | Q(touser__in=request.user.userprofile.usersunder.all())
                | Q(user__username__in=["MeriemDZ", "ibtissemdz"])
            ).distinct()

        elif request.user.userprofile.speciality_rolee in [
            "Office"
        ] or request.user.username in [
            "ibtissemdz",
            "RABTIDZ",
            "a.lounis@liliumpharma.com",
        ]:
            orders = orders.all()

        if request.user.userprofile.speciality_rolee in ["Superviseur_national"]:
            users = User.objects.filter(userprofile__work_as_commercial=True)
            orders = orders.filter(
                Q(user=request.user)
                | Q(user__in=users)
                | Q(touser=request.user)
                | Q(touser__in=users)
                | Q(user__in=request.user.userprofile.usersunder.all())
                | Q(user__username__in=["MeriemDZ", "ibtissemdz"])
            ).distinct()

        return orders

    def get(self, request, id=""):
        if id == "":
            filters = self.apply_filters(request)
            q = self.apply_keyword_filter(request)

            orders_list = self.get_filtered_orders(request, filters, q)
            serializer = OrderSerializer(orders_list, many=True)

            return Response(serializer.data, status=200)
        else:
            order = Order.objects.get(id=id)

            if order.status == "en cours":
                order.status = "traite"
                order.done_date = date.today()

            if order.status == "confirme":
                if request.GET.get("bl"):
                    order.bl = request.GET.get("bl")
                order.status = "en cours"

            if order.status == "initial":
                order.status = "confirme"
                order.validation_date = date.today()

            order.save()
            return Response(OrderSerializer(order).data, status=200)

    def post(self, request, id="", format=None):
        order_obj = self.get_object(id)

        # Serialize and validate the order data
        serializer = OrderSerializer(
            data=request.data, instance=order_obj, partial=True
        )

        if serializer.is_valid():
            # Delete existing order items linked to this order
            OrderItem.objects.filter(order=order_obj).delete()

            # Prepare and serialize order items data
            produits_data = request.data.get("items", [])
            for produit in produits_data:
                produit["order"] = order_obj.id  # Attach the order ID to each product

            order = serializer.save()
            pserializer = OrderItemSerializer(data=produits_data, many=True)

            if pserializer.is_valid():
                pserializer.save()

                # Construct the response data
                response_data = {
                    "id": order.id,
                    "observation": order.observation,
                    "items": produits_data,
                    "medecin": {
                        "id": order.client.id,
                        "nom": order.client.nom,
                        "specialite": order.client.specialite,
                        "classification": order.client.classification,
                        "telephone": order.client.telephone,
                    },
                    "commune": order.client.commune.nom,
                }

                return Response(response_data, status=status.HTTP_201_CREATED)
            else:
                # Handle product serializer errors
                return Response(pserializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Handle order serializer errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def MsOrders(request):

    if request.user.is_authenticated:
        token = Token.objects.filter(user=request.user)

        if token.exists():
            token = token.first().key
        else:
            Token.objects.create(user=request.user)
            token = Token.objects.filter(user=request.user)
            token = token.first().key

    return render(
        request,
        "micro_frontends/orders_front/index.html",
        {"token": token if request.user.is_authenticated else ""},
    )


class ExitOrderSupervisor(APIView):

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, id=""):

        filters = {}
        if request.GET.get("min_date") and request.GET.get("min_date") != "":
            filters["added__date__gte"] = request.GET.get("min_date")

        if request.GET.get("max_date") and request.GET.get("max_date") != "":
            filters["added__date__lte"] = request.GET.get("max_date")
        if request.GET.get("produit") and request.GET.get("produit") != "":
            filters["exit_orderitem__produit__id"] = request.GET.get("produit")

        if request.GET.get("status") and request.GET.get("status") != "":
            filters["status__in"] = request.GET.get("status").split(",")
        if request.GET.get("depot") and request.GET.get("depot") != "":
            filters["depot__in"] = request.GET.get("depot").split(",")
        if request.GET.get("user") and request.GET.get("user") != "":
            filters["user__username__in"] = request.GET.get("user").split(",")

        if id == "":
            if (
                request.user.userprofile.rolee not in ["Superviseur", "CountryManager"]
                and request.user.is_superuser != True
                and request.user.username not in ["liliumdz"]
                and request.user.userprofile.speciality_rolee not in ["Office"]
            ):
                exit_orders_list = ExitOrder.objects.filter(
                    user=request.user,
                    added__month=datetime.now().month,
                    added__year=datetime.now().year,
                ).order_by("-added")
            else:
                if (
                    request.user.is_superuser
                    or request.user.userprofile.speciality_rolee
                    in ["Office", "CountryManager"]
                    or request.user.username
                    in ["ibtissemdz", "RABTIDZ", "a.lounis@liliumpharma.com"]
                ):
                    print("im superuser")
                    q = Q()

                    if q:
                        exit_orders_list = (
                            ExitOrder.objects.filter(**filters)
                            .filter(q)
                            .order_by("-added")
                        )
                    else:
                        exit_orders_list = ExitOrder.objects.filter(**filters).order_by(
                            "-added"
                        )

                else:
                    q = Q(
                        user=request.user,
                        added__month=datetime.now().month,
                        added__year=datetime.now().year,
                    )
                    q |= Q(user__in=request.user.userprofile.usersunder.all())
                    exit_orders_list = (
                        ExitOrder.objects.filter(q, **filters)
                        .distinct()
                        .order_by("-added")
                    )

            serializer = ExitOrderSerializer(exit_orders_list, many=True)

            return Response(serializer.data, status=200)
        else:
            exit_order = ExitOrder.objects.get(id=id)

            if exit_order.status == "confirme":
                exit_order.status = "traite"
                exit_order.done_date = datetime.today().date()

            if exit_order.status == "initial":
                exit_order.status = "confirme"
                exit_order.user_confirmed = request.user
                exit_order.validation_date = datetime.today().date()

            exit_order.save()

            return Response(ExitOrderSerializer(exit_order).data, status=200)

    def post(self, request, id="", format=None):

        exit_order_obj = self.get_object(id)
        serializer = ExitOrderSerializer(
            data=request.data, instance=exit_order_obj, partial=True
        )
        if serializer.is_valid():
            ExitOrderItem.objects.filter(exit_order=exit_order_obj).delete()
            produits_data = request.data.get("items")
            exit_order = serializer.save()
            produits_data = list(
                map(lambda p: {**p, "exit_order": exit_order.id}, produits_data)
            )
            pserializer = ExitOrderItemSerializer(data=produits_data, many=True)
            if pserializer.is_valid():
                pserializer.save()
                return Response(
                    {
                        "id": exit_order.id,
                        "observation": exit_order.observation,
                        "items": produits_data,
                        "commune": exit_order.client.commune.nom,
                    },
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response(pserializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def MsExitOrders(request):

    if request.user.is_authenticated:
        token = Token.objects.filter(user=request.user)

        if token.exists():
            token = token.first().key
        else:
            Token.objects.create(user=request.user)
            token = Token.objects.filter(user=request.user)
            token = token.first().key

    return render(
        request,
        "micro_frontends/exit_orders_front/index.html",
        {"token": token if request.user.is_authenticated else ""},
    )


class ShareUser(APIView):

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            raise Http404

    def get_user(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404

    def get(self, request, id):
        touser = self.get_user(request.GET.get("user"))
        Order.objects.filter(id=id).update(
            transfer_date=date.today(), touser=touser, status="en cours"
        )
        instance = self.get_object(id)
        notification = Notification.objects.create(
            title=f"Transfert Bon de commande  {instance.user.username}",
            description=f"{str(instance.added)}",
            data={
                "name": "Orders",
                "title": "Bon de commande",
                "message": f"Transfert Bon de commande de {instance.user.username} a {touser.username}",
                "confirm_text": "voir le bon",
                "cancel_text": "plus tard",
                "StackName": "Orders",
                "url": f"https://app.liliumpharma.com/orders/front/?user={instance.user.username}&date={instance.added.date()}",
                "navigate_to": json.dumps(
                    {
                        "screen": "List",
                        "params": {
                            "user": instance.user.username,
                            "date": str(instance.added.date()),
                        },
                    },
                    ensure_ascii=False,
                ),
            },
        )
        notification.users.set(
            [
                touser,
            ]
        )
        # notification.send()
        return Response(status=200)


from datetime import *
from django.db.models import Q


class ordersPerUserPerMonth(APIView):

    authentication_classes = (
        TokenAuthentication,
        SessionAuthentication,
    )
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user_param = request.GET.get("user")
        if user_param:
            user = User.objects.filter(username=user_param).first()
        else:
            user = request.user
        # user=request.user

        year = date.today().year
        month_param = request.GET.get("month")
        try:
            month = int(month_param)
            tz = datetime.now().tzinfo  # Get the current time zone

            if 1 <= month <= 12:
                date_debut_mois = datetime(
                    date.today().year, month, 1, 0, 0, 0, 0, tzinfo=tz
                )
                if month == 12:
                    date_fin_mois = datetime(
                        date.today().year + 1, 1, 1, 0, 0, 0, 0, tzinfo=tz
                    )
                else:
                    date_fin_mois = datetime(
                        date.today().year, month + 1, 1, 0, 0, 0, 0, tzinfo=tz
                    )
            else:
                return Response(
                    {"error": "Mois invalide. Utilisez une valeur entre 1 et 12."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except (ValueError, TypeError):
            return Response(
                {
                    "error": "Mois invalide. Utilisez une valeur numérique entre 1 et 12."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        orders = Order.objects.filter(
            user=user, added__range=[date_debut_mois, date_fin_mois], added__year=year
        )

        data = {
            "total_orders": orders.count(),
            "orders": [],
            "transfered_orders": [],
            "transfered_orders_2": [],
            "product_summary": {},  # Ajout d'un dictionnaire pour stocker le résumé des quantités de produits
        }
        transfered_orders = Order.objects.filter(
            touser=user, added__range=[date_debut_mois, date_fin_mois], added__year=year
        )
        transfered_orders_2 = Order.objects.filter(
            Q(user=user)
            & Q(added__range=[date_debut_mois, date_fin_mois])
            & ~Q(touser=None)
        )
        for order in orders:
            order_data = {
                "order_id": order.id,
                "status": order.status,
                "date": order.added.strftime("%Y-%m-%d"),
                "products": [],
                "pharmacy": order.pharmacy.nom if order.pharmacy else "-",
                "gros": order.gros.nom if order.gros else "-",
                "super_gros": order.super_gros.name if order.super_gros else "-",
            }

            order_items = OrderItem.objects.filter(order=order)

            for item in order_items:
                product_data = {
                    "product_name": item.produit.nom,
                    "quantity": item.qtt,
                }
                order_data["products"].append(product_data)

                # Mise à jour du résumé des quantités de produits
                product_name = item.produit.nom
                if product_name in data["product_summary"]:
                    data["product_summary"][product_name] += item.qtt

            data["orders"].append(order_data)

        for order in transfered_orders:
            order_data_transfered = {
                "user": str(order.user),
                "order_id": order.id,
                "status": order.status,
                "date": order.added.strftime("%Y-%m-%d"),
                "products": [],
                "pharmacy": order.pharmacy.nom if order.pharmacy else "-",
                "gros": order.gros.nom if order.gros else "-",
                "super_gros": order.super_gros.name if order.super_gros else "-",
            }

            order_items = OrderItem.objects.filter(order=order)
            for item in order_items:
                product_data = {
                    "product_name": item.produit.nom,
                    "quantity": item.qtt,
                }
                order_data_transfered["products"].append(product_data)

                # Mise à jour du résumé des quantités de produits
                product_name = item.produit.nom
                if product_name in data["product_summary"]:
                    data["product_summary"][product_name] += item.qtt
                else:
                    data["product_summary"][product_name] = item.qtt

            data["transfered_orders"].append(order_data_transfered)

        for order in transfered_orders_2:
            order_data_transfered_2 = {
                "user": str(order.user),
                "order_id": order.id,
                "status": order.status,
                "date": order.added.strftime("%Y-%m-%d"),
                "products": [],
                "to_user": order.touser.username,
                "pharmacy": order.pharmacy.nom if order.pharmacy else "-",
                "gros": order.gros.nom if order.gros else "-",
                "super_gros": order.super_gros.name if order.super_gros else "-",
            }

            order_items = OrderItem.objects.filter(order=order)
            for item in order_items:
                product_data = {
                    "product_name": item.produit.nom,
                    "quantity": item.qtt,
                }
                order_data_transfered_2["products"].append(product_data)

                # Mise à jour du résumé des quantités de produits
                product_name = item.produit.nom
                if product_name in data["product_summary"]:
                    data["product_summary"][product_name] += item.qtt
                else:
                    data["product_summary"][product_name] = item.qtt

            data["transfered_orders_2"].append(order_data_transfered_2)

        return Response(data)



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from .models import Order, OrderItem  # Assurez-vous d'importer vos modèles
from datetime import datetime
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import User, Order, OrderItem
from .serializers import OrderSerializer
from datetime import datetime

class OrdersByUserAndDateView(APIView):

    def get(self, request, username, order_date):
        try:
            # Vérification du format du nom d'utilisateur
            name_parts = username.split()
            if len(name_parts) != 2:
                return Response({"error": "Invalid username format"}, status=400)
            first_name, last_name = name_parts

            # Filtrer l'utilisateur basé sur le prénom et nom de famille
            user = User.objects.get(first_name=first_name, last_name=last_name)

            # Convertir la date fournie dans l'URL au format de date Python
            try:
                order_date = datetime.strptime(order_date, '%Y-%m-%d').date()
            except ValueError:
                return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

            # Filtrer les commandes de cet utilisateur dans la plage de dates donnée
            orders = Order.objects.filter(user=user, added__date=order_date)

            # Utiliser le serializer pour convertir les commandes en JSON
            orders_data = OrderSerializer(orders, many=True).data

            # Comptage des commandes pour pharmacie et gros
            orders_with_pharmacy_and_gros = orders.filter(pharmacy__isnull=False, gros__isnull=False)
            count_orders_with_pharmacy_and_gros = orders_with_pharmacy_and_gros.count()

            product_qty_pharmacy_and_gros = {}
            for order in orders_with_pharmacy_and_gros:
                order_items = OrderItem.objects.filter(order=order)
                for item in order_items:
                    product_name = item.produit.nom
                    qty = item.qtt

                    if product_name in product_qty_pharmacy_and_gros:
                        product_qty_pharmacy_and_gros[product_name] += qty
                    else:
                        product_qty_pharmacy_and_gros[product_name] = qty

            # Comptage des commandes pour gros et super gros
            orders_with_gros_and_super_gros = orders.filter(gros__isnull=False, super_gros__isnull=False)
            count_orders_with_gros_and_super_gros = orders_with_gros_and_super_gros.count()

            product_qty_gros_and_super_gros = {}
            for order in orders_with_gros_and_super_gros:
                order_items = OrderItem.objects.filter(order=order)
                for item in order_items:
                    product_name = item.produit.nom
                    qty = item.qtt

                    if product_name in product_qty_gros_and_super_gros:
                        product_qty_gros_and_super_gros[product_name] += qty
                    else:
                        product_qty_gros_and_super_gros[product_name] = qty

            # Création d'un ensemble de produits uniques
            all_products = set(product_qty_pharmacy_and_gros.keys()).union(product_qty_gros_and_super_gros.keys())
            unique_products = list(all_products)

            # Préparation des données à envoyer dans la réponse
            context = {
                "orders_with_pharmacy_and_gros": orders_data,
                "orders_with_gros_and_super_gros": orders_data,
                "product_qty_pharmacy_and_gros": product_qty_pharmacy_and_gros,
                "product_qty_gros_and_super_gros": product_qty_gros_and_super_gros,
                "unique_products": unique_products,
                "count_orders_with_pharmacy_and_gros": count_orders_with_pharmacy_and_gros,
                "count_orders_with_gros_and_super_gros": count_orders_with_gros_and_super_gros,
            }
            print(str(context))

            return Response(context, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=404)
