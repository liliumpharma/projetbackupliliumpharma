from functools import partial

from django.db import IntegrityError
from .models import *
from .serializers import *
from django.db.models import Q
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.authtoken.models import Token
from regions.models import Commune
from medecins.models import Medecin
import datetime
from rapports.api.serializers import RapportSerializer
from rapports.models import Rapport
from django.contrib.auth.models import User
from leaves.models import Occasion


# class PlanAPI(APIView):
#     authentication_classes = [TokenAuthentication]
#     permission_classes = [IsAuthenticated]

#     def get(self,request):

#         if request.user.userprofile.rolee not in ["Superviseur","CountryManager"] and request.user.is_superuser!=True and request.user.username not in ["ibtissemdz","liliumdz"]:
#             plans=Plan.objects.filter(user=request.user)
#         else:
#             usernames=request.GET.get("user").split(",") if request.GET.get("user") else [request.user]

#             plans=Plan.objects.filter(user__username__in=usernames)
#         #     if request.user.is_superuser==True:
#         #         plans=Plan.objects.all()
#         #     else:
#         #         if request.user.userprofile.rolee=="Superviseur":
#         #             q=Q(user__in=request.user.userprofile.usersunder.all())
#         #         elif request.user.userprofile.rolee=="CountryManager":
#         #             q=Q(user__userprofile__commune__wilaya__pays=request.user.userprofile.commune.wilaya.pays)

#         #         plans = Plan.objects.filter(q).order_by('-added')

#         filters={  }

#         if request.GET.get("min_date"):
#             filters["day__gte"]=request.GET.get("min_date")

#         if request.GET.get("max_date"):
#             filters["day__lte"]=request.GET.get("max_date")

#         print("*********************",filters)
#         plans=plans.filter(**filters)

#         serializer=PlanSerializer(plans, many=True, context={"user":request.user})
#         return Response(serializer.data,status=status.HTTP_200_OK)

#     def post(self,request):
#         plan_id=request.data.get("plan_id")
#         commune_id=request.data.get("commune_id")
#         client_id=request.data.get("client_id")
#         task=request.data.get("task")

#         # print(task)

#         if plan_id:
#             plan=Plan.objects.get(id=plan_id)
#             if commune_id:
#                 plan.communes.add(Commune.objects.get(id=commune_id))

#                 if commune_id==2370:
#                     plan.valid_commune = True
#                     plan.commune_validation_date = datetime.datetime.today()
#                     plan.valid_clients = True
#                     plan.client_validation_date = datetime.datetime.today()
#                     plan.save()

#             if  client_id:
#                 plan.clients.add(Medecin.objects.get(id=client_id))
#             if task:
#                 PlanTask.objects.create(plan=plan, task=task["task"])

#         return Response(PlanSerializer(Plan.objects.get(id=plan_id),many=False,context={"user":request.user}).data,status=200)

#     def delete(self,request):
#         plan_id=request.data.get("plan_id")
#         commune_id=request.data.get("commune_id")
#         client_id=request.data.get("client_id")
#         task_id=request.data.get("task_id")
#         if plan_id:
#             plan=Plan.objects.get(id=plan_id)
#             print("plan found *******",client_id)
#             if commune_id:
#                 plan.communes.remove(Commune.objects.get(id=commune_id))
#                 print("commune deleted  *******")
#             if  client_id:
#                 plan.clients.remove(Medecin.objects.get(id=client_id))
#                 print("client deleted  *******")

#             if task_id:
#                 print("************ deleting task ")
#                 PlanTask.objects.get(id=task_id).delete()

#             return Response(PlanSerializer(Plan.objects.get(id=plan_id),many=False,context={"user":request.user}).data,status=200)
#         else:
#             return Response({"response":"Plan not found"},status=status.HTTP_400_BAD_REQUEST)


# class PlanCommentAPI(APIView):
#     authentication_classes = [TokenAuthentication]
#     permission_classes = [IsAuthenticated]

#     def post(self,request,format=None):
#         serializer=PlanCommentSerializer(data=request.data,instance=PlanComment(user=request.user),partial=True)
#         if serializer.is_valid():
#             comment=serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class PlanTasksPermuteAPI(APIView):
#     authentication_classes = [TokenAuthentication]
#     permission_classes = [IsAuthenticated]

#     # Permute Tasks
#     def post(self,request,format=None):
#         tasks = PlanTask.objects.filter(id__in=request.data.get('tasks'))

#         # Check if Tasks Belongs to The User
#         if tasks.first().plan.user == request.user and tasks.last().plan.user == request.user:
#             if tasks.count() == 2:
#                 tasks.first().permute(tasks.last())

#                 # Getting Plan
#                 plan = tasks.first().plan
#                 return Response(PlanSerializer(plan,many=False, context={"user":request.user}).data,status=200)
#                 # return HttpResponseRedirect(reverse('PlanAPI'))

#             return Response(status=status.HTTP_400_BAD_REQUEST)

#         # User doesn't have access
#         return Response(status=status.HTTP_403_FORBIDDEN)

# # Validation

# class PlanValidateAPI(APIView):
#     authentication_classes = [TokenAuthentication]
#     permission_classes = [IsAuthenticated]

#     def get(self,request):
#         plan_id=request.GET.get("plan_id")
#         plan_ids=request.GET.get("plan_ids")
#         username=request.GET.get("user")
#         communes=request.GET.get("communes")
#         clients=request.GET.get("clients")
#         tasks=request.GET.get("tasks")

#         if plan_id:
#             plan = Plan.objects.get(id=plan_id)
#             superior = User.objects.filter(userprofile__usersunder=plan.user)
#             if request.user in superior   or request.user.is_superuser or request.user.userprofile.rolee=="CountryManager":
#                 if communes:
#                     plan.valid_commune = True
#                     plan.commune_validation_date = datetime.datetime.today()
#                     plan.save(update_fields=['valid_commune', 'commune_validation_date'])
#                 if clients:
#                     plan.valid_clients = True
#                     plan.client_validation_date = datetime.datetime.today()
#                     plan.save(update_fields=['valid_clients', 'client_validation_date'])
#                 if tasks:
#                     plan.valid_tasks = True
#                     plan.tasks_validation_date = datetime.datetime.today()
#                     plan.save(update_fields=['valid_tasks', 'tasks_validation_date'])
#                 return Response(PlanSerializer(plan,many=False, context={"user":request.user}).data,status=status.HTTP_200_OK)
#         else:
#             if plan_ids:
#                 plans=Plan.objects.filter(id__in=plan_ids.split(",")).update(valid_commune=True)
#                 print("*******",plans)
#                 return Response(PlanSerializer(Plan.objects.filter(id__in=plan_ids.split(",")),many=True, context={"user":request.user}).data,status=200)

#         # User not Authorized
#         return Response(status=status.HTTP_403_FORBIDDEN)


# def PlanPDF(request):


#     usernames=request.GET.get("user") if request.GET.get("user") else request.user.username
#     today=datetime.datetime.today()
#     min_date=request.GET.get("min_date")
#     max_date=request.GET.get("max_date")

#     print("max date",max_date)
#     print("min date",min_date)

#     # print(today.strftime("%A"))
#     all_plans=[]
#     for username in usernames.split(","):
#         if request.user.is_superuser or request.user.userprofile.rolee=="Superviseur" or request.user.userprofile.rolee=="CountryManager":
#             plans=Plan.objects.filter(user__username=username,day__gte=min_date,day__lte=max_date)
#         else:
#             plans=Plan.objects.filter(user=request.user,day__gte=min_date,day__lte=max_date)

#         plans=[p for p in  plans if not p.free_day]
#         plans=[plans[i:i+5] for i in range(0, len(plans), 5)]

#         all_plans.append(plans)

#     # print(plans,"********************************************")
#     return render(request,"plans/pdf.html",{
#                 "all_plans":all_plans ,
#                 "user":username,
#                 "periode":today
#             })


# def SinglePlanPDF(request,id):
#     plan=Plan.objects.get(id=id)

#     return render(request,"plans/single_pdf.html",{"plan":plan})

# def MsMonthlyPlanning(request):

#     if request.user.is_authenticated:
#         token = Token.objects.filter(user=request.user)

#         if token.exists():
#             token = token.first().key
#         else:
#             Token.objects.create(user=request.user)
#             token = Token.objects.filter(user=request.user)
#             token = token.first().key

#     return render(request,"micro_frontends/monthly_planning/index.html",{
#                 "token":token if request.user.is_authenticated else ""

#             })


# class PlanTasksAPI(APIView):
#     authentication_classes = [TokenAuthentication]
#     permission_classes = [IsAuthenticated]

#     def get(self,request):
#         task_id=request.GET.get("task")
#         task=PlanTask.objects.get(id=task_id)
#         task.completed= not task.completed
#         task.save()
#         task=PlanTask.objects.get(id=task_id)
#         print(task)
#         return Response(
#             {
#                 "id": task.id,
#                 "task":task.task,
#                 "order":task.order,
#                 "completed":task.completed,
#             }
#         ,status=200)


