from django.shortcuts import render
from django.http import JsonResponse
import json
import datetime
from django.contrib.auth.decorators import login_required

from .models import *

# Create your views here.
@login_required
def front_main(request):
    from regions.models import Region, Wilaya
    from accounts.models import UserProfile, UserSectorDetail, SectorCategory, SpecialityRolee
    from django.contrib.auth.models import User

    # Regions
    regions_json = json.dumps([
        {'id': r.id, 'name': r.name}
        for r in Region.objects.all().order_by('name')
    ])

    # Wilayas where pays_id=1, include region_id for cascading
    wilayas_json = json.dumps([
        {'id': w.id, 'nom': w.nom, 'region_id': w.region_id}
        for w in Wilaya.objects.filter(pays_id=1).order_by('nom')
    ])

    # Types: SectorCategory choices excluding IN
    types_json = json.dumps([
        {'value': v, 'label': label}
        for v, label in SectorCategory.choices
        if v != SectorCategory.IN
    ])

    # Roles: only commercial/field roles
    ALLOWED_ROLES = {
        SpecialityRolee.medico_commercial,
        SpecialityRolee.commercial,
        SpecialityRolee.superviseur_national,
        SpecialityRolee.superviseur_regional,
        SpecialityRolee.superviseur,
        SpecialityRolee.countrymanager,
    }
    roles_json = json.dumps([
        {'value': v, 'label': label}
        for v, label in SpecialityRolee.choices
        if v in ALLOWED_ROLES
    ])

    # Users: active, human, work_as_commercial; include region + sector wilayas for cascading
    users_data = []
    profiles = UserProfile.objects.filter(
        user__is_active=True,
        is_human=True,
        user__is_staff=True,
    ).select_related('user').prefetch_related('sectors')

    if not request.user.is_superuser:
        user_profile = getattr(request.user, 'userprofile', None)
        if user_profile:
            role = user_profile.speciality_rolee
            if role == SpecialityRolee.countrymanager:
                pass  # Admin / Country Manager sees all
            elif role in [SpecialityRolee.superviseur_national, SpecialityRolee.superviseur_regional, SpecialityRolee.superviseur]:
                # Supervisors see themselves + users under them
                under_ids = list(user_profile.usersunder.values_list('id', flat=True))
                allowed_ids = under_ids + [request.user.id]
                profiles = profiles.filter(user_id__in=allowed_ids)
            else:
                # Commercials see only themselves
                profiles = profiles.filter(user_id=request.user.id)
        else:
            profiles = profiles.filter(user_id=request.user.id)

    # Map region name → region id for client-side filtering
    region_name_to_id = {r.name: r.id for r in Region.objects.all()}

    for p in profiles:
        users_data.append({
            'id': p.user.id,
            'username': p.user.username,
            'speciality_rolee': p.speciality_rolee,
            'region_id': region_name_to_id.get(p.region),
            'wilaya_ids': list(p.sectors.values_list('id', flat=True)),
        })
    users_json = json.dumps(users_data)

    context = {
        'regions_json': regions_json,
        'wilayas_json': wilayas_json,
        'types_json': types_json,
        'roles_json': roles_json,
        'users_json': users_json,
        'today_date': datetime.date.today().strftime('%d/%m/%Y'),
    }
    return render(request, 'main/list.html', context)

def front_add(request):
    return render(request, 'main/index.html')

import requests
from django.http import JsonResponse

def proxy_openrouteservice(request):
    start = request.GET.get('start')
    end = request.GET.get('end')

    # Remplacez par votre propre clé API OpenRouteService
    api_key = '5b3ce3597851110001cf62480f0f56a3b8da4df384f203a20d3eb034'

    url = f"https://api.openrouteservice.org/v2/directions/driving-car"
    params = {
        "api_key": api_key,
        "start": start,
        "end": end
    }

    # Faire la requête vers l'API OpenRouteService
    response = requests.get(url, params=params)

    # Retourner la réponse sous forme de JSON
    return JsonResponse(response.json())

import re
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Deplacement, NuitDetail

