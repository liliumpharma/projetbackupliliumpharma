from django.contrib import admin
from .models import *

admin.site.register(LeaveType)
admin.site.register(AbsenceType)
admin.site.register(Occasion)


@admin.register(Absence)
class AbsencesAdmin(admin.ModelAdmin):
    list_display = ["date", "user", "approved"]
    list_filter = ["user", "user__userprofile__family"]
    date_hierarchy = "added"


@admin.register(Leave)
class LeavesAdmin(admin.ModelAdmin):
    list_display = ["id", "start_date", "end_date", "user", "approved"]
    list_filter = ["user", "user__userprofile__family"]
    date_hierarchy = "added"

    class Media:
        js = ("js/holidays/changeform.js",)

    # search_fields=["name","description"]
    # inlines = (ProductAttributesInline, ProductImageInline )

    # def get_inline_instances(self, request, obj=None):
    #     if not obj:
    #         return list()
    #     return super().get_inline_instances(request, obj)

    # def image1(self, obj):
    #     return mark_safe(f'<img src="{obj.image.url}" height="120px" />'
    # )


#
