import json
from datetime import date, datetime
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import DelegateEvaluation, EvaluationAnswer
from django.contrib.auth.models import User
from django.urls import reverse

def get_user_role(user):
    """Récupère le rôle en utilisant strictement le champ .speciality_rolee"""
    try:
        return getattr(user.userprofile, 'speciality_rolee', getattr(user, 'speciality_rolee', ''))
    except AttributeError:
        return ""

def is_supervisor_role(role):
    """Vérifie si le rôle correspond à l'un des trois types de superviseurs"""
    return role in ['Superviseur', 'Superviseur_regional', 'Superviseur_national']

def is_country_manager(role):
    return role == 'CountryManager'

def is_delegate(role):
    """Vérifie si le rôle correspond à un délégué (Medico_commercial ou Commercial)"""
    return role in ['Medico_commercial', 'Commercial']

@login_required
def landing_page_front(request):
    role = get_user_role(request.user)
    
    # Redirection stricte des délégués
    if is_delegate(role):
        if role == 'Medico_commercial':
            return redirect('medical_evaluation_front')
        elif role == 'Commercial':
            return redirect('commercial_evaluation_front')
            
    # CountryManager, Superviseurs (et autres comme Admin) accèdent au dashboard
    return render(request, 'evaluations/landing-page.html')

@login_required
def medical_evaluation_front(request):
    role = get_user_role(request.user)

    # Redirection si un délégué commercial essaie d'y accéder
    if role == 'Commercial':
        return redirect('commercial_evaluation_front')

    context = {}
    target_username = request.GET.get('user')

    if target_username and (is_supervisor_role(role) or is_country_manager(role) or request.user.is_superuser):
        target_user = User.objects.filter(username=target_username).first()
        month = request.GET.get('month')
        year = request.GET.get('year')

        if target_user and month and year:
            evaluation = DelegateEvaluation.objects.filter(user=target_user, month=month, year=year).first()
            if evaluation:
                answers = {ans.question_id: ans.answer_data for ans in evaluation.answers.all()}
                context['read_only'] = True
                context['answers_json'] = json.dumps(answers)
                context['evaluation_score'] = evaluation.total_score

    return render(request, 'evaluations/index_medical.html', context)


@login_required
def commercial_evaluation_front(request):
    role = get_user_role(request.user)  # This gets the role using .speciality_rolee

    if role == "Medico_commercial":
        return redirect("medical_evaluation_front")

    context = {"user_role": role}  

    target_username = request.GET.get("user")
    # ... (keep the rest of your existing logic for target_user and read_only mode)

    if target_username and (
        is_supervisor_role(role)
        or is_country_manager(role)
        or request.user.is_superuser
    ):
        target_user = User.objects.filter(username=target_username).first()
        month = request.GET.get("month")
        year = request.GET.get("year")

        if target_user and month and year:
            evaluation = DelegateEvaluation.objects.filter(
                user=target_user, month=month, year=year
            ).first()
            if evaluation:
                answers = {
                    ans.question_id: ans.answer_data for ans in evaluation.answers.all()
                }
                context["read_only"] = True
                context["answers_json"] = json.dumps(answers)
                context["evaluation_score"] = evaluation.total_score

    return render(request, "evaluations/index_commercial.html", context)

    if target_username and (
        is_supervisor_role(role)
        or is_country_manager(role)
        or request.user.is_superuser
    ):
        target_user = User.objects.filter(username=target_username).first()
        month = request.GET.get("month")
        year = request.GET.get("year")

        if target_user and month and year:
            evaluation = DelegateEvaluation.objects.filter(
                user=target_user, month=month, year=year
            ).first()
            if evaluation:
                answers = {
                    ans.question_id: ans.answer_data for ans in evaluation.answers.all()
                }
                context["read_only"] = True
                context["answers_json"] = json.dumps(answers)
                context["evaluation_score"] = evaluation.total_score

    return render(request, "evaluations/index_commercial.html", context)


