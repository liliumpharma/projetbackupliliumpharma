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

