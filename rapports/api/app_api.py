from django.contrib import messages
from notifications.models import Notification
from rapports.models import Rapport, Visite, Comment
from .serializers import (
    RapportSerializer,
    CommentAppSerializer,
    RapportAppSerializer,
    VisiteSerializer,
)
from produits.api.serializers import ProduitVisiteSerializer
from django.http import Http404, HttpResponseForbidden
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from django.db.models import Count
from rapports.get_rapports import rapport_list
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import (
    SessionAuthentication,
    BasicAuthentication,
    TokenAuthentication,
)
from medecins.models import Medecin
from leaves.models import *
from itertools import chain
from produits.models import Produit, ProduitVisite
from datetime import datetime, date, timedelta
from django.core.paginator import Paginator
from rest_framework.parsers import MultiPartParser, FileUploadParser, FormParser
import json
from django.utils.dateformat import DateFormat


from plans.models import Plan
from accounts.models import UserProfile
from deals.models import Deal
from notifications.utils import send_to_user



class RapportAppAPI(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_object(self, pk):
        try:
            return Rapport.objects.get(pk=pk)
        except Rapport.DoesNotExist:
            raise Http404

    def pagination_response(self, rapports, json, details, result_length, all_length):
        response = {
            "pages": rapports.paginator.num_pages,
            "result": {"rapports": json.data, "details": details},
            "length": result_length,
            "all_length": all_length,
        }
        try:
            response["previous"] = rapports.previous_page_number()
        except:
            pass
        try:
            response["next"] = rapports.next_page_number()
        except:
            pass
        return response

    # def put(self, request, id="", format=None):
    #     print(str(request.user) + " is putting a report")
    #     user_profile = UserProfile.objects.get(user=request.user)



    #     # Détermination de la date du rapport
    #     if id:
    #         rapport = Rapport.objects.filter(id=id).first()
    #         report_added_date = rapport.added if rapport else datetime.today()
    #     else:
    #         report_added_date = datetime.today()

    #     # Vérif absences
    #     if Absence.objects.filter(date=report_added_date, user=request.user).exists():
    #         print("There are absences on the same date as the report.")
    #         return Response({"message": "forbidden"}, status=403)

    #     # Vérif congés
    #     leaves_on_date = Leave.objects.filter(
    #         start_date__lte=report_added_date,
    #         end_date__gt=report_added_date,
    #         user=request.user,
    #     )

    #     if leaves_on_date.exists():
    #         leave = leaves_on_date.first()

    #         # Préparer les données (tout en str)
    #         data = {
    #             "name": "Attention | حذاري",
    #             "title": "Attention | حذاري",
    #             "message": "Vous avez enregistré un congé pour aujourd'hui. "
    #                        "Il n'est pas possible d'ajouter un rapport.\n"
    #                        "لديك إجازة لليوم. لا يُمكن إضافة تقرير جديد",
    #             "confirm_text": "Liste des congés",
    #             "cancel_text": "Annuler",
    #             "StackName": "Holidays",
    #             "navigate_to": json.dumps({
    #                 "screen": "Details",
    #                 "params": {"congé": leave.id, "should_fetch": True}
    #             })
    #         }

    #         # Créer la notification en base
    #         notification = Notification.objects.create(
    #             title="ATTENTION !",
    #             description=data["message"],
    #             data=data
    #         )
    #         notification.users.add(request.user)

    #         # Envoyer en push
    #         send_to_user(
    #             username=request.user.username,
    #             title="ATTENTION !",
    #             description=data["message"],
    #             data={k: str(v) for k, v in data.items()}
    #         )

    #         return Response({
    #             "message": "Vous êtes en congé aujourd'hui. Rapport non autorisé.",
    #             "type": "error"
    #         }, status=403)

    # # Si pas de congé → traitement normal
    # # ...


    #     print("valid commune ==> " + str(user_planning.valid_commune))

    #     print("valid client ==> " + str(user_planning.valid_clients))

    #     print("valid tasks ==> " + str(user_planning.valid_tasks))
    #     # if user_planning.valid_commune and user_planning.valid_clients and user_profile.rolee not in ["CountryManager"]:

    #     # notification=Notification.objects.create(
    #     # title=f"ATTENTION",
    #     # description=f"Vous avez enregistré un congé pour aujourd'hui. Il n'est pas possible d'ajouter un rapport.\nلديك إجازة لليوم. لا يُمكن إضافة تقرير جديد",
    #     # data={
    #     #         "name":"Attention | حذاري",
    #     #         "title":"Attention | حذاري",
    #     #         "message" : f"Votre planning n'est pas validé, veuillez consulter votre supérieur.\nلديك إجازة لليوم. لا يُمكن إضافة تقرير جديد",
    #     #         "confirm_text":"Liste des congés",
    #     #         "cancel_text":"Annuler",
    #     #         "StackName":"Holidays",
    #     #         "navigate_to":json.dumps({
    #     #                "screen":"Details",
    #     #                 "params":{
    #     #                     "congé":leave.id,
    #     #                     "should_fetch":True
    #     #                     }
    #     #             })
    #     #     },
    #     # )
    #     # notification.users.add(request.user)
    #     # notification.send()
    #     # return Response({"message":"forbbiden"},status=403)

    #     messages.warning(
    #         request,
    #         "Vous avez déjà ajouté un rapport aujourd'hui. Veuillez consulter la liste des rapports.",
    #     )

    #     if id == "":  # CREATING NEW RAPPORT
    #         try:
    #             rapport = Rapport.objects.get(added=datetime.today(), user=request.user)
    #             rapport_exists = Rapport.objects.get(
    #                 added=datetime.today(), user=request.user
    #             )
    #             if rapport_exists:
    #                 print("Repport exists !")
    #                 notification = Notification.objects.create(
    #                     title=f"Nouveau commentaire !",
    #                     description=f"ATTENTION ",
    #                     data={
    #                         "name": "Attention | حذاري",
    #                         "title": "Attention | حذاري",
    #                         "message": f"Vous avez déjà un rapport ajouté aujourd'hui, Veuillez Consulter la liste des rapports.\nلقد قمت بإضافة تقرير اليوم، لا يمكنك إظافة تقرير آخر.",
    #                         "confirm_text": "Voir le rapport",
    #                         "cancel_text": "Annuler",
    #                         "StackName": "Rapports",
    #                         "url": f"https://app.liliumpharma.com/rapports/PDF/{rapport.id}",
    #                         "navigate_to": json.dumps(
    #                             {
    #                                 "screen": "Details",
    #                                 "params": {
    #                                     "rapport": rapport.id,
    #                                     "should_fetch": True,
    #                                 },
    #                             }
    #                         ),
    #                     },
    #                 )

    #                 users_to_notify = request.user.userprofile.get_users_to_notify()

    #                 # Step 2: Exclude the current user from the list
    #                 # users_to_notify = users_to_notify.exclude(id=request.user.id)

    #                 # Step 5: Set the users for the notification
    #                 notification.users.set(users_to_notify)
    #                 return Response({"error": "cannot add rapport"}, status=403)

    #         except Rapport.DoesNotExist:
    #             serializer = RapportAppSerializer(
    #                 data=request.data,
    #                 instance=Rapport(user=request.user, added=date.today()),
    #                 partial=True,
    #             )
    #             if serializer.is_valid():
    #                 serializer = RapportAppSerializer(
    #                     data=request.data,
    #                     instance=Rapport(user=request.user, added=date.today()),
    #                     partial=True,
    #                 )
    #                 if serializer.is_valid() and user_profile.rolee in [
    #                     "CountryManager"
    #                 ]:
    #                     rapport = serializer.save()
    #                     r = RapportSerializer(instance=rapport)
    #                     return Response(r.data, status=status.HTTP_201_CREATED)
    #                 if (
    #                     serializer.is_valid()
    #                     and user_planning.valid_commune
    #                     and user_planning.valid_clients
    #                     and user_profile.rolee not in ["CountryManager"]
    #                 ):
    #                     rapport = serializer.save()
    #                     r = RapportSerializer(instance=rapport)
    #                     return Response(r.data, status=status.HTTP_201_CREATED)
    #                 if (
    #                     serializer.is_valid()
    #                     and user_planning.valid_tasks
    #                     and user_profile.rolee not in ["CountryManager"]
    #                 ):
    #                     rapport = serializer.save()
    #                     r = RapportSerializer(instance=rapport)
    #                     return Response(r.data, status=status.HTTP_201_CREATED)
    #             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #     else:
    #         rapport = self.get_object(id)
    #         print(
    #             "user "
    #             + str(request.user)
    #             + " is_superuser"
    #             + str(request.user.is_superuser)
    #         )
    #         if request.user == rapport.user or request.user.is_superuser:
    #             serializer = RapportAppSerializer(
    #                 data=request.data, instance=rapport, partial=True
    #             )
    #             if serializer.is_valid():
    #                 r = serializer.save()
    #                 rr = RapportSerializer(instance=r)
    #                 return Response(rr.data)
    #             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #         else:
    #             return Response({"message": "forbbiden"}, status=403)

    def put(self, request, id="", format=None):
        print(str(request.user) + " is putting a report")
        user_profile = UserProfile.objects.get(user=request.user)
        # GETTING PLANNING
        user_planning = Plan.objects.get(day=datetime.today().date(), user=request.user)
        print(user_planning)
        print("hiiiiii")
        print(str(self))

        if id:
            rapport = Rapport.objects.filter(id=id).first()
            report_added_date = rapport.added

        else:
            report_added_date = datetime.today().date()

        absences_on_date = Absence.objects.filter(
            date=report_added_date, user=request.user
        )
        if absences_on_date.exists():
            print("There are absences on the same date as the report.")
            return Response({"message": "forbbiden"}, status=403)

        leave = Leave.objects.filter(
            start_date__lte=report_added_date,
            end_date__gt=report_added_date,
            user=request.user,
        ).first()
        leaves_on_date = Leave.objects.filter(
            start_date__lte=report_added_date,
            end_date__gt=report_added_date,
            user=request.user,
        )
        print(str(leaves_on_date))
        if leaves_on_date.exists():
            print("There are leaves covering the same date as the report.")
            notification = Notification.objects.create(
                title=f"ATTENTION !",
                description=f"Vous avez enregistré un congé pour aujourd'hui. Il n'est pas possible d'ajouter un rapport.\nلديك إجازة لليوم. لا يُمكن إضافة تقرير جديد",
                data={
                    "name": "Attention | حذاري",
                    "title": "Attention | حذاري",
                    "message": f"Vous avez enregistré un congé pour aujourd'hui. Il n'est pas possible d'ajouter un rapport.\nلديك إجازة لليوم. لا يُمكن إضافة تقرير جديد",
                    "confirm_text": "Liste des congés",
                    "cancel_text": "Annuler",
                    "StackName": "Holidays",
                    "navigate_to": json.dumps(
                        {
                            "screen": "Details",
                            "params": {"congé": leave.id, "should_fetch": True},
                        }
                    ),
                },
            )
            notification.users.add(request.user)
            # notification.send()
            return Response({"message": "forbbiden"}, status=403)

        print("valid commune ==> " + str(user_planning.valid_commune))

        print("valid client ==> " + str(user_planning.valid_clients))

        print("valid tasks ==> " + str(user_planning.valid_tasks))
        # if user_planning.valid_commune and user_planning.valid_clients and user_profile.rolee not in ["CountryManager"]:

        # notification=Notification.objects.create(
        # title=f"ATTENTION",
        # description=f"Vous avez enregistré un congé pour aujourd'hui. Il n'est pas possible d'ajouter un rapport.\nلديك إجازة لليوم. لا يُمكن إضافة تقرير جديد",
        # data={
        #         "name":"Attention | حذاري",
        #         "title":"Attention | حذاري",
        #         "message" : f"Votre planning n'est pas validé, veuillez consulter votre supérieur.\nلديك إجازة لليوم. لا يُمكن إضافة تقرير جديد",
        #         "confirm_text":"Liste des congés",
        #         "cancel_text":"Annuler",
        #         "StackName":"Holidays",
        #         "navigate_to":json.dumps({
        #                "screen":"Details",
        #                 "params":{
        #                     "congé":leave.id,
        #                     "should_fetch":True
        #                     }
        #             })
        #     },
        # )
        # notification.users.add(request.user)
        # notification.send()
        # return Response({"message":"forbbiden"},status=403)

        messages.warning(
            request,
            "Vous avez déjà ajouté un rapport aujourd'hui. Veuillez consulter la liste des rapports.",
        )

        if id == "":  # CREATING NEW RAPPORT
            try:
                rapport = Rapport.objects.get(added=datetime.today().date(), user=request.user)
                rapport_exists = Rapport.objects.get(
                    added=datetime.today().date(), user=request.user
                )
                if rapport_exists:
                    print("Repport exists !")
                    notification = Notification.objects.create(
                        title=f"Nouveau commentaire !",
                        description=f"ATTENTION ",
                        data={
                            "name": "Attention | حذاري",
                            "title": "Attention | حذاري",
                            "message": f"Vous avez déjà un rapport ajouté aujourd'hui, Veuillez Consulter la liste des rapports.\nلقد قمت بإضافة تقرير اليوم، لا يمكنك إظافة تقرير آخر.",
                            "confirm_text": "Voir le rapport",
                            "cancel_text": "Annuler",
                            "StackName": "Rapports",
                            "url": f"https://app.liliumpharma.com/rapports/PDF/{rapport.id}",
                            "navigate_to": json.dumps(
                                {
                                    "screen": "Details",
                                    "params": {
                                        "rapport": rapport.id,
                                        "should_fetch": True,
                                    },
                                }
                            ),
                        },
                    )

                    users_to_notify = request.user.userprofile.get_users_to_notify()

                    # Step 2: Exclude the current user from the list
                    # users_to_notify = users_to_notify.exclude(id=request.user.id)

                    # Step 5: Set the users for the notification
                    notification.users.set(users_to_notify)
                    return Response({"error": "cannot add rapport"}, status=403)

            except Rapport.DoesNotExist:
                serializer = RapportAppSerializer(
                    data=request.data,
                    instance=Rapport(user=request.user, added=date.today()),
                    partial=True,
                )
                if serializer.is_valid():
                    serializer = RapportAppSerializer(
                        data=request.data,
                        instance=Rapport(user=request.user, added=date.today()),
                        partial=True,
                    )
                    if serializer.is_valid() and user_profile.rolee in [
                        "CountryManager"
                    ]:
                        rapport = serializer.save()
                        r = RapportSerializer(instance=rapport)
                        return Response(r.data, status=status.HTTP_201_CREATED)
                    if (
                        serializer.is_valid()
                        and user_planning.valid_commune
                        and user_planning.valid_clients
                        and user_profile.rolee not in ["CountryManager"]
                    ):
                        rapport = serializer.save()
                        r = RapportSerializer(instance=rapport)
                        return Response(r.data, status=status.HTTP_201_CREATED)
                    if (
                        serializer.is_valid()
                        and user_planning.valid_tasks
                        and user_profile.rolee not in ["CountryManager"]
                    ):
                        rapport = serializer.save()
                        r = RapportSerializer(instance=rapport)
                        return Response(r.data, status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            rapport = self.get_object(id)
            print(
                "user "
                + str(request.user)
                + " is_superuser"
                + str(request.user.is_superuser)
            )
            if request.user == rapport.user or request.user.is_superuser:
                serializer = RapportAppSerializer(
                    data=request.data, instance=rapport, partial=True
                )
                if serializer.is_valid():
                    r = serializer.save()
                    rr = RapportSerializer(instance=r)
                    return Response(rr.data)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"message": "forbbiden"}, status=403)
    
    def get(self, request, format=None):
        if request.user.is_authenticated:
            request.session['user_id'] = request.user.id
            print("User_id est dans session")
            print(request.session.get('user_id')
)
        else:
            print("METHODE GET sur Rapports mais aucun utilisateur connecté (AnonymousUser)")

        if  request.user.is_superuser or request.user.userprofile.rolee=="Superviseur" or request.user.userprofile.rolee=="CountryManager" :
            rapports_list=rapport_list(request)
        else:
            rapports_month=Rapport.objects.filter(added__month=datetime.now().month,added__year=datetime.now().year,user=request.user).order_by('-added')
            rapport_updatable=Rapport.objects.filter(can_update=True,user=request.user).exclude(id__in=rapports_month.values('id')).order_by('-added')
            rapports_list=list(chain(rapports_month,rapport_updatable))

        # rapports_list = rapport_list(request)

        produits = Produit.objects.filter(
            pays=request.user.userprofile.commune.wilaya.pays
        )

        visites = Visite.objects.filter(rapport__in=rapports_list)

        medecins = Medecin.objects.filter(visite__in=visites).distinct()

        medecin_nbr = len(medecins) - len(
            medecins.filter(specialite__in=["Pharmacie", "Grossiste", "SuperGros"])
        )

        details = (
            Medecin.objects.filter(id__in=medecins.values("id"))
            .values("specialite")
            .annotate(dcount=Count("specialite"))
        )
        other_details = " ".join(
            [f'{detail["dcount"]} {detail["specialite"]} ' for detail in details]
        )

        other_details = "\n"
        other_details += " ".join(
            [
                str(len(visites.filter(produits__id=produit.id))) + " " + produit.nom
                for produit in produits
            ]
        )

        details = f"{len(medecins)} clients {medecin_nbr} medecins {other_details}"

        paginator = Paginator(rapports_list, 3)
        page = (
            request.GET.get("page")
            if request.GET.get("page") and request.GET.get("page") != "0"
            else None
        )
        rapports = paginator.get_page(page)

        serializer = RapportSerializer(rapports, many=True)

        return Response(
            self.pagination_response(
                rapports, serializer, details, len(rapports_list), len(rapports_list)
            ),
            status=200,
        )


