# admin.py
from django.contrib import admin
from django.urls import reverse
from django.utils.html import mark_safe
from django.http import HttpResponseRedirect
from .models import *

@admin.register(Company)
class AdminCompany(admin.ModelAdmin):
    list_display = ["name", "_print","_printrules"]

    def _print(self, obj):
      url = reverse('companyPDF', args=[obj.id])
      return mark_safe(f"<a id=\"id-du-bouton-imprimer\" href='{url}' target='_blank'>print</a>")

    _print.short_description = 'Company informations'

    def _printrules(self, obj):
      url = reverse('RulesPDF', args=[obj.id])
      return mark_safe(f"<a id=\"id-du-bouton-imprimer\" href='{url}' target='_blank'>print</a>")

    _printrules.short_description = 'Internal Rules'
