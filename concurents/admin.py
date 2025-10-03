from django.contrib import admin
from .models import *


class CompositionInline(admin.StackedInline):
    model = Composition
    title="compositions"


@admin.register(CProduct)
class CProductAdmin(admin.ModelAdmin):
    list_display = ('product','company',"name","marketing","user")
    list_filter = ('valid','shape',"product")
    search_fields = ('company','name', "composition")
    inlines=[ CompositionInline, ]
    # def _products(self,obj):
    #     return " ".join([f'{p.product}-{p.qtt}' for p in obj.dealproduct_set.all()])
    # def _print(self,obj):
    #   return mark_safe(f"<a href='/deals/print/{obj.id}/' target='_blank'>imprimer</a>") 


admin.site.register(Shape)
