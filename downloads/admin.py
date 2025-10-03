from django.contrib import admin

from downloads.models import Downloadable
from medecins.admin import InputFilter
from .models import Downloadable
from django.utils.safestring import mark_safe
from django.utils.html import format_html

class UIDFilter(InputFilter):
    parameter_name = 'uid'
    title = 'UID'

    def queryset(self, request, queryset):
        if self.value() is not None:
            uid = self.value()
            # print("len(uid.split(" ") ) >= 1len(uid.split(" ") ) >= 1***************************",)
            return queryset.filter(id__in=[idd.strip() for idd in uid.split("+") if idd!=""]) if uid!="" else queryset

# @admin.register(Downloadable)
class DownloadableAdmin(admin.ModelAdmin):
    list_display = ('id', 'link_name', 'users_list',  'display_attachment')
    list_filter = ('users',UIDFilter)
    filter_horizontal = ('users',)

    def display_attachment(self, obj):
        # Display a link to the attachment
        if obj.attachement:
            return format_html('<a href="{}" target="_blank">{}</a>', obj.attachement.url, obj.attachement.name)
        else:
            return "-"

    display_attachment.short_description = 'Attachment'

    def users_list(self, obj):
        # Display a comma-separated list of users
        return ", ".join([user.username for user in obj.users.all()])

    users_list.short_description = 'Users'

admin.site.register(Downloadable, DownloadableAdmin)