@csrf_exempt
@login_required
def submit_evaluation(request):
    if request.method == 'POST':
        user = request.user

        payload = request.POST
        if not payload and request.body:
            try:
                payload = json.loads(request.body)
            except:
                pass

        # Use month/year from the payload if provided (sent by both forms via URL params),
        # otherwise fall back to the previous calendar month.
        try:
            target_month = int(payload.get('month') or 0)
            target_year  = int(payload.get('year')  or 0)
            if not (1 <= target_month <= 12) or target_year < 2000:
                raise ValueError("out of range")
        except (ValueError, TypeError):
            today = date.today()
            if today.month == 1:
                target_month = 12
                target_year  = today.year - 1
            else:
                target_month = today.month - 1
                target_year  = today.year

        eval_type = payload.get('evaluation_type', 'MEDICAL')

        try:
            with transaction.atomic():
                evaluation, created = DelegateEvaluation.objects.get_or_create(
                    user=user,
                    month=target_month,
                    year=target_year,
                    defaults={
                        'evaluation_type': eval_type,
                        'total_score': float(payload.get('own_perc', 0.0))
                    }
                )

                if not created:
                    return JsonResponse({'error': 'Evaluation already exists for this month'}, status=400)

                saved_keys = []
                for key, value in payload.items():
                    if key.startswith('q'):
                        try:
                            parsed_value = json.loads(value)
                        except (ValueError, TypeError):
                            parsed_value = value

                        EvaluationAnswer.objects.create(
                            evaluation=evaluation,
                            question_id=key,
                            answer_data=parsed_value
                        )
                        saved_keys.append(key)

                return JsonResponse({'message': 'Evaluation saved successfully', 'month': target_month, 'year': target_year, 'saved_questions': saved_keys})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def evaluations_users_api(request):
    role = get_user_role(request.user)
    
    if not (is_supervisor_role(role) or is_country_manager(role)) and not request.user.is_superuser:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    month = int(request.GET.get('month', datetime.now().month))
    year = int(request.GET.get('year', datetime.now().year))
    
    delegate_roles = ['Medico_commercial', 'Commercial']
    
    if is_country_manager(role) or request.user.is_superuser:
        # Le CountryManager voit tous les délégués
        users_qs = User.objects.filter(userprofile__speciality_rolee__in=delegate_roles, is_active=True).select_related('userprofile')
    elif is_supervisor_role(role):
        # Le Superviseur voit uniquement ses underusers qui sont délégués
        try:
            users_qs = request.user.userprofile.usersunder.filter(
                userprofile__speciality_rolee__in=delegate_roles,
                is_active=True
            ).select_related('userprofile')
        except AttributeError:
            users_qs = User.objects.none()
    else:
        users_qs = User.objects.none()
        
    response_data = []
    
    for u in users_qs:
        eval_exists = DelegateEvaluation.objects.filter(user=u, month=month, year=year).exists()
        
        own_perc = 0
        if eval_exists:
            evaluation = DelegateEvaluation.objects.filter(user=u, month=month, year=year).first()
            own_perc = evaluation.total_score if evaluation.total_score else 0

        u_profile = getattr(u, 'userprofile', None)
        u_role = getattr(u_profile, 'speciality_rolee', '')

        response_data.append({
            "user": u.username,
            "name": f"{u.first_name} {u.last_name}".strip() or u.username,
            "role": u_role, 
            "region": getattr(u_profile, 'region', 'Non Spécifié'),
            "has_eval": eval_exists,
            "has_sup_eval": False,
            "family": getattr(u_profile, 'family', ''),
            "has_direction_eval": False,
            "pourcentage": 0,
            "own_perc": own_perc,
        })
        
    return JsonResponse(response_data, safe=False)

@login_required
def print_evaluation(request):
    role = get_user_role(request.user)
    
    if not (is_supervisor_role(role) or is_country_manager(role)) and not request.user.is_superuser:
        return HttpResponseForbidden('Accès non autorisé')

    target_username = request.GET.get('user')
    month = request.GET.get('month')
    year = request.GET.get('year')

    if not target_username or not month or not year:
        return render(request, 'evaluations/print.html', {'error': 'Paramètres manquants'})

    target_user = User.objects.filter(username=target_username).first()
    if not target_user:
        return render(request, 'evaluations/print.html', {'error': 'Utilisateur introuvable'})

    evaluation = DelegateEvaluation.objects.filter(
        user=target_user,
        month=int(month),
        year=int(year)
    ).first()

    if not evaluation:
        return render(request, 'evaluations/print.html', {'error': "Aucune évaluation trouvée pour ce mois"})

    answers = {ans.question_id: ans.answer_data for ans in evaluation.answers.all()}
    MONTH_NAMES = ['', 'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
                   'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']

    context = {
        'evaluation': evaluation,
        'target_user': target_user,
        'answers': answers,
        'month_name': MONTH_NAMES[int(month)],
        'year': year,
    }
    return render(request, 'evaluations/print.html', context)

