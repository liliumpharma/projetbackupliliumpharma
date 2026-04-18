from rapports.models import Rapport, Visite
from plans.models import PlanTask
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
from accounts.models import UserSectorDetail


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
        family = request.GET.get("family", "").strip()

        if commercial_input:
            print("1")
            rapports_list = rapport_list(request)
            print("---> " + str(rapports_list))

            # Retrieve visits and doctors in one go (single queryset, reuse it)
            visites = Visite.objects.filter(rapport__in=rapports_list)
            visite_ids = visites.values_list("id", flat=True)
            print("1")

            # Count medecins and their specializations
            medecin_counts = (
                Medecin.objects.filter(visite__id__in=visite_ids)
                .values("specialite")
                .annotate(dcount=Count("id"))
            )
            print("je suis dans api/api/py RapportAPI")
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
                prd_visites_count = visites.filter(produits__id=produit_id).count()
                prd_medecins_count = Medecin.objects.filter(
                    id__in=visites.filter(produits__id=produit_id).values("medecin__id")
                ).count()

                other_details += f" dont ({prd_visites_count} visites et {prd_medecins_count} medecins) contenant le produit"
            print("5")

            # Build sector map once for all users — avoids N queries in get_sector_category
            user_ids = list(rapports_list.values_list('user_id', flat=True).distinct())
            sector_details = (
                UserSectorDetail.objects
                .filter(user_profile__user_id__in=user_ids)
                .prefetch_related('wilayas')
                .select_related('user_profile')
            )
            sector_map = {}
            for sd in sector_details:
                uid = sd.user_profile.user_id
                wilaya_ids = set(sd.wilayas.values_list('id', flat=True))
                sector_map.setdefault(uid, []).append((wilaya_ids, sd.category))

            # Prefetch visites, comments, and their users to kill N+1 queries
            # Prefetch visites with their wilaya chain so get_sector_category uses the cache
            rapports_list = rapports_list.prefetch_related(
                'visite_set__medecin__commune__wilaya',
                'comment_set__user'
            )

            # --- NEW: Filter by Sector before serializing ---
            sector_filter = request.GET.get("sector", "").strip()
            
            if sector_filter:
                filtered_rapports = []
                for rapport in rapports_list:
                    # Extract wilaya IDs for this specific rapport using the prefetched cache
                    wilaya_ids = set(v.medecin.commune.wilaya_id for v in rapport.visite_set.all())
                    
                    # Determine the category using the same logic as the serializer
                    categories = set()
                    for sector_wilaya_ids, category in sector_map.get(rapport.user_id, []):
                        if sector_wilaya_ids & wilaya_ids:
                            categories.add(category)
                    
                    # Apply hierarchy logic
                    final_category = None
                    if 'DEP' in categories:
                        final_category = 'DEP'
                    elif 'SEMI' in categories:
                        final_category = 'SEMI'
                    elif 'IN' in categories:
                        final_category = 'IN'

                    # Keep it if it matches the filter
                    if final_category == sector_filter:
                        filtered_rapports.append(rapport)
                
                rapports_list = filtered_rapports
            # --- END NEW FILTER ---

            # --- END NEW FILTER ---

            # --- NEW: Pre-fetch tasks to kill N+1 queries ---
            user_ids_filtered = list(set(r.user_id for r in rapports_list))
            dates_filtered = list(set(r.added for r in rapports_list))
            
            tasks = PlanTask.objects.filter(
                plan__user_id__in=user_ids_filtered, 
                plan__day__in=dates_filtered
            ).select_related('plan')
            
            task_map = {}
            for task in tasks:
                key = (task.plan.user_id, task.plan.day)
                task_map.setdefault(key, []).append({
                    "id": task.id,
                    "task": task.task,
                    "completed": task.completed
                })
            # --- END TASK PRE-FETCH ---

            # Add task_map to the context
            serializer = RapportSerializer(rapports_list, many=True, context={
                'sector_map': sector_map, 
                'task_map': task_map, 
                'request': request
            })
            
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

