from requests import Response
from .models import *

from io import StringIO
import xlsxwriter
from rest_framework.views import APIView
from rest_framework import authentication, permissions
from django.http import HttpResponse
from django.db.models import *
from django.contrib.auth.models import User
from accounts.models import UserProxy as User
from datetime import date
from produits.models import Produit
from liliumpharm.workbook import Workbook
from medecins.models import *
from rapports.models import Visite
from django.utils import timezone


class EtatStockClientExcel(APIView):
    def get(self, request, format=None):
        current_month = timezone.now().month
        current_year = timezone.now().year

        response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        workbook = xlsxwriter.Workbook(response, {'in_memory': True})
        worksheet = workbook.add_worksheet(f"Etat stocks clients")
        border_format = workbook.add_format({'border': 1})

        title = f'Etat de stock | {current_year}'
        title_format = workbook.add_format({'bold': True, 'font_size': 20, 'align': 'center', 'valign': 'vcenter'})
        worksheet.merge_range('A1:C1', title, title_format)

        row = 2
        worksheet.write(row, 0, 'Date')
        worksheet.write(row, 1, 'User')
        worksheet.write(row, 2, 'Medecin')
        worksheet.merge_range(row, 3, row, 4, 'Produits/Qtt')
        # worksheet.write(row, 4, 'Quantité')

        response['Content-Disposition'] = f'attachment; filename=Etat de stock client.xlsx'

        latest_visits = Visite.objects.filter(
            medecin=OuterRef('medecin'),
            rapport__added__month=current_month,
            rapport__added__year=current_year,
        ).order_by('-rapport__added').values('id')[:1]

        latest_visites_queryset = Visite.objects.filter(
            id=Subquery(latest_visits)
        )

        medecin_products = {}

        for latest_visite in latest_visites_queryset:
            medecin_name = latest_visite.medecin.nom
            observation = latest_visite.observation
            produits = latest_visite.produits.all()
            for produit in produits:
                qtt = produit.produitvisite_set.filter(visite=latest_visite).first().qtt
                if qtt > 0:
                    visite_date = latest_visite.rapport.added
                    formatted_date = visite_date.strftime('%Y-%m-%d') 
                    rapport_user = latest_visite.rapport.user.username
    
                    if medecin_name not in medecin_products:
                        medecin_products[medecin_name] = {'formatted_date': formatted_date, 'rapport_user': rapport_user, 'products': {}}
    
                    if produit.nom not in medecin_products[medecin_name]['products']:
                        medecin_products[medecin_name]['products'][produit.nom] = qtt
                    else:
                        medecin_products[medecin_name]['products'][produit.nom] += qtt

        for medecin_name, data in medecin_products.items():
            row += 1
            worksheet.write(row, 0, data['formatted_date'])
            worksheet.write(row, 1, data['rapport_user'])
            worksheet.write(row, 2, medecin_name)

            products_cell = ""
            for product_name, product_quantity in data['products'].items():
                products_cell += f" {product_name}:{product_quantity} Boite(s)   |   \n----------------\n"

            worksheet.set_row(row, None, None, {'valign': 'top'})

            worksheet.write(row, 3, products_cell.strip())  # Utilisez strip() pour supprimer le dernier saut de ligne
            row += 1
            
        workbook.close()
        return response

class AllExportExcel(APIView):

    def get(self, request, format=None):
        # Getting Today's Date
        today = date.today()


        response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    
        workbook = xlsxwriter.Workbook(response, {'in_memory': True})
    
        worksheet = workbook.add_worksheet(f"Liste Bon de commandes")
        border_format = workbook.add_format({'border': 1})

        # Set the title of the table
        title = 'Liste Bons de commandes | 2023'
        title_format = workbook.add_format({'bold': True, 'font_size': 20, 'align': 'center', 'valign': 'vcenter'})
        worksheet.write('A1', title, title_format)
        worksheet.merge_range('A1:C1', title, title_format)


        # Init Row Index
        row = 1

        indexx=10

        # Writing Headers
        worksheet.write(row, 0, 'ID')
        worksheet.write(row, 1, 'Date')
        worksheet.write(row, 2, 'User')
        worksheet.write(row, 3, 'Pharmacies')
        worksheet.write(row, 4, 'Grossistes')
        worksheet.write(row, 5, 'Super Grossistes')
        worksheet.write(row, 6, 'Status')
        worksheet.write(row, 7, 'From Office')
        worksheet.write(row, 8, 'FF')
        worksheet.write(row, 9, 'FM')
        worksheet.write(row, 10, 'IRON')
        worksheet.write(row, 11, 'YES CAL')
        worksheet.write(row, 12, 'YES VIT')
        worksheet.write(row, 13, 'ADVAGEN')
        worksheet.write(row, 14, 'DHEA 75mg')
        worksheet.write(row, 15, 'HAIRVOL')
        worksheet.write(row, 16, 'SUB12')
        worksheet.write(row, 17, 'MENOLIB')
        worksheet.write(row, 18, 'THYROLIB')
        worksheet.write(row, 19, 'HEPALIB')
        worksheet.write(row, 20, 'SOPK FREE')
        worksheet.write(row, 21, 'DIGEST PLUS')
        worksheet.write(row, 22, 'ANAFLAM')
        worksheet.write(row, 23, 'URICITRIL')
        worksheet.write(row, 24, 'URISOFT')
        worksheet.write(row, 25, 'BESTFER')
        worksheet.write(row, 26, 'New B')
        worksheet.write(row, 27, 'SLEEP ALAISE')
        worksheet.write(row, 28, 'GOLD MAG')



        # Define product columns and headers
        product_columns = {
            'FF': 8,
            'FM': 9,
            'IRON': 10,
            'YES CAL': 11,
            'YES VIT': 12,
            'ADVAGEN': 13,
            'DHEA 75mg': 14,
            'HAIRVOL': 15,
            'SUB12': 16,
            'MENOLIB': 17,
            'THYROLIB': 18,
            'HEPALIB': 19,
            'SOPK FREE': 20,
            'DIGEST PLUS': 21,
            'ANAFLAM': 22,
            'URICITRIL':23,
            'URISOFT':24,
            'BESTFER':25,
            'New B':26,
            'SLEEP ALAISE':27,
            'GOLD MAG':28,
        }

        year = request.GET.get("added__year")
        month = request.GET.get("added__month")
        print(year)
        print(month)
        from_office = request.GET.get("from_company__exact")
        print(from_office)
        print(str(from_office))

        if (month):
            try:
                if (from_office == '1'):
                    print("ici 1")
                    orders = Order.objects.filter(added__year = year, added__month=month, from_company=True)
                else:
                    print("ici 2")

                    orders = Order.objects.filter(added__year = year, added__month=month)
                response['Content-Disposition'] = f'attachment; filename=Bon de commande - date extraction mois {month}-{year}.xlsx'
            except User.DoesNotExist:
                print("no user")
                return Response({"message": "order not found."}, status=400)
        else:
            orders = Order.objects.filter(added__year = date.today().year)
            print("le fichier va generer et telecharger")
            response['Content-Disposition'] = f'attachment; filename=Bon de commande - date extraction année {year}.xlsx'


        for order in sorted(orders, key=lambda x: x.added):
            # Incrementing Row
            row += 1

            date_value = order.added.date()
            formatted_date = date_value.strftime('%Y-%m-%d') 

            worksheet.write(row, 0, order.id)
            worksheet.write(row, 1, formatted_date)
            worksheet.write(row, 2, order.user.username)
            worksheet.write(row, 3, order.pharmacy.nom if order.pharmacy else "")
            worksheet.write(row, 4, order.gros.nom if order.gros else "")
            worksheet.write(row, 5, order.super_gros.name if order.super_gros else "")
            worksheet.write(row, 6, order.status)
            worksheet.write(row, 7, order.from_company)

            order_items = OrderItem.objects.filter(order=order)

            for product_name, col in product_columns.items():
                print(f"produittttttttt {product_name}")
                order_item = next((item for item in order_items if item.produit.nom == product_name), None)
                
                if order_item and order_item.qtt > 0:
                    print("ifffffff")
                    print(f"order item {order_item} et order item qtt {order_item.qtt}")
                    worksheet.write(row, col, order_item.qtt)
                else:
                    print("elseeee")
                    worksheet.write(row, col, "")



        print("le fichier excel va t'il exporter")
        workbook.close()
        return response