@login_required
def evaluation_view_url_api(request):
    role = get_user_role(request.user)
    
    if not (is_supervisor_role(role) or is_country_manager(role)) and not request.user.is_superuser:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
        
    target_username = request.GET.get('user')
    month = request.GET.get('month')
    year = request.GET.get('year')
    
    if not target_username or not month or not year:
        return JsonResponse({'error': 'Missing parameters'}, status=400)
        
    target_user = User.objects.filter(username=target_username).first()
    if not target_user:
        return JsonResponse({'error': 'User not found'}, status=404)
        
    eval_exists = DelegateEvaluation.objects.filter(user=target_user, month=month, year=year).exists()
    if not eval_exists:
        return JsonResponse({'error': 'Evaluation not found'}, status=404)
        
    target_role = get_user_role(target_user)
    
    if target_role == 'Commercial':
        url = reverse('commercial_evaluation_front')
    else:
        url = reverse('medical_evaluation_front')
        
    return JsonResponse({'url': f"{url}?user={target_username}&month={month}&year={year}"})

@login_required
def evaluations_visits_per_user_api(request):
    try:
        from medecins.models import Medecin
        from rapports.models import Visite
        from datetime import datetime, date, timedelta
        from django.contrib.auth.models import User
        
        u = request.GET.get("user")
        if u:
            user = User.objects.filter(username=u).first()
        else:
            user = request.user
            
        current_year = int(request.GET.get("year", datetime.now().year))
        month_param = request.GET.get("month")
        
        try:
            month = int(month_param)
            if 1 <= month <= 12:
                # Local datetime.now().tzinfo is used historically in the project
                date_debut_mois = datetime(current_year, month, 1, 0, 0, 0, 0, tzinfo=datetime.now().tzinfo)
                if month == 12:
                    date_fin_mois = datetime(current_year + 1, 1, 1, 0, 0, 0, 0, tzinfo=datetime.now().tzinfo)
                else:
                    date_fin_mois = datetime(current_year, month + 1, 1, 0, 0, 0, 0, tzinfo=datetime.now().tzinfo)
            else:
                return JsonResponse({"error": "Mois invalide. Utilisez une valeur entre 1 et 12."}, status=400)
        except (ValueError, TypeError):
            return JsonResponse({"error": "Mois invalide. Utilisez une valeur numérique entre 1 et 12."}, status=400)

        date_fin_mois = date_fin_mois - timedelta(days=1)
        
        specialites_a_exclure = ["Pharmacie", "Grossiste", "SuperGros"]

        medecins_visites = (
            Medecin.objects.filter(
                visite__rapport__added__range=(date_debut_mois, date_fin_mois),
                visite__rapport__added__year=current_year,
                visite__rapport__user=user,
            )
            .exclude(specialite__in=specialites_a_exclure)
            .values("id", "nom", "specialite", "commune__nom", "commune__wilaya__nom")
            .distinct()
        )

        nombre_medecins_visites = medecins_visites.count()
        noms_medecins_visites = " | ".join(
            [f"{m['id']} {m['nom']}" for m in medecins_visites]
        )
        
        specialty_counts = {}
        details = []
        for m in medecins_visites:
            spec = m.get("specialite") or "Inconnu"
            specialty_counts[spec] = specialty_counts.get(spec, 0) + 1
            
            # Format region avoiding 'None' display
            w_nom = m.get('commune__wilaya__nom') or ''
            c_nom = m.get('commune__nom') or ''
            region = f"{w_nom} - {c_nom}".strip(" -")
            
            details.append({
                "id": m["id"],
                "nom": m["nom"],
                "specialite": spec,
                "region": region
            })

        data = {
            "nombre_visites": nombre_medecins_visites,
            "noms_medecins_visites": noms_medecins_visites,
            "details_medecins_visites": details,
            "specialty_counts": specialty_counts
        }

        return JsonResponse(data)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=500)

