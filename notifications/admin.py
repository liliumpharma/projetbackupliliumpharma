from django.contrib import admin

from .models import *

@admin.register(Notification)
class PlanAdmin(admin.ModelAdmin):
    list_display=["title", "_users", ]

    def _users(self,obj):
        return f"{' '.join([user.username for user in obj.users.all()])}"


def make_not_read(modeladmin, request, queryset):
    queryset.update(read=False)

make_not_read.short_description = "Remove Read"
make_not_read.allowed_permissions = ('change',)

@admin.register(UserNotification)
class UserNotificationAdmin(admin.ModelAdmin):
    list_display = ["user", "notification_description", "read", "read_at"]
    list_filter = ["read", "read_at"]
    search_fields = ["user__username", "notification__title"]
    actions = [make_not_read]

    def notification_description(self, obj):
        return obj.notification.description
    notification_description.short_description = 'Notification Description'