#     def post(self,request):
#         task=request.data.get("task")
#         added=request.data.get("added")
#         plan=Plan.objects.get(day=added,user=request.user)
#         order=len(PlanTask.objects.filter(plan=plan))+1
#         p_task=PlanTask(plan=plan,task=task,order=order)
#         p_task.save()
#         return Response(
#             RapportSerializer(Rapport.objects.get(added=added,user=request.user), many=False).data,
#             status=200)


from functools import partial
from .models import *
from .serializers import *
from django.db.models import Q
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.authtoken.models import Token
from regions.models import Commune
from medecins.models import Medecin
from datetime import datetime
from rapports.api.serializers import RapportSerializer
from rapports.models import Rapport
from notifications.models import Notification
import json
from django.contrib.auth.models import User
from django.contrib import messages


# class PlanAPI(APIView):
#     authentication_classes = [TokenAuthentication]
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         user = request.user
#         selected = request.GET.get("user")
#         min_date = request.GET.get("max_date")
#         if (
#             request.user.userprofile.rolee
#             not in ["Superviseur", "CountryManager", "Superviseur_regional"]
#             and not request.user.is_superuser
#             and request.user.username not in ["ibtissemdz", "liliumdz"]
#         ):
#             plans = Plan.objects.filter(user=request.user)
#         else:
#             if selected == "tous":
#                 response = []
#                 if request.user.userprofile.speciality_rolee == "Superviseur_national":
#                     users_under = request.user.userprofile.usersunder.all()
#                     response = [u.username for u in users_under]
#                     plans = Plan.objects.filter(
#                         Q(user=request.user) | Q(user__username__in=response)
#                     )

#                 elif (
#                     request.user.userprofile.speciality_rolee in ["CountryManager"]
#                     or request.user.is_superuser
#                 ):
#                     users_under = User.objects.filter(
#                         userprofile__is_human=True
#                     ).exclude(userprofile__speciality_rolee="Office")
#                     response = [u.username for u in users_under]
#                     plans = Plan.objects.filter(
#                         Q(user=request.user) | Q(user__username__in=response)
#                     )
#             else:
#                 usernames = (
#                     request.GET.get("user").split(",")
#                     if request.GET.get("user")
#                     else [request.user.username]
#                 )
#                 plans = Plan.objects.filter(user__username__in=usernames)

#         #     if request.user.is_superuser==True:
#         #         plans=Plan.objects.all()
#         #     else:
#         #         if request.user.userprofile.rolee=="Superviseur":
#         #             q=Q(user__in=request.user.userprofile.usersunder.all())
#         #         elif request.user.userprofile.rolee=="CountryManager":
#         #             q=Q(user__userprofile__commune__wilaya__pays=request.user.userprofile.commune.wilaya.pays)

#         #         plans = Plan.objects.filter(q).order_by('-added')

#         filters = {}

#         if request.GET.get("min_date"):
#             filters["day__gte"] = request.GET.get("min_date")

#         if request.GET.get("max_date"):
#             filters["day__lte"] = request.GET.get("max_date")

#         if request.GET.get("with_communes") == "0":
#             filters["communes__isnull"] = True

#         if request.GET.get("with_communes") == "1":
#             filters["communes__isnull"] = False

#         if request.GET.get("with_clients") == "0":
#             filters["clients__isnull"] = True

#         if request.GET.get("with_clients") == "1":
#             filters["clients__isnull"] = False

#         # if request.GET.get("not_valid") == "1":
#         #     filters["valid_commune","valid_clients","valid_tasks"] = False
#         # if request.GET.get("not_valid") == "1":
#         #     filters["valid_clients"] = False
#         if request.GET.get("not_valid") == "1":
#             filters["valid_tasks"] = False

#         if request.GET.get("not_valid") == "1":
#             filters["valid_clients"] = False

#         if request.GET.get("not_valid") == "1":
#             filters["valid_commune"] = False

#         if request.GET.get("not_valid") == "1":
#             filters["valid_tasks"] = False

#         if request.GET.get("not_valid") == "1":
#             filters["valid_clients"] = False

#         if request.GET.get("not_valid") == "1":
#             filters["valid_commune"] = False


#         plans = plans.filter(**filters)
#         serializer = PlanSerializer(
#             plans, many=True, context={"user": request.user, "date_min": min_date}
#         )
#         return Response(serializer.data, status=status.HTTP_200_OK)


