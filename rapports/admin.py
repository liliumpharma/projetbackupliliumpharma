from django.contrib import admin
from .models import *
from django.contrib.admin import DateFieldListFilter
from django.utils import timezone
from django.utils.html import format_html
from django.urls import reverse

from django.contrib import messages
from django.db import transaction
from django.forms import inlineformset_factory
from django.utils import timezone
from plans.models import Plan, PlanTask

from django import forms



def make_updatable(modeladmin, request, queryset):
    queryset.update(can_update=True)


make_updatable.short_description = "Add Updatable"
make_updatable.allowed_permissions = ("change",)


def make_non_updatable(modeladmin, request, queryset):
    queryset.update(can_update=False)


make_non_updatable.short_description = "Remove Updatable"
make_non_updatable.allowed_permissions = ("change",)


# class VisiteInline(admin.StackedInline):
#   model = Visite
#   verbose_name_plural = 'visites'


class VisiteInline(admin.TabularInline):  # Use TabularInline for better performance
    model = Visite
    verbose_name_plural = "visites"
    extra = 0
    fields = ("medecin", "priority")  # Display only the name of the doctor and priority
    readonly_fields = ("medecin", "priority")




class PlanTaskAdminForm(forms.ModelForm):
    class Meta:
        model = PlanTask
        fields = ("task", "completed")
        widgets = {
            "task": forms.Textarea(attrs={"rows": 2, "style": "width:100%;"}),
        }

# class CommentInline(admin.StackedInline):
#   model = Comment
#   verbose_name_plural = 'comments'

class RapportAdmin(admin.ModelAdmin):
    list_display = ("id", "added", "user", "can_update")
    search_fields = ["user__userprofile__telephone", "user__username"]
    list_filter = ("can_update", "user")
    date_hierarchy = "added"
    inlines = [VisiteInline]
    actions = [make_updatable, make_non_updatable]

    # Important: override the template for Rapport only
    change_form_template = "admin/rapports/rapport/change_form.html"
    add_form_template = "admin/rapports/rapport/change_form.html"

    def get_queryset(self, request):
        qs = super(RapportAdmin, self).get_queryset(request)

        # Exclude reports from 2020, 2021, and 2022
        qs = qs.exclude(added__year__in=[2020, 2021, 2022, 2023])

        if request.user.is_superuser:
            return qs
        qs = qs.filter(
            user__userprofile__commune__wilaya__pays=request.user.userprofile.commune.wilaya.pays
        )
        if request.user.userprofile.rolee == "Superviseur":
            qs = qs.filter(user__in=request.user.userprofile.usersunder.all())
        return qs

    # -------- Tasks integration (PlanTask inside Rapport admin) --------

    def _plan_for_rapport(self, rapport):
        """
        Map Rapport(user, added) -> Plan(user, day).
        Create Plan if missing (Plan only needs day+user in your model).
        """
        plan, _ = Plan.objects.get_or_create(day=rapport.added, user=rapport.user)
        return plan

    def _tasks_formset_class(self):
        return inlineformset_factory(
            parent_model=Plan,
            model=PlanTask,
            form=PlanTaskAdminForm,
            extra=1,
            can_delete=True,
        )


    def _build_tasks_formset_for_render(self, request, obj):
        """
        Build a tasks formset for rendering (GET/POST).
        - On change view: uses the real Plan of that rapport day/user.
        - On add view: uses a dummy Plan instance so user can type tasks before save.
        """
        PlanTaskFormSet = self._tasks_formset_class()

        if obj is not None:
            plan = self._plan_for_rapport(obj)
        else:
            # Add form: allow typing tasks even before rapport exists.
            # We'll attach them to the real Plan after the Rapport is saved.
            day = None
            user_id = None
            if request.method == "POST":
                day = request.POST.get("added") or None
                user_id = request.POST.get("user") or None

            dummy_day = day or timezone.localdate()
            dummy_plan = Plan(day=dummy_day, user_id=user_id or request.user.id)  # unsaved is fine for rendering
            plan = dummy_plan

        if request.method == "POST":
            return PlanTaskFormSet(request.POST, instance=plan, prefix="tasks")
        return PlanTaskFormSet(instance=plan, prefix="tasks")

    def render_change_form(self, request, context, add=False, change=False, form_url="", obj=None):
        context["tasks_formset"] = self._build_tasks_formset_for_render(request, obj)
        return super().render_change_form(request, context, add=add, change=change, form_url=form_url, obj=obj)

    def _save_tasks_from_post(self, request, rapport_obj):
        """
        After saving a Rapport, persist tasks to the corresponding Plan(day/user).
        """
        # If the formset is not present in POST, do nothing (safety)
        if "tasks-TOTAL_FORMS" not in request.POST:
            return

        plan = self._plan_for_rapport(rapport_obj)
        PlanTaskFormSet = self._tasks_formset_class()
        formset = PlanTaskFormSet(request.POST, instance=plan, prefix="tasks")

        if not formset.is_valid():
            # Don’t block the Rapport save (admin already saved it), but warn clearly.
            messages.error(request, f"Tasks not saved: {formset.non_form_errors()}")
            return

        with transaction.atomic():
            formset.save()

    def response_add(self, request, obj, post_url_continue=None):
        # Save tasks after the Rapport is created
        self._save_tasks_from_post(request, obj)
        return super().response_add(request, obj, post_url_continue=post_url_continue)

    def response_change(self, request, obj):
        # Save tasks after editing an existing Rapport
        self._save_tasks_from_post(request, obj)
        return super().response_change(request, obj)


