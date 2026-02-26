from django.contrib import admin
from django.utils.safestring import mark_safe
from django.db.models import Sum
from django.contrib.admin import SimpleListFilter
from django.db.models import Q
from .models import *
from accounts.models import UserProfile
from produits.models import Produit

from liliumpharm.utils import month_number_to_french_name


from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import MonthComment

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from datetime import datetime
from dateutil.relativedelta import relativedelta


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
        if (
            db_field.name == "related_client"
        ):  # Yeah Tertaggg - COME ON BABY TEL3ABLI BIH SHUIY...
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
        users = set([userprofile for userprofile in UserProfile.objects.all()])
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
    # list_display = ["source", "wilaya", "client","user", *[p.nom.replace(" ", "_") for p in Produit.objects.all()]]
    list_display = ["source", "wilaya", "client", "user"]
    list_filter = [
        SourceFilter,
        ClientFilter,
        "client__wilaya",
        ("products", custom_titled_filter("---------- Tout les Produits ----------")),
        UserFilter,
    ]
    # list_filter= [("source", custom_titled_filter('---------- Tout les Super Grossistes ----------')),
    #                 ("client", custom_titled_filter('---------- Tout les Grossistes ----------')),
    #                 ("client__wilaya", custom_titled_filter('---------- Tout les Wilaya ----------')),
    #                 ("products", custom_titled_filter('---------- Tout les Produits ----------')), UserFilter]
    search_fields = [
        "client__name",
    ]
    date_hierarchy = "source__date"  # Hmmm You Touch My TKHALALAAAAAA TARTAG

    ordering = [
        "client",
    ]

    change_list_template = "admin/order/change_list.html"

    def changelist_view(self, request, extra_context=None):

        params = request.GET

        # Building Filter as String
        string_filter_request = ""

        query = Q()

        if "source__id__exact" in params:
            query &= Q(source__id__exact=params.get("source__id__exact"))
            string_filter_request += (
                f'&source__id__exact={params.get("source__id__exact")}'
            )

        if "source__date__month" in params:
            query &= Q(source__date__month=params.get("source__date__month"))
            string_filter_request += f'&month={params.get("source__date__month")}'

        if "source__date__year" in params:
            query &= Q(source__date__year=params.get("source__date__year"))
            string_filter_request += f'&year={params.get("source__date__year")}'

        if "client__id__exact" in params:
            query &= Q(client__id__exact=params.get("client__id__exact"))
            string_filter_request += (
                f'&client__id__exact={params.get("client__id__exact")}'
            )

        if "client__wilaya__id__exact" in params:
            query &= Q(
                client__wilaya__id__exact=params.get("client__wilaya__id__exact")
            )
            string_filter_request += (
                f'&client_wilaya_id={params.get("client__wilaya__id__exact")}'
            )

        if "products__id__exact" in params:
            query &= Q(products__id__exact=params.get("products__id__exact"))
            string_filter_request += (
                f'&products__id__exact={params.get("products__id__exact")}'
            )

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

    def FF(self, obj):
        query_set = OrderProduct.objects.filter(order=obj, produit__nom="FF")
        return query_set.first().qtt if query_set.exists() else 0

    def FM(self, obj):
        query_set = OrderProduct.objects.filter(order=obj, produit__nom="FM")
        return query_set.first().qtt if query_set.exists() else 0

    def IRON(self, obj):
        query_set = OrderProduct.objects.filter(order=obj, produit__nom="IRON")
        return query_set.first().qtt if query_set.exists() else 0

    def YES_CAL(self, obj):
        query_set = OrderProduct.objects.filter(order=obj, produit__nom="YES CAL")
        return query_set.first().qtt if query_set.exists() else 0

    def YES_VIT(self, obj):
        query_set = OrderProduct.objects.filter(order=obj, produit__nom="YES VIT")
        return query_set.first().qtt if query_set.exists() else 0

    def ADVAGEN(self, obj):
        query_set = OrderProduct.objects.filter(order=obj, produit__nom="ADVAGEN")
        return query_set.first().qtt if query_set.exists() else 0

    def DHEA_75mg(self, obj):
        query_set = OrderProduct.objects.filter(order=obj, produit__nom="DHEA 75mg")
        return query_set.first().qtt if query_set.exists() else 0

    def HAIRVOL(self, obj):
        query_set = OrderProduct.objects.filter(order=obj, produit__nom="HAIRVOL")
        return query_set.first().qtt if query_set.exists() else 0

    def SUB12(self, obj):
        query_set = OrderProduct.objects.filter(order=obj, produit__nom="SUB12")
        return query_set.first().qtt if query_set.exists() else 0

    def MENOLIB(self, obj):
        query_set = OrderProduct.objects.filter(order=obj, produit__nom="MENOLIB")
        return query_set.first().qtt if query_set.exists() else 0

    def THYROLIB(self, obj):
        query_set = OrderProduct.objects.filter(order=obj, produit__nom="THYROLIB")
        return query_set.first().qtt if query_set.exists() else 0

    def HEPALIB(self, obj):
        query_set = OrderProduct.objects.filter(order=obj, produit__nom="HEPALIB")
        return query_set.first().qtt if query_set.exists() else 0

    def SOPK_FREE(self, obj):
        query_set = OrderProduct.objects.filter(order=obj, produit__nom="SOPK FREE")
        return query_set.first().qtt if query_set.exists() else 0

    def URISOFT(self, obj):
        query_set = OrderProduct.objects.filter(order=obj, produit__nom="URISOFT")
        return query_set.first().qtt if query_set.exists() else 0

    def URICITRIL(self, obj):
        query_set = OrderProduct.objects.filter(order=obj, produit__nom="URICITRIL")
        return query_set.first().qtt if query_set.exists() else 0

    def BESTFER(self, obj):
        query_set = OrderProduct.objects.filter(order=obj, produit__nom="BESTFER")
        return query_set.first().qtt if query_set.exists() else 0

    def DIGEST_PLUS(self, obj):
        query_set = OrderProduct.objects.filter(order=obj, produit__nom="DIGEST PLUS")
        return query_set.first().qtt if query_set.exists() else 0

    def ANAFLAM(self, obj):
        query_set = OrderProduct.objects.filter(order=obj, produit__nom="ANAFLAM")
        return query_set.first().qtt if query_set.exists() else 0
    
    def New_B(self, obj):
        query_set = OrderProduct.objects.filter(order=obj, produit__nom="New B")
        return query_set.first().qtt if query_set.exists() else 0