@login_required
def evaluations_visits_per_user_pharma_gro_api(request):
    try:
        from medecins.models import Medecin
        from rapports.models import Visite
        from datetime import datetime, date, timedelta
        from django.contrib.auth.models import User
        
        u = request.GET.get("user")
        if u:
            user = User.objects.filter(username=u).first()
        else:
            user = request.user
            
        current_year = int(request.GET.get("year", datetime.now().year))
        month_param = request.GET.get("month")
        
        try:
            month = int(month_param)
            if 1 <= month <= 12:
                date_debut_mois = datetime(current_year, month, 1, 0, 0, 0, 0, tzinfo=datetime.now().tzinfo)
                if month == 12:
                    date_fin_mois = datetime(current_year + 1, 1, 1, 0, 0, 0, 0, tzinfo=datetime.now().tzinfo)
                else:
                    date_fin_mois = datetime(current_year, month + 1, 1, 0, 0, 0, 0, tzinfo=datetime.now().tzinfo)
            else:
                return JsonResponse({"error": "Mois invalide. Utilisez une valeur entre 1 et 12."}, status=400)
        except (ValueError, TypeError):
            return JsonResponse({"error": "Mois invalide. Utilisez une valeur numérique entre 1 et 12."}, status=400)

        date_fin_mois = date_fin_mois - timedelta(days=1)
        
        specialites_a_inclure = ["Pharmacie", "Grossiste"]

        medecins_visites = (
            Medecin.objects.filter(
                visite__rapport__added__range=(date_debut_mois, date_fin_mois),
                visite__rapport__added__year=current_year,
                visite__rapport__user=user,
            )
            .filter(specialite__in=specialites_a_inclure)
            .values("id", "nom", "specialite", "commune__nom", "commune__wilaya__nom")
            .distinct()
        )

        nombre_medecins_visites = medecins_visites.count()
        noms_medecins_visites = " | ".join(
            [f"{m['id']} {m['nom']}" for m in medecins_visites]
        )

        total_visites_count = Visite.objects.filter(
            rapport__added__range=(date_debut_mois, date_fin_mois),
            rapport__added__year=current_year,
            rapport__user=user,
            medecin__specialite__in=specialites_a_inclure,
        ).count()

        specialty_counts = {}
        details = []
        for m in medecins_visites:
            spec = m.get("specialite") or "Inconnu"
            specialty_counts[spec] = specialty_counts.get(spec, 0) + 1

            w_nom = m.get('commune__wilaya__nom') or ''
            c_nom = m.get('commune__nom') or ''
            region = f"{w_nom} - {c_nom}".strip(" -")

            details.append({
                "id": m["id"],
                "nom": m["nom"],
                "specialite": spec,
                "region": region
            })

        data = {
            "nombre_visites": nombre_medecins_visites,
            "total_visites": total_visites_count,
            "noms_medecins_visites": noms_medecins_visites,
            "details_medecins_visites": details,
            "specialty_counts": specialty_counts
        }

        return JsonResponse(data)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=500)

