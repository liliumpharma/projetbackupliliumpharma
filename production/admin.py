from django.contrib import admin
from .models import *

class EntreeAdmin(admin.ModelAdmin):
    list_display = ('number', 'user', 'fournisseur', 'produit', 'quantity', 'unite', 'price', 'devise', 'added')
    list_filter = ('user', 'fournisseur', 'e_type', 'subtype', 'devise', 'added')
    search_fields = ('number', 'user__username', 'fournisseur__nom', 'produit__nom')
    ordering = ('-added',)
    date_hierarchy = 'added'
    list_per_page = 20

    # Vous pouvez aussi définir des champs en ligne (inlines) si vous avez des modèles associés
    # inlines = [EntreeInline]  # Si vous avez des objets associés à Entree

    # Champs à afficher lors de l'ajout ou de la modification

    # Widgets pour certains champs (par exemple, un calendrier pour 'added')
    # formfield_overrides = {
    #     models.DateTimeField: {'widget': AdminDateWidget},
    # }

admin.site.register(Entree, EntreeAdmin)

class SortieAdmin(admin.ModelAdmin):
    list_display = ('entree', 'user')
    ordering = ('-added',)
    date_hierarchy = 'added'
    list_per_page = 20

    # Vous pouvez aussi définir des champs en ligne (inlines) si vous avez des modèles associés
    # inlines = [EntreeInline]  # Si vous avez des objets associés à Entree

    # Champs à afficher lors de l'ajout ou de la modification

    # Widgets pour certains champs (par exemple, un calendrier pour 'added')
    # formfield_overrides = {
    #     models.DateTimeField: {'widget': AdminDateWidget},
    # }

admin.site.register(Sortie, SortieAdmin)

class RetourAdmin(admin.ModelAdmin):
    list_display = ('entree', 'user')
    ordering = ('-added',)
    date_hierarchy = 'added'
    list_per_page = 20

    # Vous pouvez aussi définir des champs en ligne (inlines) si vous avez des modèles associés
    # inlines = [EntreeInline]  # Si vous avez des objets associés à Entree

    # Champs à afficher lors de l'ajout ou de la modification

    # Widgets pour certains champs (par exemple, un calendrier pour 'added')
    # formfield_overrides = {
    #     models.DateTimeField: {'widget': AdminDateWidget},
    # }

admin.site.register(Retour, RetourAdmin)



@admin.register(OrderProduction)
class OrderProductionAdmin(admin.ModelAdmin):
    list_display = ('id','batch_number', 'user', 'produit', 'process_type', 'added')
    list_filter = ('process_type', 'user', 'produit')
    search_fields = ('batch_number', 'user__username', 'produit__nom')

@admin.register(ItemOrderProduction)
class ItemOrderProductionAdmin(admin.ModelAdmin):
    list_display = ('id','order_production', 'item', 'qtt')  # Affiche les champs dans la liste admin
    list_filter = ('order_production',)  # Permet de filtrer les objets par ordre de production
    search_fields = ('item',)  # Permet de rechercher par nom d'article


@admin.register(ItemOrderProductionBash)
class ItemOrderProductionBashAdmin(admin.ModelAdmin):
    list_display = ('ref','item_order_production', 'qtt', 'location', 'added')  # Champs à afficher dans la liste
    search_fields = ('item_order_production__item',)  # Permet la recherche par nom d'article
    list_filter = ('location',)  # Permet de filtrer les éléments par 'location'
    ordering = ('-added',)  # Trie les éléments par la date de création décroissante
