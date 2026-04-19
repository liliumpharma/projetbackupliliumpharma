from django.contrib import admin
from monthly_evaluations.models import *
from django.utils.html import mark_safe
from django.urls import reverse
from accounts.models import UserProfile
from django.http import HttpResponseRedirect


# Register your models here.
@admin.register(Monthly_Evaluation)
class Monthly_Evaluation(admin.ModelAdmin):
    list_display=['id',"user",'added_date',"sup_evaluation","user_sup_evaluation","_print"]
    list_filter = ['added', "user", "user__userprofile__lines","sup_evaluation","user_sup_evaluation"]
    date_hierarchy = 'added'



    def _print(self, obj):
        url = reverse('pdf_view', args=[obj.id])
        return mark_safe(f"<a id=\"id-du-bouton-imprimer\" href='{url}' target='_blank'>Imprimer</a>")
    _print.short_description = 'Print'

    def print_pdf(self, request, queryset):
        url = reverse('pdf_view', args=[queryset.first().id])
        return HttpResponseRedirect(url)

    actions = [print_pdf]


    @admin.display(description="added_date")
    def added_date(self, obj):
        return obj.added



@admin.register(SupEvaluation)
class SupEvaluation(admin.ModelAdmin):
    list_display=['added_date',"user",]
    list_filter = ['added', "user", "user__userprofile__lines"]
    date_hierarchy = 'added'



    @admin.display(description="added_date")
    def added_date(self, obj):
        return obj.added
    


@admin.register(SupEvaluationToDirection)
class SupEvaluationToDirectionAdmin(admin.ModelAdmin):
    list_display = ('user', 'added')
    search_fields = ('user__username', 'added')
    list_filter = ('added',)

@admin.register(DirectionEvaluationToSup)
class DirectionEvaluationToSupAdmin(admin.ModelAdmin):
    list_display = ('user', 'added')
    search_fields = ('user__username', 'added')
    list_filter = ('added',)

@admin.register(DirectionToDelegateEvaluation)
class DirectionToDelegateEvaluationAdmin(admin.ModelAdmin):
    list_display = ('user', 'added')
    search_fields = ('user__username', 'added')
    list_filter = ('added',)

@admin.register(Commercial_Monthly_Evaluation)
class CommercialMonthlyEvaluationAdmin(admin.ModelAdmin):
    list_display = ('user', 'added','_print')
    search_fields = ('user__username', 'added')
    list_filter = ('added',)

    def _print(self, obj):
        url = reverse('pdf_view', args=[obj.id])
        return mark_safe(f"<a id=\"id-du-bouton-imprimer\" href='{url}' target='_blank'>Imprimer</a>")
    _print.short_description = 'Print'