@login_required
def evaluations_visits_more_than_once_api(request):
    try:
        from medecins.models import Medecin
        from rapports.models import Visite
        from datetime import datetime, date, timedelta
        from django.contrib.auth.models import User
        from django.db.models import Count
        from django.core.exceptions import ObjectDoesNotExist
        
        u = request.GET.get("user")
        if u:
            user = User.objects.filter(username=u).first()
        else:
            user = request.user
            
        current_year = int(request.GET.get("year", datetime.now().year))
        month_param = request.GET.get("month")
        
        try:
            month = int(month_param)
            if 1 <= month <= 12:
                # Local datetime.now().tzinfo is used historically in the project
                date_debut_mois = datetime(current_year, month, 1, 0, 0, 0, 0, tzinfo=datetime.now().tzinfo)
                if month == 12:
                    date_fin_mois = datetime(current_year + 1, 1, 1, 0, 0, 0, 0, tzinfo=datetime.now().tzinfo)
                else:
                    date_fin_mois = datetime(current_year, month + 1, 1, 0, 0, 0, 0, tzinfo=datetime.now().tzinfo)
            else:
                return JsonResponse({"error": "Mois invalide. Utilisez une valeur entre 1 et 12."}, status=400)
        except (ValueError, TypeError):
            return JsonResponse({"error": "Mois invalide. Utilisez une valeur numérique entre 1 et 12."}, status=400)

        medecins_visites = (
            Visite.objects.filter(
                rapport__added__gte=date_debut_mois,
                rapport__added__lt=date_fin_mois,
                rapport__added__year=current_year,
                rapport__user=user,
            )
            .values("medecin", "rapport__added")
        )

        from collections import defaultdict
        doctor_visits = defaultdict(list)
        for mv in medecins_visites:
            d = mv["rapport__added"]
            if hasattr(d, 'strftime'):
                d_str = d.strftime('%Y-%m-%d')
            else:
                d_str = str(d).split(' ')[0]
            doctor_visits[mv["medecin"]].append(d_str)

        multi_visit_doctors = {k: sorted(list(set(v))) for k, v in doctor_visits.items() if len(v) > 1}

        role = get_user_role(user)
        is_commercial = (role == 'Commercial')
        commercial_specialties = ["Pharmacie", "Grossiste", "SuperGros"]
        
        noms_medecins_visites = []
        for doc_id, dates in multi_visit_doctors.items():
            try:
                medecin_obj = Medecin.objects.get(id=doc_id)
                if is_commercial:
                    if medecin_obj.specialite not in commercial_specialties:
                        continue
                else:
                    if medecin_obj.specialite in commercial_specialties:
                        continue
                    
                noms_medecins_visites.append({
                    "id": doc_id,
                    "nom": f"{doc_id} {medecin_obj.nom}",
                    "specialite": medecin_obj.specialite or "Inconnu",
                    "classification": medecin_obj.classification or "",
                    "total_visites": len(dates),
                    "dates_visites": dates
                })
            except ObjectDoesNotExist:
                continue

        data = {
            "nombre_medecins_visites": len(noms_medecins_visites),
            "noms_medecins_visites": noms_medecins_visites,
        }

        return JsonResponse(data)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=500)

@login_required
def evaluations_doctors_not_visited_api(request):
    try:
        from medecins.models import Medecin
        from rapports.models import Visite
        from datetime import datetime, date, timedelta
        from django.contrib.auth.models import User
        
        u = request.GET.get("user")
        if u:
            user = User.objects.filter(username=u).first()
        else:
            user = request.user
            
        current_year = int(request.GET.get("year", datetime.now().year))
        month_param = request.GET.get("month")
        
        try:
            month = int(month_param)
            if 1 <= month <= 12:
                date_debut_mois = datetime(current_year, month, 1, 0, 0, 0, 0, tzinfo=datetime.now().tzinfo)
                if month == 12:
                    date_fin_mois = datetime(current_year + 1, 1, 1, 0, 0, 0, 0, tzinfo=datetime.now().tzinfo)
                else:
                    date_fin_mois = datetime(current_year, month + 1, 1, 0, 0, 0, 0, tzinfo=datetime.now().tzinfo)
            else:
                return JsonResponse({"error": "Mois invalide."}, status=400)
        except (ValueError, TypeError):
            return JsonResponse({"error": "Mois invalide."}, status=400)

        # Les médecins dans le portfolio de l'utilisateur
        medecins_users = Medecin.objects.filter(users=user)
        role = get_user_role(user)
        is_commercial = (role == 'Commercial')
        commercial_specialties = ["Pharmacie", "Grossiste", "SuperGros"]
        
        if is_commercial:
            medecins_users = medecins_users.filter(specialite__in=commercial_specialties)
        else:
            medecins_users = medecins_users.exclude(specialite__in=commercial_specialties)

        medecins_non_visites_data = []

        for medecin_user in medecins_users:
            est_visite = Visite.objects.filter(
                rapport__added__gte=date_debut_mois,
                rapport__added__lt=date_fin_mois,
                rapport__added__year=current_year,
                rapport__user=user,
                medecin=medecin_user,
            ).exists()

            if not est_visite:
                derniere_visite = (
                    Visite.objects.filter(rapport__user=user, medecin=medecin_user)
                    .order_by("-rapport__added")
                    .first()
                )

                date_derniere_visite = (
                    derniere_visite.rapport.added.strftime("%Y-%m-%d")
                    if derniere_visite and hasattr(derniere_visite.rapport.added, 'strftime')
                    else (str(derniere_visite.rapport.added).split(' ')[0] if derniere_visite else None)
                )
                
                medecins_non_visites_data.append(
                    {
                        "id": medecin_user.pk,
                        "nom": medecin_user.nom,
                        "specialite": medecin_user.specialite or "Inconnu",
                        "date_derniere_visite": date_derniere_visite,
                    }
                )

        data = {
            "nombre_medecins_non_visites": len(medecins_non_visites_data),
            "medecins_non_visites": medecins_non_visites_data,
        }
        return JsonResponse(data)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=500)

