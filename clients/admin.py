from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.db.models import Sum, Q, Prefetch
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from .models import *
from .models import MonthComment
from accounts.models import UserProfile
from produits.models import Produit
from liliumpharm.utils import month_number_to_french_name


class MonthListFilter(admin.SimpleListFilter):
    title = _("Month")
    parameter_name = "month"

    def lookups(self, request, model_admin):
        months = [
            (1, _("January")),
            (2, _("February")),
            (3, _("March")),
            (4, _("April")),
            (5, _("May")),
            (6, _("June")),
            (7, _("July")),
            (8, _("August")),
            (9, _("September")),
            (10, _("October")),
            (11, _("November")),
            (12, _("December")),
        ]
        return months

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(date__month=self.value())


@admin.register(MonthComment)
class MonthCommentAdmin(admin.ModelAdmin):
    list_display = ("from_user", "to_user", "date", "comment", "date_added")
    list_filter = (
        MonthListFilter,
        "from_user",
    )
    search_fields = ("from_user__username", "to_user__username", "comment")
    date_hierarchy = "date_added"


def custom_titled_filter(title):
    class Wrapper(admin.FieldListFilter):
        def __new__(cls, *args, **kwargs):
            instance = admin.FieldListFilter.create(*args, **kwargs)
            instance.title = title
            return instance

    return Wrapper


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ["name", "related_client", "user", "wilaya", "Number_of_Grossiste"]
    list_filter = ["supergro", "related_client"]
    search_fields = [
        "name",
    ]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "related_client": 
            kwargs["queryset"] = Client.objects.filter(supergro=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def Number_of_Grossiste(self, obj):
        return obj.client_set.count() if obj.supergro else "-"

    def user(self, obj):
        if not obj.supergro:
            users_string = "".join(
                f"<div>{userprofile.user.first_name} {userprofile.user.last_name}</div>"
                for userprofile in UserProfile.objects.filter(sectors=obj.wilaya)
            )
            return mark_safe(users_string)
        return "-"


class OrderProductTabular(admin.TabularInline):
    model = OrderProduct


class UserFilter(SimpleListFilter):
    title = "---------- Tout les Utilisateurs ----------"
    parameter_name = "user"

    def lookups(self, request, model_admin):
        users = set([userprofile for userprofile in UserProfile.objects.select_related('user').all()])
        return [(user.user.id, user.user.username) for user in users]

    def queryset(self, request, queryset):
        userprofile = UserProfile.objects.filter(user__id=self.value())
        if userprofile.exists():
            userprofile = userprofile.first()
            return queryset.filter(client__wilaya__in=userprofile.sectors.all())
        return queryset


class SourceFilter(SimpleListFilter):
    title = "---------- Toutes les sources ----------"
    parameter_name = "source"

    def lookups(self, request, model_admin):
        months = request.GET.getlist("source__date__month")
        years = request.GET.getlist("source__date__year")
        return [
            (ordersource.id, ordersource.source.name)
            for ordersource in OrderSource.objects.filter(
                date__year__in=years, date__month__in=months
            )
        ]

    def queryset(self, request, queryset):
        sources = OrderSource.objects.filter(id=self.value())
        if sources.exists():
            return queryset.filter(source__in=sources)
        return queryset


class ClientFilter(SimpleListFilter):
    title = "---------- Toutes les clients ----------"
    parameter_name = "client"

    def lookups(self, request, model_admin):
        months = request.GET.getlist("source__date__month")
        years = request.GET.getlist("source__date__year")
        return [
            (order.client.id, order.client.name)
            for order in Order.objects.filter(
                source__date__year__in=years, source__date__month__in=months
            )
        ]

    def queryset(self, request, queryset):
        clients = Client.objects.filter(id=self.value())
        if clients.exists():
            return queryset.filter(client__in=clients)
        return queryset


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderProductTabular]
    list_display = ["source", "wilaya", "client", "user"]
    list_filter = [
        SourceFilter,
        ClientFilter,
        "client__wilaya",
        ("products", custom_titled_filter("---------- Tout les Produits ----------")),
        UserFilter,
    ]
    search_fields = [
        "client__name",
    ]
    date_hierarchy = "source__date"
    ordering = [
        "client",
    ]
    change_list_template = "admin/order/change_list.html"

    # Optimization: Prefetch to prevent N+1 Queries
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('client__wilaya', 'source').prefetch_related(
            'orderproduct_set__produit'
        )

    def changelist_view(self, request, extra_context=None):
        params = request.GET
        string_filter_request = ""
        query = Q()

        if "source__id__exact" in params:
            query &= Q(source__id__exact=params.get("source__id__exact"))
            string_filter_request += f'&source__id__exact={params.get("source__id__exact")}'

        if "source__date__month" in params:
            query &= Q(source__date__month=params.get("source__date__month"))
            string_filter_request += f'&month={params.get("source__date__month")}'

        if "source__date__year" in params:
            query &= Q(source__date__year=params.get("source__date__year"))
            string_filter_request += f'&year={params.get("source__date__year")}'

        if "client__id__exact" in params:
            query &= Q(client__id__exact=params.get("client__id__exact"))
            string_filter_request += f'&client__id__exact={params.get("client__id__exact")}'

        if "client__wilaya__id__exact" in params:
            query &= Q(client__wilaya__id__exact=params.get("client__wilaya__id__exact"))
            string_filter_request += f'&client_wilaya_id={params.get("client__wilaya__id__exact")}'

        if "products__id__exact" in params:
            query &= Q(products__id__exact=params.get("products__id__exact"))
            string_filter_request += f'&products__id__exact={params.get("products__id__exact")}'

        if "user" in params:
            query &= Q(client__wilaya__userprofile__user__id=params.get("user"))
            string_filter_request += f'&user={params.get("user")}'

        total_products = []
        orders = Order.objects.filter(query)
        order_products = OrderProduct.objects.filter(order__in=orders)
        products = Produit.objects.all()
        global_total = 0

        for product in products:
            total = (
                order_products.filter(produit=product)
                .values("produit__nom")
                .annotate(total=Sum("qtt"))
            )
            total = total[0]["total"] if total else 0
            total_products.append({"product": product.nom, "total": total})
            global_total += total

        context = {
            "total_products": total_products,
            "global_total": global_total,
            "params": string_filter_request[1:],
        }
        return super(OrderAdmin, self).changelist_view(request, extra_context=context)

    @admin.display(ordering="client__wilaya__nom")
    def wilaya(self, obj):
        return obj.client.wilaya.nom if obj.client else ""

    def user(self, obj):
        query_set = UserProfile.objects.filter(sectors=obj.client.wilaya)
        return mark_safe("".join(f"{user.user.username}</br>" for user in query_set))

    # Helper function for fetching quantities purely from prefetched memory
    def get_product_quantity(self, obj, product_name):
        for op in obj.orderproduct_set.all():
            if op.produit.nom == product_name:
                return op.qtt
        return 0

    def FF(self, obj): return self.get_product_quantity(obj, "FF")
    def FM(self, obj): return self.get_product_quantity(obj, "FM")
    def IRON(self, obj): return self.get_product_quantity(obj, "IRON")
    def YES_CAL(self, obj): return self.get_product_quantity(obj, "YES CAL")
    def YES_VIT(self, obj): return self.get_product_quantity(obj, "YES VIT")
    def ADVAGEN(self, obj): return self.get_product_quantity(obj, "ADVAGEN")
    def DHEA_75mg(self, obj): return self.get_product_quantity(obj, "DHEA 75mg")
    def HAIRVOL(self, obj): return self.get_product_quantity(obj, "HAIRVOL")
    def SUB12(self, obj): return self.get_product_quantity(obj, "SUB12")
    def MENOLIB(self, obj): return self.get_product_quantity(obj, "MENOLIB")
    def THYROLIB(self, obj): return self.get_product_quantity(obj, "THYROLIB")
    def HEPALIB(self, obj): return self.get_product_quantity(obj, "HEPALIB")
    def SOPK_FREE(self, obj): return self.get_product_quantity(obj, "SOPK FREE")
    def URISOFT(self, obj): return self.get_product_quantity(obj, "URISOFT")
    def URICITRIL(self, obj): return self.get_product_quantity(obj, "URICITRIL")
    def BESTFER(self, obj): return self.get_product_quantity(obj, "BESTFER")
    def DIGEST_PLUS(self, obj): return self.get_product_quantity(obj, "DIGEST PLUS")
    def ANAFLAM(self, obj): return self.get_product_quantity(obj, "ANAFLAM")
    def New_B(self, obj): return self.get_product_quantity(obj, "New B")


