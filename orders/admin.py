from django.contrib import admin
from .models import *
from django.utils.safestring import mark_safe
import base64
from django.template.loader import render_to_string



def make_confirmed(modeladmin, request, queryset):
    queryset.update(status="traite")
make_confirmed.short_description = "status traité"


def make_initial(modeladmin, request, queryset):
    queryset.update(status="initial")
make_initial.short_description = "status initial"



def make_pending(modeladmin, request, queryset):
    queryset.update(status="en cours")
make_pending.short_description = "status initial"

    
class ModelAInline(admin.StackedInline):
  model = OrderItem
  verbose_name_plural = 'produits'


class ExitOrderItemAInline(admin.StackedInline):
  model = ExitOrderItem
  verbose_name_plural = 'produits'




class OrderAdmin(admin.ModelAdmin):
    list_display = ('id','added','pharmacy',"gros","super_gros",'user',"observation",'items',"_pdf","from_company")
    list_filter = ('added','user','from_company', 'gros', 'super_gros')
    date_hierarchy = 'added'
    # fields = ('created_at','etat','wilaya','email','telephone','borderau')
    inlines = [ModelAInline]
    actions = [make_confirmed,make_initial]
    # readonly_fields = ['recu','destination','telephone', 'email','dateAller','dateRetour','nom','prenom','ville','nbrAdulte','nbrEnfant','nbrChambre']
        # if 'is_submitted' in readonly_fields:
        #     readonly_fields.remove('is_submitted')
        # return readonly_fields

    # list_per_page = 5


    def get_queryset(self, request):
        qs = super(OrderAdmin, self).get_queryset(request)
        if request.user.is_superuser or request.user.userprofile.speciality_rolee in ["Superviseur_national", "CountryManager","Admin"]:
            return qs
        else:
            qs=qs.filter(commune__wilaya__pays= request.user.userprofile.commune.wilaya.pays)
            if request.user.userprofile.rolee in ["Superviseur","Office"]:
                qs=qs.filter(users__in=request.user.userprofile.usersunder.all())
            return qs
            

    def _pdf(self,obj):
        return mark_safe(f'<a  target="_blank" class="btn btn-danger" href="https://app.liliumpharma.com/orders/{obj.id}"> PDF</a>')

    
    def region(self,obj):
        return  f"{obj.commune.wilaya} {obj.commune} " 


    def items(self,obj):
        return mark_safe(obj.items_admin())


admin.site.register(Order,OrderAdmin)


class ExitOrderAdmin(admin.ModelAdmin):
    list_display = ('added','user',"observation",'items')
    list_filter = ('added','user')
    date_hierarchy = 'added'
    # fields = ('created_at','etat','wilaya','email','telephone','borderau')
    inlines = [ExitOrderItemAInline]
    actions = [make_confirmed,make_initial]
    # readonly_fields = ['recu','destination','telephone', 'email','dateAller','dateRetour','nom','prenom','ville','nbrAdulte','nbrEnfant','nbrChambre']
        # if 'is_submitted' in readonly_fields:
        #     readonly_fields.remove('is_submitted')
        # return readonly_fields

    # list_per_page = 5


    def _pdf(self,obj):
        return mark_safe(f'<a  target="_blank" class="btn btn-danger" href="https://app.liliumpharma.com/orders/exits/{obj.id}"> PDF</a>')

    def items(self,obj):
        return mark_safe(obj.items_admin())


admin.site.register(ExitOrder,ExitOrderAdmin)
# admin.site.register(OrderSource)

