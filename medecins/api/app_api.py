from medecins.models import Medecin
from .serializers import MedecinPlanSerializer, MedecinSerializer
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import (
    SessionAuthentication,
    BasicAuthentication,
    TokenAuthentication,
)
from rest_framework.response import Response
from rest_framework import status
import datetime
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.models import User
from medecins.get_medecins import get_medecins
from accounts.models import UserProfile
from django.db.models import Count
from liliumpharm.redis_cli import RedisConnect
import json
from medecins.save_to_redis import SaveRedisThread
from rest_framework.permissions import AllowAny



MEDICAL = [
    "Généraliste",
    "Diabetologue",
    "Neurologue",
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
    "Interniste",
    "Endocrinologue",
    "Dentiste",
    "ORL",
    "Gastrologue",
]
COMMERCIAL = ["Pharmacie", "Grossiste", "SuperGros"]


from django.db.models import Q, OuterRef, Subquery, F
from rapports.models import Visite


class PlanMedecinAPI(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_search(self, request):
        filters = {}

        # Gestion des utilisateurs
        if request.GET.get("user"):
            filters["users__id"] = request.GET.get("user")
        else:
            user_profile = request.user.userprofile
            if user_profile.rolee == "CountryManager" or request.user.is_superuser:
                filters = {}
            else:
                # Utiliser `in_bulk` pour récupérer les utilisateurs en une seule requête
                user_ids = list(
                    user_profile.usersunder.values_list("id", flat=True)
                ) + [request.user.id]
                filters["users__in"] = user_ids

        # Filtrage par mot clé et nom
        keyword = request.GET.get("keyword") or request.GET.get("medecin")
        print(" keyboard " + str(keyword))
        if keyword is None:
            print("keyword is none")
        if keyword:
            filters["nom__icontains"] = keyword

        # Précharger les relations importantes pour éviter les requêtes supplémentaires
        medecins_list = (
            Medecin.objects.filter(**filters).select_related("commune").distinct()
        )

        # Filtrer par visites
        visited = request.GET.get("visited")
        if visited and visited != "all":
            today = datetime.date.today()
            # Précharger les rapports et visites
            medecins_with_visits = medecins_list.filter(
                visite__rapport__added__month=today.month,
                visite__rapport__added__year=today.year,
            ).distinct()

            if visited == "unvisited":
                medecins_list = medecins_list.exclude(
                    id__in=medecins_with_visits.values_list("id", flat=True)
                )
            elif visited == "visited":
                medecins_list = medecins_with_visits

        # Exclusions et autres filtres
        rapport = request.GET.get("rapport")
        if rapport:
            medecins_list = medecins_list.exclude(visite__rapport__id=rapport)

        if request.GET.get("commercial") == "1":
            medecins_list = medecins_list.exclude(specialite__in=MEDICAL)

        spec = request.GET.get("spec")
        if spec:
            medecins_list = medecins_list.filter(specialite=request.GET.get("spec"))

        plan_id = request.GET.get("plan_id")
        if plan_id:
            medecins_list = medecins_list.exclude(plan__id=plan_id)

        commune = request.GET.get("commune")
        if commune:
            medecins_list = medecins_list.filter(commune__id=commune)

        # Récupération finale des résultats et pagination
        print(
            f"Searching from {request.user} ................................................."
        )

        if request.GET.get("search") == "1":
            # Si `search=1`, renvoyer tous les résultats sans pagination
            serializer = MedecinSerializer(medecins_list, many=True)
            return Response(serializer.data, status=200)
        else:
            # Utiliser la pagination
            paginator = Paginator(medecins_list, 20)
            page = (
                request.GET.get("page")
                if request.GET.get("page") and request.GET.get("page") != "0"
                else 1
            )
            medecins = paginator.page(page)
            medecins_json = MedecinSerializer(medecins, many=True)

            return Response(
                self.pagination_response(medecins, medecins_json, medecins_list),
                status=200,
            )

    def pagination_response(self, medecins, json, medecins_list):
        # Optimisation du calcul des spécialités et des visites
        specialite_counts = (
            Medecin.objects.filter(id__in=medecins_list.values("id"))
            .values("specialite")
            .annotate(dcount=Count("specialite"))
        )

        medecin_nbr = (
            len(medecins_list)
            - medecins_list.filter(
                specialite__in=["Pharmacie", "Grossiste", "SuperGros"]
            ).count()
        )

        details = [
            {"specialite": "medecin", "nbr_visites": medecin_nbr},
            *[
                {"specialite": detail["specialite"], "nbr_visites": detail["dcount"]}
                for detail in specialite_counts
            ],
        ]

        response = {
            "pages": medecins.paginator.num_pages,
            "result": json.data,
            "details": details,
            "length": len(medecins_list),
        }

        if medecins.has_previous():
            response["previous"] = medecins.previous_page_number()
        if medecins.has_next():
            response["next"] = medecins.next_page_number()

        return response

    def get(self, request, id="", format=None):
        if request.GET.get("search") == "1":
            return self.get_search(request)

        medecins_list = Medecin.objects.all()  # Or apply other filters as necessary
        paginator = Paginator(medecins_list, 20)

        page = (
            request.GET.get("page")
            if request.GET.get("page") and request.GET.get("page") != "0"
            else 1
        )
        medecins = paginator.page(page)
        medecins_json = MedecinSerializer(medecins, many=True)

        return Response(
            self.pagination_response(medecins, medecins_json, medecins_list),
            status=200,
        )

    def post(self, request, id="", format=None):
        print(f"{request.user} is trying to add a new medecin {request.data}")
        if id == "":  # CREATING NEW MEDECIN
            serializer = MedecinSerializer(data=request.data)
            if serializer.is_valid():
                if (
                    request.data.get("specialite") in MEDICAL
                    and request.user.userprofile.can_add_medecin
                ) or (
                    request.data.get("specialite") in COMMERCIAL
                    and request.user.userprofile.can_add_client
                ):
                    medecin = serializer.save()
                    medecin.users.add(request.user)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            medecin = self.get_object(id)
            if medecin.user_can_update(request.user):
                serializer = MedecinSerializer(medecin, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"message": "forbidden"}, status=403)

    def get_object(self, pk):
        try:
            return Medecin.objects.get(pk=pk)
        except Medecin.DoesNotExist:
            raise Http404


