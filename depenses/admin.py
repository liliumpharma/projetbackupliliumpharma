from django.contrib import admin
from django.urls import reverse
from django.utils.html import mark_safe
from .models import *  # Import your Spend model

# Register your models here.
@admin.register(Spend)
# @admin.register(SpendComment)

class SpendAdmin(admin.ModelAdmin):
    list_display = ('added', 'price', 'status',"_print")
    list_filter = ('added', 'status')
    search_fields = ('user__username',)
    date_hierarchy = 'added'

    def _print(self, obj):
        url = reverse('SpendPDF', args=[obj.id])
        return mark_safe(f"<a id=\"id-du-bouton-imprimer\" href='{url}' target='_blank'>Imprimer</a>")
    _print.short_description = 'Print'

    def print_pdf(self, request, queryset):
        url = reverse('SpendPDF', args=[queryset.first().id])
        return HttpResponseRedirect(url)

    actions = [print_pdf]
    @admin.display(description="added_date")
    def added_date(self, obj):
        return obj.added
        

admin.site.register(SpendComment)