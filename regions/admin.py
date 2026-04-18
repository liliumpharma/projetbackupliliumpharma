from django.contrib import admin
from .models import *


class RegionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


admin.site.register(Region, RegionAdmin)


class PaysAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom')
    search_fields = ('nom',)


admin.site.register(Pays, PaysAdmin)


class WilayaAdmin(admin.ModelAdmin):
    list_display = ('id', 'code_name', 'nom', 'region')
    search_fields = ('nom',)
    list_filter = ['pays', 'region']
    list_editable = ['region']


admin.site.register(Wilaya, WilayaAdmin)


class CommuneAdmin(admin.ModelAdmin):
    list_display = ('id', 'wilaya', 'nom')
    search_fields = ('nom',)
    list_filter = ('wilaya__pays', 'wilaya__region', 'wilaya')


admin.site.register(Commune, CommuneAdmin)
