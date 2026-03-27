from django.contrib import admin
from .models import DelegateEvaluation, EvaluationAnswer

class EvaluationAnswerInline(admin.TabularInline):
    model = EvaluationAnswer
    extra = 0
    readonly_fields = ('question_id', 'answer_data')
    can_delete = False

@admin.register(DelegateEvaluation)
class DelegateEvaluationAdmin(admin.ModelAdmin):
    list_display = ('user', 'month', 'year', 'evaluation_type', 'total_score', 'created_at')
    list_filter = ('evaluation_type', 'month', 'year')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    readonly_fields = ('user', 'month', 'year', 'evaluation_type', 'total_score')
    inlines = [EvaluationAnswerInline]

@admin.register(EvaluationAnswer)
class EvaluationAnswerAdmin(admin.ModelAdmin):
    list_display = ('evaluation', 'question_id')
    search_fields = ('evaluation__user__username', 'question_id')
    readonly_fields = ('evaluation', 'question_id', 'answer_data')