class AllExitOrdersExportExcel(APIView):

    def get(self, request, format=None):
        
        # Getting Today's Date
        today = date.today()


        response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response['Content-Disposition'] = f'attachment; filename=Bon de sortie - date extraction {today}.xlsx'
    
        workbook = xlsxwriter.Workbook(response, {'in_memory': True})
    
        worksheet = workbook.add_worksheet(f"Liste Bons de sortie")
        border_format = workbook.add_format({'border': 1})

        # Set the title of the table
        title = 'Liste Bons de sortie | 2023'
        title_format = workbook.add_format({'bold': True, 'font_size': 20, 'align': 'center', 'valign': 'vcenter'})
        worksheet.write('A1', title, title_format)
        worksheet.merge_range('A1:C1', title, title_format)


        # Init Row Index
        row = 1

        indexx=10

        # Writing Headers
        worksheet.write(row, 0, 'ID')
        worksheet.write(row, 1, 'Date')
        worksheet.write(row, 2, 'User')
        worksheet.write(row, 3, 'Status')
        worksheet.write(row, 4, 'Brochure')
        worksheet.write(row, 5, 'Depôt')
        worksheet.write(row, 6, 'Confirmed by')
        worksheet.write(row, 7, 'FF')
        worksheet.write(row, 8, 'FM')
        worksheet.write(row, 9, 'IRON')
        worksheet.write(row, 10, 'YES CAL')
        worksheet.write(row, 11, 'YES VIT')
        worksheet.write(row, 12, 'ADVAGEN')
        worksheet.write(row, 13, 'DHEA 75mg')
        worksheet.write(row, 14, 'HAIRVOL')
        worksheet.write(row, 15, 'SUB12')
        worksheet.write(row, 16, 'MENOLIB')
        worksheet.write(row, 17, 'THYROLIB')
        worksheet.write(row, 18, 'HEBALIB')
        worksheet.write(row, 19, 'SOPK FREE')
        worksheet.write(row, 20, 'DIGEST PLUS')
        worksheet.write(row,21, 'ANAFLAM')


        # Define product columns and headers
        product_columns = {
            'FF': 7,
            'FM':8,
            'IRON': 9,
            'YES CAL': 10,
            'YES VIT': 11,
            'ADVAGEN': 12,
            'DHEA 75mg': 13,
            'HAIRVOL': 14,
            'SUB12': 15,
            'MENOLIB': 16,
            'THYROLIB': 17,
            'HEBALIB': 18,
            'SOPK FREE': 19,
            'DIGEST PLUS': 20,
            'ANAFLAM': 21,
        }


        year = request.GET.get("added__year")
        month = request.GET.get("added__month")
        ye = str(year)
        if (month):
            try:
                orders = ExitOrder.objects.filter(added__year = year, added__month=month)
                response['Content-Disposition'] = f'attachment; filename=Bon de sortie - date extraction mois {month}-{ye}.xlsx'
            except:
                return Response({"message": "order not found."}, status=400)
        else:
            orders = ExitOrder.objects.filter(added__year = date.today().year)
            response['Content-Disposition'] = f'attachment; filename=Bon de sortie - date extraction année {ye}.xlsx'

        # Looping through ExitOrders
        for order in orders:
            # Incrementing Row
            row += 1

            date_value = order.added.date()
            formatted_date = date_value.strftime('%Y-%m-%d') 

            worksheet.write(row, 0, order.id)
            worksheet.write(row, 1, formatted_date)
            worksheet.write(row, 2, order.user.username)
            worksheet.write(row, 3, order.status)
            if order.brochure:
                worksheet.write(row, 4, "Oui")
            else:
                worksheet.write(row, 4, "Non")
            worksheet.write(row, 5, order.depot)
            worksheet.write(row, 6, order.user_confirmed.username if order.user_confirmed else "-")

            order_items = ExitOrderItem.objects.filter(order=order)

            for product_name, col in product_columns.items():
                order_item = next((item for item in order_items if item.produit.nom == product_name), None)

                if order_item and order_item.qtt > 0:
                    worksheet.write(row, col, order_item.qtt)
                else:
                    worksheet.write(row, col, "-")

        
        workbook.close()
        return response









import re
from collections import defaultdict
from datetime import datetime, timedelta, date as date_cls
from io import BytesIO
from typing import Dict, List, Tuple, Optional

import xlsxwriter
from xlsxwriter.utility import xl_rowcol_to_cell

from django.db.models import Q
from django.http import HttpResponse
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from .models import Order, OrderItem


_ILLEGAL_XML_RE = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F]")


def _xlsx_safe(value) -> str:
    if value is None:
        return ""
    s = str(value)
    s = _ILLEGAL_XML_RE.sub("", s)
    s = s.replace("\uFFFE", "").replace("\uFFFF", "")
    if len(s) > 32767:
        s = s[:32767]
    return s


def _yn(v: bool) -> str:
    return "Oui" if bool(v) else "Non"


def _make_unique_headers(headers: List[str]) -> List[str]:
    seen: Dict[str, int] = {}
    out: List[str] = []
    for h in headers:
        base = _xlsx_safe(h).strip() or "Produit"
        if base not in seen:
            seen[base] = 1
            out.append(base)
        else:
            seen[base] += 1
            out.append(f"{base} ({seen[base]})")
    return out


def _label_pharmacy(obj) -> str:
    name = getattr(obj, "nom", "") if obj else ""
    return _xlsx_safe(f"Pharmacie - {name}".strip(" -"))


def _label_gros(obj) -> str:
    name = getattr(obj, "nom", "") if obj else ""
    return _xlsx_safe(f"Grossiste - {name}".strip(" -"))


def _label_supergros(obj) -> str:
    name = getattr(obj, "name", "") if obj else ""
    return _xlsx_safe(f"Super Grossiste - {name}".strip(" -"))


def _get_client_fournisseur(order: Order) -> Tuple[str, str]:
    office = "Office - Lilium"
    pharm_lbl = _label_pharmacy(getattr(order, "pharmacy", None)) if getattr(order, "pharmacy_id", None) else ""
    gros_lbl = _label_gros(getattr(order, "gros", None)) if getattr(order, "gros_id", None) else ""
    sgros_lbl = _label_supergros(getattr(order, "super_gros", None)) if getattr(order, "super_gros_id", None) else ""

    if pharm_lbl:
        return pharm_lbl, (gros_lbl or sgros_lbl or office)
    if gros_lbl:
        return gros_lbl, (sgros_lbl or office)
    if sgros_lbl:
        return sgros_lbl, office
    return "-", office


