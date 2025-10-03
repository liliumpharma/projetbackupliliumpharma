from django.contrib import admin
from .models import PaybookUser, Versement, Creance, CreanceClient
from django.utils.html import format_html


@admin.register(PaybookUser)
class PaybookUserAdmin(admin.ModelAdmin):
    list_display = ('date', 'number', 'user', 'still_using')
    search_fields = ('date', 'number', 'user__username')
    list_filter = ('still_using',)

from django.contrib import admin
from django.db.models import Sum
from .models import Versement

@admin.register(Versement)
class VersementAdmin(admin.ModelAdmin):
    list_display = ('date_document','done','num_recu', 'way_of_payment', 'get_paybook_user_name', 'formatted_somme', 'display_link_button')
    list_filter = ('way_of_payment', 'paybook__user__username','done')
    date_hierarchy = 'date_document'

    def get_paybook_user_name(self, obj):
        if obj.paybook:
            user = obj.paybook.user
            return f"{user.first_name} {user.last_name}"
        else:
            return None

    get_paybook_user_name.short_description = 'Paybook User Name'

    def display_link_button(self, obj):
        if obj.link:
            return format_html('<a href="{}" target="_blank" class="button">Voir l''attachement</a>', obj.link)
        else:
            return '-'

    display_link_button.short_description = 'Pièce jointe'


    def formatted_somme(self, obj):
        # Formate la somme avec des espaces pour faciliter la lecture
        formatted = '{:,.2f}'.format(float(obj.somme)).replace(',', ' ')
        return formatted

    formatted_somme.short_description = 'Somme'

    def total_somme(self, request):
        print ("-")
        queryset = Versement.objects.all()
        for versement in queryset :
            total = sum(float(versement.somme.replace(' ', '').replace(',', '.')) for versement in queryset if versement.somme)
        return total


@admin.register(Creance)
class CreanceAdmin(admin.ModelAdmin):
    list_display = ('date', 'user', 'attachement')
    search_fields = ('date', 'number')

@admin.register(CreanceClient)
class CreanceAdmin(admin.ModelAdmin):
    list_display = ('date', 'user', 'client')
    search_fields = ('date', 'client', 'user')