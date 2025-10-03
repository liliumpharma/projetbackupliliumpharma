from django.contrib import admin
from .models import *



class PaysAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom')
    search_fields = ('nom',)


admin.site.register(Pays,PaysAdmin)


class WilayaAdmin(admin.ModelAdmin):
    list_display = ('id', 'code_name', 'nom')
    search_fields = ('nom',)
    list_filter = ['pays',]

    # autocomplete_fields = ["pays"]


admin.site.register(Wilaya,WilayaAdmin)

class CommuneAdmin(admin.ModelAdmin):
    list_display = ('id', 'wilaya','nom')
    search_fields = ('nom',)
    list_filter=('wilaya__pays',"wilaya")
    # autocomplete_fields = ["wilaya"]


admin.site.register(Commune,CommuneAdmin)