class OrderSourceProductInLine(admin.TabularInline):
    model = OrderSourceProduct
    verbose_name = "Produit en Stock"
    verbose_name_plural = "Produits en Stock"


from datetime import datetime


class YearListFilter(admin.SimpleListFilter):
    title = "Year"
    parameter_name = "year"

    def lookups(self, request, model_admin):
        return (("2024", "2024"),("2025", "2025"),)

    def queryset(self, request, queryset):
        print("fatahfatahfatah")
        params = request.GET.dict()
        print(params)
        print(queryset)
        #if self.value() == "2024" or self.value() is None:
        if self.value() == "2024":
            return queryset.filter(date__year="2024")
        elif self.value() =="2025":
            return queryset.filter(date__year="2025")
        else:
            return queryset.none()


@admin.register(OrderSource)
class OrderSourceAdmin(admin.ModelAdmin):
    inlines = [
        OrderSourceProductInLine,
    ]
    # list_display = ["Supergrossiste", "attachement",  "Month", "number_of_orders", *[p.nom.replace(" ", "_") for p in Produit.objects.all()], "Reports"]
    list_display = ["Supergrossiste", "attachement", "Month", "Reports"]
    list_filter = [
        (
            "source",
            custom_titled_filter(
                "------------------ Tout les Super Grossistes ------------------"
            ),
        ),
        YearListFilter,
    ]
    date_hierarchy = "date"

    def attachement(self, obj):
        if obj.attachement_file:
            return mark_safe(
                f'<a class="btn btn-outline-success" target="_blank" href="/media/{obj.attachement_file}">Attachement</a>'
            )

        return mark_safe(
            f'<div class="btn btn-outline-danger disabled">No Attachement</a>'
        )

    attachement.short_description = "Attachment"

    # def number_of_orders(self, obj):
    #     return mark_safe(f'<div class="text-bold text-center text-danger">{obj.order_set.all().count()}</a>')

    def Supergrossiste(self, obj):
        return obj.source.name

    def Month(self, obj):
        return f"{obj.date.month}/{obj.date.year}"

    def Reports(self, obj):
        month = obj.date.month
        year = obj.date.year
        return mark_safe(
            f'<a class="btn btn-outline-success float-right" target="_blank" href="/clients/print-sales/{obj.id}">Rapport des Ventes</a>'
        )

    @staticmethod
    def get_product_quantity(product_name, source_order):
        query_set = (
            OrderProduct.objects.filter(
                produit__nom=product_name, order__in=source_order.order_set.all()
            )
            .values("produit__nom")
            .annotate(total=Sum("qtt"))
        )
        return query_set[0].get("total") if query_set else 0

    def FF(self, obj):
        product = obj.ordersourceproduct_set.filter(produit__nom="FF")
        quantity = product.first().qtt if product.exists() else 0
        return mark_safe(
            f'<span>{OrderSourceAdmin.get_product_quantity("FF", obj)} | </span> <span style="color: orange">{quantity}</span>'
        )

    def FM(self, obj):
        product = obj.ordersourceproduct_set.filter(produit__nom="FM")
        quantity = product.first().qtt if product.exists() else 0
        return mark_safe(
            f'<span>{OrderSourceAdmin.get_product_quantity("FM", obj)} | </span> <span style="color: orange">{quantity}</span>'
        )

    def IRON(self, obj):
        product = obj.ordersourceproduct_set.filter(produit__nom="IRON")
        quantity = product.first().qtt if product.exists() else 0
        return mark_safe(
            f'<span>{OrderSourceAdmin.get_product_quantity("IRON", obj)} | </span> <span style="color: orange">{quantity}</span>'
        )

    def YES_CAL(self, obj):
        product = obj.ordersourceproduct_set.filter(produit__nom="YES CAL")
        quantity = product.first().qtt if product.exists() else 0
        return mark_safe(
            f'<span>{OrderSourceAdmin.get_product_quantity("YES CAL", obj)} | </span> <span style="color: orange">{quantity}</span>'
        )

    def YES_VIT(self, obj):
        product = obj.ordersourceproduct_set.filter(produit__nom="YES VIT")
        quantity = product.first().qtt if product.exists() else 0
        return mark_safe(
            f'<span">{OrderSourceAdmin.get_product_quantity("YES VIT", obj)} | </span> <span style="color: orange">{quantity}</span>'
        )

    def ADVAGEN(self, obj):
        product = obj.ordersourceproduct_set.filter(produit__nom="ADVAGEN")
        quantity = product.first().qtt if product.exists() else 0
        return mark_safe(
            f'<span>{OrderSourceAdmin.get_product_quantity("ADVAGEN", obj)} | </span> <span style="color: orange">{quantity}</span>'
        )

    def DHEA_75mg(self, obj):
        product = obj.ordersourceproduct_set.filter(produit__nom="DHEA 75mg")
        quantity = product.first().qtt if product.exists() else 0
        return mark_safe(
            f'<span>{OrderSourceAdmin.get_product_quantity("DHEA 75mg", obj)} | </span> <span style="color: orange">{quantity}</span>'
        )

    def HAIRVOL(self, obj):
        product = obj.ordersourceproduct_set.filter(produit__nom="HAIRVOL")
        quantity = product.first().qtt if product.exists() else 0
        return mark_safe(
            f'<span>{OrderSourceAdmin.get_product_quantity("HAIRVOL", obj)} | </span> <span style="color: orange">{quantity}</span>'
        )

    def SUB12(self, obj):
        product = obj.ordersourceproduct_set.filter(produit__nom="SUB12")
        quantity = product.first().qtt if product.exists() else 0
        return mark_safe(
            f'<span>{OrderSourceAdmin.get_product_quantity("SUB12", obj)} | </span> <span style="color: orange">{quantity}</span>'
        )

    def MENOLIB(self, obj):
        product = obj.ordersourceproduct_set.filter(produit__nom="MENOLIB")
        quantity = product.first().qtt if product.exists() else 0
        return mark_safe(
            f'<span>{OrderSourceAdmin.get_product_quantity("MENOLIB", obj)} | </span> <span style="color: orange">{quantity}</span>'
        )

    def THYROLIB(self, obj):
        product = obj.ordersourceproduct_set.filter(produit__nom="THYROLIB")
        quantity = product.first().qtt if product.exists() else 0
        return mark_safe(
            f'<span>{OrderSourceAdmin.get_product_quantity("THYROLIB", obj)} | </span> <span style="color: orange">{quantity}</span>'
        )

    def HEPALIB(self, obj):
        product = obj.ordersourceproduct_set.filter(produit__nom="HEPALIB")
        quantity = product.first().qtt if product.exists() else 0
        return mark_safe(
            f'<span>{OrderSourceAdmin.get_product_quantity("HEPALIB", obj)} | </span> <span style="color: orange">{quantity}</span>'
        )

    def SOPK_FREE(self, obj):
        product = obj.ordersourceproduct_set.filter(produit__nom="SOPK FREE")
        quantity = product.first().qtt if product.exists() else 0
        return mark_safe(
            f'<span>{OrderSourceAdmin.get_product_quantity("SOPK FREE", obj)} | </span> <span style="color: orange">{quantity}</span>'
        )

    def URISOFT(self, obj):
        product = obj.ordersourceproduct_set.filter(produit__nom="URISOFT")
        quantity = product.first().qtt if product.exists() else 0
        return mark_safe(
            f'<span>{OrderSourceAdmin.get_product_quantity("URISOFT", obj)} | </span> <span style="color: orange">{quantity}</span>'
        )

    def URICITRIL(self, obj):
        product = obj.ordersourceproduct_set.filter(produit__nom="URICITRIL")
        quantity = product.first().qtt if product.exists() else 0
        return mark_safe(
            f'<span>{OrderSourceAdmin.get_product_quantity("URICITRIL", obj)} | </span> <span style="color: orange">{quantity}</span>'
        )

    def BESTFER(self, obj):
        product = obj.ordersourceproduct_set.filter(produit__nom="BESTFER")
        quantity = product.first().qtt if product.exists() else 0
        return mark_safe(
            f'<span>{OrderSourceAdmin.get_product_quantity("BESTFER", obj)} | </span> <span style="color: orange">{quantity}</span>'
        )

    def DIGEST_PLUS(self, obj):
        product = obj.ordersourceproduct_set.filter(produit__nom="DIGEST PLUS")
        quantity = product.first().qtt if product.exists() else 0
        return mark_safe(
            f'<span>{OrderSourceAdmin.get_product_quantity("DIGEST PLUS", obj)} | </span> <span style="color: orange">{quantity}</span>'
        )

    def ANAFLAM(self, obj):
        product = obj.ordersourceproduct_set.filter(produit__nom="ANAFLAM")
        quantity = product.first().qtt if product.exists() else 0
        return mark_safe(
            f'<span>{OrderSourceAdmin.get_product_quantity("ANAFLAM", obj)} | </span> <span style="color: orange">{quantity}</span>'
        )
    def New_B(self, obj):
        product = obj.ordersourceproduct_set.filter(produit__nom="New B")
        quantity = product.first().qtt if product.exists() else 0
        return mark_safe(
            f'<span>{OrderSourceAdmin.get_product_quantity("New B", obj)} | </span> <span style="color: orange">{quantity}</span>'
        )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "source":
            kwargs["queryset"] = Client.objects.filter(supergro=True)
        return super(OrderSourceAdmin, self).formfield_for_foreignkey(
            db_field, request, **kwargs
        )

    def get_form(self, request, obj=None, **kwargs):
        from datetime import date

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
    from datetime import datetime
    from dateutil.relativedelta import relativedelta

    for data in queryset:
        date_after_month = data.date + relativedelta(months=1)
        user_target_month = UserTargetMonth.objects.filter(
            date=date_after_month, user=data.user
        )

        if not user_target_month.exists():
            user_target_month = UserTargetMonth.objects.create(
                date=date_after_month, user=data.user
            )

            for utm in data.usertargetmonthproduct_set.all():
                UserTargetMonthProduct.objects.create(
                    usermonth=user_target_month,
                    product=utm.product,
                    quantity=utm.quantity,
                )