class OrderSourceProductInLine(admin.TabularInline):
    model = OrderSourceProduct
    verbose_name = "Produit en Stock"
    verbose_name_plural = "Produits en Stock"


class YearListFilter(admin.SimpleListFilter):
    title = "Year"
    parameter_name = "year"

    def lookups(self, request, model_admin):
        return (("2025", "2025"), ("2026", "2026"))

    def queryset(self, request, queryset):
        if self.value() == "2025":
            return queryset.filter(date__year="2025")
        elif self.value() == "2026":
            return queryset.filter(date__year="2026")
        return queryset


@admin.register(OrderSource)
class OrderSourceAdmin(admin.ModelAdmin):
    inlines = [OrderSourceProductInLine]
    list_display = ["Supergrossiste", "attachement", "Month", "Reports"]
    list_filter = [
        ("source", custom_titled_filter("------------------ Tout les Super Grossistes ------------------")),
        YearListFilter,
    ]
    date_hierarchy = "date"

    # Optimization: Prefetch related data
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('source').prefetch_related(
            'ordersourceproduct_set__produit',
            'order_set__orderproduct_set__produit'
        )

    def attachement(self, obj):
        if obj.attachement_file:
            return mark_safe(f'<a class="btn btn-outline-success" target="_blank" href="/media/{obj.attachement_file}">Attachement</a>')
        return mark_safe(f'<div class="btn btn-outline-danger disabled">No Attachement</a>')

    attachement.short_description = "Attachment"

    def Supergrossiste(self, obj): return obj.source.name
    def Month(self, obj): return f"{obj.date.month}/{obj.date.year}"

    def Reports(self, obj):
        return mark_safe(f'<a class="btn btn-outline-success float-right" target="_blank" href="/clients/print-sales/{obj.id}">Rapport des Ventes</a>')

    # Replaced inefficient DB calls with memory calculation using prefetched objects
    def get_product_quantity(self, obj, product_name):
        total_ordered = sum(
            op.qtt 
            for order in obj.order_set.all() 
            for op in order.orderproduct_set.all() 
            if op.produit.nom == product_name
        )
        
        stock_qtt = 0
        for osp in obj.ordersourceproduct_set.all():
            if osp.produit.nom == product_name:
                stock_qtt = osp.qtt
                break
                
        return mark_safe(f'<span>{total_ordered} | </span> <span style="color: orange">{stock_qtt}</span>')

    def FF(self, obj): return self.get_product_quantity(obj, "FF")
    def FM(self, obj): return self.get_product_quantity(obj, "FM")
    def IRON(self, obj): return self.get_product_quantity(obj, "IRON")
    def YES_CAL(self, obj): return self.get_product_quantity(obj, "YES CAL")
    def YES_VIT(self, obj): return self.get_product_quantity(obj, "YES VIT")
    def ADVAGEN(self, obj): return self.get_product_quantity(obj, "ADVAGEN")
    def DHEA_75mg(self, obj): return self.get_product_quantity(obj, "DHEA 75mg")
    def HAIRVOL(self, obj): return self.get_product_quantity(obj, "HAIRVOL")
    def SUB12(self, obj): return self.get_product_quantity(obj, "SUB12")
    def MENOLIB(self, obj): return self.get_product_quantity(obj, "MENOLIB")
    def THYROLIB(self, obj): return self.get_product_quantity(obj, "THYROLIB")
    def HEPALIB(self, obj): return self.get_product_quantity(obj, "HEPALIB")
    def SOPK_FREE(self, obj): return self.get_product_quantity(obj, "SOPK FREE")
    def URISOFT(self, obj): return self.get_product_quantity(obj, "URISOFT")
    def URICITRIL(self, obj): return self.get_product_quantity(obj, "URICITRIL")
    def BESTFER(self, obj): return self.get_product_quantity(obj, "BESTFER")
    def DIGEST_PLUS(self, obj): return self.get_product_quantity(obj, "DIGEST PLUS")
    def ANAFLAM(self, obj): return self.get_product_quantity(obj, "ANAFLAM")
    def New_B(self, obj): return self.get_product_quantity(obj, "New B")

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "source":
            kwargs["queryset"] = Client.objects.filter(supergro=True)
        return super(OrderSourceAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        form = super(OrderSourceAdmin, self).get_form(request, obj, **kwargs)
        try:
            form.base_fields["date"].initial = date.today()
        except:
            pass
        return form


class UserTargetMonthProductInLine(admin.TabularInline):
    model = UserTargetMonthProduct


@admin.action(description="Clôner pour le Prochain Mois")
def duplicate_for_next_month(modeladmin, request, queryset):
    for data in queryset:
        date_after_month = data.date + relativedelta(months=1)
        
        # Robust Fix: Use get_or_create to prevent duplicating duplicate entries
        user_target_month, created = UserTargetMonth.objects.get_or_create(
            date=date_after_month, 
            user=data.user
        )

        if created:
            for utm in data.usertargetmonthproduct_set.all():
                UserTargetMonthProduct.objects.create(
                    usermonth=user_target_month,
                    product=utm.product,
                    quantity=utm.quantity,
                )


@admin.register(UserTargetMonth)
class UserTargetMonthAdmin(admin.ModelAdmin):
    inlines = (UserTargetMonthProductInLine,)
    list_filter = ["user", "user__userprofile__family"]
    list_display = [
        "user",
        "mois",
        *[p.nom.replace(" ", "_") for p in Produit.objects.all()],
        "print_button",
    ]
    date_hierarchy = "date"
    actions = [duplicate_for_next_month]

    # Optimization: prefetch_related here solves your slow loading and N+1 issue
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user__userprofile').prefetch_related(
            'usertargetmonthproduct_set__product'
        )

    def get_family(self, obj):
        return obj.user.userprofile.family

    get_family.short_description = "Family"

    def mois(self, obj):
        if obj.date:
            return f"{month_number_to_french_name(obj.date.month)} {obj.date.year}"
        return "-"

    def print_button(self, obj):
        url = reverse("usertargetmonth_print", args=[obj.id])
        return format_html('<a class="button" href="{}" target="_blank">Imprimer</a>', url)

    print_button.short_description = "Impression"

    # This method is now 100% memory based and will correctly match the inline View perfectly

    def get_quantity(self, obj, product_name):
        # Normalize the requested name (lowercase, replace underscores with spaces)
        search_target = product_name.lower().replace("_", " ")
        
        for utm_product in obj.usertargetmonthproduct_set.all():
            # Normalize the database name the exact same way
            db_product_name = utm_product.product.nom.lower().replace("_", " ")
            
            # Now "GOLD_MAG" and "Gold mag" will perfectly match as "gold mag"
            if db_product_name == search_target:
                return utm_product.quantity
                
        return "0"

    def FF(self, obj): return self.get_quantity(obj, "FF")
    def SLEEP_ALAISE(self, obj): return self.get_quantity(obj, "SLEEP_ALAISE")
    def GOLD_MAG(self, obj): return self.get_quantity(obj, "GOLD_MAG")
    def FM(self, obj): return self.get_quantity(obj, "FM")
    def IRON(self, obj): return self.get_quantity(obj, "IRON")
    def YES_CAL(self, obj): return self.get_quantity(obj, "YES CAL")
    def YES_VIT(self, obj): return self.get_quantity(obj, "YES VIT")
    def ADVAGEN(self, obj): return self.get_quantity(obj, "ADVAGEN")
    def DHEA_75mg(self, obj): return self.get_quantity(obj, "DHEA 75mg")
    def HAIRVOL(self, obj): return self.get_quantity(obj, "HAIRVOL")
    def SUB12(self, obj): return self.get_quantity(obj, "SUB12")
    def MENOLIB(self, obj): return self.get_quantity(obj, "MENOLIB")
    def THYROLIB(self, obj): return self.get_quantity(obj, "THYROLIB")
    def HEPALIB(self, obj): return self.get_quantity(obj, "HEPALIB")
    def SOPK_FREE(self, obj): return self.get_quantity(obj, "SOPK FREE")
    def URISOFT(self, obj): return self.get_quantity(obj, "URISOFT")
    def URICITRIL(self, obj): return self.get_quantity(obj, "URICITRIL")
    def BESTFER(self, obj): return self.get_quantity(obj, "BESTFER")
    def DIGEST_PLUS(self, obj): return self.get_quantity(obj, "DIGEST PLUS")
    def ANAFLAM(self, obj): return self.get_quantity(obj, "ANAFLAM")
    def New_B(self, obj): return self.get_quantity(obj, "New B")
    def Prosta_Soft(self, obj): return self.get_quantity(obj, "Prosta Soft")
    def Mamilis(self, obj): return self.get_quantity(obj, "Mamilis")
    def Veno_Soft(self, obj): return self.get_quantity(obj, "Veno Soft")


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "excel_file",
        "date",
    ]