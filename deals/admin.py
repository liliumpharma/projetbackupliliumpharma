from django.contrib import admin
from .models import *
from django.utils.html import mark_safe
    
class CommentInline(admin.StackedInline):
  model = DealComment
  verbose_name_plural = ' ملاحظات الادارة '



class DealItemInline(admin.StackedInline):
  model = DealProduct
  verbose_name_plural = 'produits'


class Delegue_RepresentantInline(admin.StackedInline):
    model = Delegue_Representant
    verbose_name_plural = 'Délégué representant'
    extra = 1  # Nombre de lignes vides à afficher pour ajouter des instances
    fields = ('user', 'date_debut_recuperation', 'date_reprise_recuperation', 'comment')
    # Permet d'ajouter des enregistrements vides pour les nouveaux RH





@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    list_display = ('id','added','_medecin',"description","user","cost","dtype","status","_products","_print")
    list_filter = ('added','user',"status","dtype","medecin__specialite")
    date_hierarchy = 'starting_date'
    search_fields=["medecin__nom","medecin__id"]
    inlines = [CommentInline, DealItemInline, Delegue_RepresentantInline]

    def _products(self,obj):
        return " ".join([f'{p.product}-{p.qtt}' for p in obj.dealproduct_set.all()])
    def _print(self,obj):
      return mark_safe(f"<a href='/deals/print/{obj.id}/' target='_blank'>imprimer</a>")    
    def _medecin(self,obj):
        medecin_info = ""
        for medecin in obj.medecin.all():
            medecin_info += f"-{medecin.nom} <br>"
        return mark_safe(medecin_info)

admin.site.register(DealType)
admin.site.register(DealStatus)

            





