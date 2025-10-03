from rapports.models import Rapport, Visite
from .serializers import RapportSerializer
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from django.db.models import Count
from rapports.get_rapports import rapport_list
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from django.core.paginator import Paginator
from medecins.models import Medecin


# class RapportAPI(APIView):
#     authentication_classes = [SessionAuthentication, BasicAuthentication]
#     permission_classes = [IsAuthenticated]

#     def pagination_response(
#         self, rapports, serializer, result_length, visites, medecins, other
#     ):
#         response = {
#             "pages": rapports.paginator.num_pages,
#             "result": serializer.data,
#             "length": result_length,
#             "visites": visites,
#             "medecins": medecins,
#             "other": other,
#         }
#         try:
#             response["previous"] = rapports.previous_page_number()
#         except:
#             pass
#         try:
#             response["next"] = rapports.next_page_number()
#         except:
#             pass
#         return response

#     def get(self, request, format=None):
#         print(str(request))
#         commercial_input = request.GET.get("commercial", "").strip()

#         if commercial_input:
#             print("1")
#             page = request.GET.get("page")
#             rapports_list = rapport_list(request)
#             print("---> " + str(rapports_list))

#             # Retrieve visits and doctors in one go
#             visites = Visite.objects.filter(rapport__in=rapports_list)
#             print("1")

#             # Count medecins and their specializations
#             medecin_counts = (
#                 Medecin.objects.filter(visite__in=visites)
#                 .values("specialite")
#                 .annotate(dcount=Count("id"))
#             )

#             # Separate medical and commercial counts
#             medecin_nbr = sum(
#                 count["dcount"]
#                 for count in medecin_counts
#                 if count["specialite"] not in ["Pharmacie", "Grossiste", "SuperGros"]
#             )
#             print("1")
#             commerciale_nbr = sum(
#                 count["dcount"]
#                 for count in medecin_counts
#                 if count["specialite"] in ["Pharmacie", "Grossiste", "SuperGros"]
#             )

#             # Prepare details strings
#             other_details = f" ({medecin_nbr}) Medical ({commerciale_nbr}) Commercial "

#             # Add specialty details
#             specialty_details = [
#                 f'({count["dcount"]}) {count["specialite"]}' for count in medecin_counts
#             ]
#             other_details += " ".join(specialty_details)
#             print("4")

#             # Product-specific visits
#             produit_id = request.GET.get("produit")
#             if produit_id:
#                 prd_visites = visites.filter(produits__id=produit_id)
#                 prd_medecins = Medecin.objects.filter(
#                     id__in=prd_visites.values("medecin__id")
#                 )
#                 other_details += f" dont ({len(prd_visites)} visites et {len(prd_medecins)} medecins) contenant le produit"

#             # Pagination
#             paginator = Paginator(rapports_list, 10)
#             rapports = paginator.get_page(page)
#             print("5")

#             serializer = RapportSerializer(rapports, many=True)

#             return Response(
#                 self.pagination_response(
#                     rapports,
#                     serializer,
#                     len(rapports_list),
#                     len(visites),
#                     len(medecin_counts),  # Using medecin_counts for accurate count
#                     other_details,
#                 ),
#                 status=200,
#             )
#         else:
#             return Response(status=400)


class RapportAPI(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        print(str(request))
        commercial_input = request.GET.get("commercial", "").strip()

        if commercial_input:
            print("1")
            rapports_list = rapport_list(request)
            print("---> " + str(rapports_list))

            # Retrieve visits and doctors in one go
            visites = Visite.objects.filter(rapport__in=rapports_list)
            print("1")

            # Count medecins and their specializations
            medecin_counts = (
                Medecin.objects.filter(visite__in=visites)
                .values("specialite")
                .annotate(dcount=Count("id"))
            )

            # Separate medical and commercial counts
            medecin_nbr = sum(
                count["dcount"]
                for count in medecin_counts
                if count["specialite"] not in ["Pharmacie", "Grossiste", "SuperGros"]
            )
            print("1")
            commerciale_nbr = sum(
                count["dcount"]
                for count in medecin_counts
                if count["specialite"] in ["Pharmacie", "Grossiste", "SuperGros"]
            )

            # Prepare details strings
            other_details = f" ({medecin_nbr}) Medical ({commerciale_nbr}) Commercial "

            # Add specialty details
            specialty_details = [
                f'({count["dcount"]}) {count["specialite"]}' for count in medecin_counts
            ]
            other_details += " ".join(specialty_details)
            print("4")

            # Product-specific visits
            produit_id = request.GET.get("produit")
            if produit_id:
                prd_visites = visites.filter(produits__id=produit_id)
                prd_medecins = Medecin.objects.filter(
                    id__in=prd_visites.values("medecin__id")
                )
                other_details += f" dont ({len(prd_visites)} visites et {len(prd_medecins)} medecins) contenant le produit"

            print("5")

            serializer = RapportSerializer(rapports_list, many=True)

            return Response(
                {
                    "result": serializer.data,
                    "length": len(rapports_list),
                    "visites": len(visites),
                    "medecins": len(medecin_counts),
                    "other": other_details,
                },
                status=200,
            )
        else:
            return Response(status=400)