@login_required
def evaluations_doctors_visited_duo_api(request):
    try:
        from medecins.models import Medecin
        from rapports.models import Visite
        from datetime import datetime, date, timedelta
        from django.contrib.auth.models import User
        from django.db.models.functions import TruncDate
        from collections import defaultdict
        
        u = request.GET.get("user")
        if u:
            user = User.objects.filter(username=u).first()
        else:
            user = request.user
            
        current_year = int(request.GET.get("year", datetime.now().year))
        month_param = request.GET.get("month")
        
        try:
            month = int(month_param)
            if 1 <= month <= 12:
                # Local datetime.now().tzinfo is used historically in the project
                date_debut_mois = datetime(current_year, month, 1, 0, 0, 0, 0, tzinfo=datetime.now().tzinfo)
                if month == 12:
                    date_fin_mois = datetime(current_year + 1, 1, 1, 0, 0, 0, 0, tzinfo=datetime.now().tzinfo)
                else:
                    date_fin_mois = datetime(current_year, month + 1, 1, 0, 0, 0, 0, tzinfo=datetime.now().tzinfo)
            else:
                return JsonResponse({"error": "Mois invalide."}, status=400)
        except (ValueError, TypeError):
            return JsonResponse({"error": "Mois invalide."}, status=400)

        supervisors = User.objects.filter(
            userprofile__usersunder=user,
            userprofile__rolee='Superviseur'
        )

        visites_user = set(Visite.objects.filter(
            rapport__added__gte=date_debut_mois,
            rapport__added__lt=date_fin_mois,
            rapport__added__year=current_year,
            rapport__user=user
        ).annotate(day=TruncDate("rapport__added")).values_list("medecin_id", "day"))
        
        visites_sup = set()
        if supervisors.exists():
            visites_sup = set(Visite.objects.filter(
                rapport__added__gte=date_debut_mois,
                rapport__added__lt=date_fin_mois,
                rapport__added__year=current_year,
                rapport__user__in=supervisors
            ).annotate(day=TruncDate("rapport__added")).values_list("medecin_id", "day"))

        duo_keys = visites_user.intersection(visites_sup)
        duo_medecin_ids = {k[0] for k in duo_keys}
        
        doc_dates = defaultdict(list)
        for med_id, day in duo_keys:
            d_str = day.strftime('%Y-%m-%d') if hasattr(day, 'strftime') else str(day).split(' ')[0]
            doc_dates[med_id].append(d_str)

        specialites_a_exclure = ["Pharmacie", "Grossiste", "SuperGros"]
        doctors = Medecin.objects.filter(id__in=duo_medecin_ids).exclude(specialite__in=specialites_a_exclure)

        noms_medecins_visites = []
        for d in doctors:
            dates_visites = sorted(list(set(doc_dates[d.id])))
            noms_medecins_visites.append({
                "id": d.id,
                "nom": f"{d.id} {d.nom}",
                "specialite": d.specialite or "Inconnu",
                "classification": d.classification or "",
                "total_visites": len(dates_visites),
                "dates_visites": dates_visites
            })

        data = {
            "nombre_medecins_visites": len(noms_medecins_visites),
            "noms_medecins_visites": noms_medecins_visites,
        }

        return JsonResponse(data)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=500)