admin.site.register(Rapport, RapportAdmin)


class InputFilter(admin.SimpleListFilter):
    template = "admin/input_filter.html"

    def lookups(self, request, model_admin):
        # Dummy, required to show the filter.
        return (
            ("2", "shared"),
            ("1", "unshared"),
            ("0", "all"),
        )


class UIDFilter(InputFilter):
    parameter_name = "uid"
    title = " Visite ID"

    def queryset(self, request, queryset):
        if self.value() is not None:
            uid = self.value()
            # print("len(uid.split(" ") ) >= 1len(uid.split(" ") ) >= 1***************************",)
            return (
                queryset.filter(
                    id__in=[idd.strip() for idd in uid.split("+") if idd != ""]
                )
                if uid != ""
                else queryset
            )


class MultiSelectFilter(admin.SimpleListFilter):
    title = "Spécialité Médicale"
    parameter_name = "specialite"

    def lookups(self, request, model_admin):
        return (
            ("Pharmacie,Grossiste,SuperGros", "Commercial"),
            (
                "Orthopedie,Nutritionist,Dermatologue,Généraliste,Diabetologue,Neurologue,Psychologue,Gynécologue,Rumathologue,Allergologue,Phtisio,Cardiologue,Urologue,Hematologue,Interniste,Gastrologue,Endocrinologue,Dentiste,ORL",
                "Médical",
            ),
            ("Pharmacie", "Pharmacie"),
            ("Grossiste", "Grossiste"),
            ("SuperGros", "SuperGros"),
            ("Orthopedie", "Orthopedie"),
            ("Nutritionist", "Nutritionist"),
            ("Dermatologue", "Dermatologue"),
            ("Généraliste", "Généraliste"),
            ("Diabetologue", "Diabetologue"),
            ("Neurologue", "Neurologue"),
            ("Psychologue", "Psychologue"),
            ("Gynécologue", "Gynécologue"),
            ("Rumathologue", "Rumathologue"),
            ("Allergologue", "Allergologue"),
            ("Phtisio", "Phtisio"),
            ("Cardiologue", "Cardiologue"),
            ("Urologue", "Urologue"),
            ("Hematologue", "Hematologue"),
            ("Interniste", "Interniste"),
            ("Gastrologue", "Gastrologue"),
            ("Endocrinologue", "Endocrinologue"),
            ("Dentiste", "Dentiste"),
            ("ORL", "ORL"),
            ("Maxilo facial", "Maxilo facial"),
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(medecin__specialite__in=self.value().split(","))
        return queryset


class UIDFilter(InputFilter):
    parameter_name = "uid"
    title = "UID"

    def queryset(self, request, queryset):
        if self.value() is not None:
            uid = self.value()
            # print("len(uid.split(" ") ) >= 1len(uid.split(" ") ) >= 1***************************",)
            return (
                queryset.filter(
                    id__in=[idd.strip() for idd in uid.split("+") if idd != ""]
                )
                if uid != ""
                else queryset
            )


# class VisiteAdmin(admin.ModelAdmin):
#     list_display = ("id", "rapport_user", "date_rapport", "medecin", "observation")
#     search_fields = ["medecin__id", "medecin__nom"]
#     list_filter = (
#         "rapport__user",
#         MultiSelectFilter,
#         "medecin__commune",
#         "medecin__uploaded_from_excel",
#     )
#     date_hierarchy = "rapport__added"

#     def get_list_filter(self, request):
#         list_filter = super().get_list_filter(request)
#         list_filter += ("medecin__specialite",)
#         return list_filter

#     def rapport_user(self, obj):
#         # Assurez-vous que `rapport` est bien défini dans le modèle `Visite`
#         return obj.rapport.user if obj.rapport else "N/A"

#     rapport_user.short_description = "User"

#     # autocomplete_fields = ["medecin","rapport","produits"]

#     def get_queryset(self, request):
#         qs = super(VisiteAdmin, self).get_queryset(request)
#         if request.user.is_superuser:
#             return qs
#         else:
#             qs = qs.filter(
#                 rapport__user__userprofile__commune__wilaya__pays=request.user.userprofile.commune.wilaya.pays
#             )
#             if request.user.userprofile.rolee == "Superviseur":
#                 qs = qs.filter(
#                     rapport__user__in=request.user.userprofile.usersunder.all()
#                 )
#             return qs
from django.utils import timezone
from django.db.models import Q


class VisiteAdmin(admin.ModelAdmin):
    list_display = ("id", "rapport_user", "date_rapport", "medecin", "observation")
    search_fields = ["medecin__id", "medecin__nom"]
    list_filter = (
        "rapport__user",
        MultiSelectFilter,
        "medecin__commune",
        "medecin__uploaded_from_excel",
    )
    date_hierarchy = "rapport__added"

    def get_list_filter(self, request):
        list_filter = super().get_list_filter(request)
        list_filter += ("medecin__specialite",)
        return list_filter

    def rapport_user(self, obj):
        return obj.rapport.user if obj.rapport else "N/A"

    rapport_user.short_description = "User"

    def get_queryset(self, request):
        qs = super(VisiteAdmin, self).get_queryset(request)

        # Get the current date and filter by month and year
        now = timezone.now()
        current_month_filter = Q(rapport__added__month=now.month)

        # Exclude medecins assigned to users with id=102 or id=103
        medecin_exclude_filter = ~Q(medecin__users__id__in=[102, 103])

        if request.user.is_superuser:
            return qs.filter(current_month_filter).filter(medecin_exclude_filter)
        else:
            # Filter by user's country and current month, exclude medecins assigned to user 102 and 103
            qs = (
                qs.filter(
                    rapport__user__userprofile__commune__wilaya__pays=request.user.userprofile.commune.wilaya.pays
                )
                .filter(current_month_filter)
                .filter(medecin_exclude_filter)
            )

            if request.user.userprofile.rolee == "Superviseur":
                qs = qs.filter(
                    rapport__user__in=request.user.userprofile.usersunder.all()
                ).filter(medecin_exclude_filter)
            return qs

    # Override formfield_for_foreignkey to limit Rapport choices to current month and exclude medecins
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "rapport":
            now = timezone.now()
            # Filter rapports to only include the current month
            kwargs["queryset"] = Rapport.objects.filter(
                added__year=now.year, added__month=now.month
            )
        elif db_field.name == "medecin":
            # Exclude medecins assigned to users with id=102 or id=103
            kwargs["queryset"] = Medecin.objects.exclude(users__id__in=[102, 103])
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    # def has_change_permission(self, request, obj=None):
    #     if not obj:
    #         return False # So they can see the change list page
    #     if request.user.is_superuser or obj.rapport.user.userprofile.commune.wilaya.pays == request.user.userprofile.commune.wilaya.pays:
    #         return True
    #     else:
    #         return False


admin.site.register(Visite, VisiteAdmin)


class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "rapport", "comment", "added")
    # readonly_fields=('user',)

    class Media:
        js = ("js/comment.js",)

    def get_queryset(self, request):
        qs = super(CommentAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        else:
            qs = qs.filter(
                rapport__user__userprofile__commune__wilaya__pays=request.user.userprofile.commune.wilaya.pays
            )
            if request.user.userprofile.rolee == "Superviseur":
                qs = qs.filter(
                    rapport__user__in=request.user.userprofile.usersunder.all()
                )
            return qs

    def has_change_permission(self, request, obj=None):
        if not obj:
            return False  # So they can see the change list page
        if (
            request.user.is_superuser
            or obj.rapport.user.userprofile.commune.wilaya.pays
            == request.user.userprofile.commune.wilaya.pays
        ):
            return True
        else:
            return False

    def get_changeform_initial_data(self, request):
        get_data = super(CommentAdmin, self).get_changeform_initial_data(request)
        get_data["user"] = request.user.pk
        return get_data


admin.site.register(Comment, CommentAdmin)

admin.site.register(QRCodeModel)

from django import forms
from django.contrib import admin
from .models import Anomalies, Rapport
from datetime import datetime

# Custom form to filter the rapport field
class AnomaliesAdminForm(forms.ModelForm):
    class Meta:
        model = Anomalies
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(AnomaliesAdminForm, self).__init__(*args, **kwargs)
        current_year = datetime.now().year
        # Filter the 'rapport' field to only show reports from the current year
        self.fields['rapport'].queryset = Rapport.objects.filter(added__year=current_year)


# Register the Anomalies model to the admin
from datetime import datetime
from django import forms
from datetime import datetime

class AnomaliesAdmin(admin.ModelAdmin):
    list_display = ('rapport', 'user', 'Anomalie', 'date', 'added', 'print_button')
    list_filter = ('user', 'Anomalie', 'date', 'added')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "rapport":
            # Filtrer les rapports pour n'afficher que ceux de l'année 2025
            kwargs["queryset"] = Rapport.objects.filter(added__year=2025)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def print_button(self, obj):
        # Générer un lien vers la vue d'impression des anomalies avec l'ID de l'utilisateur
        return format_html('<a class="button" href="{}?user_id={}">Imprimer</a>',
                           reverse('anomalies-print'),
                           obj.user.id)

    print_button.short_description = 'Imprimer les Anomalies'
    print_button.allow_tags = True

admin.site.register(Anomalies, AnomaliesAdmin)
