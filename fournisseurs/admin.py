from django.contrib import admin
from django.urls import reverse
from django.utils.html import mark_safe
from .models import *

# @admin.register(Fournisseur)
# admin.site.register(Fournisseur)


class InformationsInline(admin.StackedInline):
    model = Information
    max_num = 1


class FournisseurAdmin(admin.ModelAdmin):
    list_display = ("id", "societe", "activite", "famille", "pays", "code_postal")
    list_filter = ("societe", "famille", "pays", "code_postal")
    inlines = [InformationsInline]


admin.site.register(Fournisseur, FournisseurAdmin)


class ItemAdmin(admin.ModelAdmin):
    list_display = ("id", "description", "get_fournisseur_societe", "type")

    def get_fournisseur_societe(self, obj):
        return obj.fournisseur.societe

    get_fournisseur_societe.short_description = "Fournisseur Société"


admin.site.register(Item, ItemAdmin)


class AchatAdmin(admin.ModelAdmin):
    list_display = ("id", "get_item_description", "Quantity", "unit")

    def get_item_description(self, obj):
        return obj.item.description

    get_item_description.short_description = "Item Description"


admin.site.register(Achat, AchatAdmin)


class SortieAdmin(admin.ModelAdmin):
    list_display = ("id", "get_item_description", "Quantity", "unit", "destination")

    def get_item_description(self, obj):
        return obj.item.description

    get_item_description.short_description = "Item Description"


admin.site.register(Sortie, SortieAdmin)