@csrf_exempt
def create_deplacement(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        raw_distance = data.get('distance', '')
        cleaned_distance = re.sub(r'[^\d.]', '', raw_distance)  # Keep only numbers and decimal points

        print(str(data))

        # Save Deplacement
        deplacement = Deplacement.objects.create(
            start_date=data['startDate'],
            end_date=data['endDate'],
            nb_jours=data['nbJours'],
            nb_nuits=data['nbNuits'],
            wilaya1=data['wilaya1'],
            wilaya2=data['wilaya2'],
            distance=cleaned_distance,
            user=request.user
        )

        # Save NuitDetails
        for nuit in data.get('nuitsDetails', []):
            NuitDetail.objects.create(
                deplacement=deplacement,
                nuit=nuit['nuit'],
                start_date=nuit['startDate'],
                end_date=nuit['endDate']
            )
        print("deplacement created succefully")

        return JsonResponse({'status': 'success', 'message': 'Deplacement created successfully!'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


from django.http import JsonResponse
from .models import Deplacement
from django.db.models import Q

from django.http import JsonResponse
from .models import Deplacement

@login_required
def get_wilaya_real_sales(request):
    from clients.models import OrderProduct

    wilaya_id = request.GET.get('wilaya_id')
    month     = request.GET.get('month')  # "YYYY-MM"

    if not wilaya_id or not month:
        return JsonResponse({'error': 'Missing parameters'}, status=400)

    try:
        year, mon = month.split('-')
        year, mon = int(year), int(mon)
    except ValueError:
        return JsonResponse({'error': 'Invalid month format'}, status=400)

    prev_year = year if mon > 1 else year - 1
    prev_mon  = mon - 1 if mon > 1 else 12

    def calc_stats(y, m):
        qs = (
            OrderProduct.objects
            .filter(
                order__source__date__year=y,
                order__source__date__month=m,
                order__client__wilaya_id=wilaya_id,
            )
            .select_related('produit')
        )
        total_units = 0
        total_value = 0.0
        for op in qs:
            total_units += op.qtt
            total_value += op.qtt * float(op.produit.price)
        return total_units, total_value

    curr_units, curr_value = calc_stats(year, mon)
    _prev_units, prev_value = calc_stats(prev_year, prev_mon)

    if prev_value > 0:
        evolution_pct = round((curr_value - prev_value) / prev_value * 100, 1)
    else:
        evolution_pct = None

    return JsonResponse({
        'current_units': curr_units,
        'current_value': round(curr_value, 2),
        'previous_value': round(prev_value, 2),
        'evolution_pct': evolution_pct,
    })


def get_deplacements(request):
    print("GETTING DEPLACEMNTS")
    filters = {}
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    nb_jours = request.GET.get('nb_jours')
    nb_nuits = request.GET.get('nb_nuits')

    if start_date:
        filters['start_date__gte'] = start_date
    if end_date:
        filters['end_date__lte'] = end_date
    if nb_jours:
        filters['nb_jours'] = nb_jours
    if nb_nuits:
        filters['nb_nuits'] = nb_nuits

    deplacements = Deplacement.objects.filter(**filters).select_related('user').prefetch_related('nuits_details')
    data = []
    for deplacement in deplacements:
        nuits_details = [
            {
                'nuit': nuit.nuit,
                'start_date': nuit.start_date.strftime('%Y-%m-%d'),
                'end_date': nuit.end_date.strftime('%Y-%m-%d'),
            }
            for nuit in deplacement.nuits_details.all()
        ]
        data.append({
            'id': deplacement.id,
            'user': deplacement.user.username,
            'status': deplacement.status,
            'start_date': deplacement.start_date.strftime('%Y-%m-%d'),
            'end_date': deplacement.end_date.strftime('%Y-%m-%d'),
            'nb_jours': deplacement.nb_jours,
            'nb_nuits': deplacement.nb_nuits,
            'wilaya1': deplacement.wilaya1,
            'wilaya2': deplacement.wilaya2,
            'distance': deplacement.distance,
            'created_at': deplacement.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'nuits_details': nuits_details,
        })
    
    return JsonResponse(data, safe=False)


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from .models import Deplacement
import json

@csrf_exempt
def update_status(request, deplacement_id):
    if request.method == 'PATCH':
        try:
            # Parse the request body
            data = json.loads(request.body)
            next_status = data.get('status')

            # Get the Deplacement object
            deplacement = get_object_or_404(Deplacement, id=deplacement_id)

            # Update the status
            deplacement.status = next_status
            deplacement.save()

            # Respond with the updated status
            return JsonResponse({'status': 'success', 'new_status': deplacement.status})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    # Return a 405 if the method is not allowed
    return JsonResponse({'error': 'Method not allowed'}, status=405)


def build_dep_trips(plan_dates_data, unplanned_dates_data, days_per_trip, times):
    """
    Phase 1 - Pool all 'Honored' dates (valid planned + all unplanned) and group them consecutively.
    Phase 2 - Group 'Dishonored' dates (missing/wrong_region planned) consecutively amongst themselves.
    Phase 3 - Sort internally and pad missing trips up to the required 'times'.
    """
    from datetime import date as date_type

    days_per_trip = max(1, days_per_trip)
    trips = []

    # ── Phase 1: Separate dates into Honored and Dishonored ──────────────────
    honored_dates = []
    dishonored_dates = []

    for p in plan_dates_data:
        slot = dict(p, status="planned")
        # If the rapport is missing or wrong region, the plan was not honored
        if p.get("rapport_status") in ["missing", "wrong_region"]:
            dishonored_dates.append(slot)
        else:
            honored_dates.append(slot)

    # All unplanned dates inherently have a rapport, so they are honored
    for u in unplanned_dates_data:
        slot = dict(u, status="unplanned")
        honored_dates.append(slot)

    # ── Phase 2: Group Honored dates consecutively ───────────────────────────
    honored_dates.sort(key=lambda x: x["date"])
    current_trip = []

    for slot in honored_dates:
        slot_date = date_type.fromisoformat(slot["date"])

        if not current_trip:
            current_trip.append(slot)
        else:
            last_slot = current_trip[-1]
            last_date = date_type.fromisoformat(last_slot["date"])
            consecutive = (slot_date - last_date).days == 1
            trip_has_room = len(current_trip) < days_per_trip

            if consecutive and trip_has_room:
                current_trip.append(slot)
            else:
                # Pad current trip with non_honore slots and save it
                while len(current_trip) < days_per_trip:
                    current_trip.append({"status": "non_honore"})
                trips.append(current_trip)
                current_trip = [slot]

    # Finalize any open honored trip
    if current_trip:
        while len(current_trip) < days_per_trip:
            current_trip.append({"status": "non_honore"})
        trips.append(current_trip)

    # ── Phase 3: Group Dishonored dates ──────────────────────────────────────
    dishonored_dates.sort(key=lambda x: x["date"])
    current_trip = []

    for slot in dishonored_dates:
        slot_date = date_type.fromisoformat(slot["date"])

        if not current_trip:
            current_trip.append(slot)
        else:
            last_slot = current_trip[-1]
            last_date = date_type.fromisoformat(last_slot["date"])
            consecutive = (slot_date - last_date).days == 1
            trip_has_room = len(current_trip) < days_per_trip

            if consecutive and trip_has_room:
                current_trip.append(slot)
            else:
                while len(current_trip) < days_per_trip:
                    current_trip.append({"status": "non_honore"})
                trips.append(current_trip)
                current_trip = [slot]

    if current_trip:
        while len(current_trip) < days_per_trip:
            current_trip.append({"status": "non_honore"})
        trips.append(current_trip)

    # ── Phase 4: Sort internally and chronologically globally ────────────────
    # Push non_honore to the bottom of their respective trips
    for trip in trips:
        trip.sort(key=lambda x: x.get("date", "9999-99-99"))

    # Sort the list of all trips chronologically by their first real date
    def get_trip_start(trip):
        for slot in trip:
            if slot.get("status") != "non_honore":
                return slot.get("date", "9999-99-99")
        return "9999-99-99"

    trips.sort(key=get_trip_start)

    # ── Phase 5: Pad missing trips up to the required 'times' ────────────────
    while len(trips) < times:
        trips.append([{"status": "non_honore"} for _ in range(days_per_trip)])

    return trips


@login_required
def get_communes_by_wilaya(request):
    """Return communes for one or more wilaya IDs (used by the admin sector form)."""
    from regions.models import Commune
    wilaya_ids = request.GET.getlist('wilaya_id')
    communes = (
        Commune.objects
        .filter(wilaya_id__in=wilaya_ids)
        .order_by('nom')
        .values('id', 'nom')
    )
    return JsonResponse(list(communes), safe=False)


def _merge_orders(date_orders, wilaya_ids,
                  specific_commune_ids=None, excluded_commune_ids=None):
    """
    Aggregate order data for one sector from the nested structure
    ``date_orders[w_id][c_id] = {'ids': [...], 'total_value': float}``.

    * specific_commune_ids – non-empty set/list → only include orders whose
      client commune is in this set (exception-commune sector).
    * excluded_commune_ids – non-empty set/list → skip orders whose client
      commune is in this set (general-wilaya sector when exceptions exist).
    Both can be empty/None; in that case all orders for the wilayas are summed.
    """
    all_ids = []
    total = 0.0
    for wid in wilaya_ids:
        if wid not in date_orders:
            continue
        for cid, data in date_orders[wid].items():
            if specific_commune_ids:
                if cid not in specific_commune_ids:
                    continue
            elif excluded_commune_ids and cid in excluded_commune_ids:
                continue
            all_ids.extend(data['ids'])
            total += data['total_value']
    return {'ids': all_ids, 'total_value': total} if all_ids else None


@login_required
def get_sector_table(request):
    from accounts.models import UserSectorDetail, SectorCategory, SpecialityRolee
    from regions.models import Region
    from plans.models import Plan
    from medecins.models import Medecin
    from rapports.models import Visite, Rapport
    from django.db.models import Prefetch, Count
    from collections import OrderedDict

    COMMERCIAL_SPECIALITES = {"Pharmacie", "Grossiste", "SuperGros"}

    CATEGORY_ORDER = {SectorCategory.SEMI: 0, SectorCategory.DEP: 1}

    # Apply filters
    user_id    = request.GET.get('user_id')
    category   = request.GET.get('type')
    region_id  = request.GET.get('region_id')
    wilaya_id  = request.GET.get('wilaya_id')
    role       = request.GET.get('role')
    start_date = request.GET.get('start_date')
    end_date   = request.GET.get('end_date')

    # Base queryset: always exclude IN, only active/human/staff users
    qs = (
        UserSectorDetail.objects
        .exclude(category=SectorCategory.IN)
        .filter(
            user_profile__user__is_active=True,
            user_profile__is_human=True,
            user_profile__user__is_staff=True,
        )
        .select_related('user_profile__user')
        .prefetch_related('wilayas', 'communes')
        .order_by('user_profile__user__username')
    )

    if not request.user.is_superuser:
        user_profile = getattr(request.user, 'userprofile', None)
        if user_profile:
            current_user_role = user_profile.speciality_rolee
            if current_user_role == SpecialityRolee.countrymanager:
                pass  # Country Manager sees all
            elif current_user_role in [SpecialityRolee.superviseur_national, SpecialityRolee.superviseur_regional, SpecialityRolee.superviseur]:
                # Supervisors see themselves + users under them
                under_ids = list(user_profile.usersunder.values_list('id', flat=True))
                allowed_ids = under_ids + [request.user.id]
                qs = qs.filter(user_profile__user_id__in=allowed_ids)
            else:
                # Commercials see only themselves
                qs = qs.filter(user_profile__user_id=request.user.id)
        else:
            qs = qs.filter(user_profile__user_id=request.user.id)

    # Month-frequency filter: derive target month from start_date (fallback to today)
    if start_date:
        try:
            _target_date = datetime.date.fromisoformat(start_date)
            target_month = _target_date.month
            target_month_str = _target_date.strftime('%Y-%m')
        except (ValueError, AttributeError):
            _target_date = datetime.date.today()
            target_month = _target_date.month
            target_month_str = _target_date.strftime('%Y-%m')
    else:
        _target_date = datetime.date.today()
        target_month = _target_date.month
        target_month_str = _target_date.strftime('%Y-%m')

    if target_month % 2 == 0:
        qs = qs.filter(Q(month_frequency='ALL') | Q(month_frequency='EVEN'))
    else:
        qs = qs.filter(Q(month_frequency='ALL') | Q(month_frequency='ODD'))

    if user_id:
        qs = qs.filter(user_profile__user_id=user_id)
    if category:
        qs = qs.filter(category=category)
    if region_id:
        try:
            region_name = Region.objects.get(id=region_id).name
            qs = qs.filter(user_profile__region=region_name)
        except Region.DoesNotExist:
            pass
    if wilaya_id:
        qs = qs.filter(wilayas__id=wilaya_id)
    if role:
        qs = qs.filter(user_profile__speciality_rolee=role)

    # Pre-fetch ValidatedSector snapshot for the current qs + month — avoids N+1
    from deplacement.models import ValidatedSector
    _val_qs = ValidatedSector.objects.filter(
        sector__in=qs,
        month=target_month_str,
    ).values('sector_id', 'prix_valide', 'is_approved_by_dir')
    validation_dict = {v['sector_id']: v for v in _val_qs}

    # Group by user preserving alphabetical order
    user_map = OrderedDict()
    for sd in qs:
        uid = sd.user_profile.user_id
        if uid not in user_map:
            user_map[uid] = {
                'user_id': uid,
                'username': sd.user_profile.user.username,
                'sectors': [],
            }
        wilaya_ids_sd = list(sd.wilayas.values_list('id', flat=True))
        wilaya_names_sd = ", ".join(sd.wilayas.values_list('nom', flat=True))
        commune_ids_sd = list(sd.communes.values_list('id', flat=True))
        commune_names_sd = ", ".join(sd.communes.values_list('nom', flat=True))
        user_map[uid]["sectors"].append(
            {
                "id": sd.id,
                "wilaya": wilaya_names_sd,
                "wilaya_ids": wilaya_ids_sd,
                "commune_ids": commune_ids_sd,
                "commune_names": commune_names_sd,
                "category": sd.category,
                "times": sd.times or 1,
                "days": sd.days or 1,
                "medical": sd.medical or 0,
                "commercial": sd.commercial or 0,
                "value": float(sd.value) if sd.value is not None else None,
                "hotel_cost": (
                    float(sd.hotel_cost) if sd.hotel_cost is not None else None
                ),
                "prix_valide": (
                    float(validation_dict[sd.id]['prix_valide'])
                    if sd.id in validation_dict
                    else None
                ),
                "is_approved_by_dir": (
                    validation_dict[sd.id]['is_approved_by_dir']
                    if sd.id in validation_dict
                    else False
                ),
            }
        )

    # Sort each user's sectors: SEMI first, then DEP
    result = []
    for entry in user_map.values():
        entry['sectors'].sort(key=lambda s: (CATEGORY_ORDER.get(s['category'], 99), s['wilaya']))
        result.append(entry)

    # Attach plan_dates per sector
    for entry in result:
        uid = entry['user_id']

        # ── User-level rapport data (computed once per user) ──────────────────
        rq = Rapport.objects.filter(user_id=uid)
        if start_date:
            rq = rq.filter(added__gte=start_date)
        if end_date:
            rq = rq.filter(added__lte=end_date)
        rapport_date_strs = {str(d) for d in rq.values_list('added', flat=True)}

        tq = Visite.objects.filter(rapport__user_id=uid)
        if start_date:
            tq = tq.filter(rapport__added__gte=start_date)
        if end_date:
            tq = tq.filter(rapport__added__lte=end_date)
        total_by_date = {
            str(v['rapport__added']): v['total']
            for v in tq.values('rapport__added').annotate(total=Count('id'))
        }

        # ── 1. Build Precedence Map for this User (IN > SEMI > DEP) ───────────
        all_user_sectors = UserSectorDetail.objects.filter(user_profile__user_id=uid).prefetch_related('wilayas', 'communes')
        c_map = {}  # commune_id -> {'sec_id': ..., 'cat': ..., 'prio': ...}
        w_map = {}  # wilaya_id  -> {'sec_id': ..., 'cat': ..., 'prio': ...}
        
        mapping_priority = {"IN": 3, "SEMI": 2, "DEP": 1}

        for sec in all_user_sectors:
            cat = sec.category
            prio = mapping_priority.get(cat, 0)
            specific_communes = list(sec.communes.all())
            if specific_communes:
                for c in specific_communes:
                    existing = c_map.get(c.id)
                    if not existing or prio > existing['prio']:
                        c_map[c.id] = {'sec_id': sec.id, 'prio': prio, 'cat': cat}
            else:
                specific_wilayas = list(sec.wilayas.all())
                for w in specific_wilayas:
                    existing = w_map.get(w.id)
                    if not existing or prio > existing['prio']:
                        w_map[w.id] = {'sec_id': sec.id, 'prio': prio, 'cat': cat}

        # ── 2. Bucket Plans by exact Sector ────────────────────────────────────
        plan_qs = Plan.objects.filter(user_id=uid).distinct().order_by('day').prefetch_related('communes', 'clients__commune')
        if start_date:
            plan_qs = plan_qs.filter(day__gte=start_date)
        if end_date:
            plan_qs = plan_qs.filter(day__lte=end_date)

        plans_by_sector = {} # sector_id -> list of plans
        plan_severity = {"DEP": 3, "SEMI": 2, "IN": 1} # For mixed region days

        for plan in plan_qs:
            plan_sec_id = None
            current_sev = 0

            for c in plan.communes.all():
                mapping = c_map.get(c.id) or w_map.get(c.wilaya_id)
                if mapping:
                    sev = plan_severity.get(mapping['cat'], 0)
                    if sev > current_sev:
                        current_sev = sev
                        plan_sec_id = mapping['sec_id']

            if plan_sec_id:
                plans_by_sector.setdefault(plan_sec_id, []).append(plan)

        # ── 3. Bucket Visites by exact Sector & Date ──────────────────────────
        visite_qs = Visite.objects.filter(rapport__user_id=uid).values(
            "rapport__added", "rapport__id", "medecin__specialite", 
            "medecin_id", "medecin__commune_id", "medecin__wilaya_id", "medecin__commune__nom"
        )
        if start_date:
            visite_qs = visite_qs.filter(rapport__added__gte=start_date)
        if end_date:
            visite_qs = visite_qs.filter(rapport__added__lte=end_date)

        visites_by_sec_date = {} 
        for v in visite_qs:
            c_id = v['medecin__commune_id']
            w_id = v['medecin__wilaya_id']
            mapping = c_map.get(c_id) or w_map.get(w_id)
            if mapping:
                sec_id = mapping['sec_id']
                date_str = str(v["rapport__added"])

                if sec_id not in visites_by_sec_date:
                    visites_by_sec_date[sec_id] = {}
                if date_str not in visites_by_sec_date[sec_id]:
                    visites_by_sec_date[sec_id][date_str] = {
                        "medical": 0, "commercial": 0, "rapport_id": v["rapport__id"],
                        "medecin_ids": set(), "commune_names": set()
                    }
                
                rc = visites_by_sec_date[sec_id][date_str]
                if v['medecin__specialite'] in COMMERCIAL_SPECIALITES:
                    rc["commercial"] += 1
                else:
                    rc["medical"] += 1
                rc["medecin_ids"].add(v['medecin_id'])
                if v['medecin__commune__nom']:
                    rc["commune_names"].add(v['medecin__commune__nom'])

        # ── 4. Bucket Orders by exact Sector & Date ────────────────────────────
        from orders.models import Order
        oq = Order.objects.filter(user_id=uid).select_related(
            'pharmacy', 'gros', 'super_gros'
        ).prefetch_related('orderitem_set__produit')
        if start_date:
            oq = oq.filter(added__date__gte=start_date)
        if end_date:
            oq = oq.filter(added__date__lte=end_date)

        orders_by_sec_date = {} 
        for order in oq:
            target_client = order.pharmacy or order.gros or order.super_gros
            if target_client and hasattr(target_client, 'wilaya_id'):
                c_id = getattr(target_client, 'commune_id', None)
                w_id = target_client.wilaya_id
                
                mapping = c_map.get(c_id) or w_map.get(w_id)
                if mapping:
                    sec_id = mapping['sec_id']
                    date_str = str(order.added.date())

                    if sec_id not in orders_by_sec_date:
                        orders_by_sec_date[sec_id] = {}
                    if date_str not in orders_by_sec_date[sec_id]:
                        orders_by_sec_date[sec_id][date_str] = {'ids': [], 'total_value': 0.0}

                    orders_by_sec_date[sec_id][date_str]['ids'].append(order.id)
                    orders_by_sec_date[sec_id][date_str]['total_value'] += float(order.valeur_net)

        # ── 5. Process Output for strictly SEMI and DEP Sectors ───────────────
        for sector in entry['sectors']:
            sec_id = sector['id']
            
            sec_plans = plans_by_sector.get(sec_id, [])
            sec_visites = visites_by_sec_date.get(sec_id, {})
            sec_orders = orders_by_sec_date.get(sec_id, {})

            dates_data = []
            for plan in sec_plans:
                date_str = str(plan.day)
                clients = plan.clients.all()
                commercial_plan = sum(1 for c in clients if c.specialite in COMMERCIAL_SPECIALITES)

                if date_str not in rapport_date_strs:
                    rapport_status = 'missing'
                elif total_by_date.get(date_str, 0) == 0:
                    rapport_status = 'empty'
                elif date_str not in sec_visites:
                    rapport_status = 'wrong_region'
                else:
                    rapport_status = 'ok'

                rc = sec_visites.get(date_str, {'medical': 0, 'commercial': 0, 'medecin_ids': set(), 'commune_names': set()})

                plan_client_ids = {c.id for c in clients}
                visited_ids = rc.get('medecin_ids', set())
                total_planned = len(plan_client_ids)
                similarity = round(len(plan_client_ids & visited_ids) / total_planned * 100) if total_planned else 0

                dates_data.append({
                    "date": date_str,
                    "medical": len(clients) - commercial_plan,
                    "commercial": commercial_plan,
                    "rapport_medical": rc["medical"],
                    "rapport_commercial": rc["commercial"],
                    "rapport_id": rc.get("rapport_id"),
                    "rapport_status": rapport_status,
                    "rendement_orders": sec_orders.get(date_str, None),
                    "similarity": similarity,
                    "plan_communes": sorted({c.commune.nom for c in clients if c.commune_id and c.commune}),
                    "rapport_communes": sorted(rc.get('commune_names', set())),
                })

            # Unplanned Dates (Phone calls, ad-hoc visits inside this exact sector)
            planned_date_strs = {d['date'] for d in dates_data}
            unplanned_dates = []
            for date_str, rc in sec_visites.items():
                if date_str not in planned_date_strs:
                    unplanned_dates.append({
                        "date": date_str,
                        "rapport_medical": rc["medical"],
                        "rapport_commercial": rc["commercial"],
                        "rapport_id": rc.get("rapport_id"),
                        "rendement_orders": sec_orders.get(date_str, None),
                        "rapport_communes": sorted(rc.get('commune_names', set())),
                    })

            # Orphan Orders (Phone orders unlinked to a rapport in this sector)
            orphan_ids = []
            orphan_total = 0.0
            for date_str, ord_data in sec_orders.items():
                if date_str not in sec_visites:
                    orphan_ids.extend(ord_data['ids'])
                    orphan_total += ord_data['total_value']

            sector['orphan_orders'] = {'ids': orphan_ids, 'total_value': orphan_total} if orphan_ids else None

            if sector["category"] == "DEP":
                sector["trips"] = build_dep_trips(dates_data, unplanned_dates, sector["days"], sector["times"])
            else:
                total_valid_slots = len(dates_data) + len(unplanned_dates)

                while total_valid_slots < sector["times"]:
                    dates_data.append(None)
                    total_valid_slots += 1

                if not dates_data and unplanned_dates:
                    shifted = unplanned_dates.pop(0)
                    shifted["status"] = "unplanned"
                    dates_data.append(shifted)

                sector["plan_dates"] = dates_data
                sector["unplanned_dates"] = unplanned_dates

    return JsonResponse(result, safe=False)

# ─────────────────────────────────────────────────────────────────────────────
# TASK 2 — Unified sector validation (supervisor price + direction approval)
# ─────────────────────────────────────────────────────────────────────────────

@csrf_exempt
@login_required
def save_sector_validation(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    try:
        data              = json.loads(request.body)
        sector_id         = data.get('sector_id')
        month             = data.get('month')          # 'YYYY-MM'
        prix_valide       = data.get('prix_valide')
        medical_visits    = data.get('medical_visits', 0)
        commercial_visits = data.get('commercial_visits', 0)
        order_count       = data.get('order_count', 0)
        action            = data.get('action', 'save_price')  # 'save_price' | 'approve'

        if sector_id is None or not month or prix_valide is None:
            return JsonResponse({'error': 'Missing parameters'}, status=400)

        # RBAC: only Supervisors and CountryManagers may validate prices
        user_role = getattr(getattr(request.user, 'userprofile', None), 'speciality_rolee', '')
        ALLOWED_VALIDATORS = {'Superviseur_regional', 'Superviseur_national', 'Superviseur', 'CountryManager'}
        if user_role not in ALLOWED_VALIDATORS and not request.user.is_superuser:
            return JsonResponse({'error': 'Forbidden: You do not have permission to validate prices.'}, status=403)

        from accounts.models import UserSectorDetail
        from deplacement.models import ValidatedSector

        sector = UserSectorDetail.objects.select_related('user_profile__user').get(id=sector_id)
        target_user = sector.user_profile.user

        obj, created = ValidatedSector.objects.get_or_create(
            sector=sector,
            month=month,
            defaults={
                'user':              target_user,
                'prix_valide':       prix_valide,
                'medical_visits':    medical_visits,
                'commercial_visits': commercial_visits,
                'order_count':       order_count,
                'validated_by_sup':  request.user,
            },
        )

        # Security: once Direction has approved, only CountryManagers may touch it
        if not created and obj.is_approved_by_dir:
            if user_role != 'CountryManager' and not request.user.is_superuser:
                return JsonResponse({'error': 'Forbidden: already approved by Direction'}, status=403)

        if action == 'save_price':
            obj.prix_valide       = prix_valide
            obj.medical_visits    = medical_visits
            obj.commercial_visits = commercial_visits
            obj.order_count       = order_count
            if obj.validated_by_sup is None:
                obj.validated_by_sup = request.user
            obj.save(update_fields=['prix_valide', 'medical_visits', 'commercial_visits',
                                    'order_count', 'validated_by_sup', 'updated_at'])

        elif action == 'approve':
            obj.prix_valide        = prix_valide  # CountryManager may readjust
            obj.is_approved_by_dir = True
            obj.approved_by_dir    = request.user
            obj.save(update_fields=['prix_valide', 'is_approved_by_dir', 'approved_by_dir', 'updated_at'])

        else:
            return JsonResponse({'error': 'Invalid action'}, status=400)

        return JsonResponse({'status': 'success', 'created': created, 'action': action})

    except UserSectorDetail.DoesNotExist:
        return JsonResponse({'error': 'Sector not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ─────────────────────────────────────────────────────────────────────────────
# TASK 3 — Reimbursement sheet (printable A4)
# ─────────────────────────────────────────────────────────────────────────────

@login_required
def reimbursement_sheet_view(request, user_id, month):
    from django.shortcuts import get_object_or_404
    from django.contrib.auth.models import User
    from accounts.models import UserProfile
    from deplacement.models import ValidatedSector
    from django.http import HttpRequest
    from datetime import datetime as dt
    import calendar
    import json

    MONTH_NAMES_FR = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
                      'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']

    commercial_user = get_object_or_404(User, id=user_id)

    try:
        year, mon = int(month.split('-')[0]), int(month.split('-')[1])
        month_display = f"{MONTH_NAMES_FR[mon - 1]} {year}"
    except Exception:
        return JsonResponse({'error': 'Invalid format'}, status=400)

    last_day     = calendar.monthrange(year, mon)[1]
    end_date_str = f"{year}-{mon:02d}-{last_day:02d}"

    # Derive validation state from the ValidatedSector snapshot table
    _vs_qs = ValidatedSector.objects.filter(user=commercial_user, month=month)
    validated_by_supervisor = _vs_qs.filter(validated_by_sup__isnull=False).exists()
    validated_by_direction  = _vs_qs.filter(is_approved_by_dir=True).exists()

    # ── Reuse get_sector_table for 100 % data consistency ────────────────────
    fake_request = HttpRequest()
    fake_request.user = request.user
    fake_request.GET = {
        'user_id':    user_id,
        'start_date': f"{month}-01",
        'end_date':   end_date_str,
    }
    response = get_sector_table(fake_request)

    data = json.loads(response.content) if response.status_code == 200 else []
    validated_days = []
    total_net = 0.0

    def parse_date(d_str):
        try:
            return dt.strptime(d_str, '%Y-%m-%d').strftime('%d/%m/%Y')
        except Exception:
            return d_str

    def is_valid(entry):
        if not entry or entry.get('status') == 'non_honore':
            return False
        if entry.get('rapport_status') in ('missing', 'wrong_region'):
            return False
        return True

    if data:
        user_data = data[0]
        for s in user_data.get('sectors', []):
            # Only include sectors fully approved by the Direction
            if not s.get('is_approved_by_dir'):
                continue

            valid_count = 0
            max_allowed = s.get('times') or 1
            cat         = s.get('category')
            prix_valide = float(s.get('prix_valide'))  # guaranteed non-null for approved sectors

            if cat == 'SEMI':
                entries = [e for e in (s.get('plan_dates') or []) + (s.get('unplanned_dates') or []) if e]
                entries.sort(key=lambda x: x.get('date', '9999-99-99'))

                for entry in entries:
                    if not is_valid(entry):
                        continue
                    valid_count += 1
                    if valid_count > max_allowed:
                        break

                    orders        = entry.get('rendement_orders')
                    ord_count     = len(orders.get('ids', [])) if orders else 0
                    ord_value     = float(orders.get('total_value', 0.0)) if orders else 0.0
                    c_list        = entry.get('rapport_communes')
                    communes_disp = ", ".join(c_list) if c_list else (s.get('commune_names') or s.get('wilaya'))
                    total_net    += prix_valide

                    validated_days.append({
                        'date':             parse_date(entry.get('date')),
                        'wilaya_nom':       s.get('wilaya'),
                        'communes_list':    communes_disp,
                        'type':             'SEMI',
                        'medical_count':    entry.get('rapport_medical', 0),
                        'commercial_count': entry.get('rapport_commercial', 0),
                        'order_count':      ord_count,
                        'order_value':      ord_value,
                        'prix_valide':      prix_valide,
                    })

            elif cat == 'DEP':
                for trip in (s.get('trips') or []):
                    trip_slots = [slot for slot in trip if slot]
                    if not trip_slots or not all(is_valid(slot) for slot in trip_slots):
                        continue
                    valid_count += 1
                    if valid_count > max_allowed:
                        break

                    med_count  = sum(slot.get('rapport_medical', 0) for slot in trip_slots)
                    com_count  = sum(slot.get('rapport_commercial', 0) for slot in trip_slots)
                    ord_count  = sum(
                        len(slot.get('rendement_orders', {}).get('ids', []))
                        for slot in trip_slots if slot.get('rendement_orders')
                    )
                    ord_value  = sum(
                        float(slot.get('rendement_orders', {}).get('total_value', 0.0))
                        for slot in trip_slots if slot.get('rendement_orders')
                    )
                    d1        = parse_date(trip_slots[0].get('date'))
                    d2        = parse_date(trip_slots[-1].get('date'))
                    date_disp = f"{d1} au {d2}" if d1 != d2 else d1
                    total_net += prix_valide

                    validated_days.append({
                        'date':             date_disp,
                        'wilaya_nom':       s.get('wilaya'),
                        'communes_list':    s.get('commune_names') or "Plusieurs communes",
                        'type':             'DEP',
                        'medical_count':    med_count,
                        'commercial_count': com_count,
                        'order_count':      ord_count,
                        'order_value':      ord_value,
                        'prix_valide':      prix_valide,
                    })

    validated_days.sort(key=lambda d: d['date'])

    supervisor_name = ''
    try:
        sup_profile = UserProfile.objects.filter(usersunder=commercial_user).first()
        if sup_profile:
            supervisor_name = sup_profile.user.get_full_name() or sup_profile.user.username
    except Exception:
        pass

    return render(request, 'main/reimbursement_sheet.html', {
        'commercial_user':        commercial_user,
        'month':                  month,
        'month_display':          month_display,
        'validated_days':         validated_days,
        'total_valide':           total_net,
        'supervisor_name':        supervisor_name,
        'validated_by_supervisor': validated_by_supervisor,
        'validated_by_direction':  validated_by_direction,
    })