# @admin.register(UserTargetMonth)
# class UserTargetMonthAdmin(admin.ModelAdmin):
#     inlines = (UserTargetMonthProductInLine,)
#     list_filter = ["user", "user__userprofile__family"]
#     list_display = [
#         "user",
#         "get_family",
#         "mois",
#         *[p.nom.replace(" ", "_") for p in Produit.objects.all()],
#     ]
#     date_hierarchy = "date"
#     actions = [duplicate_for_next_month]

#     def get_family(self, obj):
#         return obj.user.userprofile.family

#     get_family.short_description = "Family"

#     def mois(self, obj):
#         return f"{month_number_to_french_name(obj.date.month)} {obj.date.year}"

#     def FF(self, obj):
#         query_set = UserTargetMonthProduct.objects.filter(
#             usermonth=obj, product__nom="FF"
#         )
#         return query_set.first().quantity if query_set.exists() else "0"

#     def FM(self, obj):
#         query_set = UserTargetMonthProduct.objects.filter(
#             usermonth=obj, product__nom="FM"
#         )
#         return query_set.first().quantity if query_set.exists() else "0"

#     def IRON(self, obj):
#         query_set = UserTargetMonthProduct.objects.filter(
#             usermonth=obj, product__nom="IRON"
#         )
#         return query_set.first().quantity if query_set.exists() else "0"

