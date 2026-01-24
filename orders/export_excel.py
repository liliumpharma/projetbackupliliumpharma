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
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.http import HttpResponse
from django.utils import timezone
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from .models import Order, OrderItem


# -----------------------
# Excel safety utilities
# -----------------------
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


# -----------------------
# Business labels (FR only outside Dashboard)
# -----------------------
def _label_pharmacy(med) -> str:
    name = getattr(med, "nom", "") if med else ""
    return _xlsx_safe(f"Pharmacie - {name}".strip(" -"))


def _label_gros(med) -> str:
    name = getattr(med, "nom", "") if med else ""
    return _xlsx_safe(f"Grossiste - {name}".strip(" -"))


def _label_supergros(client) -> str:
    name = getattr(client, "name", "") if client else ""
    return _xlsx_safe(f"Super Grossiste - {name}".strip(" -"))


def _get_client_fournisseur(order: Order) -> Tuple[str, str]:
    office = "Office - Lilium"

    pharm_lbl = _label_pharmacy(order.pharmacy) if getattr(order, "pharmacy", None) else ""
    gros_lbl = _label_gros(order.gros) if getattr(order, "gros", None) else ""
    sgros_lbl = _label_supergros(order.super_gros) if getattr(order, "super_gros", None) else ""

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
    # Query helpers
    # -----------------------
    @staticmethod
    def _parse_csv_param(raw: Optional[str]) -> List[str]:
        if not raw:
            return []
        s = str(raw).strip().strip("'").strip('"').strip()
        parts = [p.strip().strip("'").strip('"').strip() for p in s.split(",")]
        return [p for p in parts if p]

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
        UI defaults:
          - min_date default = yesterday
          - max_date default = today
          - if max_date missing => today
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
        """
        Requirement:
          - by day if duration <= 31 days
          - by week if > 31 days
          - never show by month
        """
        if days_inclusive <= 31:
            return 1, "Jour", "يومي"
        return 7, "Semaine", "أسبوعي"

    @staticmethod
    def _ceil_div(a: int, b: int) -> int:
        return (a + b - 1) // b

    @staticmethod
    def _build_buckets(min_d: date_cls, max_d: date_cls, bucket_size: int) -> Tuple[List[date_cls], date_cls]:
        """
        Rolling buckets starting at min_d, padded to end of last full bucket.
        """
        days = OrdersExportExcel._period_days_inclusive(min_d, max_d)
        n_buckets = OrdersExportExcel._ceil_div(days, bucket_size)
        padded_max = min_d + timedelta(days=(n_buckets * bucket_size - 1))
        starts = [min_d + timedelta(days=(i * bucket_size)) for i in range(n_buckets)]
        return starts, padded_max

    @staticmethod
    def _fr_month_abbrev(m: int) -> str:
        # Compact, professional: Jan/Fev/Mar/...
        return {
            1: "Jan",
            2: "Fev",
            3: "Mar",
            4: "Avr",
            5: "Mai",
            6: "Jun",
            7: "Jul",
            8: "Aou",
            9: "Sep",
            10: "Oct",
            11: "Nov",
            12: "Dec",
        }.get(int(m), "Mois")

    @classmethod
    def _timeline_labels(cls, bucket_starts: List[date_cls], bucket_size: int) -> List[str]:
        """
        Professional axis labels:
          - Daily: show 'DD Mon' at the first tick and at month boundaries; otherwise show 'DD'.
                 show year only when it's 01 Jan.
          - Weekly: show compact ranges, add year only on the first bucket or when crossing years.
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
                    f"{s.day:02d} {cls._fr_month_abbrev(s.month)} {s.year}–{e.day:02d} {cls._fr_month_abbrev(e.month)} {e.year}"
                )
                continue

            if s.month == e.month:
                core = f"{s.day:02d}–{e.day:02d} {cls._fr_month_abbrev(s.month)}"
            else:
                core = f"{s.day:02d} {cls._fr_month_abbrev(s.month)}–{e.day:02d} {cls._fr_month_abbrev(e.month)}"

            out.append(f"{core} {s.year}" if i == 0 else core)

        return out

    @staticmethod
    def _top_n_with_ties_nonzero(metric: Dict[str, float], n: int) -> List[Tuple[str, float]]:
        """
        Top N, allow >N when tied at cutoff; drop <=0 to avoid huge ties at 0.
        """
        items = [(k, float(v)) for k, v in metric.items() if float(v) > 0]
        items.sort(key=lambda x: x[1], reverse=True)
        if not items:
            return [("-", 0.0)]
        if len(items) <= n:
            return items
        cutoff = items[n - 1][1]
        return [kv for kv in items if kv[1] >= cutoff]

    # -----------------------
    # Filters / scoping
    # -----------------------
    def apply_filters(self, request, effective_min: date_cls, effective_max: date_cls) -> Dict:
        filters: Dict = {}
        filters["added__date__gte"] = effective_min
        filters["added__date__lte"] = effective_max

        if request.GET.get("produit"):
            filters["orderitem__produit__id"] = request.GET.get("produit")

        if request.GET.get("status"):
            status_list = self._parse_csv_param(request.GET.get("status"))
            if status_list:
                filters["status__in"] = status_list

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

        # Role scoping (keep behavior; do not drop filters)
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

    def get(self, request, *args, **kwargs):
        # Effective dates (defaults)
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

        # Enforce requested user filter by intersection BEFORE any aggregates (applies to all sheets)
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
        single_user_key = _xlsx_safe(effective_users[0]) if single_user_mode else ""

        order_ids = [o.id for o in orders]

        # Precompute labels
        order_user: Dict[int, str] = {o.id: _xlsx_safe(o.user.username) for o in orders}
        order_party: Dict[int, Tuple[str, str]] = {o.id: _get_client_fournisseur(o) for o in orders}

        items_qs = (
            OrderItem.objects.filter(order_id__in=order_ids)
            .select_related("produit")
            .order_by("order_id", "id")
        )

        # Aggregates
        items_by_order: Dict[int, List[OrderItem]] = defaultdict(list)
        product_totals: Dict[str, int] = defaultdict(int)
        user_prod_totals: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        user_totals_qty: Dict[str, int] = defaultdict(int)
        party_totals: Dict[Tuple[str, str], Dict[str, int]] = defaultdict(lambda: defaultdict(int))

        order_total_qty: Dict[int, int] = defaultdict(int)
        order_total_value: Dict[int, float] = defaultdict(float)

        for it in items_qs:
            oid = it.order_id
            items_by_order[oid].append(it)

            pname = _xlsx_safe(getattr(it.produit, "nom", ""))
            qty = int(getattr(it, "qtt", 0) or 0)

            # Pricing: Produit.price ONLY (DA)
            unit_price = float(getattr(it.produit, "price", 0) or 0)
            line_value = float(qty) * float(unit_price)

            product_totals[pname] += qty
            order_total_qty[oid] += qty
            order_total_value[oid] += line_value

            uname = order_user.get(oid, "-")
            user_prod_totals[uname][pname] += qty

            client, fournisseur = order_party.get(oid, ("-", "Office - Lilium"))
            party_totals[(client, fournisseur)][pname] += qty

        # Totals by user (qty) for Totaux Délégués
        for uname, prodmap in user_prod_totals.items():
            user_totals_qty[uname] = int(sum(int(v) for v in prodmap.values()))

        # Unique headers for product columns
        product_names_sorted = sorted(product_totals.keys(), key=lambda s: s.lower())
        product_headers_unique = _make_unique_headers(product_names_sorted)
        prod_by_index = product_names_sorted

        # -----------------------
        # Dashboard timelines + per-user metrics
        # -----------------------
        days_inclusive = self._period_days_inclusive(eff_min, eff_max)
        bucket_size, grain_fr, grain_ar = self._grain_for_period(days_inclusive)
        bucket_starts, _padded_max = self._build_buckets(eff_min, eff_max, bucket_size)

        timeline_labels = self._timeline_labels(bucket_starts, bucket_size)
        timeline_orders = [0] * len(bucket_starts)
        timeline_qty = [0] * len(bucket_starts)
        timeline_value = [0.0] * len(bucket_starts)

        orders_by_user: Dict[str, int] = defaultdict(int)
        qty_by_user: Dict[str, int] = defaultdict(int)
        value_by_user: Dict[str, float] = defaultdict(float)
        medical_count_by_user: Dict[str, int] = defaultdict(int)
        commercial_count_by_user: Dict[str, int] = defaultdict(int)

        for o in orders:
            oid = o.id
            d = o.added.date()

            if d < eff_min or d > eff_max:
                continue

            idx = int((d - eff_min).days) // int(bucket_size)
            if 0 <= idx < len(bucket_starts):
                timeline_orders[idx] += 1
                timeline_qty[idx] += int(order_total_qty.get(oid, 0))
                timeline_value[idx] += float(order_total_value.get(oid, 0.0))

            uname = _xlsx_safe(o.user.username)
            orders_by_user[uname] += 1
            qty_by_user[uname] += int(order_total_qty.get(oid, 0))
            value_by_user[uname] += float(order_total_value.get(oid, 0.0))

            if (o.pharmacy_id is not None) and (o.gros_id is not None):
                medical_count_by_user[uname] += 1
            if (o.pharmacy_id is None) and (o.gros_id is not None) and (o.super_gros_id is not None):
                commercial_count_by_user[uname] += 1

        if not timeline_labels:
            timeline_labels = ["-"]
            timeline_orders = [0]
            timeline_qty = [0]
            timeline_value = [0.0]

        # Single-user cumulative (per order, not bucketed)
        cum_dates: List[datetime] = []
        cum_values: List[float] = []
        if single_user_mode:
            running = 0.0
            for o in sorted(orders, key=lambda x: x.added):
                running += float(order_total_value.get(o.id, 0.0))
                cum_dates.append(o.added)
                cum_values.append(running)
            if not cum_dates:
                cum_dates = [timezone.now()]
                cum_values = [0.0]

        # Single-user product mix (pie): total quantities by product, top slices + "Autres"
        pie_products: List[str] = []
        pie_qtys: List[int] = []
        if single_user_mode:
            prodmap = user_prod_totals.get(single_user_key, {})
            pairs = [(p, int(q)) for p, q in prodmap.items() if int(q) > 0]
            pairs.sort(key=lambda x: x[1], reverse=True)

            # Keep pie readable: top 10 products + "Autres"
            top_n = 10
            top = pairs[:top_n]
            rest_sum = sum(q for _, q in pairs[top_n:])

            for p, q in top:
                pie_products.append(_xlsx_safe(p) or "-")
                pie_qtys.append(int(q))

            if rest_sum > 0:
                pie_products.append("Autres")
                pie_qtys.append(int(rest_sum))

            if not pie_products:
                pie_products = ["-"]
                pie_qtys = [0]

        # -----------------------
        # Workbook options
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

        # Palette
        DARK = "#1B5E20"
        MED = "#2E7D32"
        LIGHT = "#E8F5E9"

        # Formats
        fmt_title = wb.add_format({"bold": True, "font_size": 14, "bg_color": DARK, "font_color": "white"})
        fmt_section = wb.add_format({"bold": True, "font_size": 11, "bg_color": MED, "font_color": "white"})
        fmt_k = wb.add_format({"bold": True, "bg_color": LIGHT, "border": 1})
        fmt_cell = wb.add_format({"border": 1})
        fmt_wrap = wb.add_format({"border": 1, "text_wrap": True, "valign": "top"})
        fmt_card = wb.add_format({"bold": True, "bg_color": MED, "font_color": "white", "border": 1})
        fmt_num = wb.add_format({"border": 1, "num_format": "0"})
        fmt_dt = wb.add_format({"border": 1, "num_format": "yyyy-mm-dd hh:mm"})
        fmt_money = wb.add_format({"border": 1, "num_format": "#,##0.00"})

        # Dashboard formats
        fmt_dash_title = wb.add_format({"bold": True, "font_size": 16, "bg_color": DARK, "font_color": "white"})
        fmt_dash_band = wb.add_format({"bold": True, "font_size": 12, "bg_color": MED, "font_color": "white"})

        # ==========================================================
        # SHEET ORDER:
        # Commandes / Totaux Délégués / Totaux Clients / Sommaire / Dashboard
        # (Hidden sheet created last.)
        # ==========================================================

        # =========================
        # Sheet 1: Commandes
        # =========================
        ws_cmd = wb.add_worksheet("Commandes")
        ws_cmd.hide_gridlines(2)
        ws_cmd.set_tab_color(MED)
        ws_cmd.set_column(0, 0, 24)
        ws_cmd.set_column(1, 1, 62)
        ws_cmd.set_column(2, 6, 18)

        r = 0
        ws_cmd.merge_range(r, 0, r, 6, "BON DE COMMANDES — Export Excel", fmt_title)
        r += 2

        ws_cmd.merge_range(r, 0, r, 6, "Filtres appliqués", fmt_section)
        r += 1

        filter_lines = [
            ("Utilisateur(s)", request.GET.get("user") or "-"),
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
            ws_cmd.write_string(r, 0, _xlsx_safe(k), fmt_k)
            ws_cmd.merge_range(r, 1, r, 6, _xlsx_safe(v), fmt_cell)
            r += 1

        r += 1
        ws_cmd.merge_range(r, 0, r, 6, "Commandes (format carte)", fmt_section)
        r += 1

        for o in orders:
            header = f"{_xlsx_safe(o.user.username)} — Bon de Commande N° {o.id}"
            ws_cmd.merge_range(r, 0, r, 6, _xlsx_safe(header), fmt_card)
            r += 1

            ws_cmd.write_string(r, 0, "Ajouté le", fmt_k)
            ws_cmd.write_datetime(r, 1, o.added, fmt_dt)

            ws_cmd.write_string(r, 2, "Statut", fmt_k)
            ws_cmd.write_string(r, 3, _xlsx_safe(o.status), fmt_cell)

            ws_cmd.write_string(r, 4, "Transfert à", fmt_k)
            ws_cmd.write_string(r, 5, _xlsx_safe(o.touser.username) if o.touser else "-", fmt_cell)
            r += 1

            ws_cmd.write_string(r, 0, "Flag", fmt_k)
            ws_cmd.write_string(r, 1, _yn(bool(o.flag)), fmt_cell)
            ws_cmd.write_string(r, 2, "From company", fmt_k)
            ws_cmd.write_string(r, 3, _yn(bool(o.from_company)), fmt_cell)
            ws_cmd.write_string(r, 4, "En attente", fmt_k)
            ws_cmd.write_string(r, 5, _yn(bool(o.attente)), fmt_cell)
            r += 1

            products_lines = []
            for it in items_by_order.get(o.id, []):
                products_lines.append(f"{_xlsx_safe(it.produit.nom)} ({int(it.qtt or 0)})")
            products_text = ", ".join(products_lines) if products_lines else "-"

            kv = [
                ("Pharmacie", _label_pharmacy(o.pharmacy) if o.pharmacy else "-"),
                ("Grossiste", _label_gros(o.gros) if o.gros else "-"),
                ("Super Grossiste", _label_supergros(o.super_gros) if o.super_gros else "-"),
                ("Produits", products_text),
                ("Observation", _xlsx_safe(o.observation) if o.observation else "-"),
                ("Cause Flag", _xlsx_safe(o.cause) if o.cause else "-"),
            ]
            for k, v in kv:
                ws_cmd.write_string(r, 0, _xlsx_safe(k), fmt_k)
                ws_cmd.merge_range(r, 1, r, 6, _xlsx_safe(v), fmt_wrap)
                r += 1

            r += 1

        # =========================
        # Sheet 2: Totaux Délégués
        # =========================
        ws_del = wb.add_worksheet("Totaux Délégués")
        ws_del.hide_gridlines(2)
        ws_del.set_tab_color(MED)
        ws_del.set_column(0, 0, 28)
        ws_del.set_column(1, len(product_headers_unique) + 2, 14)

        # Add TOTAL VALEUR (DA)
        cols_user = ["Délégué"] + product_headers_unique + ["TOTAL", "TOTAL VALEUR (DA)"]
        user_rows = []
        for uname in sorted(user_totals_qty.keys(), key=lambda s: s.lower()):
            row = [uname]
            tot_qty = 0
            for pname in prod_by_index:
                v = int(user_prod_totals[uname].get(pname, 0))
                row.append(v)
                tot_qty += v
            row.append(tot_qty)
            row.append(float(value_by_user.get(uname, 0.0)))  # DA
            user_rows.append(row)

        if not user_rows:
            user_rows = [["-", *([0] * len(product_headers_unique)), 0, 0.0]]

        ws_del.add_table(
            0, 0, len(user_rows), len(cols_user) - 1,
            {
                "data": user_rows,
                "columns": (
                    [{"header": cols_user[0], "format": fmt_cell}]
                    + [{"header": h, "format": fmt_num} for h in cols_user[1:-1]]
                    + [{"header": cols_user[-1], "format": fmt_money}]
                ),
                "style": "Table Style Medium 21",
                "autofilter": True,
                "banded_rows": True,
            },
        )
        ws_del.freeze_panes(1, 1)

        # =========================
        # Sheet 3: Totaux Clients
        # =========================
        ws_cli = wb.add_worksheet("Totaux Clients")
        ws_cli.hide_gridlines(2)
        ws_cli.set_tab_color(MED)
        ws_cli.set_column(0, 0, 36)
        ws_cli.set_column(1, 1, 36)
        ws_cli.set_column(2, len(product_headers_unique) + 2, 14)

        cols_party = ["Client", "Fournisseur"] + product_headers_unique + ["TOTAL"]
        party_rows = []
        for (client, fournisseur) in sorted(party_totals.keys(), key=lambda t: (t[0].lower(), t[1].lower())):
            row = [_xlsx_safe(client), _xlsx_safe(fournisseur)]
            tot = 0
            for pname in prod_by_index:
                v = int(party_totals[(client, fournisseur)].get(pname, 0))
                row.append(v)
                tot += v
            row.append(tot)
            party_rows.append(row)

        if not party_rows:
            party_rows = [["-", "-", *([0] * len(product_headers_unique)), 0]]

        ws_cli.add_table(
            0, 0, len(party_rows), len(cols_party) - 1,
            {
                "data": party_rows,
                "columns": (
                    [{"header": cols_party[0], "format": fmt_cell}, {"header": cols_party[1], "format": fmt_cell}]
                    + [{"header": h, "format": fmt_num} for h in cols_party[2:]]
                ),
                "style": "Table Style Medium 21",
                "autofilter": True,
                "banded_rows": True,
            },
        )
        ws_cli.freeze_panes(1, 2)

        # =========================
        # Sheet 4: Sommaire
        # =========================
        ws_sum = wb.add_worksheet("Sommaire")
        ws_sum.hide_gridlines(2)
        ws_sum.set_tab_color(MED)
        ws_sum.set_column(0, 0, 16)
        ws_sum.set_column(1, 1, 18)
        ws_sum.set_column(2, 3, 34)
        ws_sum.set_column(4, 4 + len(product_headers_unique) - 1, 14)
        ws_sum.set_column(4 + len(product_headers_unique), 4 + len(product_headers_unique), 18)

        sum_headers = ["Bon de commande", "Utilisateur", "Client", "Fournisseur"] + product_headers_unique + ["Total valeur (DA)"]

        sommaire_rows = []
        for o in orders:
            oid = o.id
            uname = _xlsx_safe(o.user.username)
            client, fournisseur = _get_client_fournisseur(o)

            prod_qty_map = defaultdict(int)
            for it in items_by_order.get(oid, []):
                pn = _xlsx_safe(getattr(it.produit, "nom", ""))
                prod_qty_map[pn] += int(getattr(it, "qtt", 0) or 0)

            row = [int(oid), uname, _xlsx_safe(client), _xlsx_safe(fournisseur)]
            for pname in prod_by_index:
                row.append(int(prod_qty_map.get(pname, 0)))
            row.append(float(order_total_value.get(oid, 0.0)))  # DA
            sommaire_rows.append(row)

        if not sommaire_rows:
            sommaire_rows = [[0, "-", "-", "-", *([0] * len(product_headers_unique)), 0.0]]

        ws_sum.add_table(
            0, 0, len(sommaire_rows), len(sum_headers) - 1,
            {
                "data": sommaire_rows,
                "columns": (
                    [{"header": sum_headers[0], "format": fmt_num},
                     {"header": sum_headers[1], "format": fmt_cell},
                     {"header": sum_headers[2], "format": fmt_cell},
                     {"header": sum_headers[3], "format": fmt_cell}]
                    + [{"header": h, "format": fmt_num} for h in sum_headers[4:-1]]
                    + [{"header": sum_headers[-1], "format": fmt_money}]
                ),
                "style": "Table Style Medium 21",
                "autofilter": True,
                "banded_rows": True,
            },
        )
        ws_sum.freeze_panes(1, 4)

        # =========================
        # Sheet 5: Dashboard (STYLING IMPROVED)
        # =========================
        dash = wb.add_worksheet("Dashboard")
        dash.hide_gridlines(2)
        dash.set_tab_color(DARK)

        # Fit better on a 15" screen: reduce the effective dashboard width + zoom out slightly
        dash.set_zoom(90)

        # Keep a small left margin, then a compact working area (avoids horizontal scrolling).
        dash.set_column(0, 0, 2)    # A: margin
        dash.set_column(1, 1, 36)   # B: titles / anchor
        dash.set_column(2, 9, 14)   # C..J: compact grid for chart placement (no need to go to M/N)

        # Header (merge only across A..J)
        dash.merge_range(0, 0, 0, 9, "Tableau de bord | لوحة القيادة", fmt_dash_title)

        def _style_chart(chart):
            chart.set_chartarea({"fill": {"color": LIGHT}, "border": {"color": MED}})
            chart.set_plotarea({"fill": {"color": "white"}})
            chart.set_legend({"none": True})

        def _bar_height_for(ncats: int) -> int:
            # Slightly taller per category (more readable), but capped.
            return int(min(920, max(360, 120 + 28 * max(1, ncats))))

        # Layout helpers: stack charts vertically (prevents horizontal scrolling).
        _PX_PER_ROW = 20  # approximate default row height in pixels for spacing
        _CHART_W = 980    # safe width for most 15" screens (Excel window + ribbon)
        _CHART_H = 360    # taller line charts for readability
        _CHART_H_WIDE = 380
        _CHART_H_PIE = 520

        def _cell_b(row0: int) -> str:
            # Anchor all charts on column B to preserve the left margin.
            return f"B{row0 + 1}"

        def _next_row(row0: int, chart_h_px: int, gap_rows: int = 3) -> int:
            return row0 + int(chart_h_px / _PX_PER_ROW) + gap_rows

        # =========================
        # Sheet 6: Donnees Graphiques (hidden, LAST)
        # =========================
        ws_data = wb.add_worksheet("Donnees Graphiques")
        ws_data.hide_gridlines(2)
        ws_data.hide()

        # Timeline table
        ws_data.write_row(0, 0, ["Temps", "Nb commandes", "Qte totale", "Valeur totale (DA)"], fmt_k)
        for i, lab in enumerate(timeline_labels, start=1):
            ws_data.write_string(i, 0, _xlsx_safe(lab), fmt_cell)
            ws_data.write_number(i, 1, int(timeline_orders[i - 1]), fmt_num)
            ws_data.write_number(i, 2, int(timeline_qty[i - 1]), fmt_num)
            ws_data.write_number(i, 3, float(timeline_value[i - 1]), fmt_money)
        timeline_last = len(timeline_labels)  # data rows are 1..timeline_last

        # Single-user cumulative table (per order)
        cum_header_row = timeline_last + 3
        cum_last = cum_header_row
        if single_user_mode:
            ws_data.write_row(cum_header_row, 0, ["Date commande", "Valeur cumulée (DA)"], fmt_k)
            for j in range(len(cum_dates)):
                ws_data.write_datetime(cum_header_row + 1 + j, 0, cum_dates[j], fmt_dt)
                ws_data.write_number(cum_header_row + 1 + j, 1, float(cum_values[j]), fmt_money)
            cum_last = cum_header_row + len(cum_dates)

        # Single-user product mix table (pie)
        pie_row = cum_last + 3
        pie_last = pie_row
        if single_user_mode:
            ws_data.write_row(pie_row, 0, ["Produit", "Quantité"], fmt_k)
            for j, (p, q) in enumerate(zip(pie_products, pie_qtys), start=1):
                ws_data.write_string(pie_row + j, 0, _xlsx_safe(p), fmt_cell)
                ws_data.write_number(pie_row + j, 1, int(q), fmt_num)
            pie_last = pie_row + len(pie_products)

        # Comparison blocks
        def _write_user_block(start_row: int, title: str, metric: Dict[str, float], money: bool = False) -> Tuple[int, int, int]:
            data = self._top_n_with_ties_nonzero(metric, 10)
            ws_data.write_row(start_row, 0, ["Delegue", title], fmt_k)
            for j, (u, v) in enumerate(data, start=1):
                ws_data.write_string(start_row + j, 0, _xlsx_safe(u), fmt_cell)
                ws_data.write_number(start_row + j, 1, float(v), fmt_money if money else fmt_num)
            last_row = start_row + len(data)
            return start_row, last_row, len(data)

        row_u_orders = row_u_qty = row_u_value = row_u_med = row_u_com = 0
        last_u_orders = last_u_qty = last_u_value = last_u_med = last_u_com = 0
        n_orders = n_qty = n_val = n_med = n_com = 1

        if comparison_mode:
            start = max(timeline_last, pie_last) + 3
            row_u_orders, last_u_orders, n_orders = _write_user_block(start, "Nb commandes", {k: float(v) for k, v in orders_by_user.items()}, money=False)
            start = last_u_orders + 3
            row_u_qty, last_u_qty, n_qty = _write_user_block(start, "Qte totale", {k: float(v) for k, v in qty_by_user.items()}, money=False)
            start = last_u_qty + 3
            row_u_value, last_u_value, n_val = _write_user_block(start, "Valeur totale (DA)", {k: float(v) for k, v in value_by_user.items()}, money=True)
            start = last_u_value + 3
            row_u_med, last_u_med, n_med = _write_user_block(start, "Nb BDC Medical", {k: float(v) for k, v in medical_count_by_user.items()}, money=False)
            start = last_u_med + 3
            row_u_com, last_u_com, n_com = _write_user_block(start, "Nb BDC Commercial", {k: float(v) for k, v in commercial_count_by_user.items()}, money=False)

        # -------------------------
        # Dashboard charts (professional: stacked vertically, taller, no horizontal scroll)
        # -------------------------
        dash.merge_range(2, 0, 2, 9, f"Tendances ({grain_fr}) | الاتجاهات ({grain_ar})", fmt_dash_band)

        def _x_axis_opts(n_points: int) -> Dict:
            # Show fewer tick labels when crowded + slight rotation for readability.
            interval = max(1, n_points // 12) if n_points > 14 else 1
            rotation = -35 if n_points > 10 else 0
            return {
                "name": "Temps | الزمن",
                "interval_unit": interval,
                "num_font": {"size": 10, "rotation": rotation},
            }

        def _make_line(title: str, col_values: int, y_name: str, line_color: str, width: int, height: int):
            ch = wb.add_chart({"type": "line"})
            ch.set_style(10)
            _style_chart(ch)
            ch.set_title({"name": title, "name_font": {"size": 12, "bold": True}})
            ch.set_y_axis({"name": y_name, "num_font": {"size": 10}, "major_gridlines": {"visible": False}})
            ch.set_x_axis(_x_axis_opts(timeline_last))
            ch.add_series(
                {
                    "name": y_name,
                    "categories": ["Donnees Graphiques", 1, 0, timeline_last, 0],
                    "values": ["Donnees Graphiques", 1, col_values, timeline_last, col_values],
                    "line": {"color": line_color, "width": 2.5},
                }
            )
            ch.set_size({"width": width, "height": height})
            return ch

        # Trend charts (stacked)
        cur_row = 3  # row index for first chart anchor

        ch_orders = _make_line(
            f"Nombre de commandes ({grain_fr}) | عدد الطلبات ({grain_ar})",
            1,
            "Nombre | العدد",
            MED,
            _CHART_W,
            _CHART_H,
        )
        dash.insert_chart(_cell_b(cur_row), ch_orders, {"x_offset": 12, "y_offset": 8})
        cur_row = _next_row(cur_row, _CHART_H, gap_rows=4)

        ch_qty = _make_line(
            f"Quantité totale ({grain_fr}) | إجمالي الكمية ({grain_ar})",
            2,
            "Quantité | الكمية",
            DARK,
            _CHART_W,
            _CHART_H,
        )
        dash.insert_chart(_cell_b(cur_row), ch_qty, {"x_offset": 12, "y_offset": 8})
        cur_row = _next_row(cur_row, _CHART_H, gap_rows=4)

        ch_val = _make_line(
            f"Valeur totale (DA) ({grain_fr}) | إجمالي القيمة (DA) ({grain_ar})",
            3,
            "Valeur (DA) | القيمة (DA)",
            MED,
            _CHART_W,
            _CHART_H_WIDE,
        )
        dash.insert_chart(_cell_b(cur_row), ch_val, {"x_offset": 12, "y_offset": 8})
        cur_row = _next_row(cur_row, _CHART_H_WIDE, gap_rows=5)

        # Single-user: cumulative + product mix pie (stacked, larger, no horizontal scroll)
        if single_user_mode:
            dash.merge_range(cur_row, 0, cur_row, 9, "Analyse utilisateur | تحليل المستخدم", fmt_dash_band)
            cur_row += 1

            ch_cum = wb.add_chart({"type": "line"})
            ch_cum.set_style(10)
            _style_chart(ch_cum)
            ch_cum.set_title({"name": "Valeur cumulée (DA) | القيمة التراكمية (DA)", "name_font": {"size": 12, "bold": True}})
            ch_cum.set_y_axis({"name": "Valeur (DA) | القيمة (DA)", "num_font": {"size": 10}, "major_gridlines": {"visible": False}})
            ch_cum.set_x_axis({"name": "Date | التاريخ", "num_font": {"size": 10, "rotation": -35}})
            ch_cum.add_series(
                {
                    "name": "Cumul (DA) | التراكم (DA)",
                    "categories": ["Donnees Graphiques", cum_header_row + 1, 0, cum_last, 0],
                    "values": ["Donnees Graphiques", cum_header_row + 1, 1, cum_last, 1],
                    "line": {"color": DARK, "width": 2.5},
                }
            )
            ch_cum.set_size({"width": _CHART_W, "height": _CHART_H})
            dash.insert_chart(_cell_b(cur_row), ch_cum, {"x_offset": 12, "y_offset": 8})
            cur_row = _next_row(cur_row, _CHART_H, gap_rows=4)

            ch_pie = wb.add_chart({"type": "pie"})
            ch_pie.set_style(10)
            ch_pie.set_title({"name": "Répartition produits (Qté) | توزيع المنتجات (كمية)", "name_font": {"size": 12, "bold": True}})

            # Larger legend keys/squares + better readability.
            ch_pie.set_legend({
                "position": "right",
                "font": {"size": 11},
                "key": {"width": 28, "height": 28},
            })

            ch_pie.add_series(
                {
                    "name": "Quantité | الكمية",
                    "categories": ["Donnees Graphiques", pie_row + 1, 0, pie_last, 0],
                    "values":     ["Donnees Graphiques", pie_row + 1, 1, pie_last, 1],
                    "data_labels": {"percentage": True},
                }
            )
            ch_pie.set_size({"width": _CHART_W, "height": _CHART_H_PIE})
            dash.insert_chart(_cell_b(cur_row), ch_pie, {"x_offset": 12, "y_offset": 8})
            cur_row = _next_row(cur_row, _CHART_H_PIE, gap_rows=5)

        # Comparison-only charts (stacked vertically, no horizontal scroll)
        if comparison_mode:
            dash.merge_range(cur_row, 0, cur_row, 9, "Comparaison utilisateurs | مقارنة المستخدمين", fmt_dash_band)
            cur_row += 1

            def _make_bar(title: str, row_start: int, row_end: int, x_name: str, fill_color: str, border_color: str, height: int, width: int):
                ch = wb.add_chart({"type": "bar"})
                ch.set_style(10)
                _style_chart(ch)
                ch.set_title({"name": title, "name_font": {"size": 12, "bold": True}})
                ch.set_x_axis({"name": x_name, "num_font": {"size": 10}, "major_gridlines": {"visible": False}})
                ch.set_y_axis({"name": "Utilisateur | المستخدم", "num_font": {"size": 10}})
                ch.add_series(
                    {
                        "name": x_name,
                        "categories": ["Donnees Graphiques", row_start + 1, 0, row_end, 0],
                        "values": ["Donnees Graphiques", row_start + 1, 1, row_end, 1],
                        "fill": {"color": fill_color},
                        "border": {"color": border_color},
                    }
                )
                ch.set_size({"width": width, "height": height})
                return ch

            h_orders = _bar_height_for(n_orders)
            ch_u_orders = _make_bar(
                "Commandes / utilisateur | الطلبات / المستخدم",
                row_u_orders, last_u_orders,
                "Nombre | العدد",
                MED, DARK,
                h_orders,
                _CHART_W,
            )
            dash.insert_chart(_cell_b(cur_row), ch_u_orders, {"x_offset": 12, "y_offset": 8})
            cur_row = _next_row(cur_row, h_orders, gap_rows=4)

            h_qty = _bar_height_for(n_qty)
            ch_u_qty = _make_bar(
                "Quantité / utilisateur | الكمية / المستخدم",
                row_u_qty, last_u_qty,
                "Quantité | الكمية",
                DARK, MED,
                h_qty,
                _CHART_W,
            )
            dash.insert_chart(_cell_b(cur_row), ch_u_qty, {"x_offset": 12, "y_offset": 8})
            cur_row = _next_row(cur_row, h_qty, gap_rows=4)

            h_val = _bar_height_for(n_val)
            ch_u_val = _make_bar(
                "Valeur / utilisateur (DA) | القيمة / المستخدم (DA)",
                row_u_value, last_u_value,
                "Valeur (DA) | القيمة (DA)",
                MED, DARK,
                h_val,
                _CHART_W,
            )
            dash.insert_chart(_cell_b(cur_row), ch_u_val, {"x_offset": 12, "y_offset": 8})
            cur_row = _next_row(cur_row, h_val, gap_rows=4)

            h_med = _bar_height_for(n_med)
            ch_u_med = _make_bar(
                "Pharmacie → Grossiste / meilleur delegué medical| صيدلية → موزّع / أفضل مندوب طبي",
                row_u_med, last_u_med,
                "Nombre | العدد",
                MED, DARK,
                h_med,
                _CHART_W,
            )
            dash.insert_chart(_cell_b(cur_row), ch_u_med, {"x_offset": 12, "y_offset": 8})
            cur_row = _next_row(cur_row, h_med, gap_rows=4)

            h_com = _bar_height_for(n_com)
            ch_u_com = _make_bar(
                "BDC Grossiste → SuperGros / meilleur delegué commercial | موزّع → موزّع كبير / أفضل مندوب مبيعات",
                row_u_com, last_u_com,
                "Nombre | العدد",
                DARK, MED,
                h_com,
                _CHART_W,
            )
            dash.insert_chart(_cell_b(cur_row), ch_u_com, {"x_offset": 12, "y_offset": 8})
            cur_row = _next_row(cur_row, h_com, gap_rows=4)

        wb.close()
        output.seek(0)

        filename = f"bon_de_commandes_{timezone.now().strftime('%Y%m%d_%H%M')}.xlsx"
        resp = HttpResponse(
            output.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        resp["Content-Disposition"] = f'attachment; filename="{filename}"'
        return resp