class OrdersExportExcel(APIView):
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated,)

    # -----------------------
    # Parsing / Defaults
    # -----------------------
    @staticmethod
    def _parse_csv_param(raw: Optional[str]) -> List[str]:
        if not raw:
            return []
        s = str(raw).strip().strip("'").strip('"').strip()
        if not s:
            return []
        if s.lower() in {"tous", "all", "*"}:
            return []
        parts = [p.strip().strip("'").strip('"').strip() for p in s.split(",")]
        parts = [p for p in parts if p and p.lower() not in {"tous", "all", "*"}]
        return parts

    @staticmethod
    def _parse_date_yyyy_mm_dd(raw: Optional[str]) -> Optional[date_cls]:
        if not raw:
            return None
        try:
            return datetime.strptime(str(raw).strip(), "%Y-%m-%d").date()
        except Exception:
            return None

    @staticmethod
    def _resolve_effective_dates(request) -> Tuple[date_cls, date_cls, bool]:
        """
        Defaults (inclusive):
          - min_date default = yesterday
          - max_date default = today
        Returns: (min_d, max_d, max_was_provided)
        """
        today = timezone.localdate()
        raw_min = (request.GET.get("min_date") or "").strip()
        raw_max = (request.GET.get("max_date") or "").strip()

        min_d = OrdersExportExcel._parse_date_yyyy_mm_dd(raw_min)
        max_d = OrdersExportExcel._parse_date_yyyy_mm_dd(raw_max)

        max_provided = bool(raw_max)
        if max_d is None:
            max_d = today
        if min_d is None:
            min_d = today - timedelta(days=1)

        if min_d > max_d:
            min_d, max_d = max_d, min_d

        return min_d, max_d, max_provided

    @staticmethod
    def _period_days_inclusive(min_d: date_cls, max_d: date_cls) -> int:
        return int((max_d - min_d).days) + 1

    @staticmethod
    def _grain_for_period(days_inclusive: int) -> Tuple[int, str]:
        # Requirement: daily if <= 31 days, otherwise rolling 7-day buckets; never monthly
        if days_inclusive <= 31:
            return 1, "Jour"
        return 7, "Semaine"

    @staticmethod
    def _ceil_div(a: int, b: int) -> int:
        return (a + b - 1) // b

    @staticmethod
    def _build_buckets(min_d: date_cls, max_d: date_cls, bucket_size: int) -> List[date_cls]:
        days = OrdersExportExcel._period_days_inclusive(min_d, max_d)
        n_buckets = OrdersExportExcel._ceil_div(days, bucket_size)
        return [min_d + timedelta(days=i * bucket_size) for i in range(n_buckets)]

    @staticmethod
    def _fr_month_abbrev(m: int) -> str:
        return {
            1: "Jan", 2: "Fev", 3: "Mar", 4: "Avr", 5: "Mai", 6: "Jun",
            7: "Jul", 8: "Aou", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec",
        }.get(int(m), "Mois")

    @classmethod
    def _timeline_labels(cls, bucket_starts: List[date_cls], bucket_size: int) -> List[str]:
        out: List[str] = []
        if not bucket_starts:
            return out

        if bucket_size == 1:
            for i, d in enumerate(bucket_starts):
                if d.day == 1 and d.month == 1:
                    out.append(f"01 {cls._fr_month_abbrev(1)} {d.year}")
                elif d.day == 1:
                    out.append(f"01 {cls._fr_month_abbrev(d.month)}")
                elif i == 0:
                    out.append(f"{d.day:02d} {cls._fr_month_abbrev(d.month)}")
                else:
                    out.append(f"{d.day:02d}")
            return out

        for i, s in enumerate(bucket_starts):
            e = s + timedelta(days=bucket_size - 1)
            if s.year != e.year:
                out.append(
                    f"{s.day:02d} {cls._fr_month_abbrev(s.month)} {s.year}–"
                    f"{e.day:02d} {cls._fr_month_abbrev(e.month)} {e.year}"
                )
                continue
            if s.month == e.month:
                core = f"{s.day:02d}–{e.day:02d} {cls._fr_month_abbrev(s.month)}"
            else:
                core = f"{s.day:02d} {cls._fr_month_abbrev(s.month)}–{e.day:02d} {cls._fr_month_abbrev(e.month)}"
            out.append(f"{core} {s.year}" if i == 0 else core)
        return out

    # -----------------------
    # Type classification
    # -----------------------
    @staticmethod
    def _order_type(order: Order) -> str:
        if (getattr(order, "pharmacy_id", None) is not None) and (getattr(order, "gros_id", None) is not None):
            return "PH_GROS"

        if (
            (getattr(order, "pharmacy_id", None) is not None)
            and (getattr(order, "gros_id", None) is None)
            and (getattr(order, "super_gros_id", None) is not None)
        ):
            return "GROS_SUPER"

        if (
            (getattr(order, "pharmacy_id", None) is None)
            and (getattr(order, "gros_id", None) is not None)
            and (getattr(order, "super_gros_id", None) is not None)
        ):
            return "GROS_SUPER"

        if (
            (getattr(order, "pharmacy_id", None) is None)
            and (getattr(order, "gros_id", None) is None)
            and (getattr(order, "super_gros_id", None) is not None)
        ):
            return "OFFICE"

        return "anomalie"

    # -----------------------
    # Filters / scoping
    # -----------------------
    @staticmethod
    def _resolve_requested_users(request) -> List[str]:
        us = OrdersExportExcel._parse_csv_param(request.GET.get("user"))
        if not us:
            return []
        target_users = set(us)
        try:
            from accounts.models import UserProfile
            from django.contrib.auth import get_user_model as _get_user_model
            _UserModel = _get_user_model()

            # Supervisor expansion: add all users in the same region
            supervisors = UserProfile.objects.filter(user__username__in=us, rolee="Superviseur")
            for sup in supervisors:
                if sup.region and sup.region != "-":
                    regional_users = UserProfile.objects.filter(region=sup.region).values_list('user__username', flat=True)
                    target_users.update(regional_users)

            # Country Manager expansion: all supervisors + all users in any supervisor's usersunder list
            country_managers = UserProfile.objects.filter(user__username__in=us, rolee="CountryManager")
            if country_managers.exists():
                # All supervisors
                sup_usernames = UserProfile.objects.filter(
                    rolee="Superviseur"
                ).values_list('user__username', flat=True)
                target_users.update(sup_usernames)
                # All users that appear in any supervisor's usersunder (no duplicates via set)
                users_under_supervisors = _UserModel.objects.filter(
                    under__rolee="Superviseur"
                ).values_list('username', flat=True)
                target_users.update(users_under_supervisors)
        except Exception:
            pass
        return list(target_users)

    def apply_filters(self, request, effective_min: date_cls, effective_max: date_cls) -> Dict:
        filters: Dict = {
            "added__date__gte": effective_min,
            "added__date__lte": effective_max,
        }

        if request.GET.get("produit"):
            filters["orderitem__produit__id"] = request.GET.get("produit")

        if request.GET.get("status"):
            st = self._parse_csv_param(request.GET.get("status"))
            if st:
                filters["status__in"] = st

        if request.GET.get("user"):
            resolved_users = self._resolve_requested_users(request)
            if resolved_users:
                filters["user__username__in"] = resolved_users
        elif request.GET.get("user_region"):
            # No specific user selected — scope to all active users in the chosen region
            from accounts.models import UserProfile as _UP
            region_usernames = list(
                _UP.objects.filter(
                    region=request.GET.get("user_region"),
                    is_human=True,
                    user__is_active=True,
                ).values_list("user__username", flat=True)
            )
            if region_usernames:
                filters["user__username__in"] = region_usernames

        if request.GET.get("source"):
            sources = {"Pharmacie": "pharmacy__isnull", "Gros": "gros__isnull", "Supergros": "super_gros__isnull"}
            key = request.GET.get("source")
            if key in sources:
                filters[sources[key]] = False

        if request.GET.get("client"):
            clients = {"Pharmacie": "pharmacy__isnull", "Gros": "gros__isnull", "Supergros": "super_gros__isnull"}
            key = request.GET.get("client")
            if key in clients:
                filters[clients[key]] = False

        return filters

    def apply_keyword_filter(self, request) -> Q:
        q = Q()
        keyword = request.GET.get("keyword")
        if keyword:
            q |= Q(pharmacy__nom__icontains=keyword)
            q |= Q(gros__nom__icontains=keyword)
            q |= Q(super_gros__name__icontains=keyword)
        return q

    def get_filtered_orders(self, request, filters: Dict, q: Q):
        orders = Order.objects.filter(**filters).filter(q).order_by("-added").distinct()

        if request.GET.get("office") == "1":
            orders = orders.filter(from_company=True)

        if request.GET.get("attente") == "1":
            orders = orders.filter(flag=True)

        if request.GET.get("flag") == "1":
            orders = orders.exclude(status="traite")

        try:
            up = request.user.userprofile
            rolee = getattr(up, "rolee", "")
            spec = getattr(up, "speciality_rolee", "")
        except Exception:
            rolee, spec = "", ""

        if (
            rolee not in ["Superviseur", "CountryManager"]
            and not request.user.is_superuser
            and request.user.username not in ["liliumdz"]
            and spec not in ["Office"]
        ):
            orders = orders.filter(
                Q(user=request.user) | Q(touser=request.user) | Q(user__username__in=["MeriemDZ", "ibtissemdz"])
            ).distinct()

        elif (rolee == "Superviseur" and spec not in ["Superviseur_national"]):
            orders = orders.filter(
                Q(user=request.user)
                | Q(user__in=up.usersunder.all())
                | Q(touser=request.user)
                | Q(touser__in=up.usersunder.all())
                | Q(user__username__in=["MeriemDZ", "ibtissemdz"])
            ).distinct()

        elif spec in ["Office"] or request.user.username in ["ibtissemdz", "RABTIDZ", "a.lounis@liliumpharma.com"]:
            orders = orders

        if spec in ["Superviseur_national"]:
            orders = orders.filter(
                Q(user=request.user)
                | Q(touser=request.user)
                | Q(user__in=up.usersunder.all())
                | Q(touser__in=up.usersunder.all())
                | Q(user__username__in=["MeriemDZ", "ibtissemdz"])
            ).distinct()

        return orders.distinct()

    # -----------------------
    # Main
    # -----------------------
    def get(self, request, *args, **kwargs):
        eff_min, eff_max, max_provided = self._resolve_effective_dates(request)
        eff_min_str = eff_min.strftime("%Y-%m-%d")
        eff_max_str = eff_max.strftime("%Y-%m-%d")

        end_ar = (request.GET.get("max_date") or "").strip() or "اليوم"
        start_ar = eff_min_str
        RLM = "\u200f"
        LRM = "\u200e"
        date_span = f"{eff_min_str} → {end_ar}"

        def _rtl_title(ar_core: str) -> str:
            return f"{RLM}{ar_core}{RLM} {LRM}{date_span}{LRM}"

        filters = self.apply_filters(request, eff_min, eff_max)
        q = self.apply_keyword_filter(request)

        orders_qs = (
            self.get_filtered_orders(request, filters, q)
            .select_related("user", "user__userprofile", "touser", "pharmacy", "gros", "super_gros")
            .distinct()
        )
        orders_all: List[Order] = list(orders_qs)

        requested_users = self._resolve_requested_users(request)
        if requested_users:
            allowed = {str(o.user.username) for o in orders_all}
            effective_users = [u for u in requested_users if u in allowed]
            sel_set = set(effective_users)
            orders = [o for o in orders_all if str(o.user.username) in sel_set]
        else:
            orders = orders_all
            effective_users = sorted({str(o.user.username) for o in orders})

        single_user_mode = bool(requested_users) and (len(effective_users) == 1)
        comparison_mode = not single_user_mode
        single_user = _xlsx_safe(effective_users[0]) if single_user_mode else ""

        order_type: Dict[int, str] = {o.id: self._order_type(o) for o in orders}
        order_ids = [o.id for o in orders]

        items_qs = (
            OrderItem.objects.filter(order_id__in=order_ids)
            .select_related("produit")
            .order_by("order_id", "id")
        )

        items_by_order: Dict[int, List[OrderItem]] = defaultdict(list)
        order_total_qty: Dict[int, int] = defaultdict(int)
        order_total_value: Dict[int, float] = defaultdict(float)
        product_totals: Dict[str, int] = defaultdict(int)

        type_prod_totals: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))

        for it in items_qs:
            oid = it.order_id
            items_by_order[oid].append(it)

            pname = _xlsx_safe(getattr(it.produit, "nom", ""))
            qty = int(getattr(it, "qtt", 0) or 0)

            unit_price = float(getattr(it.produit, "price", 0) or 0)
            line_value = float(qty) * float(unit_price)

            product_totals[pname] += qty
            order_total_qty[oid] += qty
            order_total_value[oid] += line_value

            t = order_type.get(oid, "anomalie")
            type_prod_totals[t][pname] += qty

        product_names_sorted = sorted(product_totals.keys(), key=lambda s: s.lower())
        product_headers_unique = _make_unique_headers(product_names_sorted)
        prod_by_index = product_names_sorted

        dash_orders = [o for o in orders if order_type.get(o.id) in ("PH_GROS", "GROS_SUPER")]

        days_inclusive = self._period_days_inclusive(eff_min, eff_max)
        bucket_size, grain_fr = self._grain_for_period(days_inclusive)
        bucket_starts = self._build_buckets(eff_min, eff_max, bucket_size)
        timeline_labels = self._timeline_labels(bucket_starts, bucket_size) or ["-"]
        n_t = len(timeline_labels)

        # short range rule (<= 7 days => bars, >= 8 days => lines)
        short_range_bars = days_inclusive <= 7

        med_orders_t = [0] * n_t
        med_qty_t = [0] * n_t
        med_val_t = [0.0] * n_t

        com_orders_t = [0] * n_t
        com_qty_t = [0] * n_t
        com_val_t = [0.0] * n_t

        med_cnt_by_user: Dict[str, int] = defaultdict(int)
        med_qty_by_user: Dict[str, int] = defaultdict(int)
        med_val_by_user: Dict[str, float] = defaultdict(float)

        com_cnt_by_user: Dict[str, int] = defaultdict(int)
        com_qty_by_user: Dict[str, int] = defaultdict(int)
        com_val_by_user: Dict[str, float] = defaultdict(float)

        for o in dash_orders:
            oid = o.id
            t = order_type.get(oid)
            
            # --- UPDATE: Bulletproof specialty_rolee logic ---
            try:
                # Get profile safely, handling if it doesn't exist
                up = getattr(o.user, "userprofile", None)
                spec_val = ""
                if up:
                    # Prioritize correct spelling, fallback to old spelling
                    spec_val = getattr(up, "specialty_rolee", getattr(up, "speciality_rolee", ""))
                
                # If still empty, check the user object directly just in case
                if not spec_val:
                    # Prioritize correct spelling, fallback to old spelling
                    spec_val = getattr(o.user, "specialty_rolee", getattr(o.user, "speciality_rolee", ""))
                    
                spec = str(spec_val).strip() if spec_val else ""
                
                # Clean up if Django returns a string literal of "None"
                if spec in ["None", "null", "-"]: 
                    spec = ""
                    
            except Exception:
                spec = ""
                
            raw_uname = _xlsx_safe(o.user.username)
            uname = f"{spec} : {raw_uname}" if spec else raw_uname

            d = o.added.date()
            if d < eff_min or d > eff_max:
                continue

            idx = int((d - eff_min).days) // int(bucket_size)
            if idx < 0:
                continue
            if idx >= n_t:
                idx = n_t - 1

            qty = int(order_total_qty.get(oid, 0))
            val = float(order_total_value.get(oid, 0.0))

            if t == "PH_GROS":
                med_cnt_by_user[uname] += 1
                med_qty_by_user[uname] += qty
                med_val_by_user[uname] += val
                if single_user_mode and uname == single_user:
                    med_orders_t[idx] += 1
                    med_qty_t[idx] += qty
                    med_val_t[idx] += val

            elif t == "GROS_SUPER":
                com_cnt_by_user[uname] += 1
                com_qty_by_user[uname] += qty
                com_val_by_user[uname] += val
                if single_user_mode and uname == single_user:
                    com_orders_t[idx] += 1
                    com_qty_t[idx] += qty
                    com_val_t[idx] += val

        # -------- Top 3 clients (single user only) --------
        top_pharm_rows: List[Tuple[str, int]] = []
        top_gros_rows: List[Tuple[str, int]] = []
        if single_user_mode:
            pharm_counts: Dict[str, int] = defaultdict(int)
            gros_counts: Dict[str, int] = defaultdict(int)

            for o in orders:
                if _xlsx_safe(o.user.username) != single_user:
                    continue
                t = order_type.get(o.id)
                if t == "PH_GROS":
                    nm = _xlsx_safe(getattr(getattr(o, "pharmacy", None), "nom", "-")) or "-"
                    pharm_counts[nm] += 1
                elif t == "GROS_SUPER":
                    nm = _xlsx_safe(getattr(getattr(o, "gros", None), "nom", "-")) or "-"
                    gros_counts[nm] += 1

            top_pharm_rows = sorted(pharm_counts.items(), key=lambda x: (x[1], x[0]), reverse=True)[:3]
            top_gros_rows = sorted(gros_counts.items(), key=lambda x: (x[1], x[0]), reverse=True)[:3]

        # -----------------------
        # Workbook
        # -----------------------
        output = BytesIO()
        wb = xlsxwriter.Workbook(
            output,
            {
                "in_memory": True,
                "remove_timezone": True,
                "strings_to_formulas": False,
                "strings_to_urls": False,
                "nan_inf_to_errors": True,
            },
        )

        DARK = "#1B5E20"
        MED = "#2E7D32"
        LIGHT = "#E8F5E9"
        GRID = "#D9D9D9"

        fmt_title = wb.add_format({"bold": True, "font_size": 14, "bg_color": DARK, "font_color": "white"})
        fmt_section = wb.add_format({"bold": True, "font_size": 11, "bg_color": MED, "font_color": "white"})
        fmt_k = wb.add_format({"bold": True, "bg_color": LIGHT, "border": 1})
        fmt_cell = wb.add_format({"border": 1})
        fmt_num = wb.add_format({"border": 1, "num_format": "0"})
        fmt_money = wb.add_format({"border": 1, "num_format": "#,##0.00"})
        fmt_pct = wb.add_format({"border": 1, "num_format": "0.0%"})
        fmt_date = wb.add_format({"border": 1, "num_format": "yyyy-mm-dd"})
        fmt_warn = wb.add_format({"bold": True, "font_color": "#B71C1C"})
        fmt_center = wb.add_format({"border": 1, "align": "center", "valign": "vcenter"})
        fmt_center_k = wb.add_format({"border": 1, "align": "center", "valign": "vcenter", "bold": True, "bg_color": LIGHT})

        # Colors for the roles
        fmt_role_blue = wb.add_format({"font_color": "#0D47A1", "bold": True})    # Commercial
        fmt_role_green = wb.add_format({"font_color": "#2E7D32", "bold": True})   # Medico_commercial
        fmt_role_red = wb.add_format({"font_color": "#B71C1C", "bold": True})     # Superviseur
        # Color for the username (standard black)
        fmt_user_black = wb.add_format({"font_color": "#000000", "bold": False}) 
        # The base cell format (to keep the border)
        fmt_cell = wb.add_format({"border": 1})

        # =========================
        # Sheet: Sommaire
        # =========================
        ws_sum = wb.add_worksheet("Sommaire")
        ws_sum.hide_gridlines(2)
        ws_sum.set_tab_color(MED)

        ws_sum.set_column(0, 0, 16)
        ws_sum.set_column(1, 1, 14)
        ws_sum.set_column(2, 2, 12)
        ws_sum.set_column(3, 3, 18)
        ws_sum.set_column(4, 5, 34)
        ws_sum.set_column(6, 6 + len(product_headers_unique) - 1, 14)
        ws_sum.set_column(6 + len(product_headers_unique), 6 + len(product_headers_unique), 18)

        r = 0
        last_col_sum = 6 + len(product_headers_unique)
        ws_sum.merge_range(r, 0, r, last_col_sum, "SOMMAIRE — Export Excel", fmt_title)
        r += 2

        ws_sum.merge_range(r, 0, r, last_col_sum, "Filtres appliqués", fmt_section)
        r += 1

        filter_lines = [
            ("Utilisateur(s)", request.GET.get("user") or "Tous"),
            ("Du (min_date)", eff_min_str),
            ("Au (max_date)", eff_max_str),
            ("Produit (id)", request.GET.get("produit") or "-"),
            ("Status", request.GET.get("status") or "-"),
            ("Keyword", request.GET.get("keyword") or "-"),
            ("Source", request.GET.get("source") or "-"),
            ("Client", request.GET.get("client") or "-"),
            ("Office Lilium (param office)", _yn(request.GET.get("office") == "1")),
            ("En attente (param attente)", _yn(request.GET.get("attente") == "1")),
            ("Flag ≠ traité (param flag)", _yn(request.GET.get("flag") == "1")),
            ("Exporté le", timezone.now().strftime("%Y-%m-%d %H:%M")),
            ("Nombre de commandes", str(len(orders))),
        ]
        for k, v in filter_lines:
            ws_sum.write_string(r, 0, _xlsx_safe(k), fmt_k)
            ws_sum.merge_range(r, 1, r, last_col_sum, _xlsx_safe(v), fmt_cell)
            r += 1

        r += 1

        ws_sum.merge_range(r, 0, r, last_col_sum, "Totaux par type de transaction (Qté)", fmt_section)
        r += 1

        small_start_col = 5
        small_headers = ["Type"] + product_headers_unique + ["Totale"]

        type_rows_order = ["OFFICE", "GROS_SUPER", "PH_GROS", "anomalie"]
        small_data = []
        for t in type_rows_order:
            row_vals = [_xlsx_safe(t)]
            total = 0
            for pname in prod_by_index:
                qv = int(type_prod_totals.get(t, {}).get(pname, 0))
                row_vals.append(qv)
                total += qv
            row_vals.append(total)
            small_data.append(row_vals)

        small_first_row = r
        small_last_row = r + len(small_data)
        small_last_col = small_start_col + len(small_headers) - 1

        small_columns = [{"header": "Type", "format": fmt_cell}]
        for h in product_headers_unique:
            small_columns.append({"header": h, "format": fmt_num})
        small_columns.append({"header": "Totale", "format": fmt_num})

        ws_sum.add_table(
            small_first_row, small_start_col, small_last_row, small_last_col,
            {
                "data": small_data,
                "columns": small_columns,
                "style": "Table Style Medium 21",
                "autofilter": False,
                "banded_rows": True,
            },
        )

        r = small_last_row + 2

        ws_sum.merge_range(r, 0, r, last_col_sum, "Table Sommaire", fmt_section)
        r += 1

        sum_headers = (
            ["Bon de commande", "Date", "Type", "Utilisateur", "Client", "Fournisseur"]
            + product_headers_unique
            + ["Total valeur (DA)"]
        )

        sommaire_rows = []
        for o in orders:
            oid = o.id
            uname = _xlsx_safe(o.user.username)
            client, fournisseur = _get_client_fournisseur(o)
            typ = order_type.get(oid) or "anomalie"

            prod_qty_map = defaultdict(int)
            for it in items_by_order.get(oid, []):
                pn = _xlsx_safe(getattr(it.produit, "nom", ""))
                prod_qty_map[pn] += int(getattr(it, "qtt", 0) or 0)

            row = [
                int(oid),
                o.added.date(),
                _xlsx_safe(typ),
                uname,
                _xlsx_safe(client),
                _xlsx_safe(fournisseur),
            ]
            for pname in prod_by_index:
                row.append(int(prod_qty_map.get(pname, 0)))
            row.append(float(order_total_value.get(oid, 0.0)))
            sommaire_rows.append(row)

        if not sommaire_rows:
            sommaire_rows = [[0, timezone.localdate(), "anomalie", "-", "-", "-", *([0] * len(product_headers_unique)), 0.0]]

        table_first_row = r
        table_last_row = r + len(sommaire_rows)
        table_last_col = len(sum_headers) - 1

        columns = [
            {"header": "Bon de commande", "format": fmt_num},
            {"header": "Date", "format": fmt_date},
            {"header": "Type", "format": fmt_cell},
            {"header": "Utilisateur", "format": fmt_cell},
            {"header": "Client", "format": fmt_cell},
            {"header": "Fournisseur", "format": fmt_cell},
        ]
        for h in sum_headers[6:-1]:
            columns.append({"header": h, "format": fmt_num})
        columns.append({"header": "Total valeur (DA)", "format": fmt_money})

        ws_sum.add_table(
            table_first_row, 0, table_last_row, table_last_col,
            {
                "data": sommaire_rows,
                "columns": columns,
                "style": "Table Style Medium 21",
                "autofilter": True,
                "banded_rows": True,
            },
        )

        # =========================
        # Sheet: Donnees Graphiques (hidden)
        # =========================
        ws_data = wb.add_worksheet("Donnees Graphiques")
        ws_data.hide_gridlines(2)
        ws_data.hide()

        row_time0 = 0
        ws_data.write_row(
            row_time0, 0,
            ["Temps", "MED Nb", "MED Qté", "MED Valeur (DA)", "COM Nb", "COM Qté", "COM Valeur (DA)"],
            fmt_k
        )
        for i, lab in enumerate(timeline_labels, start=1):
            ws_data.write_string(row_time0 + i, 0, _xlsx_safe(lab), fmt_cell)
            ws_data.write_number(row_time0 + i, 1, int(med_orders_t[i - 1]), fmt_num)
            ws_data.write_number(row_time0 + i, 2, int(med_qty_t[i - 1]), fmt_num)
            ws_data.write_number(row_time0 + i, 3, float(med_val_t[i - 1]), fmt_money)
            ws_data.write_number(row_time0 + i, 4, int(com_orders_t[i - 1]), fmt_num)
            ws_data.write_number(row_time0 + i, 5, int(com_qty_t[i - 1]), fmt_num)
            ws_data.write_number(row_time0 + i, 6, float(com_val_t[i - 1]), fmt_money)

        time_last = row_time0 + len(timeline_labels)

        def _write_metric_block(start_row: int, header: str, metric: Dict[str, float], money: bool) -> Tuple[int, int, int]:
            items = [(u, float(v)) for u, v in metric.items() if float(v) > 0]
            items.sort(key=lambda x: x[1], reverse=True)

            ws_data.write_row(start_row, 0, ["Utilisateur", header], fmt_k)

            if not items:
                ws_data.write_string(start_row + 1, 0, "-", fmt_cell)
                ws_data.write_number(start_row + 1, 1, 0.0, fmt_money if money else fmt_num)
                return start_row, start_row + 1, 1

            for j, (u, v) in enumerate(items, start=1):
                # --- UPDATE: Color Logic for Roles ---
                # Inside your loop where you process users
                if " : " in u:
                    role, name = u.split(" : ", 1)
    
                    # 1. Pick the color based on the role
                    if role == "Commercial":
                        role_fmt = fmt_role_blue
                    elif role == "Medico_commercial":
                        role_fmt = fmt_role_green
                    elif "Superviseur" in role:
                        role_fmt = fmt_role_red
                    else:
                        role_fmt = fmt_user_black # Default if role is unknown

                    # 2. Write the rich string: [Format1, String1, Format2, String2, BaseCellFormat]
                    ws_data.write_rich_string(
                        start_row + j, 0, 
                        role_fmt, role,          # Role in its specific color
                        fmt_user_black, f" : {name}", # Username in black
                        fmt_cell                 # Applies the border to the whole cell
                    )
                else:
                    ws_data.write_string(start_row + j, 0, _xlsx_safe(u), fmt_cell)
                
                ws_data.write_number(start_row + j, 1, float(v), fmt_money if money else fmt_num)

            last_row = start_row + len(items)
            return start_row, last_row, len(items)

        def _write_top_clients_block(
            start_row: int,
            left_header: str,
            right_header: str,
            rows: List[Tuple[str, int]],
        ) -> Tuple[int, int, int]:
            ws_data.write_row(start_row, 0, [_xlsx_safe(left_header), _xlsx_safe(right_header)], fmt_k)
            if not rows:
                ws_data.write_string(start_row + 1, 0, "-", fmt_cell)
                ws_data.write_number(start_row + 1, 1, 0, fmt_num)
                return start_row, start_row + 1, 1

            for j, (name, cnt) in enumerate(rows, start=1):
                ws_data.write_string(start_row + j, 0, _xlsx_safe(name), fmt_cell)
                ws_data.write_number(start_row + j, 1, int(cnt), fmt_num)

            last_row = start_row + len(rows)
            return start_row, last_row, len(rows)

        row = time_last + 3

        # Medical blocks
        med_orders_row0, med_orders_last, n_med_orders = _write_metric_block(
            row, "Nb commandes", {k: float(v) for k, v in med_cnt_by_user.items()}, money=False
        )
        row = med_orders_last + 3
        med_qty_row0, med_qty_last, n_med_qty = _write_metric_block(
            row, "Qté totale", {k: float(v) for k, v in med_qty_by_user.items()}, money=False
        )
        row = med_qty_last + 3
        med_val_row0, med_val_last, n_med_val = _write_metric_block(
            row, "Valeur (DA)", {k: float(v) for k, v in med_val_by_user.items()}, money=True
        )
        row = med_val_last + 5

        # Commercial blocks
        com_orders_row0, com_orders_last, n_com_orders = _write_metric_block(
            row, "Nb commandes", {k: float(v) for k, v in com_cnt_by_user.items()}, money=False
        )
        row = com_orders_last + 3
        com_qty_row0, com_qty_last, n_com_qty = _write_metric_block(
            row, "Qté totale", {k: float(v) for k, v in com_qty_by_user.items()}, money=False
        )
        row = com_qty_last + 3
        com_val_row0, com_val_last, n_com_val = _write_metric_block(
            row, "Valeur (DA)", {k: float(v) for k, v in com_val_by_user.items()}, money=True
        )

        # Top clients blocks (single user only)
        med_top_ph_block: Optional[Tuple[int, int, int]] = None
        com_top_gros_block: Optional[Tuple[int, int, int]] = None
        row = com_val_last + 5
        if single_user_mode:
            med_top_ph_block = _write_top_clients_block(row, "Pharmacie", "Nb commandes", top_pharm_rows)
            row = med_top_ph_block[1] + 3
            com_top_gros_block = _write_top_clients_block(row, "Grossiste", "Nb commandes", top_gros_rows)

        # =========================
        # Dashboards (two sheets)
        # =========================
        

        def _x_axis_opts(n_points: int) -> Dict:
            interval = max(1, n_points // 12) if n_points > 14 else 1
            rotation = -45 if n_points > 10 else 0
            return {"name": "Temps", "interval_unit": interval, "num_font": {"size": 9, "rotation": rotation}}

        def _rows_for_px(px: int) -> int:
            return int(px / 18) + 3

        def _bar_height_for(ncats: int) -> int:
            return int(min(2200, max(360, 120 + 28 * max(1, ncats))))

        BAR_GAP = 50

        DL_NUM = {
            "value": True, "position": "outside_end", "num_format": "0",
            "font": {"color": "#263238", "bold": True}, "fill": {"color": "#FFFFFF"}, "border": {"color": "#B0BEC5"},
        }
        DL_MONEY = {
            "value": True, "position": "outside_end", "num_format": "#,##0.00",
            "font": {"color": "#263238", "bold": True}, "fill": {"color": "#FFFFFF"}, "border": {"color": "#B0BEC5"},
        }

        def _make_bar(title_ar: str, row0: int, last: int, fill_color: str, dl, t_dark, t_light, t_med, title_color):
            ch = wb.add_chart({"type": "bar"})
            ch.set_style(10)
            ch.set_chartarea({"fill": {"color": t_light}, "border": {"color": t_med}})
            ch.set_plotarea({"fill": {"color": "white"}})
            ch.set_title({"name": title_ar, "name_font": {"color": title_color}})
            ch.set_legend({"none": True})
            ch.set_x_axis({"major_gridlines": {"visible": False}})
            ch.set_y_axis({"num_font": {"size": 9}})
            ch.add_series({
                "categories": ["Donnees Graphiques", row0 + 1, 0, last, 0],
                "values":     ["Donnees Graphiques", row0 + 1, 1, last, 1],
                "gap": BAR_GAP,
                "data_labels": dl,
                "fill": {"color": fill_color},
                "border": {"color": t_dark},
            })
            return ch

        def _make_time_series_chart(title_ar: str, col_values: int, y_name: str, fill_color: str, money: bool, t_dark, t_light, t_med, title_color):
            ch = wb.add_chart({"type": "column" if short_range_bars else "line"})
            ch.set_style(10)
            ch.set_chartarea({"fill": {"color": t_light}, "border": {"color": t_med}})
            ch.set_plotarea({"fill": {"color": "white"}})
            ch.set_title({"name": title_ar, "name_font": {"color": title_color}})
            ch.set_legend({"none": True})
            ch.set_y_axis({"name": y_name, "major_gridlines": {"visible": True, "line": {"color": GRID}}})
            ch.set_x_axis(_x_axis_opts(len(timeline_labels)))
            
            series_opts = {
                "categories": ["Donnees Graphiques", row_time0 + 1, 0, time_last, 0],
                "values":     ["Donnees Graphiques", row_time0 + 1, col_values, time_last, col_values],
            }
            if short_range_bars:
                series_opts.update({
                    "gap": 75,
                    "fill": {"color": fill_color},
                    "border": {"color": t_dark},
                    "data_labels": {"value": True, "num_format": "#,##0.00" if money else "0"},
                })
            else:
                series_opts.update({
                    "line": {"color": fill_color, "width": 2.25},
                })
                
            ch.add_series(series_opts)
            ch.set_size({"width": 1240, "height": 300})
            return ch

        def _render_dashboard(sheet_name: str, channel: str):
            # Excel Charts enforce ONE color per title. 
            # Defaulting to standard dark gray/black to keep the base title intact per request.
            title_color = "#263238" 

            if channel == "MED":
                t_dark, t_med, t_light = DARK, MED, LIGHT  # Green Theme
                suffix = "من فارماسي لجروسيست"
            else:
                t_dark, t_med, t_light = "#0D47A1", "#1976D2", "#E3F2FD" # Blue Theme
                suffix = "من جروسيست لسوبر جرو"

            # Re-applying theme colors for the Sheet Titles (Cells support rich colors)
            dash_title_fmt = wb.add_format({"bold": True, "font_size": 16, "bg_color": t_dark, "font_color": "white"})
            dash_band_fmt = wb.add_format({"bold": True, "font_size": 12, "bg_color": t_med, "font_color": "white"})

            ws = wb.add_worksheet(sheet_name)
            ws.hide_gridlines(2)
            ws.set_tab_color(t_dark)
            ws.set_column(0, 0, 2)
            ws.set_column(1, 1, 42)
            ws.set_column(2, 12, 18)

            ws.merge_range(0, 0, 0, 12, sheet_name, dash_title_fmt)

            if channel == "MED":
                col_nb, col_qty, col_val = 1, 2, 3
                b_orders = (med_orders_row0, med_orders_last, n_med_orders)
                b_qty = (med_qty_row0, med_qty_last, n_med_qty)
                b_val = (med_val_row0, med_val_last, n_med_val)
            else:
                col_nb, col_qty, col_val = 4, 5, 6
                b_orders = (com_orders_row0, com_orders_last, n_com_orders)
                b_qty = (com_qty_row0, com_qty_last, n_com_qty)
                b_val = (com_val_row0, com_val_last, n_com_val)

            if comparison_mode:
                r0 = 2
                ws.merge_range(r0, 0, r0, 12, "مقارنة | مقارنة", dash_band_fmt)
                r0 += 1

                # Determine the hardcoded title based on the channel
                if channel == "MED":
                    t1_text = "ترتيب المندوبين حسب عدد الطلبيات من فارماسي لجروسيست"
                    t2_text = "ترتيب المندوبين حسب مجموع القطع في الطلبيات من فارماسي لجروسيست"
                    t3_text = "ترتيب المندوبين حسب مجموع قيمة القطع في الطلبيات من فارماسي لجروسيست"
                else:
                    t1_text = "ترتيب المندوبين حسب عدد الطلبيات من جروسيست لسوبر جرو"
                    t2_text = "ترتيب المندوبين حسب مجموع القطع في الطلبيات من جروسيست لسوبر جرو"
                    t3_text = "ترتيب المندوبين حسب مجموع قيمة القطع في الطلبيات من جروسيست لسوبر جرو"

                title1 = _rtl_title(t1_text)
                ch1 = _make_bar(title1, b_orders[0], b_orders[1], t_med, DL_NUM, t_dark, t_light, t_med, title_color)
                ch1.set_size({"width": 1240, "height": _bar_height_for(b_orders[2])})
                ws.insert_chart(xl_rowcol_to_cell(r0, 0), ch1, {"x_offset": 18, "y_offset": 12})
                r0 += _rows_for_px(_bar_height_for(b_orders[2])) + 1

                title2 = _rtl_title(t2_text)
                ch2 = _make_bar(title2, b_qty[0], b_qty[1], t_dark, DL_NUM, t_dark, t_light, t_med, title_color)
                ch2.set_size({"width": 1240, "height": _bar_height_for(b_qty[2])})
                ws.insert_chart(xl_rowcol_to_cell(r0, 0), ch2, {"x_offset": 18, "y_offset": 12})
                r0 += _rows_for_px(_bar_height_for(b_qty[2])) + 1

                title3 = _rtl_title(t3_text)
                ch3 = _make_bar(title3, b_val[0], b_val[1], t_med, DL_MONEY, t_dark, t_light, t_med, title_color)
                ch3.set_size({"width": 1240, "height": _bar_height_for(b_val[2])})
                ws.insert_chart(xl_rowcol_to_cell(r0, 0), ch3, {"x_offset": 18, "y_offset": 12})
            else:
                r0 = 2
                ws.merge_range(r0, 0, r0, 12, f"تطور | {grain_fr}", dash_band_fmt)
                r0 += 1

                if channel == "MED":
                    t1_text = "تطور عدد الطلبيات من فارماسي لجروسيست"
                    t2_text = "تطور مجموع القطع من فارماسي لجروسيست"
                    t3_text = "تطور مجموع قيمة القطع من فارماسي لجروسيست"
                    t4_text = "أفضل 3 صيدليات حسب عدد الطلبيات من فارماسي لجروسيست"
                else:
                    t1_text = "تطور عدد الطلبيات من جروسيست لسوبر جرو"
                    t2_text = "تطور مجموع القطع من جروسيست لسوبر جرو"
                    t3_text = "تطور مجموع قيمة القطع من جروسيست لسوبر جرو"
                    t4_text = "أفضل 3 موزعين حسب عدد الطلبيات من جروسيست لسوبر جرو"

                t1 = _rtl_title(t1_text)
                ch1 = _make_time_series_chart(t1, col_nb, "عدد", t_med, False, t_dark, t_light, t_med, title_color)
                ws.insert_chart(xl_rowcol_to_cell(r0, 0), ch1, {"x_offset": 18, "y_offset": 10})
                r0 += _rows_for_px(300) + 1

                t2 = _rtl_title(t2_text)
                ch2 = _make_time_series_chart(t2, col_qty, "كمية", t_dark, False, t_dark, t_light, t_med, title_color)
                ws.insert_chart(xl_rowcol_to_cell(r0, 0), ch2, {"x_offset": 18, "y_offset": 10})
                r0 += _rows_for_px(300) + 1

                t3 = _rtl_title(t3_text)
                ch3 = _make_time_series_chart(t3, col_val, "قيمة (DA)", t_med, True, t_dark, t_light, t_med, title_color)
                ch3.set_size({"width": 1240, "height": 310})
                ws.insert_chart(xl_rowcol_to_cell(r0, 0), ch3, {"x_offset": 18, "y_offset": 12})
                r0 += _rows_for_px(310) + 1

                if single_user_mode:
                    ws.merge_range(r0, 0, r0, 12, "أفضل 3 عملاء", dash_band_fmt)
                    r0 += 1
                    title4 = _rtl_title(t4_text)
                    
                    if channel == "MED" and med_top_ph_block is not None:
                        ch4 = _make_bar(title4, med_top_ph_block[0], med_top_ph_block[1], t_dark, DL_NUM, t_dark, t_light, t_med, title_color)
                        ch4.set_size({"width": 1240, "height": _bar_height_for(med_top_ph_block[2])})
                        ws.insert_chart(xl_rowcol_to_cell(r0, 0), ch4, {"x_offset": 18, "y_offset": 12})

                    if channel == "COM" and com_top_gros_block is not None:
                        ch4 = _make_bar(title4, com_top_gros_block[0], com_top_gros_block[1], t_dark, DL_NUM, t_dark, t_light, t_med, title_color)
                        ch4.set_size({"width": 1240, "height": _bar_height_for(com_top_gros_block[2])})
                        ws.insert_chart(xl_rowcol_to_cell(r0, 0), ch4, {"x_offset": 18, "y_offset": 12})
            return ws

        _render_dashboard("Dashboard Medical", "MED")
        _render_dashboard("Dashboard Commercial", "COM")

        # =========================
        # Finish (destockage sheet removed)
        # =========================
        wb.close()
        output.seek(0)

        filename = f"bon_de_commandes_{timezone.now().strftime('%Y%m%d_%H%M')}.xlsx"
        resp = HttpResponse(
            output.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        resp["Content-Disposition"] = f'attachment; filename="{filename}"'
        return resp


from rest_framework.response import Response

class OrdersPreviewAPI(OrdersExportExcel):
    """
    API endpoint that returns the exact same data as the Excel export, 
    but formatted as JSON for the web dashboard preview.
    """
    def get(self, request, *args, **kwargs):
        # 1. Dates & Filters (Reusing your existing methods)
        eff_min, eff_max, _ = self._resolve_effective_dates(request)
        filters = self.apply_filters(request, eff_min, eff_max)
        q = self.apply_keyword_filter(request)
        
        orders_qs = self.get_filtered_orders(request, filters, q).select_related(
            "user", "user__userprofile", "touser", "pharmacy", "gros", "super_gros"
        ).distinct()
        orders_all = list(orders_qs)

        # Exclude OFFICE-type orders (super_gros only, no pharmacy/gros — direct company
        # orders where the fournisseur would be "Office - Lilium") AND orders whose
        # super_gros is "LILIUM PHARMA ALG".  These must not appear in the sommaire table
        # nor affect any chart or aggregate.
        _EXCLUDED_SUPERGROS = {"LILIUM PHARMA ALG"}
        orders_all = [
            o for o in orders_all
            if self._order_type(o) != "OFFICE"
            and getattr(getattr(o, "super_gros", None), "name", None) not in _EXCLUDED_SUPERGROS
        ]

        # 2. Extract Data (similar to your Excel logic)
        items_qs = OrderItem.objects.filter(order__in=orders_all).select_related("produit")
        items_by_order = defaultdict(list)
        order_total_qty = defaultdict(int)
        order_total_value = defaultdict(float)
        type_prod_totals = defaultdict(lambda: defaultdict(int))
        product_totals = defaultdict(int)

        order_type_map = {o.id: self._order_type(o) for o in orders_all}
        
        # Calculate total value per order type
        type_val_totals = defaultdict(float)

        for it in items_qs:
            oid = it.order_id
            items_by_order[oid].append(it)
            pname = it.produit.nom if it.produit else "Inconnu"
            qty = it.qtt or 0
            val = float(qty) * float(it.produit.price or 0)
            
            product_totals[pname] += qty
            order_total_qty[oid] += qty
            order_total_value[oid] += val
            t = order_type_map.get(oid, "anomalie")
            type_prod_totals[t][pname] += qty
            type_val_totals[t] += val

        product_headers_unique = sorted(product_totals.keys(), key=lambda s: s.lower())

        # 3. Aggregations for Charts (Dashboard Medical & Commercial)
        med_cnt, med_qty, med_val = defaultdict(int), defaultdict(int), defaultdict(float)
        com_cnt, com_qty, com_val = defaultdict(int), defaultdict(int), defaultdict(float)

        for o in orders_all:
            oid = o.id
            t = order_type_map.get(oid)
            
            # Specialty role logic
            try:
                up = getattr(o.user, "userprofile", None)
                spec_val = ""
                if up:
                    spec_val = getattr(up, "speciality_rolee", getattr(up, "speciality_rolee", ""))
                if not spec_val:
                    spec_val = getattr(o.user, "speciality_rolee", getattr(o.user, "speciality_rolee", ""))
                
                spec = str(spec_val).strip() if spec_val else ""
                if spec in ["None", "null", "-"]: spec = ""
                
                # Apply short format
                if spec == "Medico_commercial":
                    spec = "MC"
                elif spec == "Commercial":
                    spec = "C"
                elif "Superviseur" in spec:
                    spec = "SV"
            except Exception:
                spec = ""
            
            uname = f"{spec} : {o.user.username}" if spec else o.user.username
            qty = order_total_qty.get(oid, 0)
            val = order_total_value.get(oid, 0.0)

            if t == "PH_GROS":
                med_cnt[uname] += 1
                med_qty[uname] += qty
                med_val[uname] += val
            elif t == "GROS_SUPER":
                com_cnt[uname] += 1
                com_qty[uname] += qty
                com_val[uname] += val

        # 3b. Build list of all filtered users formatted the same way as graph labels
        # Each entry: (plain_username, formatted_uname, raw_spec, rolee, is_active)
        _MC_EXCEPTIONS = {"hamzadz", "DebbarDZ", "tawfikdz", "MAROUANDZ"}
        _EXCLUDED_ROLES = {"Superviseur", "CountryManager"}
        all_filter_users = []  # list of (plain_username, formatted_uname, raw_spec, rolee, is_active)
        if request.GET.get("user"):
            resolved_users = self._resolve_requested_users(request)
            if resolved_users:
                from accounts.models import UserProfile
                from django.contrib.auth import get_user_model
                UserModel2 = get_user_model()
                user_objs = UserModel2.objects.filter(username__in=resolved_users).prefetch_related('userprofile')
                for u in user_objs:
                    try:
                        up2 = getattr(u, "userprofile", None)
                        spec_val2 = ""
                        rolee2 = ""
                        if up2:
                            spec_val2 = getattr(up2, "speciality_rolee", "")
                            rolee2 = str(getattr(up2, "rolee", "") or "").strip()
                        if not spec_val2:
                            spec_val2 = getattr(u, "speciality_rolee", "")
                        raw_spec2 = str(spec_val2).strip() if spec_val2 else ""
                        if raw_spec2 in ["None", "null", "-"]: raw_spec2 = ""
                        spec2 = raw_spec2
                        if spec2 == "Medico_commercial": spec2 = "MC"
                        elif spec2 == "Commercial": spec2 = "C"
                        elif "Superviseur" in spec2: spec2 = "SV"
                    except Exception:
                        raw_spec2 = ""
                        rolee2 = ""
                        spec2 = ""
                    formatted_uname = f"{spec2} : {u.username}" if spec2 else u.username
                    all_filter_users.append((u.username, formatted_uname, raw_spec2, rolee2, bool(u.is_active)))

        # 3b. Daily working-day aggregations (exclude Friday=4, Saturday=5)
        daily_pg_cnt = defaultdict(int)
        daily_pg_qty = defaultdict(int)
        daily_pg_val = defaultdict(float)
        daily_gs_cnt = defaultdict(int)
        daily_gs_qty = defaultdict(int)
        daily_gs_val = defaultdict(float)

        working_days = []
        cur_day = eff_min
        while cur_day <= eff_max:
            if cur_day.weekday() not in (4, 5):  # 4=Friday, 5=Saturday
                working_days.append(cur_day)
            cur_day += timedelta(days=1)

        day_labels = [d.strftime("%d/%m") for d in working_days]
        day_label_set = set(day_labels)

        def get_effective_working_date(dt):
            d = dt.date() if hasattr(dt, 'date') else dt
            wd = d.weekday()
            if wd not in (4, 5):
                return d
            if wd == 4:  # Friday
                next_sun = d + timedelta(days=2)
                prev_thu = d - timedelta(days=1)
            else:        # Saturday
                next_sun = d + timedelta(days=1)
                prev_thu = d - timedelta(days=2)
            
            if next_sun.month == d.month:
                return next_sun
            else:
                return prev_thu

        for o in orders_all:
            oid = o.id
            t = order_type_map.get(oid)
            eff_date = get_effective_working_date(o.added)
            ds = eff_date.strftime("%d/%m")
            if ds not in day_label_set:
                continue
            qty = order_total_qty.get(oid, 0)
            val = order_total_value.get(oid, 0.0)
            if t == "PH_GROS":
                daily_pg_cnt[ds] += 1
                daily_pg_qty[ds] += qty
                daily_pg_val[ds] += val
            elif t == "GROS_SUPER":
                daily_gs_cnt[ds] += 1
                daily_gs_qty[ds] += qty
                daily_gs_val[ds] += val

        # 4. Prepare JSON Payload
        # Helper to sort a dict by value (smallest to biggest) and return separated lists
        def argsort_dict(d):
            sorted_items = sorted(d.items(), key=lambda x: x[1])
            return [k for k, v in sorted_items], [v for k, v in sorted_items]

        med_labels_orders, med_orders = argsort_dict(med_cnt)
        med_labels_qty, med_qty_vals = argsort_dict(med_qty)
        med_labels_val, med_val_vals = argsort_dict(med_val)

        com_labels_orders, com_orders = argsort_dict(com_cnt)
        com_labels_qty, com_qty_vals = argsort_dict(com_qty)
        com_labels_val, com_val_vals = argsort_dict(com_val)

        # Build single_user info if exactly one user was requested (before supervisor expansion)
        single_user_info = None
        raw_requested = self._parse_csv_param(request.GET.get("user"))
        if len(raw_requested) == 1:
            try:
                from django.contrib.auth import get_user_model
                _UserModel = get_user_model()
                _u = _UserModel.objects.select_related('userprofile').get(username=raw_requested[0])
                _up = getattr(_u, 'userprofile', None)
                is_cm = _up and getattr(_up, 'rolee', '') == 'CountryManager'
                _rolee = getattr(_up, 'rolee', '') if _up else ''
                single_user_info = {
                    "username": _u.username,
                    "speciality_rolee": "Country Manager" if is_cm else (getattr(_up, 'speciality_rolee', '') if _up else ''),
                    "region": "Algerie" if is_cm else (getattr(_up, 'region', '') if _up else ''),
                    "rolee": _rolee,
                }
            except Exception:
                pass

        # Build missing products list
        from produits.models import Produit
        _is_single_commercial = (
            single_user_info is not None
            and single_user_info.get("rolee") == "Commercial"
        )
        if _is_single_commercial:
            # For a single Commercial user: compare against their target products in the date range
            from clients.models import UserTargetMonthProduct
            from django.contrib.auth import get_user_model
            _UserModel = get_user_model()
            try:
                _commercial_user = _UserModel.objects.get(username=raw_requested[0])
                _target_product_names = set(
                    UserTargetMonthProduct.objects.filter(
                        usermonth__user=_commercial_user,
                    ).values_list('product__nom', flat=True)
                )
            except Exception:
                _target_product_names = set()
            missing_products = sorted(_target_product_names - set(product_headers_unique), key=lambda s: s.lower())
        else:
            all_product_names = set(Produit.objects.values_list('nom', flat=True))
            missing_products = sorted(all_product_names - set(product_headers_unique), key=lambda s: s.lower())

        payload = {
            "single_user": single_user_info,
            "missing_products": missing_products,
            "filters": {
                "Utilisateur(s)": request.GET.get("user") or "Tous",
                **( {"Région": request.GET.get("user_region")} if request.GET.get("user_region") and not request.GET.get("user") else {} ),
                "Du (min_date)": eff_min.strftime("%Y-%m-%d"),
                "Au (max_date)": eff_max.strftime("%Y-%m-%d"),
                "Nombre de commandes": len(orders_all),
            },
            "totaux_type": {
                "headers": ["Type"] + product_headers_unique + ["Total", "Valeur total"],
                "rows": []
            },
            "sommaire": {
                "headers": ["Bon de commande", "Date", "Type", "Utilisateur", "Client", "Fournisseur"] + product_headers_unique + ["Total valeur (DA)"],
                "rows": []
            },
            "dash_med": {
                "labels_orders": med_labels_orders,
                "orders": med_orders,
                "labels_qty": med_labels_qty,
                "qty": med_qty_vals,
                "labels_val": med_labels_val,
                "val": med_val_vals,
                "zero_users": [
                    plain for plain, fmt, _, rolee, active in all_filter_users
                    if fmt not in med_val
                    and active
                    and rolee not in _EXCLUDED_ROLES
                ],
            },
            "dash_com": {
                "labels_orders": com_labels_orders,
                "orders": com_orders,
                "labels_qty": com_labels_qty,
                "qty": com_qty_vals,
                "labels_val": com_labels_val,
                "val": com_val_vals,
                "zero_users": [
                    plain for plain, fmt, spec, rolee, active in all_filter_users
                    if fmt not in com_val
                    and active
                    and rolee not in _EXCLUDED_ROLES
                    and (spec != "Medico_commercial" or plain in _MC_EXCEPTIONS)
                ],
            },
            "dash_daily": {
                "labels": day_labels,
                "ph_gros_val": [daily_pg_val[d] for d in day_labels],
                "ph_gros_qty": [daily_pg_qty[d] for d in day_labels],
                "ph_gros_cnt": [daily_pg_cnt[d] for d in day_labels],
                "gros_super_val": [daily_gs_val[d] for d in day_labels],
                "gros_super_qty": [daily_gs_qty[d] for d in day_labels],
                "gros_super_cnt": [daily_gs_cnt[d] for d in day_labels],
            }
        }

        # Populate Totaux Type Table
        for t in ["OFFICE", "GROS_SUPER", "PH_GROS", "anomalie"]:
            row = [t]
            total = 0
            for pname in product_headers_unique:
                q = type_prod_totals[t].get(pname, 0)
                row.append(q)
                total += q
            row.append(total)
            # Append Valeur total for this type
            row.append(type_val_totals.get(t, 0.0))
            payload["totaux_type"]["rows"].append(row)

        # Populate Sommaire Table
        for o in orders_all:
            oid = o.id
            client, fournisseur = _get_client_fournisseur(o)
            typ = order_type_map.get(oid) or "anomalie"
            
            prod_qty_map = defaultdict(int)
            for it in items_by_order.get(oid, []):
                prod_qty_map[it.produit.nom] += (it.qtt or 0)

            row = [
                oid, o.added.strftime("%Y-%m-%d"), typ, o.user.username, client, fournisseur
            ]
            for pname in product_headers_unique:
                row.append(prod_qty_map.get(pname, 0))
            row.append(order_total_value.get(oid, 0.0))
            payload["sommaire"]["rows"].append(row)

        # If exactly 1 Commercial user is selected, hide dashboard sections (keep daily chart)
        if single_user_info and single_user_info.get("rolee") == "Commercial":
            payload.pop("dash_med", None)
            payload.pop("dash_com", None)

        return Response(payload)