#     def YES_CAL(self, obj):
#         query_set = UserTargetMonthProduct.objects.filter(
#             usermonth=obj, product__nom="YES CAL"
#         )
#         return query_set.first().quantity if query_set.exists() else "0"

#     def YES_VIT(self, obj):
#         query_set = UserTargetMonthProduct.objects.filter(
#             usermonth=obj, product__nom="YES VIT"
#         )
#         return query_set.first().quantity if query_set.exists() else "0"

#     def ADVAGEN(self, obj):
#         query_set = UserTargetMonthProduct.objects.filter(
#             usermonth=obj, product__nom="ADVAGEN"
#         )
#         return query_set.first().quantity if query_set.exists() else "0"

#     def DHEA_75mg(self, obj):
#         query_set = UserTargetMonthProduct.objects.filter(
#             usermonth=obj, product__nom="DHEA 75mg"
#         )
#         return query_set.first().quantity if query_set.exists() else "0"

#     def HAIRVOL(self, obj):
#         query_set = UserTargetMonthProduct.objects.filter(
#             usermonth=obj, product__nom="HAIRVOL"
#         )
#         return query_set.first().quantity if query_set.exists() else "0"

#     def SUB12(self, obj):
#         query_set = UserTargetMonthProduct.objects.filter(
#             usermonth=obj, product__nom="SUB12"
#         )
#         return query_set.first().quantity if query_set.exists() else "0"

