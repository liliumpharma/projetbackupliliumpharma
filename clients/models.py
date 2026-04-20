from django.db import models
from django.contrib.auth.models import User
from produits.models import Produit
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from notifications.models import Notification
import json
from datetime import datetime

import pandas as pd


class Client(models.Model):
    # Foreign Keys
    name = models.CharField(max_length=100)
    wilaya = models.ForeignKey(to="regions.Wilaya", on_delete=models.CASCADE)

    supergro = models.BooleanField(default=False)

    related_client = models.ForeignKey(
        to="clients.Client",
        verbose_name="Client Supérieur",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    def __str__(self):
        return "{} {}".format(self.name, f"- Super Grossiste" if self.supergro else "")


class Source(models.Model):
    excel_file = models.FileField(null=True, blank=True, verbose_name="Excel File")
    date = models.DateField()
    date_added = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = "Source de Vente"
        verbose_name_plural = "Source des Ventes"

    def __str__(self):
        return f"{self.date} - {self.excel_file}"


class OrderSource(models.Model):
    source = models.ForeignKey(to=Client, on_delete=models.CASCADE)
    source_file = models.ForeignKey(to=Source, null=True, on_delete=models.CASCADE)
    date = models.DateField()
    excel_file = models.FileField(null=True, blank=True, verbose_name="Excel File")
    attachement_file = models.FileField(
        null=True, blank=True, verbose_name="Attachement"
    )

    class Meta:
        verbose_name = "Mois SuperGro"
        verbose_name_plural = "Mois SuperGro"

    def __str__(self):
        return f"{self.source.name} - {self.date.month}/{self.date.year}"


class OrderSourceProduct(models.Model):
    # Foreign Keys
    source = models.ForeignKey(to=OrderSource, on_delete=models.CASCADE)
    produit = models.ForeignKey("produits.Produit", on_delete=models.CASCADE)
    qtt = models.IntegerField()

    def __str__(self):
        return f"{self.produit.nom}--{self.qtt}"


class MonthComment(models.Model):
    # Foreign Keys
    from_user = models.ForeignKey(
        to=User, related_name="from_user", on_delete=models.CASCADE
    )
    to_user = models.ForeignKey(
        to=User, related_name="to_user", null=True, on_delete=models.CASCADE
    )

    date = models.DateField()
    comment = models.TextField()

    date_added = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return f"{self.from_user} commented to {self.to_user} on {self.date} : {self.comment}"


class Order(models.Model):
    # Foreign Keys
    source = models.ForeignKey(to=OrderSource, on_delete=models.CASCADE)

    client = models.ForeignKey(to=Client, on_delete=models.CASCADE, null=True, blank=True)
    products = models.ManyToManyField(
        to="produits.Produit", through="clients.OrderProduct"
    )

    date = models.DateField(default=datetime.now, blank=True)

    @property
    def products_count(self):
        return self.products.all().count()

    @property
    def products_str(self):
        string = ""
        for p in OrderProduct.objects.filter(order=self):
            string += f"{p.produit.nom} ({p.qtt}) "

        return string

    def __str__(self):
        return f"{self.client} bought {self.products_count} Product(s) - {self.products_str} | Source {self.source}"


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    produit = models.ForeignKey("produits.Produit", on_delete=models.CASCADE)
    qtt = models.IntegerField()

    def __str__(self):
        return f"{self.produit.nom}--{self.qtt}"


# class UserTargetMonth(models.Model):
#     user=models.ForeignKey(to=User, on_delete=models.CASCADE)
#     date=models.DateField(null=True, blank=True)

#     class Meta:
#         unique_together=['user', 'date']
#         ordering = ['-date']

#     def __str__(self):
#         return f"{self.user.username} - as of {self.date}"


class UserTargetMonth(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    date = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ["user", "date"]
        ordering = ["-date"]

    def __str__(self):
        return f"{self.user.username} - as of {self.date}"


class UserTargetMonthProduct(models.Model):
    usermonth = models.ForeignKey(to=UserTargetMonth, on_delete=models.CASCADE)
    product = models.ForeignKey(to=Produit, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(verbose_name="Target Quantity")

    def __str__(self):
        return f"{self.usermonth} | {self.product} - {self.quantity}"


# Signals
@receiver(post_save, sender=Source)
def process_excel(sender, instance, **kwargs):
    if instance.excel_file:
        # Deleting Orders
        instance.ordersource_set.all().delete()

        # Preparing Excel File
        xlsx = pd.ExcelFile(instance.excel_file.path)

        # Processing First Sheet
        sheet1 = pd.read_excel(xlsx, "Ventes")
        for row in sheet1.iterrows():
            data = row[1]

            # Checking Client Existance
            client = Client.objects.filter(name__iexact=data[0], supergro=True)
            if not client.exists():
                raise ValidationError(f"Le Super Grossite {data[0]} n'existe pas")
            client = client.first()

            order_source = OrderSource.objects.filter(
                source_file=instance, source=client, date=instance.date
            )

            if order_source.exists():
                order_source = order_source.first()
            else:
                order_source = OrderSource.objects.create(
                    source_file=instance, source=client, date=instance.date
                )

            # Checking Client Existance
            client = Client.objects.filter(name__iexact=data[1])
            if not client.exists():
                raise ValidationError(f"Le Client {data[1]} n'existe pas")
            client = client.first()

            # Check if an Order exists
            order = Order.objects.filter(
                source=order_source, client=client, date=order_source.date
            )
            if order.exists():
                order = order.first()
            else:
                order = Order.objects.create(
                    source=order_source, client=client, date=order_source.date
                )

            # Checking Product Existance
            product = Produit.objects.filter(nom__iexact=data[2])
            if not product.exists():
                raise ValidationError(f"Le Produit {data[2]} n'existe pas")
            product = product.first()

            # Adding Products
            OrderProduct.objects.create(order=order, produit=product, qtt=data[3])

        # Processing Second Sheet
        sheet2 = pd.read_excel(xlsx, "Stock")
        for row in sheet2.iterrows():
            data = row[1]

            # Checking Client Existance
            client = Client.objects.filter(name=data[0], supergro=True)
            if not client.exists():
                raise ValidationError(f"Le Super Grossite {data[0]} n'existe pas")
            client = client.first()

            order_source = OrderSource.objects.filter(
                source_file=instance, source=client, date=instance.date
            )

            if order_source.exists():
                order_source = order_source.first()
            else:
                order_source = OrderSource.objects.create(
                    source_file=instance, source=client, date=instance.date
                )

            # Checking Product Existance
            product = Produit.objects.filter(nom=data[1])
            if not product.exists():
                raise ValidationError(f"Le Produit {data[1]} n'existe pas")
            product = product.first()

            # Adding Products
            OrderSourceProduct.objects.create(
                source=order_source, produit=product, qtt=data[2]
            )


@receiver(post_save, sender=MonthComment)
def notify_on_create(sender, instance, **kwargs):
    notification = Notification.objects.create(
        title=f"{instance.from_user.username} a commenté un Mois de Vente",
        description=f"Ventes du {str(instance.date)}",
        data={
            "name": "Mois de Vente",
            "title": "Mois de Vente",
            "message": f"{instance.from_user.username} vient juste de commenter les ventes du {str(instance.date)}",
            "confirm_text": "Ouvrir les Ventes",
            "cancel_text": "Plus Tard",
            "StackName": "Sales",
            "navigate_to": json.dumps(
                {
                    "screen": "Sales",
                    # "params":{
                    #     "rapport":instance.rapport.id,
                    #     "should_fetch":True
                    #     }
                }
            ),
        },
    )
    notification.users.set(
        [usr for usr in instance.from_user.userprofile.get_users_to_notify()]
    )
    # notification.send()


from django.db.models import Sum
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
import logging
_bi_log = logging.getLogger("clients.bi_signals")

def _log_wilaya_product(year, month, wilaya_obj, product_obj):
    """Write one BIPendingUpdate row for a (wilaya, product, year, month) combo."""
    try:
        BIPendingUpdate.objects.get_or_create(
            year=year, month=month,
            wilaya=wilaya_obj, product=product_obj,
            user_profile=None,
        )
    except Exception as exc:
        _bi_log.error("_log_wilaya_product failed: %s", exc, exc_info=True)


def _log_user_profile(year, month, profile):
    """Write one BIPendingUpdate row to trigger a dashboard rebuild for this user."""
    try:
        BIPendingUpdate.objects.get_or_create(
            year=year, month=month,
            wilaya=None, product=None,
            user_profile=profile,
        )
    except Exception as exc:
        _bi_log.error("_log_user_profile failed: %s", exc, exc_info=True)


def _log_user_all_months(profile):
    """Log a dashboard rebuild for every known (year, month) this user appears in."""
    try:
        dates = OrderSource.objects.values('date__year', 'date__month').distinct()
        for d in dates:
            _log_user_profile(d['date__year'], d['date__month'], profile)
    except Exception as exc:
        _bi_log.error("_log_user_all_months failed: %s", exc, exc_info=True)

# ---------------------------------------------------------------------------
# Signal: OrderProduct  (SuperGros sales rows)
# ---------------------------------------------------------------------------

@receiver(post_save, sender=OrderProduct)
@receiver(post_delete, sender=OrderProduct)
def _bi_log_order_product(sender, instance, **kwargs):
    try:
        sale_date = instance.order.source.date
        _log_wilaya_product(
            sale_date.year, sale_date.month,
            instance.order.client.wilaya,
            instance.produit,
        )
    except Exception as exc:
        _bi_log.error("_bi_log_order_product failed: %s", exc, exc_info=True)


# ---------------------------------------------------------------------------
# Signal: OrderItem  (direct pharmacy / gros orders used in DashboardSnapshot)
# ---------------------------------------------------------------------------

def _connect_order_item_signals():
    try:
        from orders.models import OrderItem as _OrderItem

        @receiver(post_save, sender=_OrderItem, weak=False)
        @receiver(post_delete, sender=_OrderItem, weak=False)
        def _bi_log_order_item(sender, instance, **kwargs):
            try:
                order = instance.order
                profile = order.user.userprofile
                _log_user_profile(order.added.year, order.added.month, profile)
            except Exception:
                pass
    except Exception as exc:
        _bi_log.error("_bi_log_order_product failed: %s", exc, exc_info=True)


_connect_order_item_signals()


# ---------------------------------------------------------------------------
# Signal: UserSectorDetail  (sector assignments changed → full user rebuild)
# ---------------------------------------------------------------------------

def _connect_sector_detail_signals():
    try:
        from accounts.models import UserSectorDetail as _USD

        @receiver(post_save, sender=_USD, weak=False)
        @receiver(post_delete, sender=_USD, weak=False)
        def _bi_log_sector_detail(sender, instance, **kwargs):
            _log_user_all_months(instance.user_profile)
    except Exception as exc:
        _bi_log.error("_bi_log_order_product failed: %s", exc, exc_info=True)


_connect_sector_detail_signals()


# ---------------------------------------------------------------------------
# Signal: UserProfile  (role / lines / region changed → full user rebuild)
# ---------------------------------------------------------------------------

def _connect_user_profile_signals():
    try:
        from accounts.models import UserProfile as _UP

        @receiver(post_save, sender=_UP, weak=False)
        def _bi_log_user_profile(sender, instance, **kwargs):
            _log_user_all_months(instance)
    except Exception as exc:
        _bi_log.error("_bi_log_order_product failed: %s", exc, exc_info=True)


_connect_user_profile_signals()


# ---------------------------------------------------------------------------
# Existing supervisor auto-fill signal (kept unchanged)
# ---------------------------------------------------------------------------

# We listen for both saves (updates/creates) and deletes
@receiver(post_save, sender=UserTargetMonthProduct)
@receiver(post_delete, sender=UserTargetMonthProduct)
def auto_fill_supervisor_targets(sender, instance, **kwargs):
    # Import UserProfile here to avoid circular import issues
    from accounts.models import UserProfile

    # 1. Identify the user whose target was just saved/deleted
    try:
        profile = instance.usermonth.user.userprofile
    except UserProfile.DoesNotExist:
        return

    role = profile.speciality_rolee

    # 2. INFINITE LOOP PROTECTION: Only run if a Délégué's target is changed.
    if role not in ["Commercial", "Medico_commercial"]:
        return

    target_date = instance.usermonth.date
    product = instance.product
    region = getattr(profile, "region", None)

    # =================================================================
    # PART A: UPDATE LOCAL SUPERVISORS (Based on Region)
    # =================================================================
    if region:
        # Sum of all 'Commercial' users in this specific region
        commercial_sum = (
            UserTargetMonthProduct.objects.filter(
                usermonth__date__year=target_date.year,
                usermonth__date__month=target_date.month,
                product=product,
                usermonth__user__userprofile__region=region,
                usermonth__user__userprofile__speciality_rolee="Commercial",
            ).aggregate(total=Sum("quantity"))["total"]
            or 0
        )

        # Sum of all 'Medico_commercial' users in this specific region
        medico_sum = (
            UserTargetMonthProduct.objects.filter(
                usermonth__date__year=target_date.year,
                usermonth__date__month=target_date.month,
                product=product,
                usermonth__user__userprofile__region=region,
                usermonth__user__userprofile__speciality_rolee="Medico_commercial",
            ).aggregate(total=Sum("quantity"))["total"]
            or 0
        )

        # Find all Supervisors in the SAME region
        supervisors_in_region = UserProfile.objects.filter(
            region=region,
            speciality_rolee__in=[
                "Superviseur_national",
                "Superviseur_regional",
                "Superviseur",
            ],
        )

        for sup in supervisors_in_region:
            sup_role = sup.speciality_rolee
            work_as_com = getattr(sup, "work_as_commercial", False)

            target_to_assign = None

            # Rule: Any supervisor working as commercial gets the Commercial Sum
            if work_as_com:
                target_to_assign = commercial_sum

            # Rule: Superviseur_national (and regional) NOT working as commercial get Medico Sum
            elif not work_as_com and sup_role in [
                "Superviseur_national",
                "Superviseur_regional",
            ]:
                target_to_assign = medico_sum

            # Overwrite / Create the Supervisor's Target
            if target_to_assign is not None:
                sup_usermonth, _ = UserTargetMonth.objects.get_or_create(
                    user=sup.user, date=target_date
                )
                sup_target_product, tp_created = (
                    UserTargetMonthProduct.objects.get_or_create(
                        usermonth=sup_usermonth,
                        product=product,
                        defaults={"quantity": target_to_assign},
                    )
                )
                if not tp_created:
                    sup_target_product.quantity = target_to_assign
                    sup_target_product.save()

    # =================================================================
    # PART B: UPDATE COUNTRY MANAGER (Medical All + Commercial Special)
    # =================================================================

    # 1. The CountryManager ALWAYS gets the sum of Medico_commercials
    medico_global_sum = (
        UserTargetMonthProduct.objects.filter(
            usermonth__date__year=target_date.year,
            usermonth__date__month=target_date.month,
            product=product,
            usermonth__user__userprofile__speciality_rolee="Medico_commercial",
        ).aggregate(total=Sum("quantity"))["total"]
        or 0
    )

    # 2. They ONLY get the Commercial sum if the product is one of the Special 4
    special_products = ["ADVAGEN", "HAIRVOL", "GOLD MAG", "SLEEP ALAISE"]
    commercial_global_sum = 0

    if product.nom.upper() in special_products:
        commercial_global_sum = (
            UserTargetMonthProduct.objects.filter(
                usermonth__date__year=target_date.year,
                usermonth__date__month=target_date.month,
                product=product,
                usermonth__user__userprofile__speciality_rolee="Commercial",
            ).aggregate(total=Sum("quantity"))["total"]
            or 0
        )

    # 3. Combine them for the final CountryManager target
    global_delegues_sum = medico_global_sum + commercial_global_sum

    # Find the CountryManager(s) and overwrite their target
    country_managers = UserProfile.objects.filter(speciality_rolee="CountryManager")

    for cm in country_managers:
        cm_usermonth, _ = UserTargetMonth.objects.get_or_create(
            user=cm.user, date=target_date
        )
        cm_target_product, cm_created = UserTargetMonthProduct.objects.get_or_create(
            usermonth=cm_usermonth,
            product=product,
            defaults={"quantity": global_delegues_sum},
        )
        if not cm_created:
            cm_target_product.quantity = global_delegues_sum
            cm_target_product.save()


# ---------------------------------------------------------------------------
# Signal: UserTargetMonthProduct  (target changed → log per-wilaya + dashboard)
# Runs AFTER auto_fill_supervisor_targets to avoid reacting to its cascade saves.
# ---------------------------------------------------------------------------

@receiver(post_save, sender=UserTargetMonthProduct)
@receiver(post_delete, sender=UserTargetMonthProduct)
def _bi_log_target_change(sender, instance, **kwargs):
    from accounts.models import UserProfile as _UP
    try:
        profile = instance.usermonth.user.userprofile
        target_date = instance.usermonth.date

        # Only react to real delegates — supervisors are auto-filled above and
        # would create an infinite cascade if we logged them too.
        if profile.speciality_rolee not in ["Commercial", "Medico_commercial"]:
            return

        # One row per (wilaya, product) so sync_bi_allocation can be granular.
        for wilaya in profile.sectors.all():
            _log_wilaya_product(target_date.year, target_date.month, wilaya, instance.product)

        # Also queue a dashboard rebuild for this user.
        _log_user_profile(target_date.year, target_date.month, profile)
    except Exception:
        pass


class BISnapshot(models.Model):
    """
    Flat Data Warehouse table for the Business Intelligence Dashboard.
    Populated manually via the Admin panel to prevent server overload.
    """
    year = models.IntegerField()
    month = models.IntegerField()
    
    user_id = models.IntegerField()
    user_name = models.CharField(max_length=255)
    role = models.CharField(max_length=100)
    lines = models.CharField(max_length=100, null=True, blank=True)
    sector_category = models.CharField(max_length=50, null=True, blank=True)
    region = models.CharField(max_length=100, null=True, blank=True)

    wilaya = models.CharField(max_length=100)
    supergros_name = models.CharField(max_length=255, null=True, blank=True)
    
    product_id = models.IntegerField()
    product_name = models.CharField(max_length=255)
    
    qty = models.FloatField(default=0.0)
    value = models.FloatField(default=0.0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "BI Snapshot"
        verbose_name_plural = "BI Snapshots"
        # Indexing these fields makes frontend filtering lightning fast
        indexes = [
            models.Index(fields=['year', 'month']),
            models.Index(fields=['user_id']),
            models.Index(fields=['product_id']),
        ]

    def __str__(self):
        return f"{self.month}/{self.year} - {self.user_name} - {self.product_name}"
    
class SupergrosSalesSnapshot(models.Model):
    """Pure, unallocated sales data straight from the SuperGros reports."""
    year = models.IntegerField()
    month = models.IntegerField()

    wilaya = models.CharField(max_length=100)
    supergros_name = models.CharField(max_length=255)

    product_id = models.IntegerField()
    product_name = models.CharField(max_length=255)
    lines = models.CharField(max_length=100, null=True, blank=True)

    qty = models.FloatField(default=0.0)
    value = models.FloatField(default=0.0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['year', 'month']),
        ]


class DashboardSnapshot(models.Model):
    """Flat table specifically for taruser_desktop.html zero-second load times."""
    year = models.IntegerField()
    month = models.IntegerField()

    user_id = models.IntegerField()
    user_name = models.CharField(max_length=255)
    role = models.CharField(max_length=100)
    lines = models.CharField(max_length=100, null=True, blank=True)
    sector_category = models.CharField(max_length=50, null=True, blank=True)
    region = models.CharField(max_length=100, null=True, blank=True)
    work_as_commercial = models.BooleanField(default=False)

    product_id = models.IntegerField(default=0)
    product_name = models.CharField(max_length=255, default="Aucun")

    target_value = models.FloatField(default=0.0)
    achieved_value = models.FloatField(default=0.0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['year', 'month']),
            models.Index(fields=['user_id']),
        ]


class BIPendingUpdate(models.Model):
    """
    Dirty-log / to-do list for the incremental BI refresh.
    Signals write here; the AJAX chunk processor reads and deletes here.

    Two kinds of rows:
      • wilaya + product  (user_profile=None)  → sync sales + BI allocation
      • user_profile only (wilaya=None, product=None) → sync dashboard snapshot

    unique_together prevents duplicate work when the same Excel file
    re-saves the same combo hundreds of times.  Note: PostgreSQL does NOT
    enforce uniqueness across NULL columns, so application-level get_or_create
    is the primary deduplication guard for nullable combinations.
    """
    year         = models.IntegerField()
    month        = models.IntegerField()
    wilaya       = models.ForeignKey('regions.Wilaya',        null=True, blank=True, on_delete=models.CASCADE)
    product      = models.ForeignKey('produits.Produit',      null=True, blank=True, on_delete=models.CASCADE)
    user_profile = models.ForeignKey('accounts.UserProfile',  null=True, blank=True, on_delete=models.CASCADE)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['year', 'month', 'wilaya', 'product', 'user_profile']
        verbose_name        = "BI Pending Update"
        verbose_name_plural = "BI Pending Updates"

    def __str__(self):
        if self.user_profile:
            return f"[user] {self.user_profile} – {self.month}/{self.year}"
        return f"[wilaya/product] {self.wilaya} / {self.product} – {self.month}/{self.year}"
    
class UserReportSnapshot(models.Model):
    """
    Table plate pour charger la page /clients/target_user/ en 50ms.
    Mise à jour uniquement via le bouton 'Actualiser données BI' de l'Admin.
    """
    year = models.IntegerField()
    month = models.IntegerField()
    
    user_id = models.IntegerField()
    user_name = models.CharField(max_length=255)
    role = models.CharField(max_length=100)
    region = models.CharField(max_length=100, null=True, blank=True)
    
    product_id = models.IntegerField()
    product_name = models.CharField(max_length=255)
    product_price = models.FloatField(default=0.0)

    target_qty = models.FloatField(default=0.0)
    mobile_ph_gros_qty = models.FloatField(default=0.0)
    mobile_gros_super_qty = models.FloatField(default=0.0)
    supergros_achieved_qty = models.FloatField(default=0.0)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User Report Snapshot"
        verbose_name_plural = "User Report Snapshots"
        indexes = [
            models.Index(fields=['year', 'month']),
            models.Index(fields=['user_id']),
            models.Index(fields=['product_id']),
        ]

    def __str__(self):
        return f"{self.month}/{self.year} - {self.user_name} - {self.product_name}"