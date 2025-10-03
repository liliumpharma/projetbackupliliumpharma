# from django.contrib import admin
# #from .models import *
# from .models import Produit, ProductActiveIngerients, ProductInactiveIngredients, ProductProductionInfos, ProduitVisite, ProductionStepChoices, ProductCompany, ProductInformations, ProductNote, ProductFile, ProductProductionPremixStep, ProductProductionFullProcessStep
# from django.utils.html import format_html

# # admin.site.register(Produit)
# # admin.site.register(ProductActiveIngerients)
# # admin.site.register(ProductInactiveIngredients)
# # admin.site.register(ProductProductionInfos)
# # admin.site.register(ProduitVisite)






# class CompositionInline(admin.StackedInline):
#     model = ProductActiveIngerients
#     title="ProductActiveIngerients"

# class CompositioninactiveInline(admin.StackedInline):
#     model = ProductInactiveIngredients
#     title="ProductInactiveIngredients"

# class CompositioninfosInline(admin.StackedInline):
#     model = ProductProductionInfos
#     title="ProductProductionInfos"

# class CompositioncompanyInline(admin.StackedInline):
#     model = ProductCompany
#     title="ProductCompany"

# class CompositioninfInline(admin.StackedInline):
#     model = ProductInformations
#     title="ProductInformations"

# class CompositionnoteInline(admin.StackedInline):
#     model = ProductNote
#     title="ProductNote"

# class CompositionfileInline(admin.StackedInline):
#     model = ProductFile
#     title="ProductFile"

# class CompositionstepInline(admin.StackedInline):
#     model = ProductProductionPremixStep
#     title="ProductProductionPremixStep"

# class CompositionprocessstepInline(admin.StackedInline):
#     model = ProductProductionFullProcessStep
#     title="ProductProductionFullProcessStep"
    
# @admin.register(Produit)  
# class ProductAdmin(admin.ModelAdmin):
#     list_display = ('nom','get_pays',"price","fname", "get_file_type", "get_company")
#     list_filter = ('nom','pays', "productcompany__family")
#     search_fields = ('nom','pays', "fname", "productcompany__family")
#     inlines=[ CompositionInline, CompositioninactiveInline, CompositioninfosInline, CompositioncompanyInline, CompositioninfInline, CompositionnoteInline, CompositionfileInline, CompositionstepInline, CompositionprocessstepInline]

#     def get_file_type(self, obj):
#         product_file = ProductFile.objects.filter(produit=obj).first()
#         if product_file and product_file.fil:  # Vérifie si un fichier existe
#             return format_html('<a href="{}" target="_blank">{}</a>', product_file.fil.url, "Télécharger")
#         return "Aucun fichier"
    
#     get_file_type.short_description = "Certification"
    
#     def get_company(self, obj):
#         product_company = ProductCompany.objects.filter(product=obj).first()
#         if product_company:  # Vérifie si un fichier existe
#             return product_company.family
#         return "Aucune Company"
    
#     get_company.short_description = "Company"
    
#     def get_pays(self, obj):
#         return ", ".join([p.nom for p in obj.pays.all()])
#     get_pays.short_description = "Pays"
    
from django.contrib import admin
from .models import *
from django.utils.html import mark_safe
from django.urls import reverse


class ProductFileInline(admin.StackedInline):
  model = ProductFile
  verbose_name_plural = 'fichiers'

class ProductProductionInfosInline(admin.StackedInline):
  model = ProductProductionInfos
  max_num = 1
  verbose_name_plural = 'Production Infos'

class ProductNoteInline(admin.StackedInline):
  model = ProductNote
  max_num = 1
  verbose_name_plural = 'Note'

class ProductInformationsInline(admin.StackedInline):
  model = ProductInformations
  max_num = 1
  verbose_name_plural = 'Informations'

class ProductActiveIngredientsInline(admin.StackedInline):
    model = ProductActiveIngerients
    verbose_name_plural = 'Active ingredient'

class ProductInactiveIngredientsInline(admin.StackedInline):
    model = ProductInactiveIngredients
    verbose_name_plural = 'Inactive ingredient'

class ProductCompanyInline(admin.StackedInline):
    model = ProductCompany
    max_num = 1
    verbose_name_plural = 'Company'

class ProductProductionPremixStepInline(admin.StackedInline):
    model = ProductProductionPremixStep
    extra = 1  # Nombre d'entrées supplémentaires vierges pour faciliter l'ajout
    verbose_name_plural = 'Manifacture process as premix'
    ordering = ['step_number']

class ProductProductionFullProcessStepInline(admin.StackedInline):
    model = ProductProductionFullProcessStep
    extra = 1  # Nombre d'entrées supplémentaires vierges pour faciliter l'ajout
    verbose_name_plural = 'Manifacture process as full process'
    ordering = ['step_number']

class ProduitAdmin(admin.ModelAdmin):
    list_display = ('id','get_company_family', 'nom',"_print", "_print_datasheet","_print_productdata")
    search_fields = ["nom"]
    list_filter = ['productcompany__family']
    inlines = [ProductCompanyInline, ProductInformationsInline, ProductActiveIngredientsInline, ProductInactiveIngredientsInline, ProductNoteInline, ProductFileInline, ProductProductionInfosInline, ProductProductionPremixStepInline, ProductProductionFullProcessStepInline]

    def get_company_family(self, obj):
        # obj is an instance of Produit
        product_company = obj.productcompany_set.first()  # Assuming a reverse relation from Produit to ProductCompany
        if product_company:
            return product_company.family
        return None

    get_company_family.short_description = 'Company Family'

    def _print(self, obj):
      url = reverse('QualiquantityPDF', args=[obj.id])
      return mark_safe(f"<a id=\"id-du-bouton-imprimer\" href='{url}' target='_blank'>Composition</a>")

    _print.short_description = 'Composition certificate'

    def _print_datasheet(self, obj):
      url = reverse('datasheet', args=[obj.id])
      return mark_safe(f"<a id=\"id-du-bouton-imprimer\" href='{url}' target='_blank'>DataSheet</a>")

    _print_datasheet.short_description = 'Technical DataSheet'

    def _print_productdata(self, obj):
      url = reverse('ProductData', args=[obj.id])
      return mark_safe(f"<a id=\"id-du-bouton-imprimer\" href='{url}' target='_blank'>Product Data</a>")

    _print_productdata.short_description = 'Product data'

    def print_pdf(self, request, queryset):
        url = reverse('QualiquantityPDF', args=[queryset.first().id])
        return HttpResponseRedirect(url)

    actions = [print_pdf]

admin.site.register(Produit,ProduitAdmin)



class ProduitVisiteAdmin(admin.ModelAdmin):
    list_display = ('id', 'visite','medecin','produit','qtt',"prescription","info")
    search_fields =["medecin__nom"]
    list_filter=["medecin__specialite","visite__rapport__user","produit"]
    date_hierarchy = 'visite__rapport__added'


    def info(self,obj):
        return f'{obj.visite.rapport.user}'


admin.site.register(ProduitVisite,ProduitVisiteAdmin)