@login_required
def evaluations_get_user_products_api(request):
    try:
        from produits.models import Produit
        from accounts.models import UserTargetMonthProduct
        from django.contrib.auth.models import User
        from datetime import datetime, date

        u = request.GET.get("user")
        if u:
            user = User.objects.filter(username=u).first()
        else:
            user = request.user
            
        if not user or not hasattr(user, "userprofile"):
            return JsonResponse({"error": "Utilisateur non valide ou non authentifié"}, status=400)
            
        products_data = []
        if user.userprofile.speciality_rolee == "Commercial":
            produits = Produit.objects.all()
            for produit in produits:
                products_data.append({
                    "product_id": produit.id,
                    "product_name": produit.nom,
                })
        else:
            # Les objectifs produits ne sont pas définis chaque mois, on récupère donc 
            # tous les produits assignés à cet utilisateur indépendamment de la date.
            user_target_month = UserTargetMonthProduct.objects.filter(usermonth__user=user)
            target_products = user_target_month.values_list("product__nom", flat=True).distinct()

            for user_product in target_products:
                produit = Produit.objects.filter(nom=user_product).first()
                if produit:
                    products_data.append({
                        "product_id": produit.id,
                        "product_name": produit.nom,
                    })
                    
        return JsonResponse(products_data, safe=False)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=500)

@login_required
def evaluations_visits_supergros_api(request):
    try:
        from medecins.models import Medecin
        from rapports.models import Visite
        from datetime import datetime, date, timedelta
        from django.contrib.auth.models import User
        from collections import defaultdict
        
        u = request.GET.get("user")
        if u:
            user = User.objects.filter(username=u).first()
        else:
            user = request.user
            
        current_year = int(request.GET.get("year", datetime.now().year))
        month_param = request.GET.get("month")
        
        try:
            month = int(month_param)
            if 1 <= month <= 12:
                date_debut_mois = datetime(current_year, month, 1, 0, 0, 0, 0, tzinfo=datetime.now().tzinfo)
                if month == 12:
                    date_fin_mois = datetime(current_year + 1, 1, 1, 0, 0, 0, 0, tzinfo=datetime.now().tzinfo)
                else:
                    date_fin_mois = datetime(current_year, month + 1, 1, 0, 0, 0, 0, tzinfo=datetime.now().tzinfo)
            else:
                return JsonResponse({"error": "Mois invalide."}, status=400)
        except (ValueError, TypeError):
            return JsonResponse({"error": "Mois invalide."}, status=400)

        medecins_visites = (
            Visite.objects.filter(
                rapport__added__gte=date_debut_mois,
                rapport__added__lt=date_fin_mois,
                rapport__added__year=current_year,
                rapport__user=user,
            )
            .values("medecin", "rapport__added")
        )

        doctor_visits = defaultdict(list)
        for mv in medecins_visites:
            d = mv["rapport__added"]
            if hasattr(d, 'strftime'):
                d_str = d.strftime('%Y-%m-%d')
            else:
                d_str = str(d).split(' ')[0]
            doctor_visits[mv["medecin"]].append(d_str)

        multi_visit_doctors = {k: sorted(list(set(v))) for k, v in doctor_visits.items()}
        
        noms_medecins_visites = []
        for doc_id, dates in multi_visit_doctors.items():
            try:
                medecin_obj = Medecin.objects.get(id=doc_id)
                if medecin_obj.specialite != "SuperGros":
                    continue
                    
                noms_medecins_visites.append({
                    "id": doc_id,
                    "nom": f"{doc_id} {medecin_obj.nom}",
                    "specialite": medecin_obj.specialite or "Inconnu",
                    "classification": medecin_obj.classification or "",
                    "total_visites": len(dates),
                    "dates_visites": dates
                })
            except Medecin.DoesNotExist:
                continue

        total_visites_supgros = Visite.objects.filter(
            rapport__added__gte=date_debut_mois,
            rapport__added__lt=date_fin_mois,
            rapport__added__year=current_year,
            rapport__user=user,
            medecin__specialite="SuperGros",
        ).count()

        data = {
            "nombre_medecins_visites": len(noms_medecins_visites),
            "total_visites": total_visites_supgros,
            "noms_medecins_visites": noms_medecins_visites,
        }

        return JsonResponse(data)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=500)