class MedecinAppAPI(APIView):
    #authentication_classes = []
    #permission_classes = [AllowAny]
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def pagination_response(self, medecins, json, medecins_list):

        medecin_nbr = len(medecins_list) - len(
            medecins_list.filter(specialite__in=["Pharmacie", "Grossiste", "SuperGros"])
        )

        details = (
            Medecin.objects.filter(id__in=medecins_list.values("id"))
            .values("specialite")
            .annotate(dcount=Count("specialite"))
        )

        # other_details=[{} for ]
        # other_details=f" <b>({medecin_nbr})</b> medecins "
        # other_details+=" ".join([f'<b>({detail["dcount"]})</b> {detail["specialite"]}' for detail in details])

        other_details = [
            {"specialite": "medecin", "nbr_visites": medecin_nbr},
            *[
                {
                    "specialite": detail["specialite"],
                    "nbr_visites": detail["dcount"],
                }
                for detail in details
            ],
        ]

        response = {
            "pages": medecins.paginator.num_pages,
            "result": json.data,
            "details": other_details,
            "length": len(medecins_list),
        }
        try:
            response["previous"] = medecins.previous_page_number()
        except:
            pass
        try:
            response["next"] = medecins.next_page_number()
        except:
            pass
        return response

    def get_object(self, pk):
        print("--- testing 1")
        try:
            return Medecin.objects.get(pk=pk)
        except Medecin.DoesNotExist:
            raise Http404

    def get_search(self, request):
        if request.GET.get("user"):
            filters = {"users__id": request.GET.get("user")}
        else:
            if (
                request.user.userprofile.rolee == "CountryManager"
                or request.user.is_superuser
            ):
                filters = {}
            else:
                filters = {
                    "users__in": [
                        *request.user.userprofile.usersunder.all(),
                        request.user,
                    ]
                }
        q = Q()
        if request.GET.get("keyword") != "" and request.GET.get("keyword"):
            # q |= Q(nom__icontains=request.GET.get("keyword"))
            # q |= Q(commune__nom__icontains=request.GET.get("keyword"))
            # q |= Q(specialite__icontains=request.GET.get("keyword"))
            # q |= Q(commune__wilaya__nom__icontains=request.GET.get("keyword"))
            filters["nom__icontains"] = request.GET.get("keyword")
        if request.GET.get("medecin") != "" and request.GET.get("medecin"):
            filters["nom__icontains"] = request.GET.get("medecin")
        medecins_list = Medecin.objects.filter(**filters)
        # if not q else Medecin.objects.filter(**filters).filter(q)
        if request.GET.get("visited") != "" and request.GET.get("visited") != "all":
            today = datetime.date.today()
            visited = medecins_list.filter(
                visite__rapport__added__month=today.month,
                visite__rapport__added__year=today.year,
            )
            if request.GET.get("visited") == "unvisited":
                medecins_list = medecins_list.exclude(id__in=visited.values("id"))
            if request.GET.get("visited") == "visited":
                medecins_list = visited
        if request.GET.get("rapport"):
            medecins_list = medecins_list.exclude(
                visite__rapport__id=request.GET.get("rapport")
            )
        if request.GET.get("commercial") == "1":
            medecins_list = medecins_list.exclude(specialite__in=MEDICAL)
        if request.GET.get("spec") != "" and request.GET.get("spec"):
            medecins_list = medecins_list.filter(specialite=request.GET.get("spec"))
        if request.GET.get("plan_id"):
            medecins_list = medecins_list.exclude(plan__id=request.GET.get("plan_id"))
        if request.GET.get("commune"):
            medecins_list = medecins_list.filter(commune__id=request.GET.get("commune"))
        medecins_list = medecins_list.distinct()
        print(
            "searching from "
            + str(request.user)
            + "................................................."
        )
        if request.GET.get("search") == "1":
            serializer = MedecinSerializer(medecins_list, many=True)
            return Response(serializer.data, status=200)
        else:
            paginator = Paginator(medecins_list, 20)
            page = (
                request.GET.get("page")
                if request.GET.get("page") and request.GET.get("page") != "0"
                else None
            )
            medecins = paginator.get_page(page)
            medecins_json = MedecinSerializer(medecins, many=True)
            return Response(
                self.pagination_response(medecins, medecins_json, medecins_list),
                status=200,
            )

    def get_all_by_plan(self, request):
        print("Getting all by plan *************")

        # Initialisation des filtres
        filters = Q()

        # Gestion des utilisateurs
        if request.user.is_superuser:
            medecins_list = Medecin.objects.all()
        else:
            role = request.user.userprofile.rolee
            if role == "CountryManager":
                filters = Q(
                    commune__wilaya__pays=request.user.userprofile.commune.wilaya.pays
                )
            else:
                user_id = request.GET.get("user")
                if user_id:
                    filters = Q(users__id=user_id)
                else:
                    filters = Q(
                        users__in=[
                            *request.user.userprofile.usersunder.all(),
                            request.user,
                        ]
                    )

            medecins_list = Medecin.objects.filter(filters)

        # Application d'un filtre supplémentaire si une commune est spécifiée
        commune_id = request.GET.get("commune")
        if commune_id:
            medecins_list = medecins_list.filter(commune__id=commune_id)

        # Distinction et ordonnancement
        medecins_list = medecins_list.distinct().order_by("specialite_fk__ismedical")

        print("Here IT IS")
        return Response(
            MedecinPlanSerializer(medecins_list, many=True).data, status=200
        )

    def get(self, request, id="", format=None):
        if request.GET.get("search") == "1":
            return self.get_search(request)

        if request.GET.get("all_by_plan") == "1":
            return self.get_all_by_plan(request)

        medecins_list = get_medecins(request)

        paginator = Paginator(medecins_list, 20)

        page = (
            request.GET.get("page")
            if request.GET.get("page") and request.GET.get("page") != "0"
            else None
        )
        medecins = paginator.get_page(page)
        medecins_json = MedecinSerializer(medecins, many=True)

        print("\n\n\nGETTING\n")
        return Response(
            self.pagination_response(medecins, medecins_json, medecins_list), status=200
        )

    def post(self, request, id="", format=None):
        print(str(request.user) + " is trying to add new medecin" + str(request.data))
        if id == "":  # CREATING NEW MEDECIN
            serializer = MedecinSerializer(data=request.data)
            if serializer.is_valid():
                if (
                    request.data.get("specialite") in MEDICAL
                    and request.user.userprofile.can_add_medecin
                ) or (
                    request.data.get("specialite") in COMMERCIAL
                    and request.user.userprofile.can_add_client
                ):
                    medecin = serializer.save()
                    # for usr in UserProfile.objects.filter(usersunder=request.user):
                    #     medecin.users.add(usr.user)

                    medecin.users.add(request.user)
                    save_redis = SaveRedisThread("updating_redis", request.user)
                    save_redis.start()

                    return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            medecin = self.get_object(id)
            if medecin.user_can_update(request.user):
                serializer = MedecinSerializer(medecin, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    save_redis = SaveRedisThread("updating_redis", request.user)
                    save_redis.start()
                    print("************ saved successfully ")
                    return Response(serializer.data)
                print("************ unsaved", serializer.errors)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                print("forbidden")
                return Response({"message": "forbbiden"}, status=403)


# class NewMedecinList(APIView):

#     authentication_classes = [TokenAuthentication]
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         redis = RedisConnect()

#         if request.GET.get("commercial") == "1":
#             data = redis.get_key(f"{request.user.username}_commercials")
#         elif request.GET.get("spec") != "" and request.GET.get("spec"):
#             data = redis.get_key(f"{request.user.username}_{request.GET.get('spec').lower()}")
#         else:
#             data = redis.get_key(f"{request.user.username}_medecins")

#         if data is not None:
#             return Response(json.loads(data), status=200)
#         else:
#             return Response({"error": "Data not found"}, status=404)


from rest_framework.response import Response


class NewMedecinList(APIView):
    #authentication_classes = []
    #permission_classes = [AllowAny]
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        redis = RedisConnect()
        
        # if request.user.username in ["aminadz"]:
        #     medecins_queryset = Medecin.objects.filter(users=request.user)
        #     data = medecins_queryset.values()
        #     if data is not None:
        #         return Response(data, status=200)
        #     else:
        #         return Response({"error": "Data not found"}, status=404)

        if request.GET.get("commercial") == "1":
            print("1")
            data = redis.get_key(f"{request.user.username}_commercials")
            # dt = redis.get_key(f"supergros")
            # data.append(dt)
        elif request.GET.get("spec") != "" and request.GET.get("spec"):
            print("2")
            a = request.GET.get('spec')
            print("aaaaaa")
            print(request.GET.get('spec'))
            #a.append("supergros")
            data = redis.get_key(
                f"{request.user.username}_{a.lower()}"
            )
            unique_data = {}
            if request.GET.get('spec') =="Grossiste":
                print("oui sont des grossistes")
                print("////////////")
                #print(len(data))
                zone_user = sectors = request.user.userprofile.sectors.all()
                print(zone_user)
                usrnm = ["AmelDZ", "ASMADZ", "bouchachiadz", "chirazdz", "fayzadz", "hindDZ", "itedaldz", "lounisdz", "makourdz", "NACIMADZ", "nesrinedz", "syrianadz", "Zahradz", "ChahrazedDZ"]
                qs1=0
                if request.user.username in usrnm:
                    wly_nom = ["Ain Defla", "Medea", "Blida", "Tipaza", "Alger", "Boumerdes", "Bouira", "Tizi Ouzou"]
                    qs1 = Medecin.objects.filter(specialite="Grossiste", wilaya__nom__in=wly_nom)
                else:
                    qs1 = Medecin.objects.filter(specialite="Grossiste", wilaya__in=zone_user)
                qs2 = Medecin.objects.filter(specialite="Grossiste", users=request.user)
                all_grossiste_in_same_zone = qs1.union(qs2)
                print(all_grossiste_in_same_zone)
                if data is not None:
                    data = json.loads(data.decode("utf-8"))
                for item_in_all_grossiste in all_grossiste_in_same_zone:
                    s1 = f"{item_in_all_grossiste.id} | {item_in_all_grossiste.nom} | {item_in_all_grossiste.commune}"
                    dt = {
                        "id": item_in_all_grossiste.id,
                        "nom": s1,
                        "specialite":item_in_all_grossiste.specialite,
                        "last_visite": None
                    }
                    unique_data[item_in_all_grossiste.id] = dt
                    print(dt)
                    #data.append(dt)
                data = list(unique_data.values())
                data = json.dumps(data, ensure_ascii=False)
                print(len(data))

            # dt = redis.get_key(f"supergros")

            #data = json.dumps(data2).encode()
        else:
            print("3")
            data = redis.get_key(f"{request.user.username}_medecins")

        if data:
            return Response(json.loads(data), status=200)
        else:
            print("error data not found le thread va commencer")
            thread = SaveRedisThread("RedisSaveThread", request.user)
            thread.start()
            return Response({"error": "Data not found"}, status=404)
