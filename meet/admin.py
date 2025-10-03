from django.contrib import admin
from .models import Meet

# Register the meet model with the admin site
@admin.register(Meet)
class MeetAdmin(admin.ModelAdmin):
    list_display = ('id', 'added', 'date_meet', 'link', 'note')
    list_filter = ('added', 'date_meet')
    search_fields = ('link', 'note')
    filter_horizontal = ('user',)
