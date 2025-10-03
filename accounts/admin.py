from django.contrib import admin
from .models import UserProfile, PersonalInfo, UserProduct, UserNotificationPermissions
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from plans.models import Plan
import datetime
import subprocess
from django.http import HttpResponse, JsonResponse
from django.contrib.admin.views.decorators import staff_member_required


def recive_mail(modeladmin, request, queryset):
    UserProfile.objects.filter(user__in=queryset).update(recive_mail=True)


recive_mail.short_description = "Recevoir les emails"

from rapports.views import generate_pages_pharmacie_task, generate_pages_task
def generate_plan(modeladmin, request, queryset):
    print("nabiiiiiiiiiiiiiiiiiiiil")
    print(queryset)
    today = datetime.datetime.today()
    for u in queryset:
        for day in range(1, 31):
            if not Plan.objects.filter(
                day=datetime.datetime(today.year, today.month, day).date(),
                user=u,
                updatable=True,
            ).exists():
                try:
                    Plan.objects.create(
                        day=datetime.datetime(today.year, today.month, day).date(),
                        user=u,
                        updatable=True,
                    )
                    
                except:
                    pass
        print(u.id)
        print("iciiiiiiii nabil")
        print(UserProfile.objects.get(user=u.id).speciality_rolee)
        if UserProfile.objects.get(user=u.id).speciality_rolee == "Medico_commercial":
                generate_pages_task(u.id)
                generate_pages_pharmacie_task(u.id)
        elif UserProfile.objects.get(user=u.id).speciality_rolee == "Commercial" and u.username != "Pharmacie_Recycle_Bin":
                generate_pages_pharmacie_task(u.id)


generate_plan.short_description = "Generate plans"


def updateredis(modeladmin, request, queryset):
    import subprocess
    if request.user.is_superuser:
        subprocess.run(['redis-cli', 'FLUSHALL'])

updateredis.short_description = "Mise a jour Medecins"

def not_recive_mail(modeladmin, request, queryset):
    UserProfile.objects.filter(user__in=queryset).update(recive_mail=False)


not_recive_mail.short_description = "Ne pas recevoir les emails"


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False


class PersonalInfoInline(admin.StackedInline):
    model = PersonalInfo
    can_delete = False


class UserProductInline(admin.TabularInline):
    model = UserProduct
    extra = 2


class UserNotificationPermissionsInline(admin.StackedInline):
    model = UserNotificationPermissions


class CustomUserAdmin(UserAdmin):
    inlines = (
        UserProfileInline,
        PersonalInfoInline,  # Adding PersonalInfo inline
        UserProductInline,
        UserNotificationPermissionsInline,
    )
    search_fields = ("username", "first_name", "last_name")
    list_filter = [
        "userprofile__commune__wilaya__pays",
        "userprofile__work_as_commercial",
        "userprofile__hidden",
        "userprofile__rolee",
        "userprofile__family",
        "userprofile__speciality_rolee",
        "is_superuser",
    ]
    actions = [recive_mail, not_recive_mail, generate_plan, updateredis]
    list_display = [
        "id",
        "username",
        "first_name",
        "last_name",
        "user_speciality_role",
        "user_family",
        "commune_nom",
        "work_as_commercial",
        "hidden",
        "user_is_superuser",
    ]

    class Media:
        js = ("/static/js/accounts/changeForm.js",)

    def hidden(self, obj):
        if hasattr(obj, "userprofile"):
            return obj.userprofile.hidden
        return "-"

    def work_as_commercial(self, obj):
        if hasattr(obj, "userprofile"):
            return obj.userprofile.work_as_commercial
        return "-"

    def user_role(self, obj):
        if hasattr(obj, "userprofile"):
            return obj.userprofile.get_rolee_display()
        return "-"

    user_role.short_description = "Rôle"

    def user_speciality_role(self, obj):
        if hasattr(obj, "userprofile"):
            return obj.userprofile.get_speciality_rolee_display()
        return "-"

    user_speciality_role.short_description = "Poste"

    def user_family(self, obj):
        if hasattr(obj, "userprofile"):
            return obj.userprofile.get_family_display()
        return "-"

    user_family.short_description = "family"

    def user_is_superuser(self, obj):
        return obj.is_superuser

    user_is_superuser.boolean = True
    user_is_superuser.short_description = "Superuser"

    def commune_nom(self, obj):
        return obj.userprofile.commune.nom

    commune_nom.admin_order_field = "commune__nom"
    commune_nom.short_description = "Commune"


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "display_superusers")

    def display_superusers(self, obj):
        superusers = obj.usersunder.all()
        if superusers:
            return ", ".join([str(superuser) for superuser in superusers])
        else:
            return "null"

    display_superusers.short_description = "Superutilisateur(s)"


# Register models
admin.site.register(UserProfile, UserProfileAdmin)

# Unregister default User admin and register custom User admin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

