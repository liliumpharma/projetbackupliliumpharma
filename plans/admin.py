from django.contrib import admin
from .models import *


def validate_communes(modeladmin, request, queryset):
    queryset.update(valid_commune=True)


validate_communes.short_description = "Valider les communes"


def validate_medecins(modeladmin, request, queryset):
    queryset.update(valid_clients=True)


validate_communes.short_description = "Valider les medecins"


def validate_tasks(modeladmin, request, queryset):
    queryset.update(valid_tasks=True)


validate_communes.short_description = "Valider les communes"


def non_validate_communes(modeladmin, request, queryset):
    queryset.update(valid_commune=False)


non_validate_communes.short_description = "non valide  communes"


def non_validate_medecins(modeladmin, request, queryset):
    queryset.update(valid_clients=False)


non_validate_medecins.short_description = "non valide medecins"


def non_validate_tasks(modeladmin, request, queryset):
    queryset.update(valid_tasks=False)


non_validate_tasks.short_description = "non valide tasks"


def all_validate(modeladmin, request, queryset):
    queryset.update(valid_commune=True)
    queryset.update(valid_clients=True)
    queryset.update(valid_tasks=True)


all_validate.short_description = "Tout valider"


def all_devalidate(modeladmin, request, queryset):
    queryset.update(valid_commune=False)
    queryset.update(valid_clients=False)
    queryset.update(valid_tasks=False)


all_devalidate.short_description = "Retirer validation"


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "day",
        "user",
        "valid_commune",
        "valid_clients",
        "valid_tasks",
        "updatable",
    ]
    list_filter = [
        "user",
        "day",
        "valid_clients",
        "valid_commune",
        "valid_tasks",
        "isfree",
    ]
    search_fields = ["id"]
    actions = [
        validate_communes,
        validate_medecins,
        validate_tasks,
        non_validate_communes,
        non_validate_medecins,
        non_validate_tasks,
        all_validate,
        all_devalidate,
    ]
    date_hierarchy = "day"


@admin.register(PlanTask)
class PlanTaskAdmin(admin.ModelAdmin):
    list_display = ["_date", "_user", "task", "completed"]
    exclude = ["order"]
    list_filter = ["completed", "plan__user"]

    def _date(self, obj):
        return str(obj.plan.day)

    def _user(self, obj):
        return str(obj.plan.user)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        now = timezone.now()
        # Filter plans that belong to the current month and year
        return qs.filter(plan__day__year=now.year, plan__day__month=now.month)

# Register PlanComment model
admin.site.register(PlanComment)