#     def MENOLIB(self, obj):
#         query_set = UserTargetMonthProduct.objects.filter(
#             usermonth=obj, product__nom="MENOLIB"
#         )
#         return query_set.first().quantity if query_set.exists() else "0"

#     def THYROLIB(self, obj):
#         query_set = UserTargetMonthProduct.objects.filter(
#             usermonth=obj, product__nom="THYROLIB"
#         )
#         return query_set.first().quantity if query_set.exists() else "0"

#     def HEPALIB(self, obj):
#         query_set = UserTargetMonthProduct.objects.filter(
#             usermonth=obj, product__nom="HEPALIB"
#         )
#         return query_set.first().quantity if query_set.exists() else 0

#     def SOPK_FREE(self, obj):
#         query_set = UserTargetMonthProduct.objects.filter(
#             usermonth=obj, product__nom="SOPK FREE"
#         )
#         return query_set.first().quantity if query_set.exists() else 0

#     def URISOFT(self, obj):
#         query_set = UserTargetMonthProduct.objects.filter(
#             usermonth=obj, product__nom="URISOFT"
#         )
#         return query_set.first().quantity if query_set.exists() else 0

#     def URICITRIL(self, obj):
#         query_set = UserTargetMonthProduct.objects.filter(
#             usermonth=obj, product__nom="URICITRIL"
#         )
#         return query_set.first().quantity if query_set.exists() else 0

#     def BESTFER(self, obj):
#         query_set = UserTargetMonthProduct.objects.filter(
#             usermonth=obj, product__nom="BESTFER"
#         )
#         return query_set.first().quantity if query_set.exists() else 0

