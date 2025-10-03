from django.contrib import admin
from .models import Deplacement, NuitDetail

class NuitDetailInline(admin.TabularInline):
    model = NuitDetail
    extra = 1  # Number of empty rows to display for new records

@admin.register(Deplacement)
class DeplacementAdmin(admin.ModelAdmin):
    list_display = ('user', 'start_date', 'end_date', 'nb_jours', 'nb_nuits', 'distance', 'created_at')
    search_fields = ('user__username', 'wilaya1', 'wilaya2')
    inlines = [NuitDetailInline]