class PlanAPI(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        selected = request.GET.get("user", user.username)
        min_date = request.GET.get("min_date")
        max_date = request.GET.get("max_date")

        # Determine user plans based on role and access
        if (
            user.userprofile.rolee
            not in ["Superviseur", "CountryManager", "Superviseur_regional"]
            and not user.is_superuser
            and user.username not in ["ibtissemdz", "liliumdz"]
        ):
            plans = Plan.objects.filter(user=user)
        else:
            if selected == "tous":
                if user.userprofile.speciality_rolee == "Superviseur_national":
                    users_under = user.userprofile.usersunder.all()
                    plans = Plan.objects.filter(Q(user=user) | Q(user__in=users_under))
                elif (
                    user.userprofile.speciality_rolee == "CountryManager"
                    or user.is_superuser
                ):
                    users_under = User.objects.filter(
                        userprofile__is_human=True
                    ).exclude(userprofile__speciality_rolee="Office")
                    plans = Plan.objects.filter(Q(user=user) | Q(user__in=users_under))
            else:
                usernames = selected.split(",") if selected else [user.username]
                plans = Plan.objects.filter(user__username__in=usernames)

        # Filters for the plan query
        filters = {}

        if min_date:
            filters["day__gte"] = min_date
        if max_date:
            filters["day__lte"] = max_date

        if request.GET.get("with_communes") == "0":
            filters["communes__isnull"] = True
        elif request.GET.get("with_communes") == "1":
            filters["communes__isnull"] = False

        if request.GET.get("with_clients") == "0":
            filters["clients__isnull"] = True
        elif request.GET.get("with_clients") == "1":
            filters["clients__isnull"] = False

        if request.GET.get("not_valid") == "1":
            filters.update(
                {"valid_tasks": False, "valid_clients": False, "valid_commune": False}
            )

        # Apply filters to the plans
        plans = plans.filter(**filters)

        # Serialize and return the filtered plans
        serializer = PlanSerializer(
            plans, many=True, context={"user": user, "date_min": min_date}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    # def get(self,request):

    #     if request.user.userprofile.rolee not in ["Superviseur","CountryManager","Superviseur_regional"] and request.user.is_superuser!=True and request.user.username not in ["ibtissemdz","liliumdz"]:
    #         plans=Plan.objects.filter(user=request.user)
    #     else:
    #         usernames=request.GET.get("user").split(",") if request.GET.get("user") else [request.user]
    #         print(usernames)
    #         plans=Plan.objects.filter(user__username__in=usernames)
    #     #     if request.user.is_superuser==True:
    #     #         plans=Plan.objects.all()
    #     #     else:
    #     #         if request.user.userprofile.rolee=="Superviseur":
    #     #             q=Q(user__in=request.user.userprofile.usersunder.all())
    #     #         elif request.user.userprofile.rolee=="CountryManager":
    #     #             q=Q(user__userprofile__commune__wilaya__pays=request.user.userprofile.commune.wilaya.pays)

    #     #         plans = Plan.objects.filter(q).order_by('-added')

    #     filters={  }

    #     if request.GET.get("min_date"):
    #         filters["day__gte"]=request.GET.get("min_date")

    #     if request.GET.get("max_date"):
    #         filters["day__lte"]=request.GET.get("max_date")

    #     if request.GET.get("with_communes")=="0":
    #         filters["communes__isnull"]=True

    #     if request.GET.get("with_communes")=="1":
    #         filters["communes__isnull"]=False

    #     if request.GET.get("with_clients")=="0":
    #         filters["clients__isnull"]=True

    #     if request.GET.get("with_clients")=="1":
    #         filters["clients__isnull"]=False

    #     if request.GET.get("not_valid") == "1":
    #         filters["valid_commune"] = False
    #         filters["valid_clients"] = False

    #     print("*********************",filters)
    #     plans=plans.filter(**filters)
    #     serializer=PlanSerializer(plans, many=True, context={"user":request.user})
    #     return Response(serializer.data,status=status.HTTP_200_OK)

    # def post(self, request):
    #     plan_id = request.data.get("plan_id")
    #     commune_id = request.data.get("commune_id")
    #     client_id = request.data.get("client_id")
    #     tasks = request.data.get("tasks")  # Utiliser 'tasks' comme une liste d'objets
    #     single_tasks = request.data.get("task")  # Utiliser 'task' comme un objet
    #     current_time = datetime.now().time()
    #     today = datetime.now()

    #     print("plan id: " + str(plan_id))
    #     print("commune id: " + str(commune_id))
    #     print("client id: " + str(client_id))
    #     print("tasks: " + str(tasks))
    #     print("single task: " + str(single_tasks))

    #     if plan_id:
    #         plan = Plan.objects.get(id=plan_id)

    #         if request.user.is_superuser:
    #             # Traitement des communes
    #             if commune_id:
    #                 plan.communes.add(Commune.objects.get(id=commune_id))
    #                 if commune_id == 2370:
    #                     plan.valid_commune = True
    #                     plan.commune_validation_date = today
    #                     plan.valid_clients = True
    #                     plan.client_validation_date = today
    #                     plan.save()

    #             # Traitement des clients
    #             if client_id:
    #                 plan.clients.add(Medecin.objects.get(id=client_id))

    #             # Traitement des tâches transférées
    #             if tasks:
    #                 transferred_tasks = []  # Liste pour suivre les tâches transférées

    #                 for task_item in tasks:
    #                     if task_item.get("transféré") == True:
    #                         task_id = task_item.get("id")
    #                         print(f"Traitement de la tâche transférée: {task_id}")

    #                         # Vérification si la tâche a déjà été transférée
    #                         if task_id in transferred_tasks:
    #                             print(f"Tâche avec ID {task_id} déjà transférée.")
    #                             continue  # Passer à la tâche suivante si déjà transférée

    #                         # Gestion des tâches transférées
    #                         to_user = task_item.get("transférer_to")
    #                         to_user_obj = User.objects.filter(username=to_user).first()
    #                         from_plan = Plan.objects.filter(id=plan_id).first()

    #                         if (
    #                             from_plan
    #                         ):  # Vérification de l'existence du plan d'origine
    #                             from_plan_day = from_plan.day
    #                             plan_transferred_user = Plan.objects.filter(
    #                                 user=to_user_obj, day=from_plan_day
    #                             ).first()  # Récupérer le plan de l'utilisateur transféré

    #                             if plan_transferred_user:
    #                                 # Créer la tâche transférée
    #                                 PlanTask.objects.create(
    #                                     plan=plan_transferred_user,
    #                                     task=task_item[
    #                                         "task"
    #                                     ],  # Utiliser 'task' correctement
    #                                 )
    #                                 print("Tâche transférée avec succès.")

    #                                 # Ajouter l'ID de la tâche à la liste des tâches transférées
    #                                 transferred_tasks.append(task_id)
    #                             else:
    #                                 print(
    #                                     "Aucun plan correspondant trouvé pour l'utilisateur transféré."
    #                                 )
    #                         else:
    #                             print("Plan d'origine non trouvé.")

    #             # Traitement des tâches normales
    #             if single_tasks:
    #                 print(f"Création d'une nouvelle tâche: {single_tasks['task']}")
    #                 PlanTask.objects.create(plan=plan, task=single_tasks["task"])

    #                 # Notification pour la tâche ajoutée
    #                 notification = Notification.objects.create(
    #                     title=f"Nouvelle tâche de {request.user.username}",
    #                     description=f"{request.user.username} vient d'ajouter une tâche dans le planning du {str(plan.day)}",
    #                     data={
    #                         "name": "Plans",
    #                         "title": "Ajout de commune",
    #                         "message": f"{request.user.username} vient d'ajouter une tâche dans le planning du {str(plan.day)}",
    #                         "confirm_text": "voir le planning",
    #                         "cancel_text": "plus tard",
    #                         "StackName": "Plans",
    #                         "url": f"https://app.liliumpharma.com/plans/mServices/monthly_planning/?user={plan.user}&date={plan.day}",
    #                         "navigate_to": json.dumps(
    #                             {
    #                                 "screen": "PlansList",
    #                                 "params": {
    #                                     "user": plan.user.username,
    #                                     "date": str(plan.day),
    #                                 },
    #                             }
    #                         ),
    #                     },
    #                 )
    #                 notification.send()

    #         else:
    #             # Traitement pour les utilisateurs non-superusers (logique similaire, adaptée selon les permissions)
    #             if commune_id:
    #                 if plan.day == today.date():
    #                     if current_time.hour >= 11:
    #                         return Response(
    #                             {
    #                                 "message": "Impossible d'ajouter des tâches après 11h du matin."
    #                             },
    #                             status=410,
    #                         )
    #                     else:
    #                         plan.communes.add(Commune.objects.get(id=commune_id))

    #                         if commune_id == 2370:
    #                             plan.valid_commune = True
    #                             plan.commune_validation_date = today
    #                             plan.valid_clients = True
    #                             plan.client_validation_date = today
    #                             plan.save()
    #                 else:
    #                     if plan.day > today.date():
    #                         plan.communes.add(Commune.objects.get(id=commune_id))

    #                         if commune_id == 2370:
    #                             plan.valid_commune = True
    #                             plan.commune_validation_date = today
    #                             plan.valid_clients = True
    #                             plan.client_validation_date = today
    #                             plan.save()

    #             if client_id:
    #                 if plan.day == today.date():
    #                     if current_time.hour >= 11:
    #                         return Response(
    #                             {
    #                                 "message": "Impossible d'ajouter des tâches après 11h du matin."
    #                             },
    #                             status=420,
    #                         )
    #                     else:
    #                         plan.clients.add(Medecin.objects.get(id=client_id))
    #                 else:
    #                     if plan.day > today.date():
    #                         plan.clients.add(Medecin.objects.get(id=client_id))

    #             # Traitement des tâches pour les utilisateurs non-superusers
    #             if tasks:
    #                 for task_item in tasks:
    #                     if task_item.get("transféré") == True:
    #                         # Ignorer le traitement des tâches transférées ici pour les utilisateurs normaux
    #                         continue

    #             if single_tasks:
    #                 if plan.day == today.date():
    #                     if current_time.hour >= 11:
    #                         return Response(
    #                             {
    #                                 "message": "Impossible d'ajouter des tâches après 11h du matin."
    #                             },
    #                             status=430,
    #                         )
    #                     else:
    #                         PlanTask.objects.create(
    #                             plan=plan, task=single_tasks["task"]
    #                         )

    #                         # Notification pour la tâche ajoutée
    #                         notification = Notification.objects.create(
    #                             title="Nouvelle tâche " + request.user.username,
    #                             description=f"{request.user.username} vient d'ajouter une tâche dans le planning du {str(plan.day)}",
    #                             data={
    #                                 "name": "Plans",
    #                                 "title": "Ajout de commune",
    #                                 "message": f"{request.user.username} vient d'ajouter une tâche dans le planning du {str(plan.day)}",
    #                                 "confirm_text": "voir le planning",
    #                                 "cancel_text": "plus tard",
    #                                 "StackName": "Plans",
    #                                 "url": f"https://app.liliumpharma.com/plans/mServices/monthly_planning/?user={plan.user}&date={plan.day}",
    #                                 "navigate_to": json.dumps(
    #                                     {
    #                                         "screen": "PlansList",
    #                                         "params": {
    #                                             "user": plan.user.username,
    #                                             "date": str(plan.day),
    #                                         },
    #                                     }
    #                                 ),
    #                             },
    #                         )
    #                         notification.send()
    #                 else:
    #                     if plan.day > today.date():
    #                         PlanTask.objects.create(
    #                             plan=plan, task=single_tasks["task"]
    #                         )

    #         return Response(
    #             PlanSerializer(
    #                 Plan.objects.get(id=plan_id),
    #                 many=False,
    #                 context={"user": request.user},
    #             ).data,
    #             status=200,
    #         )

    def post(self, request):
        plan_id = request.data.get("plan_id")
        commune_id = request.data.get("commune_id")
        client_id = request.data.get("client_id")
        tasks = request.data.get("tasks")  # Utiliser 'tasks' comme une liste d'objets
        single_tasks = request.data.get("task")  # Utiliser 'task' comme un objet
        current_time = datetime.now().time()
        today = datetime.now()  


        if plan_id:
            plan = Plan.objects.get(id=plan_id)

            if request.user.is_superuser:
                # Traitement des communes
                if commune_id:
                    plan.communes.add(Commune.objects.get(id=commune_id))
                    if commune_id == 2370:
                        plan.valid_commune = True
                        plan.commune_validation_date = today
                        plan.valid_clients = True
                        plan.client_validation_date = today
                        plan.save()
                        print("Commune validée et plan mis à jour.")    

                # Traitement des clients
                if client_id:
                    plan.clients.add(Medecin.objects.get(id=client_id)) 

                # Traitement des tâches transférées
                if tasks:
                    transferred_tasks = []  # Liste pour suivre les tâches transférées  
                    for task_item in tasks:
                        if task_item.get("transferred") == True:
                            task_id = task_item.get("id")

                            # Vérification si la tâche a déjà été transférée
                            if task_id in transferred_tasks:
                                continue  # Passer à la tâche suivante si déjà transférée   

                            # Gestion des tâches transférées
                            to_user = task_item.get("transferred_to")
                            to_user_obj = User.objects.filter(username=to_user).first()
                            from_plan = Plan.objects.filter(id=plan_id).first() 

                            if from_plan:  # Vérification de l'existence du plan d'origine
                                from_plan_day = from_plan.day
                                plan_transferred_user = Plan.objects.filter(
                                    user=to_user_obj, day=from_plan_day
                                ).first()  # Récupérer le plan de l'utilisateur transféré   

                                if plan_transferred_user:
                                    # Créer la tâche transférée avec les nouveaux champs
                                    PlanTask.objects.create(
                                        plan=plan_transferred_user,
                                        task=task_item["task"],
                                        is_transferred=True,
                                        transferred_by=request.user,
                                        transferred_at=timezone.now(),
                                    )
                                    transferred_tasks.append(task_id)   

                                    notification = Notification.objects.create(
                                        title=f"Test",
                                        description=f"Test",
                                        data={
                                            "name": "Orders",
                                            "title": "Bon de commande",
                                            "message": f"Test",
                                            "confirm_text": "voir le bon",
                                            "cancel_text": "plus tard",
                                            "StackName": "Orders",
                                            "navigate_to": json.dumps(
                                                {
                                                    "screen": "List",
                                                    "params": {
                                                        "user": plan.user.username,
                                                    },
                                                },
                                                ensure_ascii=False,
                                            ),
                                        },
                                    )
                                    print("Notification créée.")    

                                    if to_user_obj:
                                        notification.users.set([to_user_obj])
                                        # notification.send()
                                        print("Notification envoyée !")
                                        return Response(status=200)
                                    else:
                                        print("Utilisateur transféré non trouvé.")
                                        return Response(
                                            status=404,
                                            data={"error": "Utilisateur non trouvé"},
                                        )
                                else:
                                    print("Aucun plan correspondant trouvé pour l'utilisateur transféré.")
                            else:
                                print("Plan d'origine non trouvé.") 

                # Traitement des tâches normales
                if single_tasks:
                    print(f"Création d'une nouvelle tâche: {single_tasks['task']}")
                    PlanTask.objects.create(plan=plan, task=single_tasks["task"])   

                    # Notification pour la tâche ajoutée
                    notification = Notification.objects.create(
                        title=f"Nouvelle tâche de {request.user.username}",
                        description=f"{request.user.username} vient d'ajouter une tâche dans le planning du {str(plan.day)}",
                        data={
                            "name": "Plans",
                            "title": "Ajout de commune",
                            "message": f"{request.user.username} vient d'ajouter une tâche dans le planning du {str(plan.day)}",
                            "confirm_text": "voir le planning",
                            "cancel_text": "plus tard",
                            "StackName": "Plans",
                            "url": f"https://app.liliumpharma.com/plans/mServices/monthly_planning/?user={plan.user}&date={plan.day}",
                            "navigate_to": json.dumps(
                                {
                                    "screen": "PlansList",
                                    "params": {
                                        "user": plan.user.username,
                                        "date": str(plan.day),
                                    },
                                }
                            ),
                        },
                    )
                    print("Notification pour la nouvelle tâche créée.")
                    # notification.send()
                    print("Notification envoyée.")  


            else:
                # Traitement pour les utilisateurs non-superusers (logique similaire, adaptée selon les permissions)
                if commune_id:
                    if plan.day == today.date():
                        if current_time.hour >= 20:
                            return Response(
                                {
                                    "message": "Impossible d'ajouter des tâches après 11h du matin."
                                },
                                status=410,
                            )
                        else:
                            plan.communes.add(Commune.objects.get(id=commune_id))

                            if commune_id == 2370:
                                plan.valid_commune = True
                                plan.commune_validation_date = today
                                plan.valid_clients = True
                                plan.client_validation_date = today
                                plan.save()
                    else:
                        if plan.day > today.date():
                            plan.communes.add(Commune.objects.get(id=commune_id))

                            if commune_id == 2370:
                                plan.valid_commune = True
                                plan.commune_validation_date = today
                                plan.valid_clients = True
                                plan.client_validation_date = today
                                plan.save()

                if client_id:
                    if plan.day == today.date():
                        if current_time.hour >= 20:
                            return Response(
                                {
                                    "message": "Impossible d'ajouter des tâches après 11h du matin."
                                },
                                status=420,
                            )
                        else:
                            plan.clients.add(Medecin.objects.get(id=client_id))
                    else:
                        if plan.day > today.date():
                            plan.clients.add(Medecin.objects.get(id=client_id))

                # Traitement des tâches pour les utilisateurs non-superusers
                if tasks:
                    for task_item in tasks:
                        if task_item.get("transféré") == True:
                            # Ignorer le traitement des tâches transférées ici pour les utilisateurs normaux
                            continue

                if single_tasks:
                    if plan.day == today.date():
                        if current_time.hour >= 20:
                            return Response(
                                {
                                    "message": "Impossible d'ajouter des tâches après 11h du matin."
                                },
                                status=430,
                            )
                        else:
                            PlanTask.objects.create(
                                plan=plan, task=single_tasks["task"]
                            )

                            # Notification pour la tâche ajoutée
                            notification = Notification.objects.create(
                                title="Nouvelle tâche " + request.user.username,
                                description=f"{request.user.username} vient d'ajouter une tâche dans le planning du {str(plan.day)}",
                                data={
                                    "name": "Plans",
                                    "title": "Ajout de commune",
                                    "message": f"{request.user.username} vient d'ajouter une tâche dans le planning du {str(plan.day)}",
                                    "confirm_text": "voir le planning",
                                    "cancel_text": "plus tard",
                                    "StackName": "Plans",
                                    "url": f"https://app.liliumpharma.com/plans/mServices/monthly_planning/?user={plan.user}&date={plan.day}",
                                    "navigate_to": json.dumps(
                                        {
                                            "screen": "PlansList",
                                            "params": {
                                                "user": plan.user.username,
                                                "date": str(plan.day),
                                            },
                                        }
                                    ),
                                },
                            )
                            # notification.send()
                    else:
                        if plan.day > today.date():
                            PlanTask.objects.create(
                                plan=plan, task=single_tasks["task"]
                            )

        return Response(
            PlanSerializer(
                Plan.objects.get(id=plan_id),
                many=False,
                context={"user": request.user},
            ).data,
            status=200,
        )

    # def post(self, request):
    #     plan_id = request.data.get("plan_id")
    #     commune_id = request.data.get("commune_id")
    #     client_id = request.data.get("client_id")
    #     task = request.data.get("task")
    #     current_time = datetime.now().time()
    #     today = datetime.now()
    #     print("plan id " + str(plan_id))
    #     print("plan id " + str(commune_id))
    #     print("client id " + str(client_id))
    #     print("task " + str(task))

    #     # print(task)

    # if plan_id:
    #     plan = Plan.objects.get(id=plan_id)
    #     if request.user.is_superuser:
    #         if commune_id:
    #             plan.communes.add(Commune.objects.get(id=commune_id))
    #             if commune_id == 2370:
    #                 plan.valid_commune = True
    #                 plan.commune_validation_date = today
    #                 plan.valid_clients = True
    #                 plan.client_validation_date = today
    #                 plan.save()
    #         if client_id:
    #             plan.clients.add(Medecin.objects.get(id=client_id))
    #         if task:
    #             PlanTask.objects.create(plan=plan, task=task["task"])
    #             notification = Notification.objects.create(
    #                 title="Nouvelle tache" + request.user.username,
    #                 description=f"{request.user.username} vient d'ajouter une tâche dans le planning du {str(plan.day)}",
    #                 data={
    #                     "name": "Plans",
    #                     "title": "Ajout de commune",
    #                     "message": f"{request.user.username} vient d'ajouter une tâche dans le planning du {str(plan.day)}",
    #                     "confirm_text": "voir le planning",
    #                     "cancel_text": "plus tard",
    #                     "StackName": "Plans",
    #                     "url": f"https://app.liliumpharma.com/plans/mServices/monthly_planning/?user={plan.user}&date={plan.day}",
    #                     "navigate_to": json.dumps(
    #                         {
    #                             "screen": "PlansList",
    #                             "params": {
    #                                 "user": plan.user.username,
    #                                 "date": str(plan.day),
    #                             },
    #                         }
    #                     ),
    #                 },
    #             )
    #             # notification.users.set(
    #             #     request.user.userprofile.get_users_to_notify().exclude(id=request.user.id)
    #             # )
    #             notification.send()

    #     else:

    #         if commune_id:
    #             if plan.day == today.date():

    #                 if current_time.hour >= 11:
    #                     return Response(
    #                         {
    #                             "message": "Impossible d'ajouter des tâches après 11h du matin."
    #                         },
    #                         status=410,
    #                     )
    #                 else:
    #                     plan.communes.add(Commune.objects.get(id=commune_id))

    #                     if commune_id == 2370:
    #                         plan.valid_commune = True
    #                         plan.commune_validation_date = today
    #                         plan.valid_clients = True
    #                         plan.client_validation_date = today
    #                         plan.save()
    #             else:
    #                 if plan.day > today.date():
    #                     plan.communes.add(Commune.objects.get(id=commune_id))

    #                     if commune_id == 2370:
    #                         plan.valid_commune = True
    #                         plan.commune_validation_date = today
    #                         plan.valid_clients = True
    #                         plan.client_validation_date = today
    #                         plan.save()

    #         if client_id:
    #             if plan.day == today.date():
    #                 if current_time.hour >= 11:
    #                     return Response(
    #                         {
    #                             "message": "Impossible d'ajouter des tâches après 11h du matin."
    #                         },
    #                         status=420,
    #                     )
    #                 else:
    #                     plan.clients.add(Medecin.objects.get(id=client_id))
    #             else:
    #                 if plan.day > today.date():
    #                     plan.clients.add(Medecin.objects.get(id=client_id))

    #         # if commune_id:
    #         #     plan.communes.add(Commune.objects.get(id=commune_id))
    #         #     today=datetime.now()

    #         #     if commune_id==2370:
    #         #         plan.valid_commune = True
    #         #         plan.commune_validation_date = today
    #         #         plan.valid_clients = True
    #         #         plan.client_validation_date = today
    #         #         plan.save()

    #         # if  client_id:
    #         #     plan.clients.add(Medecin.objects.get(id=client_id))

    #         # if task:
    #         #     PlanTask.objects.create(plan=plan, task=task["task"])

    #         #     notification=Notification.objects.create(
    #         #         title="Nouvelle tache" + request.user.username,
    #         #         description=f"{request.user.username} vient d'ajouter une tâche dans le planning du {str(plan.day)}",
    #         #         data={
    #         #                 "name":"Plans",
    #         #                 "title":"Ajout de commune",
    #         #                 "message":f"{request.user.username} vient d'ajouter une tâche dans le planning du {str(plan.day)}",
    #         #                 "confirm_text":"voir le planning",
    #         #                 "cancel_text":"plus tard",
    #         #                 "StackName":"Plans",
    #         #                 "navigate_to":
    #         #                 json.dumps({
    #         #                         "screen":"PlansList",
    #         #                         "params":{
    #         #                         "user":plan.user.username,
    #         #                         "date":str(plan.day)
    #         #                         }
    #         #                     })
    #         #             },
    #         #     )
    #         #     notification.users.set(request.user.userprofile.get_users_to_notify())
    #         #     notification.send()

    #         if task:
    #             if plan.day == today.date():
    #                 if current_time.hour >= 11:
    #                     return Response(
    #                         {
    #                             "message": "Impossible d'ajouter des tâches après 11h du matin."
    #                         },
    #                         status=430,
    #                     )
    #                 else:
    #                     PlanTask.objects.create(plan=plan, task=task["task"])
    #                     notification = Notification.objects.create(
    #                         title="Nouvelle tache " + request.user.username,
    #                         description=f"{request.user.username} vient d'ajouter une tâche dans le planning du {str(plan.day)}",
    #                         data={
    #                             "name": "Plans",
    #                             "title": "Ajout de commune",
    #                             "message": f"{request.user.username} vient d'ajouter une tâche dans le planning du {str(plan.day)}",
    #                             "confirm_text": "voir le planning",
    #                             "cancel_text": "plus tard",
    #                             "StackName": "Plans",
    #                             "url": f"https://app.liliumpharma.com/plans/mServices/monthly_planning/?user={plan.user}&date={plan.day}",
    #                             "navigate_to": json.dumps(
    #                                 {
    #                                     "screen": "PlansList",
    #                                     "params": {
    #                                         "user": plan.user.username,
    #                                         "date": str(plan.day),
    #                                     },
    #                                 }
    #                             ),
    #                         },
    #                     )
    #                     # notification.users.set(request.user.userprofile.get_users_to_notify()).exclude(id=request.user.id)
    #                     # notification.send()
    #             else:
    #                 if plan.day > today.date():
    #                     PlanTask.objects.create(plan=plan, task=task["task"])
    #                     notification = Notification.objects.create(
    #                         title="Nouvelle tache " + request.user.username,
    #                         description=f"{request.user.username} vient d'ajouter une tâche dans le planning du {str(plan.day)}",
    #                         data={
    #                             "name": "Plans",
    #                             "title": "Ajout de commune",
    #                             "message": f"{request.user.username} vient d'ajouter une tâche dans le planning du {str(plan.day)}",
    #                             "confirm_text": "voir le planning",
    #                             "cancel_text": "plus tard",
    #                             "StackName": "Plans",
    #                             "url": f"https://app.liliumpharma.com/plans/mServices/monthly_planning/?user={plan.user}&date={plan.day}",
    #                             "navigate_to": json.dumps(
    #                                 {
    #                                     "screen": "PlansList",
    #                                     "params": {
    #                                         "user": plan.user.username,
    #                                         "date": str(plan.day),
    #                                     },
    #                                 }
    #                             ),
    #                         },
    #                     )
    #                     # notification.users.set(
    #                     #     request.user.userprofile.get_users_to_notify().exclude(id=request.user.id)
    #                     # )
    #                     notification.send()

    # return Response(
    #     PlanSerializer(
    #         Plan.objects.get(id=plan_id), many=False, context={"user": request.user}
    #     ).data,
    #     status=200,
    # )

    def delete(self, request):
        plan_id = request.data.get("plan_id")
        commune_id = request.data.get("commune_id")
        client_id = request.data.get("client_id")
        task_id = request.data.get("task_id")
        if plan_id:
            plan = Plan.objects.get(id=plan_id)
            print("plan found *******", client_id)
            if commune_id:
                plan.communes.remove(Commune.objects.get(id=commune_id))
                print("commune deleted  *******")
            if client_id:
                plan.clients.remove(Medecin.objects.get(id=client_id))
                print("client deleted  *******")

            if task_id:
                print("************ deleting task ")
                PlanTask.objects.get(id=task_id).delete()

            return Response(
                PlanSerializer(
                    Plan.objects.get(id=plan_id),
                    many=False,
                    context={"user": request.user},
                ).data,
                status=200,
            )
        else:
            return Response(
                {"response": "Plan not found"}, status=status.HTTP_400_BAD_REQUEST
            )


class PlanCommentAPI(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        serializer = PlanCommentSerializer(
            data=request.data, instance=PlanComment(user=request.user), partial=True
        )
        if serializer.is_valid():
            comment = serializer.save()
            plan = Plan.objects.get(id=request.data.get("plan"))
            notification = Notification.objects.create(
                title="Nouveau commentaire !",
                description=f"{request.user.username} a commenté le planning du {str(plan.day)}",
                data={
                    "name": "Plans",
                    "title": "Nouveau commentaire",
                    "message": f"{request.user.username} vient de commenter sur le planning du {str(plan.day)}",
                    "confirm_text": "voir le planning",
                    "cancel_text": "plus tard",
                    "url": f"https://app.liliumpharma.com/plans/mServices/monthly_planning/?user={plan.user}&date={plan.day}",
                    "StackName": "Plans",
                    "navigate_to": json.dumps(
                        {
                            "screen": "PlansList",
                            "params": {
                                "user": plan.user.username,
                                "date": str(plan.day),
                            },
                        }
                    ),
                },
            )
            users_to_notify = request.user.userprofile.get_users_to_notify()

            # users_to_notify = users_to_notify.exclude(id=request.user.id)
            if comment.plan.user.userprofile.notification_token:
                # Step 4: Add the plan user to the list if they have a notification token
                users_to_notify = list(users_to_notify) + [comment.plan.user]
            notification.users.set(users_to_notify)

            # notification.send()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PlanTasksPermuteAPI(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    # Permute Tasks
    def post(self, request, format=None):
        # plan_id = request.data.get("task_id")
        # print("data " + str(request.data))

        # plan = Plan.objects.filter(user=request.user)

        # if plan.exists():
        #     plan = plan.first()
        # plan = Plan.objects.filter(user=request.user).first()
        tasks = PlanTask.objects.filter(id__in=request.data.get("tasks"))
        plan = tasks.first().plan
        print("tasks " + str(tasks))
        print("count " + str(tasks.count()))
        if tasks.count() == 2:
            print("here2")
            tasks.first().permute(tasks.last())
            return Response(
                PlanSerializer(plan, many=False, context={"user": request.user}).data,
                status=200,
            )
            # return HttpResponseRedirect(reverse('PlanAPI'))
        return Response(status=status.HTTP_400_BAD_REQUEST)

    # User doesn't have access


# class PlanTasksPermuteAPI(APIView):
#     authentication_classes = [TokenAuthentication]
#     permission_classes = [IsAuthenticated]

#     # Permute Tasks
#     def post(self, request, format=None):
#         plan = Plan.objects.filter(user=request.user)

#         if plan.exists():
#             plan = plan.first()
#             task_ids = request.data.get("tasks", [])
#             if len(task_ids) != 2:
#                 return Response(
#                     {"detail": "Exactly two task IDs are required."},
#                     status=status.HTTP_400_BAD_REQUEST,
#                 )

#             tasks = PlanTask.objects.filter(id__in=task_ids)

#             if tasks.count() != 2:
#                 return Response(
#                     {"detail": "Both tasks must exist."},
#                     status=status.HTTP_400_BAD_REQUEST,
#                 )

#             task1, task2 = tasks
#             print(f"before Task 1 ID: {task1.id} with order {task1.order}")
#             print(f"before Task 2 ID: {task2.id} with order {task2.order}")

#             # Enregistrer les ordres originaux
#             original_order1 = task1.order
#             original_order2 = task2.order

#             # Mettre les ordres à -1 pour éviter les conflits d'intégrité
#             task1.order = 100
#             task2.order = 101

#             try:
#                 # Enregistrer les modifications temporaires
#                 task1.save()
#                 task2.save()

#                 # Maintenant permuter les ordres
#                 task1.order = original_order2
#                 task2.order = original_order1

#                 # Enregistrer les ordres permutés
#                 task1.save()
#                 task2.save()

#                 print(f"after Task 1 ID: {task1.id} with order {task1.order}")
#                 print(f"after Task 2 ID: {task2.id} with order {task2.order}")

#                 return Response(
#                     PlanSerializer(
#                         plan, many=False, context={"user": request.user}
#                     ).data,
#                     status=200,
#                 )
#             except IntegrityError as e:
#                 # Gestion de l'erreur d'intégrité
#                 print("IntegrityError occurred:", e)
#                 return Response(
#                     {"detail": "Error occurred while permuting task orders."},
#                     status=status.HTTP_400_BAD_REQUEST,
#                 )


# Validation

from django.utils import timezone


class PlanValidateAPI(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        plan_id = request.GET.get("plan_id")
        plan_ids = request.GET.get("plan_ids")
        username = request.GET.get("user")
        communes = request.GET.get("communes")
        clients = request.GET.get("clients")
        tasks = request.GET.get("tasks")
        if plan_id:
            plan = Plan.objects.get(id=plan_id)
            today = timezone.now()
            print(plan.day >= today.date())
            print("$$$$$$$$$$$$$$$$$")
            print("-->"+str(request.user.userprofile.rolee))
            if (
                plan.day == today.date() and today.hour <= 19
            ) or plan.day > today.date():
                superior = User.objects.filter(userprofile__usersunder=plan.user)
                if (
                    request.user in superior
                    or request.user.is_superuser
                    or request.user.userprofile.rolee == "CountryManager"
                ):
                    if communes:
                        plan.valid_commune = True
                        plan.commune_validation_date = timezone.now()
                        plan.commune_validation_user = request.user
                        plan.save(
                            update_fields=[
                                "valid_commune",
                                "commune_validation_date",
                                "commune_validation_user",
                            ]
                        )
                        text = "les communes du"
                    if clients:
                        plan.valid_clients = True
                        plan.client_validation_date = timezone.now()
                        plan.client_validation_user = request.user
                        plan.save(
                            update_fields=[
                                "valid_clients",
                                "client_validation_date",
                                "client_validation_user",
                            ]
                        )
                        text = "les clients du"
                    if tasks:
                        plan.valid_tasks = True
                        plan.tasks_validation_date = timezone.now()
                        plan.tasks_validation_user = request.user
                        plan.save(
                            update_fields=[
                                "valid_tasks",
                                "tasks_validation_date",
                                "tasks_validation_user",
                            ]
                        )
                        text = "les taches du"

                    # notification=Notification.objects.create(
                    #     title="Valdation plan",
                    #     description=f"{text} planning du {str(plan.day)} ont bien été validés",
                    #     data={
                    #             "name":"Plans",
                    #             "title":"Valdation plan",
                    #             "message":f"{text} planning du {str(plan.day)} ont bien été validés",
                    #             "confirm_text":"voir le planning",
                    #             "cancel_text":"plus tard",
                    #             "StackName":"Plans",
                    #             "url":f"https://app.liliumpharma.com/plans/mServices/monthly_planning/?user={plan.user}&date={plan.day}",
                    #             "navigate_to":
                    #             json.dumps({
                    #                     "screen":"PlansList",
                    #                     "params":{
                    #                     "user":plan.user.username,
                    #                     "date":str(plan.day)
                    #                     }
                    #                 })
                    #         },
                    # )
                    # notification.users.set([plan.user])
                    # notification.send()

                    return Response(
                        PlanSerializer(
                            plan, many=False, context={"user": request.user}
                        ).data,
                        status=status.HTTP_200_OK,
                    )
        else:
            if plan_ids:
                plans = Plan.objects.filter(id__in=plan_ids.split(",")).update(
                    valid_commune=True
                )
                print("*******", plans)
                return Response(
                    PlanSerializer(
                        Plan.objects.filter(id__in=plan_ids.split(",")),
                        many=True,
                        context={"user": request.user},
                    ).data,
                    status=200,
                )

        # User not Authorized
        return Response(status=status.HTTP_403_FORBIDDEN)


# def PlanPDF(request):
#     usernames = (
#         request.GET.get("user") if request.GET.get("user") else request.user.username
#     )
#     today = datetime.now().date()
#     min_date = request.GET.get("min_date")
#     max_date = request.GET.get("max_date")

#     print("max date", max_date)
#     print("min date", min_date)

#     # Filtrer l'utilisateur par son nom d'utilisateur
#     user = User.objects.filter(username=usernames).first()
#     usern = str(user)

#     all_plans = []

#     # Récupérer les plans de l'utilisateur
#     if (
#         request.user.is_superuser
#         or request.user.userprofile.rolee == "Superviseur"
#         or request.user.userprofile.rolee == "CountryManager"
#     ):
#         plans = Plan.objects.filter(
#             user__username=usern, day__gte=min_date, day__lte=max_date
#         )
#     else:
#         plans = Plan.objects.filter(
#             user=request.user, day__gte=min_date, day__lte=max_date
#         )

#     # Filtrer les jours de travail (non free_day)
#     plans = [p for p in plans if not p.free_day]

#     # Obtenir les communes des plans visités
#     visited_communes = set()
#     for plan in plans:
#         visited_communes.update(
#             plan.communes.all()
#         )  # Récupérer toutes les communes liées au plan

#     # Récupérer les médecins associés à l'utilisateur
#     medecins = Medecin.objects.filter(
#         users=user
#     )  # Filtrer les médecins associés à l'utilisateur

#     # Extraire toutes les communes associées aux médecins
#     all_communes = set(medecin.commune for medecin in medecins)

#     # Identifier les communes non visitées
#     non_visite_communes = all_communes - visited_communes

#     # Créer un dictionnaire avec le nombre de médecins pour chaque commune non visitée
#     non_visite_communes_with_count = {
#         commune: Medecin.objects.filter(commune=commune, users=user).count()
#         for commune in non_visite_communes
#     }

#     # Regrouper les plans par tranche de 5
#     plans = [plans[i : i + 5] for i in range(0, len(plans), 5)]
#     all_plans.append(plans)

#     print(
#         "----> Communes non visitées : " + str(non_visite_communes_with_count)
#     )  # Debug info

#     return render(
#         request,
#         "plans/pdf.html",
#         {
#             "all_plans": all_plans,
#             "user": usern,
#             "periode": today,
#             "non_visite_communes": non_visite_communes_with_count,  # Ajout des communes non visitées avec le compte des médecins
#         },
#     )


# def PlanPDF(request):
#     usernames = (
#         request.GET.get("user") if request.GET.get("user") else request.user.username
#     )
#     today = datetime.now().date()
#     min_date = request.GET.get("min_date")
#     max_date = request.GET.get("max_date")
#     from_to = f"${min_date} Au ${min_date}"

#     print("max date", max_date)
#     print("min date", min_date)

#     # Filtrer l'utilisateur par son nom d'utilisateur
#     user = User.objects.filter(username=usernames).first()
#     usern = str(user)

#     all_plans = []

#     # Récupérer les plans de l'utilisateur
#     if (
#         request.user.is_superuser
#         or request.user.userprofile.rolee == "Superviseur"
#         or request.user.userprofile.rolee == "CountryManager"
#     ):
#         plans = Plan.objects.filter(
#             user__username=usern, day__gte=min_date, day__lte=max_date
#         )
#     else:
#         plans = Plan.objects.filter(
#             user=request.user, day__gte=min_date, day__lte=max_date
#         )

#     # Filtrer les jours de travail (non free_day)
#     plans = [p for p in plans if not p.free_day]

#     # Obtenir les communes des plans visités
#     visited_communes = set()
#     for plan in plans:
#         visited_communes.update(
#             plan.communes.all()
#         )  # Récupérer toutes les communes liées au plan

#     # Récupérer les médecins associés à l'utilisateur
#     medecins = Medecin.objects.filter(
#         users=user
#     )  # Filtrer les médecins associés à l'utilisateur

#     # Extraire toutes les communes associées aux médecins
#     all_communes = set(medecin.commune for medecin in medecins)

#     # Identifier les communes non visitées pour le secteur médical
#     non_visite_communes_medical = {
#         commune
#         for commune in all_communes
#         if Medecin.objects.filter(commune=commune, users=user)
#         .exclude(specialite__in=["Pharmacie", "grossiste", "supergros"])
#         .exists()
#         and commune not in visited_communes
#     }

#     # Identifier les communes non visitées pour le secteur commercial
#     non_visite_communes_commercial = {
#         commune
#         for commune in all_communes
#         if Medecin.objects.filter(commune=commune, users=user)
#         .filter(specialite__in=["Pharmacie", "grossiste", "supergros"])
#         .exists()
#         and commune not in visited_communes
#     }

#     # Créer un dictionnaire avec le nombre de médecins pour chaque commune non visitée
#     non_visite_communes_medical_with_count = {
#         commune: Medecin.objects.filter(commune=commune, users=user).count()
#         for commune in non_visite_communes_medical
#     }

#     non_visite_communes_commercial_with_count = {
#         commune: Medecin.objects.filter(commune=commune, users=user).count()
#         for commune in non_visite_communes_commercial
#     }

#     # Regrouper les plans par tranche de 5
#     plans = [plans[i : i + 5] for i in range(0, len(plans), 5)]
#     all_plans.append(plans)

#     print(
#         "----> Communes non visitées médicales : "
#         + str(non_visite_communes_medical_with_count)
#     )  # Debug info
#     print(
#         "----> Communes non visitées commerciales : "
#         + str(non_visite_communes_commercial_with_count)
#     )  # Debug info

#     return render(
#         request,
#         "plans/pdf.html",
#         {
#             "all_plans": all_plans,
#             "user": usern,
#             "periode": today,
#             "from_to": ,
#             "non_visite_communes_medical": non_visite_communes_medical_with_count,  # Ajout des communes non visitées médicales avec le compte des médecins
#             "non_visite_communes_commercial": non_visite_communes_commercial_with_count,  # Ajout des communes non visitées commerciales avec le compte des médecins
#         },
#     )


# def PlanPDF(request):
#     usernames = (
#         request.GET.get("user") if request.GET.get("user") else request.user.username
#     )
#     today = datetime.now().date()
#     min_date = request.GET.get("min_date")
#     max_date = request.GET.get("max_date")

#     print("max date", max_date)
#     print("min date", min_date)

#     # Filtrer l'utilisateur par son nom d'utilisateur
#     user = User.objects.filter(username=usernames).first()
#     usern = str(user)
#     from_to = f"{min_date} Au {min_date}"

#     all_plans = []

#     # Récupérer les plans de l'utilisateur
#     if (
#         request.user.is_superuser
#         or request.user.userprofile.rolee == "Superviseur"
#         or request.user.userprofile.rolee == "CountryManager"
#     ):
#         plans = Plan.objects.filter(
#             user__username=usern, day__gte=min_date, day__lte=max_date
#         )
#     else:
#         plans = Plan.objects.filter(
#             user=request.user, day__gte=min_date, day__lte=max_date
#         )

#     # Filtrer les jours de travail (non free_day)
#     plans = [p for p in plans if not p.free_day]

#     # Obtenir les communes des plans visités
#     visited_communes = set()
#     for plan in plans:
#         visited_communes.update(
#             plan.communes.all()
#         )  # Récupérer toutes les communes liées au plan

#     # Récupérer les médecins associés à l'utilisateur
#     medecins = Medecin.objects.filter(
#         users=user
#     )  # Filtrer les médecins associés à l'utilisateur

#     # Extraire toutes les communes associées aux médecins
#     all_communes = set(medecin.commune for medecin in medecins)

#     # Identifier les communes non visitées pour le secteur médical
#     non_visite_communes_medical = {
#         commune
#         for commune in all_communes
#         if Medecin.objects.filter(commune=commune, users=user)
#         .exclude(specialite__in=["Pharmacie", "Grossiste", "SuperGros"])
#         .exists()
#         and commune not in visited_communes
#     }

#     # Identifier les communes non visitées pour le secteur commercial
#     non_visite_communes_commercial = {
#         commune
#         for commune in all_communes
#         if Medecin.objects.filter(commune=commune, users=user)
#         .filter(specialite__in=["Pharmacie", "Grossiste", "SuperGros"])
#         .exists()
#         and commune not in visited_communes
#     }

#     # Créer un dictionnaire avec le nombre de médecins pour chaque commune non visitée
#     non_visite_communes_medical_with_count = {
#         commune: Medecin.objects.filter(commune=commune, users=user).count()
#         for commune in non_visite_communes_medical
#     }

#     non_visite_communes_commercial_with_count = {
#         commune: Medecin.objects.filter(commune=commune, users=user).count()
#         for commune in non_visite_communes_commercial
#     }

#     # Regrouper les plans par tranche de 5
#     plans = [plans[i : i + 5] for i in range(0, len(plans), 5)]
#     all_plans.append(plans)

#     print(
#         "----> Communes non visitées médicales : "
#         + str(non_visite_communes_medical_with_count)
#     )  # Debug info
#     print(
#         "----> Communes non visitées commerciales : "
#         + str(non_visite_communes_commercial_with_count)
#     )  # Debug info

#     return render(
#         request,
#         "plans/pdf.html",
#         {
#             "all_plans": all_plans,
#             "user": usern,
#             "from_to": from_to,
#             "periode": today,
#             "non_visite_communes_medical": non_visite_communes_medical_with_count,  # Ajout des communes non visitées médicales avec le compte des médecins
#             "non_visite_communes_commercial": non_visite_communes_commercial_with_count,  # Ajout des communes non visitées commerciales avec le compte des médecins
#         },
#     )


from django.shortcuts import render
from datetime import datetime
from medecins.models import Medecin  # Assure-toi d'importer tes modèles
from datetime import datetime, timedelta
from django.shortcuts import render
from medecins.models import Medecin


def count_working_days(start_date, end_date):
    """Compter le nombre de jours de travail entre deux dates, en excluant les week-ends."""
    current_date = start_date
    working_days = 0

    while current_date <= end_date:
        if current_date.weekday() < 5:  # Exclure les week-ends (0= lundi, 6= dimanche)
            working_days += 1
        current_date += timedelta(days=1)

    return working_days


def PlanPDF(request):
    usernames = (
        request.GET.get("user") if request.GET.get("user") else request.user.username
    )
    today = datetime.now().date()
    min_date = request.GET.get("min_date")
    max_date = request.GET.get("max_date")

    # Filtrer l'utilisateur par son nom d'utilisateur
    user = User.objects.filter(username=usernames).first()
    usern = str(user)
    from_to = f"{min_date} Au {max_date}"

    all_plans = []

    # Récupérer les plans de l'utilisateur
    if (
        request.user.is_superuser
        or request.user.userprofile.rolee == "Superviseur"
        or request.user.userprofile.rolee == "CountryManager"
    ):
        plans = Plan.objects.filter(
            user__username=usern, day__gte=min_date, day__lte=max_date
        )
    else:
        plans = Plan.objects.filter(
            user=request.user, day__gte=min_date, day__lte=max_date
        )

    # Filtrer les jours de travail (non free_day)
    plans = [p for p in plans if not p.free_day]

    # Obtenir les communes des plans visités
    visited_communes = set()
    for plan in plans:
        visited_communes.update(
            plan.communes.all()
        )  # Récupérer toutes les communes liées au plan

    # Récupérer les médecins associés à l'utilisateur
    medecins = Medecin.objects.filter(
        users=user
    )  # Filtrer les médecins associés à l'utilisateur

    # Extraire toutes les communes associées aux médecins
    all_communes = set(medecin.commune for medecin in medecins)

    # Dictionnaire pour stocker le nombre de médecins par commune visitée
    excluded_specialities = ["Pharmacie", "Grossiste", "SuperGros"]

    visited_commune_medecin_count = {
        commune: Medecin.objects.filter(commune=commune, users=user)
        .exclude(specialite__in=excluded_specialities)
        .count()
        for commune in visited_communes
    }

    # Dictionnaire pour stocker le nombre de médecins et de pharmacies par commune non visitée
    non_visite_communes = {}

    # Identifier les communes non visitées pour le secteur médical et commercial
    for commune in all_communes:
        if commune not in visited_communes:
            medecin_count = (
                Medecin.objects.filter(commune=commune, users=user)
                .exclude(specialite__in=["Pharmacie", "Grossiste", "SuperGros"])
                .count()
            )
            pharmacie_count = Medecin.objects.filter(
                commune=commune, users=user, specialite="Pharmacie"
            ).count()

            # Ajouter au dictionnaire uniquement si on a des médecins ou des pharmacies
            if medecin_count > 0 or pharmacie_count > 0:
                non_visite_communes[commune] = {
                    "medecins": medecin_count,
                    "pharmacies": pharmacie_count,
                }

    # Regrouper les plans par tranche de 5
    plans = [plans[i : i + 5] for i in range(0, len(plans), 5)]
    all_plans.append(plans)

    return render(
        request,
        "plans/PDF.html",
        {
            "all_plans": all_plans,
            "user": usern,
            "from_to": from_to,
            "periode": today,
            "non_visite_communes": non_visite_communes,  # Retourne uniquement les communes non visitées avec les comptes
            "visited_commune_medecin_count": dict(
                visited_commune_medecin_count
            ),  # Nombre de médecins par commune visitée
        },
    )


# def PlanPDF(request):
#     usernames = (
#         request.GET.get("user") if request.GET.get("user") else request.user.username
#     )
#     today = datetime.now().date()
#     min_date = request.GET.get("min_date")
#     max_date = request.GET.get("max_date")

#     print("max date", max_date)
#     print("min date", min_date)

#     # Filtrer l'utilisateur par son nom d'utilisateur
#     user = User.objects.filter(username=usernames).first()
#     usern = str(user)
#     from_to = f"{min_date} Au {max_date}"

#     all_plans = []

#     # Récupérer les plans de l'utilisateur
#     if (
#         request.user.is_superuser
#         or request.user.userprofile.rolee == "Superviseur"
#         or request.user.userprofile.rolee == "CountryManager"
#     ):
#         plans = Plan.objects.filter(
#             user__username=usern, day__gte=min_date, day__lte=max_date
#         )
#     else:
#         plans = Plan.objects.filter(
#             user=request.user, day__gte=min_date, day__lte=max_date
#         )

#     # Filtrer les jours de travail (non free_day)
#     plans = [p for p in plans if not p.free_day]

#     # Obtenir les communes des plans visités
#     visited_communes = set()
#     for plan in plans:
#         visited_communes.update(
#             plan.communes.all()
#         )  # Récupérer toutes les communes liées au plan

#     # Récupérer les médecins associés à l'utilisateur
#     medecins = Medecin.objects.filter(
#         users=user
#     )  # Filtrer les médecins associés à l'utilisateur

#     # Extraire toutes les communes associées aux médecins
#     all_communes = set(medecin.commune for medecin in medecins)

#     # Dictionnaire pour stocker le nombre de médecins et de pharmacies par commune non visitée
#     non_visite_communes = {}

#     # Identifier les communes non visitées pour le secteur médical et commercial
#     for commune in all_communes:
#         if commune not in visited_communes:
#             medecin_count = (
#                 Medecin.objects.filter(commune=commune, users=user)
#                 .exclude(specialite__in=["Pharmacie", "Grossiste", "SuperGros"])
#                 .count()
#             )
#             pharmacie_count = Medecin.objects.filter(
#                 commune=commune, users=user, specialite="Pharmacie"
#             ).count()

#             # Ajouter au dictionnaire uniquement si on a des médecins ou des pharmacies
#             if medecin_count > 0 or pharmacie_count > 0:
#                 non_visite_communes[commune] = {
#                     "medecins": medecin_count,
#                     "pharmacies": pharmacie_count,
#                 }

#     # Regrouper les plans par tranche de 5
#     plans = [plans[i : i + 5] for i in range(0, len(plans), 5)]
#     all_plans.append(plans)

#     print("----> Communes non visitées : " + str(non_visite_communes))  # Debug info

#     return render(
#         request,
#         "plans/pdf.html",
#         {
#             "all_plans": all_plans,
#             "user": usern,
#             "from_to": from_to,
#             "periode": today,
#             "non_visite_communes": non_visite_communes,  # Retourne uniquement les communes non visitées avec les comptes
#         },
#     )


# def PlanPDF(request):

#     usernames = (
#         request.GET.get("user") if request.GET.get("user") else request.user.username
#     )
#     # usernames =User.objects.filter(id=37)
#     today = datetime.now().date()
#     min_date = request.GET.get("min_date")
#     max_date = request.GET.get("max_date")

#     print("max date", max_date)
#     print("min date", min_date)

#     # Filtrer les utilisateurs par leur nom d'utilisateur
#     user = User.objects.filter(username=usernames).first()
#     usern = str(user)

#     # print(today.strftime("%A"))
#     all_plans = []

#     if (
#         request.user.is_superuser
#         or request.user.userprofile.rolee == "Superviseur"
#         or request.user.userprofile.rolee == "CountryManager"
#     ):
#         plans = Plan.objects.filter(
#             user__username=usern, day__gte=min_date, day__lte=max_date
#         )
#     else:
#         plans = Plan.objects.filter(
#             user=request.user, day__gte=min_date, day__lte=max_date
#         )

#     plans = [p for p in plans if not p.free_day]
#     plans = [plans[i : i + 5] for i in range(0, len(plans), 5)]

#     all_plans.append(plans)

#     return render(
#         request,
#         "plans/pdf.html",
#         {"all_plans": all_plans, "user": usern, "periode": today},
#     )


# for username in usernames:
#     i+=1
#     print(i)
#     if request.user.is_superuser or request.user.userprofile.rolee=="Superviseur" or request.user.userprofile.rolee=="CountryManager":
#         plans=Plan.objects.filter(user__username=usern,day__gte=min_date,day__lte=max_date)
#     else:
#         plans=Plan.objects.filter(user=request.user,day__gte=min_date,day__lte=max_date)

#     plans=[p for p in  plans if not p.free_day]
#     plans=[plans[i:i+5] for i in range(0, len(plans), 5)]

#     all_plans.append(plans)

# return render(request,"plans/pdf.html",{
#             "all_plans":all_plans ,
#             "user":usern,
#             "periode":today
#         })


# def PlanPDF(request):


#     usernames=request.GET.get("user") if request.GET.get("user") else request.user.username
#     # usernames =User.objects.filter(id=37)
#     today=datetime.datetime.today()
#     min_date=request.GET.get("min_date")
#     max_date=request.GET.get("max_date")

#     print("max date",max_date)
#     print("min date",min_date)

#     # Filtrer les utilisateurs par leur nom d'utilisateur
#     user = User.objects.filter(username=usernames).first()
#     print(str(user))

#     # print(today.strftime("%A"))
#     all_plans=[]
#     for username in usernames:
#         if request.user.is_superuser or request.user.userprofile.rolee=="Superviseur" or request.user.userprofile.rolee=="CountryManager":
#             plans=Plan.objects.filter(user__username=username,day__gte=min_date,day__lte=max_date)
#         else:
#             plans=Plan.objects.filter(user=request.user,day__gte=min_date,day__lte=max_date)

#         plans=[p for p in  plans if not p.free_day]
#         plans=[plans[i:i+5] for i in range(0, len(plans), 5)]

#         all_plans.append(plans)

#     print("user" + username)
#     return render(request,"plans/pdf.html",{
#                 "all_plans":all_plans ,
#                 "user":username,
#                 "periode":today
#             })


def SinglePlanPDF(request, id):
    plan = Plan.objects.get(id=id)

    return render(request, "plans/single_pdf.html", {"plan": plan})


def MsMonthlyPlanning(request):

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
        "micro_frontends/monthly_planning/index.html",
        {"token": token if request.user.is_authenticated else ""},
    )


class PlanTasksAPI(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        task_id = request.GET.get("task")
        task = PlanTask.objects.get(id=task_id)
        task.completed = not task.completed
        task.save()
        task = PlanTask.objects.get(id=task_id)
        return Response(
            {
                "id": task.id,
                "task": task.task,
                "order": task.order,
                "completed": task.completed,
                "is_transferred": task.is_transferred,
                "transferred_by": task.transferred_by,
                "transferred_at": task.transferred_at,
            },
            status=200,
        )

    def post(self, request):
        task = request.data.get("task")
        added = request.data.get("added")
        plan = Plan.objects.get(day=added, user=request.user)
        order = len(PlanTask.objects.filter(plan=plan)) + 1
        p_task = PlanTask(plan=plan, task=task, order=order)
        p_task.save()
        return Response(
            RapportSerializer(
                Rapport.objects.get(added=added, user=request.user), many=False
            ).data,
            status=200,
        )


class RequestPlanValidateAPI(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):

        plan = Plan.objects.get(id=request.GET.get("plan_id"))
        user = request.user.username
        # Vérifier si une notification similaire existe déjà
        existing_notification = Notification.objects.filter(
            title="Demande validation de plan ",
            description=f"Délégué:{user}\nPlanning du {str(plan.day)}",
            data={
                "name": "Plans",
                "title": "Demande de validation",
                "message": f"{user} demande une validation, planning du {str(plan.day)}",
                "confirm_text": "voir le planning",
                "cancel_text": "plus tard",
                "StackName": "Plans",
                "url": f"https://app.liliumpharma.com/plans/mServices/monthly_planning/?user={user}&date={plan.day}",
                "navigate_to": json.dumps(
                    {
                        "screen": "PlansList",
                        "params": {"user": plan.user.username, "date": str(plan.day)},
                    }
                ),
            },
        ).first()

        print("notif exists >>>>>" + str(existing_notification))

        if existing_notification:
            serializer = PlanSerializer(
            plan, context={"user": request.user, "date": plan.day}
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(status=200)

        notification = Notification.objects.create(
            title="Demande validation de planning ",
            description=f"Délégué:{user}\nPlanning du {str(plan.day)}",
            data={
                "name": "Plans",
                "title": "Demande de validation",
                "message": f"{request.user.username} demande une validation, planning du {str(plan.day)}",
                "confirm_text": "voir le planning",
                "cancel_text": "plus tard",
                "StackName": "Plans",
                "url": f"https://app.liliumpharma.com/plans/mServices/monthly_planning/?user={user}&date={plan.day}",
                "navigate_to": json.dumps(
                    {
                        "screen": "PlansList",
                        "params": {"user": plan.user.username, "date": str(plan.day)},
                    }
                ),
            },
        )
        #notification.users.set(plan.user.userprofile.get_users_to_notify())
        # notification.send()

        if not plan.valid_commune and not plan.commune_request_date:
            plan.commune_request_date = datetime.now().date()
        elif not plan.valid_clients and not plan.client_request_date:
            plan.client_request_date = datetime.now().date()
        elif not plan.valid_tasks and plan.tasks_request_date:
            plan.tasks_request_date = datetime.now().date()

        plan.save()
        serializer = PlanSerializer(
            plan, context={"user": request.user, "date": plan.day}
            )
        return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=200)


def MsPlans(request):

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
        "micro_frontends/monthly_planning/index.html",
        {"token": token if request.user.is_authenticated else ""},
    )
