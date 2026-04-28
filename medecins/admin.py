from django.contrib import admin
from django.db.models import Count
from django.urls import path

from medecins.views import upload_excel
from .models import *
from accounts.models import UserProfile
from django.utils.safestring import mark_safe



class MultiSelectFilter(admin.SimpleListFilter):
    # Filter title
    title = 'Specialite'

    # model field
    parameter_name = 'specialite'

    # def __init__(self, f, request, params, model, *args, **kwargs):
    #     super().__init__(f, request, params, model, *args, **kwargs)


    def lookups(self, request, model_admin):
        # you can modify this part, this is less DRY approach.
        # P.S. assuming city_name is lowercase CharField
        return (
            ('Pharmacie,Grossiste,SuperGros', 'commercial'),
            ('Orthopedie,Nutritionist,Dermatologue,Généraliste,Diabetologue,Neurologue,Psychologue,Gynécologue,Rumathologue,Allergologue,Phtisio,Cardiologue,Urologue,Hematologue,Interniste,Gastrologue,Endocrinologue,Dentiste,ORL' ,'Medical'),
            ('Pharmacie','Pharmacie'),
            ('Grossiste','Grossiste'),
            ('SuperGros','SuperGros'),
            ('Orthopedie','Orthopedie'),
            ('Nutritionist','Nutritionist'),
            ('Dermatologue','Dermatologue'),
            ('Généraliste','Généraliste'),
            ('Diabetologue','Diabetologue'),
            ('Neurologue','Neurologue'),
            ('Psychologue','Psychologue'),
            ('Gynécologue','Gynécologue'),
            ('Rumathologue','Rumathologue'),
            ('Allergologue','Allergologue'),
            ('Phtisio','Phtisio'),
            ('Cardiologue','Cardiologue'),
            ('Urologue','Urologue'),
            ('Hematologue','Hematologue'),
            ('Interniste','Interniste'),
            ('Gastrologue', 'Gastrologue'),
            ('Endocrinologue', 'Endocrinologue'),
            ('Dentiste', 'Dentiste'),
            ('ORL', 'ORL'),
            ('Maxilo facial','Maxilo facial')
        )

    def queryset(self, request, queryset):

        if self.value():
            # filter if a choice selected
            return queryset.filter(specialite__in=self.value().split(','))
        # default for no filtering
        return queryset



class SharedFilter(admin.SimpleListFilter):
    # Filter title
    title = 'Shared'

    # model field
    parameter_name = 'shared'

    # def __init__(self, f, request, params, model, *args, **kwargs):
    #     super().__init__(f, request, params, model, *args, **kwargs)


    def lookups(self, request, model_admin):
        # you can modify this part, this is less DRY approach.
        # P.S. assuming city_name is lowercase CharField
        users=request.user.userprofile.usersunder.all() if not request.user.is_superuser else [usr.user for usr in UserProfile.objects.all()]
        return (
            ('s', 'shared'),
            ('u', 'unshared'),
            ('0','all'),
            *( (usr.id, usr.username) for usr in users )
        )

    def queryset(self, request, queryset):

        if self.value():
            # filter if a choice selected
            if self.value()=="u":
                return queryset.annotate(num_users=Count('users')).exclude(num_users__gt=1)
            elif self.value()=="s":
                return queryset.annotate(num_users=Count('users')).exclude(num_users=1)
            elif self.value()!="0":
                return queryset.annotate(num_users=Count('users')).exclude(num_users=1).filter(users__id=self.value())
                
                   
        # default for no filtering
        return queryset



class InputFilter(admin.SimpleListFilter):
    template = 'admin/input_filter.html'

    def lookups(self, request, model_admin):
        # Dummy, required to show the filter.
        return (
            ('2', 'shared'),
            ('1', 'unshared'),
            ('0','all'),
        )


class UIDFilter(InputFilter):
    parameter_name = 'uid'
    title = 'UID'
    
    def queryset(self, request, queryset):
        if self.value() is not None:
            uid = self.value()
            # print("len(uid.split(" ") ) >= 1len(uid.split(" ") ) >= 1***************************",)
            return queryset.filter(id__in=[idd.strip() for idd in uid.split("+") if idd!=""]) if uid!="" else queryset




def make_updatable(modeladmin, request, queryset):
    queryset.update(updatable=True)
    # for obj in queryset:
    #     obj.updatable=True
    #     obj.save()

