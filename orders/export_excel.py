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
from datetime import datetime, date as date_cls, timedelta
from io import BytesIO
from typing import Dict, List, Tuple, Optional

import xlsxwriter
from xlsxwriter.utility import xl_rowcol_to_cell

from django.contrib.auth import get_user_model
from django.db.models import Q
from django.http import HttpResponse
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework import authentication, permissions

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
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    # -----------------------
    # Query helpers
    # -----------------------
    @staticmethod
    def _parse_csv_param(raw: Optional[str]) -> List[str]:
        """
        UI behavior:
          - No param => ALL users
          - user=Tous => ALL users
          - user=a,b,c => explicit selection
        """
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
    def _resolve_effective_dates(request) -> Tuple[date_cls, date_cls]:
        """
        Defaults:
          - min_date default = yesterday
          - max_date default = today
          - max_date missing => today
        """
        today = timezone.localdate()
        min_d = OrdersExportExcel._parse_date_yyyy_mm_dd((request.GET.get("min_date") or "").strip())
        max_d = OrdersExportExcel._parse_date_yyyy_mm_dd((request.GET.get("max_date") or "").strip())

        if max_d is None:
            max_d = today
        if min_d is None:
            min_d = today - timedelta(days=1)

        if min_d > max_d:
            min_d, max_d = max_d, min_d
        return min_d, max_d

    @staticmethod
    def _period_days_inclusive(min_d: date_cls, max_d: date_cls) -> int:
        return int((max_d - min_d).days) + 1

    @staticmethod
    def _grain_for_period(days_inclusive: int) -> Tuple[int, str, str]:
        # Requirement: daily if <= 31 days, otherwise rolling 7-day buckets; never monthly
        if days_inclusive <= 31:
            return 1, "Jour", "يومي"
        return 7, "Semaine", "أسبوعي"

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
        """
        Professional-ish axis labels:
          - Daily: show 'DD Mon' at first label and at month boundaries; otherwise 'DD'
          - Weekly: show compact ranges, year only on first range or when crossing years
        """
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

    @staticmethod
    def _order_type(order: Order) -> str:
        # PH_GROS: Pharmacie + Grossiste
        if (getattr(order, "pharmacy_id", None) is not None) and (getattr(order, "gros_id", None) is not None):
            return "PH_GROS"        
        # NEW: Pharmacie -> Super Gros directly (no gros): classify as GROS_SUPER (commercial)
        if (
            (getattr(order, "pharmacy_id", None) is not None)
            and (getattr(order, "gros_id", None) is None)
            and (getattr(order, "super_gros_id", None) is not None)
        ):
            return "GROS_SUPER"        
        # GROS_SUPER: Grossiste + SuperGrossiste and pharmacy is None
        if (
            (getattr(order, "pharmacy_id", None) is None)
            and (getattr(order, "gros_id", None) is not None)
            and (getattr(order, "super_gros_id", None) is not None)
        ):
            return "GROS_SUPER"
        # OFFICE: SuperGrossiste only (no pharmacy, no gross)
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
    def apply_filters(self, request, effective_min: date_cls, effective_max: date_cls) -> Dict:
        filters: Dict = {
            "added__date__gte": effective_min,
            "added__date__lte": effective_max,
        }

        if request.GET.get("produit"):
            filters["orderitem__produit__id"] = request.GET.get("produit")

        if request.GET.get("status"):
            status_list = self._parse_csv_param(request.GET.get("status"))
            if status_list:
                filters["status__in"] = status_list

        # IMPORTANT: user=Tous => _parse_csv_param returns [] => no filtering
        if request.GET.get("user"):
            users_list = self._parse_csv_param(request.GET.get("user"))
            if users_list:
                filters["user__username__in"] = users_list

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

        # Role scoping (preserve your existing behavior)
        if (
            request.user.userprofile.rolee not in ["Superviseur", "CountryManager"]
            and not request.user.is_superuser
            and request.user.username not in ["liliumdz"]
            and request.user.userprofile.speciality_rolee not in ["Office"]
        ):
            orders = orders.filter(
                Q(user=request.user) | Q(touser=request.user) | Q(user__username__in=["MeriemDZ", "ibtissemdz"])
            ).distinct()

        elif (
            request.user.userprofile.rolee == "Superviseur"
            and request.user.userprofile.speciality_rolee not in ["Superviseur_national"]
        ):
            orders = orders.filter(
                Q(user=request.user)
                | Q(user__in=request.user.userprofile.usersunder.all())
                | Q(touser=request.user)
                | Q(touser__in=request.user.userprofile.usersunder.all())
                | Q(user__username__in=["MeriemDZ", "ibtissemdz"])
            ).distinct()

        elif request.user.userprofile.speciality_rolee in ["Office"] or request.user.username in [
            "ibtissemdz",
            "RABTIDZ",
            "a.lounis@liliumpharma.com",
        ]:
            orders = orders

        if request.user.userprofile.speciality_rolee in ["Superviseur_national"]:
            UserModel = get_user_model()
            users = UserModel.objects.filter(userprofile__work_as_commercial=True)
            orders = orders.filter(
                Q(user=request.user)
                | Q(user__in=users)
                | Q(touser=request.user)
                | Q(touser__in=users)
                | Q(user__in=request.user.userprofile.usersunder.all())
                | Q(user__username__in=["MeriemDZ", "ibtissemdz"])
            ).distinct()

        return orders.distinct()

    # -----------------------
    # Main
    # -----------------------
    def get(self, request, *args, **kwargs):
        eff_min, eff_max = self._resolve_effective_dates(request)
        eff_min_str = eff_min.strftime("%Y-%m-%d")
        eff_max_str = eff_max.strftime("%Y-%m-%d")

        filters = self.apply_filters(request, eff_min, eff_max)
        q = self.apply_keyword_filter(request)

        orders_qs = (
            self.get_filtered_orders(request, filters, q)
            .select_related("user", "touser", "pharmacy", "gros", "super_gros")
            .distinct()
        )
        orders: List[Order] = list(orders_qs)

        # User selection logic:
        # - no user param or user=Tous => requested_users = [] => ALL
        requested_users = self._parse_csv_param(request.GET.get("user"))

        if requested_users:
            allowed = {str(o.user.username) for o in orders}
            effective_users = [u for u in requested_users if u in allowed]
            eff_set = set(effective_users)
            orders = [o for o in orders if str(o.user.username) in eff_set]
        else:
            effective_users = sorted({str(o.user.username) for o in orders})

        single_user_mode = bool(requested_users) and (len(effective_users) == 1)
        comparison_mode = not single_user_mode
        single_user = _xlsx_safe(effective_users[0]) if single_user_mode else ""

        # Type per order (Sommaire uses all, Dashboard excludes anomalies + OFFICE)
        order_type: Dict[int, str] = {o.id: self._order_type(o) for o in orders}

        order_ids = [o.id for o in orders]

        # Items + totals
        items_qs = (
            OrderItem.objects.filter(order_id__in=order_ids)
            .select_related("produit")
            .order_by("order_id", "id")
        )

        items_by_order: Dict[int, List[OrderItem]] = defaultdict(list)
        order_total_qty: Dict[int, int] = defaultdict(int)
        order_total_value: Dict[int, float] = defaultdict(float)
        product_totals: Dict[str, int] = defaultdict(int)

        for it in items_qs:
            oid = it.order_id
            items_by_order[oid].append(it)

            pname = _xlsx_safe(getattr(it.produit, "nom", ""))
            qty = int(getattr(it, "qtt", 0) or 0)

            unit_price = float(getattr(it.produit, "price", 0) or 0)  # DA
            line_value = float(qty) * float(unit_price)

            product_totals[pname] += qty
            order_total_qty[oid] += qty
            order_total_value[oid] += line_value

        product_names_sorted = sorted(product_totals.keys(), key=lambda s: s.lower())
        product_headers_unique = _make_unique_headers(product_names_sorted)
        prod_by_index = product_names_sorted

        # -----------------------
        # Dashboard data: exclude anomalies + OFFICE
        # Only PH_GROS and GROS_SUPER go into Dashboard
        # -----------------------
        dash_orders = [o for o in orders if order_type.get(o.id) in ("PH_GROS", "GROS_SUPER")]

        # Time bucketing for single-user mode
        days_inclusive = self._period_days_inclusive(eff_min, eff_max)
        bucket_size, grain_fr, grain_ar = self._grain_for_period(days_inclusive)
        bucket_starts = self._build_buckets(eff_min, eff_max, bucket_size)
        timeline_labels = self._timeline_labels(bucket_starts, bucket_size) or ["-"]
        n_t = len(timeline_labels)

        med_orders_t = [0] * n_t
        med_qty_t = [0] * n_t
        med_val_t = [0.0] * n_t

        com_orders_t = [0] * n_t
        com_qty_t = [0] * n_t
        com_val_t = [0.0] * n_t

        # Multi-user totals by division
        med_cnt_by_user: Dict[str, int] = defaultdict(int)
        med_qty_by_user: Dict[str, int] = defaultdict(int)
        med_val_by_user: Dict[str, float] = defaultdict(float)

        com_cnt_by_user: Dict[str, int] = defaultdict(int)
        com_qty_by_user: Dict[str, int] = defaultdict(int)
        com_val_by_user: Dict[str, float] = defaultdict(float)

        for o in dash_orders:
            oid = o.id
            t = order_type.get(oid)
            uname = _xlsx_safe(o.user.username)

            d = o.added.date()
            if d < eff_min or d > eff_max:
                continue

            # bucket index
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
        fmt_date = wb.add_format({"border": 1, "num_format": "yyyy-mm-dd"})

        fmt_dash_title = wb.add_format({"bold": True, "font_size": 16, "bg_color": DARK, "font_color": "white"})
        fmt_dash_band = wb.add_format({"bold": True, "font_size": 12, "bg_color": MED, "font_color": "white"})

        # =========================
        # Sheet: Sommaire
        # =========================
        ws_sum = wb.add_worksheet("Sommaire")
        ws_sum.hide_gridlines(2)
        ws_sum.set_tab_color(MED)
        ws_sum.set_column(0, 0, 16)   # Bon
        ws_sum.set_column(1, 1, 14)   # Date
        ws_sum.set_column(2, 2, 12)   # Type
        ws_sum.set_column(3, 3, 18)   # User
        ws_sum.set_column(4, 5, 34)   # Client / Fournisseur
        ws_sum.set_column(6, 6 + len(product_headers_unique) - 1, 14)
        ws_sum.set_column(6 + len(product_headers_unique), 6 + len(product_headers_unique), 18)  # Total valeur

        r = 0
        ws_sum.merge_range(r, 0, r, 6 + len(product_headers_unique), "SOMMAIRE — Export Excel", fmt_title)
        r += 2

        ws_sum.merge_range(r, 0, r, 6 + len(product_headers_unique), "Filtres appliqués", fmt_section)
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
            ws_sum.merge_range(r, 1, r, 6 + len(product_headers_unique), _xlsx_safe(v), fmt_cell)
            r += 1

        r += 1
        ws_sum.merge_range(r, 0, r, 6 + len(product_headers_unique), "Table Sommaire", fmt_section)
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
            row.append(float(order_total_value.get(oid, 0.0)))  # DA
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
        ws_sum.freeze_panes(0, 6)

        # =========================
        # Sheet: Dashboard
        # =========================
        dash = wb.add_worksheet("Dashboard")
        dash.hide_gridlines(2)
        dash.set_tab_color(DARK)
        dash.set_column(0, 0, 2)
        dash.set_column(1, 1, 42)
        dash.set_column(2, 12, 18)
        dash.merge_range(0, 0, 0, 12, "Tableau de bord | لوحة القيادة", fmt_dash_title)

        # =========================
        # Sheet: Donnees Graphiques (hidden)
        # =========================
        ws_data = wb.add_worksheet("Donnees Graphiques")
        ws_data.hide_gridlines(2)
        ws_data.hide()

        # ---- Data table for single-user time series (both divisions)
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

        # ---- Multi-user: write 6 metric blocks (ALL users with metric > 0)
        def _write_metric_block(start_row: int, header: str, metric: Dict[str, float], money: bool) -> Tuple[int, int, int]:
            items = [(u, float(v)) for u, v in metric.items() if float(v) > 0]
            items.sort(key=lambda x: x[1], reverse=True)

            ws_data.write_row(start_row, 0, ["Utilisateur", header], fmt_k)

            if not items:
                ws_data.write_string(start_row + 1, 0, "-", fmt_cell)
                ws_data.write_number(start_row + 1, 1, 0.0, fmt_money if money else fmt_num)
                return start_row, start_row + 1, 1

            for j, (u, v) in enumerate(items, start=1):
                ws_data.write_string(start_row + j, 0, _xlsx_safe(u), fmt_cell)
                ws_data.write_number(start_row + j, 1, float(v), fmt_money if money else fmt_num)

            last_row = start_row + len(items)
            return start_row, last_row, len(items)

        row = time_last + 3

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

        # ---- Charts
        def _style_chart(chart):
            chart.set_chartarea({"fill": {"color": LIGHT}, "border": {"color": MED}})
            chart.set_plotarea({"fill": {"color": "white"}})

        def _x_axis_opts(n_points: int) -> Dict:
            interval = max(1, n_points // 12) if n_points > 14 else 1
            rotation = -45 if n_points > 10 else 0
            return {
                "name": "Temps | الزمن",
                "interval_unit": interval,
                "num_font": {"size": 9, "rotation": rotation},
            }

        def _bar_height_for(ncats: int) -> int:
            return int(min(2200, max(360, 120 + 28 * max(1, ncats))))

        def _rows_for_px(px: int) -> int:
            return int(px / 18) + 3

        # Thicker bars via series "gap" (lower gap => thicker bars)
        BAR_GAP = 50

        # Readable value labels on dark bars AND white background:
        # add a white label box + dark text (so if Excel moves outside, still readable).
        DL_NUM = {
            "value": True,
            "position": "outside_end",
            "num_format": "0",
            "font": {"color": "#263238", "bold": True},
            "fill": {"color": "#FFFFFF"},
            "border": {"color": "#B0BEC5"},
        }
        DL_MONEY = {
            "value": True,
            "position": "outside_end",
            "num_format": "#,##0.00",
            "font": {"color": "#263238", "bold": True},
            "fill": {"color": "#FFFFFF"},
            "border": {"color": "#B0BEC5"},
        }

        if comparison_mode:
            cur_row = 2
            dash.merge_range(cur_row, 0, cur_row, 12, "Medical (PH_GROS) | طبي", fmt_dash_band)
            cur_row += 1

            h_med_orders = _bar_height_for(n_med_orders)
            h_med_qty = _bar_height_for(n_med_qty)
            h_med_val = _bar_height_for(n_med_val)

            # MED Orders/User
            ch_m1 = wb.add_chart({"type": "bar"})
            ch_m1.set_style(10)
            _style_chart(ch_m1)
            ch_m1.set_title({"name": "Commandes / utilisateur | الطلبات / المستخدم"})
            ch_m1.set_x_axis({"name": "Nombre | العدد", "major_gridlines": {"visible": False}})
            ch_m1.set_y_axis({"name": "Utilisateur | المستخدم", "num_font": {"size": 9}})
            ch_m1.set_legend({"none": True})
            ch_m1.add_series({
                "categories": ["Donnees Graphiques", med_orders_row0 + 1, 0, med_orders_last, 0],
                "values":     ["Donnees Graphiques", med_orders_row0 + 1, 1, med_orders_last, 1],
                "gap": BAR_GAP,
                "data_labels": DL_NUM,
                "fill": {"color": MED},
                "border": {"color": DARK},
            })
            ch_m1.set_size({"width": 620, "height": h_med_orders})

            # MED Qty/User
            ch_m2 = wb.add_chart({"type": "bar"})
            ch_m2.set_style(10)
            _style_chart(ch_m2)
            ch_m2.set_title({"name": "Quantité / utilisateur | الكمية / المستخدم"})
            ch_m2.set_x_axis({"name": "Quantité | الكمية", "major_gridlines": {"visible": False}})
            ch_m2.set_y_axis({"name": "Utilisateur | المستخدم", "num_font": {"size": 9}})
            ch_m2.set_legend({"none": True})
            ch_m2.add_series({
                "categories": ["Donnees Graphiques", med_qty_row0 + 1, 0, med_qty_last, 0],
                "values":     ["Donnees Graphiques", med_qty_row0 + 1, 1, med_qty_last, 1],
                "gap": BAR_GAP,
                "data_labels": DL_NUM,
                "fill": {"color": DARK},
                "border": {"color": MED},
            })
            ch_m2.set_size({"width": 620, "height": h_med_qty})

            dash.insert_chart(xl_rowcol_to_cell(cur_row, 0), ch_m1, {"x_offset": 18, "y_offset": 10})
            dash.insert_chart(xl_rowcol_to_cell(cur_row, 6), ch_m2, {"x_offset": 18, "y_offset": 10})

            top_block_h = max(h_med_orders, h_med_qty)
            cur_row = cur_row + _rows_for_px(top_block_h) + 1

            # MED Value/User (DA) full width
            ch_m3 = wb.add_chart({"type": "bar"})
            ch_m3.set_style(10)
            _style_chart(ch_m3)
            ch_m3.set_title({"name": "Valeur / utilisateur (DA) | القيمة / المستخدم (DA)"})
            ch_m3.set_x_axis({"name": "Valeur (DA) | القيمة (DA)", "major_gridlines": {"visible": False}})
            ch_m3.set_y_axis({"name": "Utilisateur | المستخدم", "num_font": {"size": 9}})
            ch_m3.set_legend({"none": True})
            ch_m3.add_series({
                "categories": ["Donnees Graphiques", med_val_row0 + 1, 0, med_val_last, 0],
                "values":     ["Donnees Graphiques", med_val_row0 + 1, 1, med_val_last, 1],
                "gap": BAR_GAP,
                "data_labels": DL_MONEY,
                "fill": {"color": MED},
                "border": {"color": DARK},
            })
            ch_m3.set_size({"width": 1240, "height": h_med_val})
            dash.insert_chart(xl_rowcol_to_cell(cur_row, 0), ch_m3, {"x_offset": 18, "y_offset": 12})

            cur_row = cur_row + _rows_for_px(h_med_val) + 2

            # COMMERCIAL band
            dash.merge_range(cur_row, 0, cur_row, 12, "Commercial (GROS_SUPER) | تجاري", fmt_dash_band)
            cur_row += 1

            h_com_orders = _bar_height_for(n_com_orders)
            h_com_qty = _bar_height_for(n_com_qty)
            h_com_val = _bar_height_for(n_com_val)

            # COM Orders/User
            ch_c1 = wb.add_chart({"type": "bar"})
            ch_c1.set_style(10)
            _style_chart(ch_c1)
            ch_c1.set_title({"name": "Commandes / utilisateur | الطلبات / المستخدم"})
            ch_c1.set_x_axis({"name": "Nombre | العدد", "major_gridlines": {"visible": False}})
            ch_c1.set_y_axis({"name": "Utilisateur | المستخدم", "num_font": {"size": 9}})
            ch_c1.set_legend({"none": True})
            ch_c1.add_series({
                "categories": ["Donnees Graphiques", com_orders_row0 + 1, 0, com_orders_last, 0],
                "values":     ["Donnees Graphiques", com_orders_row0 + 1, 1, com_orders_last, 1],
                "gap": BAR_GAP,
                "data_labels": DL_NUM,
                "fill": {"color": MED},
                "border": {"color": DARK},
            })
            ch_c1.set_size({"width": 620, "height": h_com_orders})

            # COM Qty/User
            ch_c2 = wb.add_chart({"type": "bar"})
            ch_c2.set_style(10)
            _style_chart(ch_c2)
            ch_c2.set_title({"name": "Quantité / utilisateur | الكمية / المستخدم"})
            ch_c2.set_x_axis({"name": "Quantité | الكمية", "major_gridlines": {"visible": False}})
            ch_c2.set_y_axis({"name": "Utilisateur | المستخدم", "num_font": {"size": 9}})
            ch_c2.set_legend({"none": True})
            ch_c2.add_series({
                "categories": ["Donnees Graphiques", com_qty_row0 + 1, 0, com_qty_last, 0],
                "values":     ["Donnees Graphiques", com_qty_row0 + 1, 1, com_qty_last, 1],
                "gap": BAR_GAP,
                "data_labels": DL_NUM,
                "fill": {"color": DARK},
                "border": {"color": MED},
            })
            ch_c2.set_size({"width": 620, "height": h_com_qty})

            dash.insert_chart(xl_rowcol_to_cell(cur_row, 0), ch_c1, {"x_offset": 18, "y_offset": 10})
            dash.insert_chart(xl_rowcol_to_cell(cur_row, 6), ch_c2, {"x_offset": 18, "y_offset": 10})

            top_block_h = max(h_com_orders, h_com_qty)
            cur_row = cur_row + _rows_for_px(top_block_h) + 1

            # COM Value/User (DA) full width
            ch_c3 = wb.add_chart({"type": "bar"})
            ch_c3.set_style(10)
            _style_chart(ch_c3)
            ch_c3.set_title({"name": "Valeur / utilisateur (DA) | القيمة / المستخدم (DA)"})
            ch_c3.set_x_axis({"name": "Valeur (DA) | القيمة (DA)", "major_gridlines": {"visible": False}})
            ch_c3.set_y_axis({"name": "Utilisateur | المستخدم", "num_font": {"size": 9}})
            ch_c3.set_legend({"none": True})
            ch_c3.add_series({
                "categories": ["Donnees Graphiques", com_val_row0 + 1, 0, com_val_last, 0],
                "values":     ["Donnees Graphiques", com_val_row0 + 1, 1, com_val_last, 1],
                "gap": BAR_GAP,
                "data_labels": DL_MONEY,
                "fill": {"color": MED},
                "border": {"color": DARK},
            })
            ch_c3.set_size({"width": 1240, "height": h_com_val})
            dash.insert_chart(xl_rowcol_to_cell(cur_row, 0), ch_c3, {"x_offset": 18, "y_offset": 12})

        else:
            def _make_line(title: str, col_values: int, y_name: str, line_color: str, width: int, height: int):
                ch = wb.add_chart({"type": "line"})
                ch.set_style(10)
                _style_chart(ch)
                ch.set_title({"name": title})
                ch.set_legend({"none": True})
                ch.set_y_axis({
                    "name": y_name,
                    "major_gridlines": {"visible": True, "line": {"color": GRID}},
                })
                ch.set_x_axis(_x_axis_opts(len(timeline_labels)))
                ch.add_series({
                    "categories": ["Donnees Graphiques", row_time0 + 1, 0, time_last, 0],
                    "values":     ["Donnees Graphiques", row_time0 + 1, col_values, time_last, col_values],
                    "line": {"color": line_color, "width": 2.25},
                })
                ch.set_size({"width": width, "height": height})
                return ch

            cur_row = 2
            dash.merge_range(cur_row, 0, cur_row, 12, f"Medical (PH_GROS) — Tendances ({grain_fr}) | طبي", fmt_dash_band)
            cur_row += 1

            ch_mo = _make_line("Nombre de commandes / temps | عدد الطلبات / الزمن", 1, "Nombre | العدد", MED, 620, 300)
            ch_mq = _make_line("Quantité totale / temps | إجمالي الكمية / الزمن", 2, "Quantité | الكمية", DARK, 620, 300)
            dash.insert_chart(xl_rowcol_to_cell(cur_row, 0), ch_mo, {"x_offset": 18, "y_offset": 10})
            dash.insert_chart(xl_rowcol_to_cell(cur_row, 6), ch_mq, {"x_offset": 18, "y_offset": 10})

            cur_row = cur_row + _rows_for_px(300) + 1

            ch_mv = _make_line("Valeur totale (DA) / temps | إجمالي القيمة (DA) / الزمن", 3, "Valeur (DA) | القيمة (DA)", MED, 1240, 310)
            dash.insert_chart(xl_rowcol_to_cell(cur_row, 0), ch_mv, {"x_offset": 18, "y_offset": 12})

            cur_row = cur_row + _rows_for_px(310) + 2

            dash.merge_range(cur_row, 0, cur_row, 12, f"Commercial (GROS_SUPER) — Tendances ({grain_fr}) | تجاري", fmt_dash_band)
            cur_row += 1

            ch_co = _make_line("Nombre de commandes / temps | عدد الطلبات / الزمن", 4, "Nombre | العدد", MED, 620, 300)
            ch_cq = _make_line("Quantité totale / temps | إجمالي الكمية / الزمن", 5, "Quantité | الكمية", DARK, 620, 300)
            dash.insert_chart(xl_rowcol_to_cell(cur_row, 0), ch_co, {"x_offset": 18, "y_offset": 10})
            dash.insert_chart(xl_rowcol_to_cell(cur_row, 6), ch_cq, {"x_offset": 18, "y_offset": 10})

            cur_row = cur_row + _rows_for_px(300) + 1

            ch_cv = _make_line("Valeur totale (DA) / temps | إجمالي القيمة (DA) / الزمن", 6, "Valeur (DA) | القيمة (DA)", MED, 1240, 310)
            dash.insert_chart(xl_rowcol_to_cell(cur_row, 0), ch_cv, {"x_offset": 18, "y_offset": 12})

        wb.close()
        output.seek(0)

        filename = f"bon_de_commandes_{timezone.now().strftime('%Y%m%d_%H%M')}.xlsx"
        resp = HttpResponse(
            output.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        resp["Content-Disposition"] = f'attachment; filename="{filename}"'
        return resp