class VisiteAppApi(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Visite.objects.get(id=pk)
        except Visite.DoesNotExist:
            raise Http404

    def get_rapport(self, pk):
        try:
            return Rapport.objects.get(pk=pk)
        except Rapport.DoesNotExist:
            raise Http404

    def post(self, request, id="", format=None):
        rapport = self.get_rapport(request.data.get("rapport"))

        print(str(request.user) + " is trying to add visit")
        if rapport.is_updatable():

            if id == "":
                data = request.data.copy()

                if type(data.get("priority")) == "str":
                    data["priority"] = data.get("priority")

                if request.data.get("priority") == "":
                    print("proptité vide !")
                    data["priority"] = "0"

                serializer = VisiteSerializer(data=data)
                if serializer.is_valid():
                    produits_data = request.data.get("produits")
                    visite = serializer.save()
                    for p in produits_data:
                        p["visite"] = visite.id
                    pserializer = ProduitVisiteSerializer(data=produits_data, many=True)
                    if pserializer.is_valid():
                        pserializer.save()
                        return Response(
                            {
                                "id": visite.id,
                                "observation": visite.observation,
                                "priorite": visite.priority,
                                "produits": visite.products_to_json(),
                                "medecin": {
                                    "id": visite.medecin.id,
                                    "nom": visite.medecin.nom,
                                    "specialite": visite.medecin.specialite,
                                    "classification": visite.medecin.classification,
                                    "telephone": visite.medecin.telephone,
                                    # "deals":[ d.id for d in visite.medecin.deal_set.all()]
                                    "deals": [
                                        deals.id
                                        for deals in Deal.objects.filter(
                                            medecin__id=visite.medecin.id
                                        )
                                    ],
                                    # "deals":[]
                                },
                                "commune": visite.medecin.commune.nom,
                            },
                            status=status.HTTP_201_CREATED,
                        )
                    else:
                        return Response(
                            pserializer.errors, status=status.HTTP_400_BAD_REQUEST
                        )

                print(request.data)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                visite_obj = self.get_object(id)
                serializer = VisiteSerializer(data=request.data, instance=visite_obj)
                if serializer.is_valid():
                    visite_obj.produits.clear()
                    ProduitVisite.objects.filter(visite=visite_obj).delete()
                    produits_data = request.data.get("produits")
                    visite = serializer.save()
                    for p in produits_data:
                        p["visite"] = visite.id
                    pserializer = ProduitVisiteSerializer(data=produits_data, many=True)
                    if pserializer.is_valid():
                        pserializer.save()
                        return Response(
                            {
                                "id": visite.id,
                                "observation": visite.observation,
                                "priorite": visite.priority,
                                "produits": visite.products_to_json(),
                                "medecin": {
                                    "id": visite.medecin.id,
                                    "nom": visite.medecin.nom,
                                    "specialite": visite.medecin.specialite,
                                    "classification": visite.medecin.classification,
                                    "telephone": visite.medecin.telephone,
                                    # "deals":[ d.id for d in visite.medecin.deal_set.all()]
                                    "deals": [
                                        deals.id
                                        for deals in Deal.objects.filter(
                                            medecin__id=visite.medecin.id
                                        )
                                    ],
                                    # "deals":[]
                                },
                                "commune": visite.medecin.commune.nom,
                            },
                            status=status.HTTP_201_CREATED,
                        )
                    else:
                        return Response(
                            pserializer.errors, status=status.HTTP_400_BAD_REQUEST
                        )

                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            raise HttpResponseForbidden

    def delete(self, request, id, format=None):
        visite = self.get_object(id)
        visite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentAPI(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        serializer = CommentAppSerializer(
            data=request.data, instance=Comment(user=request.user), partial=True
        )
        if serializer.is_valid():
            comment = serializer.save()

            return Response(
                {
                    "id": comment.id,
                    "user": {"username": request.user.username},
                    "comment": comment.comment,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SingleRapportAPI(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Rapport.objects.get(id=pk)
        except Rapport.DoesNotExist:
            raise Http404

    def get(self, request, id, format=None):
        rappport = self.get_object(id)
        serializer = RapportAppSerializer(rappport, many=False)
        return Response(serializer.data)