#     def DIGEST_PLUS(self, obj):
#         query_set = UserTargetMonthProduct.objects.filter(
#             usermonth=obj, product__nom="DIGEST PLUS"
#         )
#         return query_set.first().quantity if query_set.exists() else 0

#     def ANAFLAM(self, obj):
#         query_set = UserTargetMonthProduct.objects.filter(
#             usermonth=obj, product__nom="ANAFLAM"
#         )
#         return query_set.first().quantity if query_set.exists() else 0


@admin.register(UserTargetMonth)
class UserTargetMonthAdmin(admin.ModelAdmin):
    inlines = (UserTargetMonthProductInLine,)
    list_filter = ["user", "user__userprofile__family"]
    list_display = [
        "user",
        # "get_family",
        "mois",
        *[p.nom.replace(" ", "_") for p in Produit.objects.all()],
        "print_button",
    ]
    date_hierarchy = "date"
    actions = [duplicate_for_next_month]

    def get_family(self, obj):
        return obj.user.userprofile.family

    get_family.short_description = "Family"

    def mois(self, obj):
        if obj.date:
            return f"{month_number_to_french_name(obj.date.month)} {obj.date.year}"
        return "-"

    def print_button(self, obj):
        # Créer une URL pour imprimer les cibles du mois
        url = reverse(
            "usertargetmonth_print", args=[obj.id]
        )  # Utilisez le nom d'URL que vous avez défini
        return format_html(
            '<a class="button" href="{}" target="_blank">Imprimer</a>', url
        )

    print_button.short_description = "Impression"

    # Méthodes pour afficher les quantités des produits
    def FF(self, obj):
        return self.get_quantity(obj, "FF")
    
    def SLEEP_ALAISE(self, obj):
        return self.get_quantity(obj, "SLEEP_ALAISE")
    
    def GOLD_MAG(self, obj):
        return self.get_quantity(obj, "GOLD_MAG")

    def FM(self, obj):
        return self.get_quantity(obj, "FM")

    def IRON(self, obj):
        return self.get_quantity(obj, "IRON")

    def YES_CAL(self, obj):
        return self.get_quantity(obj, "YES CAL")

    def YES_VIT(self, obj):
        return self.get_quantity(obj, "YES VIT")

    def ADVAGEN(self, obj):
        return self.get_quantity(obj, "ADVAGEN")

    def DHEA_75mg(self, obj):
        return self.get_quantity(obj, "DHEA 75mg")

    def HAIRVOL(self, obj):
        return self.get_quantity(obj, "HAIRVOL")

    def SUB12(self, obj):
        return self.get_quantity(obj, "SUB12")

    def MENOLIB(self, obj):
        return self.get_quantity(obj, "MENOLIB")

    def THYROLIB(self, obj):
        return self.get_quantity(obj, "THYROLIB")

    def HEPALIB(self, obj):
        return self.get_quantity(obj, "HEPALIB")

    def SOPK_FREE(self, obj):
        return self.get_quantity(obj, "SOPK FREE")

    def URISOFT(self, obj):
        return self.get_quantity(obj, "URISOFT")

    def URICITRIL(self, obj):
        return self.get_quantity(obj, "URICITRIL")

    def BESTFER(self, obj):
        return self.get_quantity(obj, "BESTFER")

    def DIGEST_PLUS(self, obj):
        return self.get_quantity(obj, "DIGEST PLUS")

    def ANAFLAM(self, obj):
        return self.get_quantity(obj, "ANAFLAM")
    
    def New_B(self, obj):
        return self.get_quantity(obj, "New B")
    def Prosta_Soft(self, obj):
        return self.get_quantity(obj, "Prosta Soft")
    
    def Mamilis(self, obj):
        return self.get_quantity(obj, "Mamilis")
    
    def Veno_Soft(self, obj):
        return self.get_quantity(obj, "Veno Soft")

    def get_quantity(self, obj, product_name):
        query_set = UserTargetMonthProduct.objects.filter(
            usermonth=obj, product__nom=product_name
        )
        return query_set.first().quantity if query_set.exists() else "0"


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "excel_file",
        "date",
    ]