@login_required
def evaluations_orders_per_product_api(request):
    try:
        from clients.models import UserTargetMonth, UserTargetMonthProduct
        from orders.models import Order, OrderItem
        from django.contrib.auth.models import User
        from django.db.models import Sum, Q

        u = request.GET.get("user")
        if u:
            user = User.objects.filter(username=u).first()
        else:
            user = request.user

        if not user:
            return JsonResponse({"error": "Utilisateur non trouvé"}, status=404)

        current_year = int(request.GET.get("year", datetime.now().year))
        month_param = request.GET.get("month")
        try:
            month = int(month_param)
            if not (1 <= month <= 12):
                raise ValueError
        except (ValueError, TypeError):
            return JsonResponse({"error": "Mois invalide."}, status=400)

        # Get most recent target per product for this user
        target_entries = (
            UserTargetMonthProduct.objects
            .filter(usermonth__user=user)
            .order_by('-usermonth__date')
            .select_related('product', 'usermonth')
        )
        seen_products = {}
        for tp in target_entries:
            if tp.product_id not in seen_products:
                seen_products[tp.product_id] = tp

        # Ph→Gros orders: pharmacy not null, gros not null, super_gros null
        ph_gros_orders = Order.objects.filter(
            user=user,
            added__year=current_year,
            added__month=month,
            pharmacy__isnull=False,
            gros__isnull=False,
            super_gros__isnull=True,
        )
        # Gros/Ph→Super orders: super_gros not null, (gros or pharmacy not null)
        gros_super_orders = Order.objects.filter(
            user=user,
            added__year=current_year,
            added__month=month,
            super_gros__isnull=False,
        ).filter(Q(gros__isnull=False) | Q(pharmacy__isnull=False))

        results = []
        for pid, tp in seen_products.items():
            product = tp.product
            price = product.price or 0
            target_qty = tp.quantity

            ph_gros_items = OrderItem.objects.filter(order__in=ph_gros_orders, produit=product)
            ph_gros_count = ph_gros_items.values('order').distinct().count()
            ph_gros_units = ph_gros_items.aggregate(total=Sum('qtt'))['total'] or 0
            ph_gros_value = round(ph_gros_units * price, 2)

            gros_super_items = OrderItem.objects.filter(order__in=gros_super_orders, produit=product)
            gros_super_count = gros_super_items.values('order').distinct().count()
            gros_super_units = gros_super_items.aggregate(total=Sum('qtt'))['total'] or 0
            gros_super_value = round(gros_super_units * price, 2)

            total_units = ph_gros_units + gros_super_units
            total_value = round(total_units * price, 2)
            target_value = round(target_qty * price, 2)
            percentage = round(total_units / target_qty * 100, 1) if target_qty > 0 else 0

            results.append({
                "product_id": pid,
                "product_name": product.nom,
                "target_quantity": target_qty,
                "target_value": target_value,
                "ph_gros": {
                    "count": ph_gros_count,
                    "total_units": ph_gros_units,
                    "total_value": ph_gros_value,
                },
                "gros_super": {
                    "count": gros_super_count,
                    "total_units": gros_super_units,
                    "total_value": gros_super_value,
                },
                "total_units": total_units,
                "total_value": total_value,
                "percentage": percentage,
            })

        return JsonResponse(results, safe=False)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=500)


from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from rapports.models import Rapport, Visite
from plans.models import Plan
from datetime import datetime, date
import calendar

class SimilarityAPIView(APIView):
    def get(self, request):
        username = request.GET.get('user')
        month = int(request.GET.get('month'))
        year = int(request.GET.get('year', 2026))

        user = User.objects.get(username=username)
        
        # Define month range
        last_day = calendar.monthrange(year, month)[1]
        date_start = date(year, month, 1)
        date_end = date(year, month, last_day)

        # Exact logic from RapportPDF
        planss = Plan.objects.filter(
            day__range=[date_start, date_end],
            user=user
        )

        total_similarity_percentage = 0
        valid_plan_count = 0

        for plan in planss:
            clients_list = plan.clients.all() # From planning/models.py
            if clients_list.count() == 0:
                continue 
            
            valid_plan_count += 1
            
            # Find reports for that specific day
            rapports_on_day = Rapport.objects.filter(added=plan.day, user=plan.user)
            
            # Count visits matching the plan
            matching_doctors = (
                Visite.objects.filter(
                    rapport__in=rapports_on_day, 
                    medecin__in=clients_list
                )
                .distinct()
                .count()
            )
            
            client_list_count = clients_list.count() or 1
            similarity_percentage = round((matching_doctors / client_list_count) * 100, 2)
            total_similarity_percentage += similarity_percentage

        average_similarity = (
            total_similarity_percentage / valid_plan_count if valid_plan_count > 0 else 0
        )

        if average_similarity > 100:
            average_similarity = 100

        return Response({
            "similarity_perc": round(average_similarity, 1)
        })