make_updatable.short_description = "Add Updatable"
make_updatable.allowed_permissions = ('change',)

def make_non_updatable(modeladmin, request, queryset):
    queryset.update(updatable=False)
    # for obj in queryset:
    #     obj.updatable=False
    #     obj.save()

make_non_updatable.short_description = "Remove Updatable"
make_non_updatable.allowed_permissions = ('change',)

def make_flag(modeladmin, request, queryset):
    queryset.update(flag=True)
    # for obj in queryset:
    #     obj.flag=True
    #     obj.save()

make_flag.short_description = "Add Flag"


def make_non_flag(modeladmin, request, queryset):
    queryset.update(flag=False)
    # for obj in queryset:
    #     obj.flag=False
    #     obj.save()

make_non_flag.short_description = "Remove Flag"


from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from rapports.models import Visite

class VisitedFilter(admin.SimpleListFilter):
    title = _('visité')
    parameter_name = 'visited'

    def lookups(self, request, model_admin):
        return (
            ('yes', _('Yes')),
            ('no', _('No')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(visite__isnull=False).distinct()
        if self.value() == 'no':
            return queryset.filter(visite__isnull=True)

class MedecinsAdmin(admin.ModelAdmin):
    list_display = ('id','added','flag',"_users" ,'nom',"specialite", "specialite_fk",'classification','wilaya','commune',"telephone","adresse",'updatable',"_has_location")
    search_fields = ("id",'nom', 'telephone','adresse')
    list_filter=(SharedFilter, 'users',MultiSelectFilter,'flag','updatable','wilaya','commune','blocked','classification','uploaded_from_excel',VisitedFilter,UIDFilter)
    # autocomplete_fields = ["users",]
    actions = [make_updatable,make_non_updatable,make_flag,make_non_flag]
    filter_horizontal = ('users',)
    date_hierarchy = 'added'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "wilaya":
            # This restricts the dropdown to only Wilayas where the Pays name contains "Alger"
            # (Using icontains covers "Algerie", "Algérie", or "Algeria" just to be safe)
            kwargs["queryset"] = Wilaya.objects.filter(pays__nom__icontains="alger")
        
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


    def _users(self,obj):
        return ",".join([user.username for user in obj.users.all()[:4] ])

    def _has_location(self,obj):
        img="/static/admin/img/icon-yes.svg" if obj.lat and obj.lon else "/static/admin/img/icon-no.svg"
        return mark_safe(f"<img src='{img}'/>") 
        
    def get_queryset(self, request):
        qs = super(MedecinsAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        else:
            qs=qs.filter(commune__wilaya__pays= request.user.userprofile.commune.wilaya.pays)
            if request.user.userprofile.rolee=="Superviseur":
                qs=qs.filter(users__in=request.user.userprofile.usersunder.all())
            return qs.distinct()

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('upload-excel/', self.admin_site.admin_view(upload_excel), name='upload_excel'),
        ]
        return custom_urls + urls
    
    # def has_change_permission(self, request, obj=None):
    #     if not obj:
    #         return False # So they can see the change list page
    #     if request.user.is_superuser or obj.commune.wilaya.pays == request.user.userprofile.commune.wilaya.pays:
    #         return True
    #     else:
    #         return False
    class Media:
        js = (
            'admin/js/vendor/jquery/jquery.js', 
            'js/chained_communes.js', 
        )

admin.site.register(Medecin,MedecinsAdmin)
admin.site.register(MedecinSpecialite)


# class MedecinModificationHistoryAdmin(admin.ModelAdmin):
#     list_display = ('id', 'medecin', 'user', 'action', 'timestamp')

# admin.site.register(MedecinModificationHistory, MedecinModificationHistoryAdmin)

class MedecinModificationHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'medecin', 'user', 'action','get_users_before','get_users_after', 'date_hour')
    search_fields = ("id",'medecin__nom','medecin__id')


    def get_users_before(self, obj):
        return ", ".join([str(user) for user in obj.users_before.all()])

    def get_users_after(self, obj):
        return ", ".join([str(user) for user in obj.users_after.all()])
    
    def date_hour(self, obj):
        return obj.timestamp.strftime("%Y-%m-%d à %H:%M")
    date_hour.short_description = 'Date/Hour'

    get_users_before.short_description = 'From'
    get_users_after.short_description = 'To'

admin.site.register(MedecinModificationHistory, MedecinModificationHistoryAdmin)