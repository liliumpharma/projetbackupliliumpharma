from django.db import models
from django.conf import settings
from django.db.models import JSONField

class DelegateEvaluation(models.Model):
    EVALUATION_TYPES = (
        ('MEDICAL', 'Medical'),
        ('COMMERCIAL', 'Commercial'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='delegate_evaluations')
    month = models.IntegerField()
    year = models.IntegerField()
    evaluation_type = models.CharField(max_length=20, choices=EVALUATION_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    total_score = models.FloatField(default=0.0)

    class Meta:
        unique_together = ('user', 'month', 'year')

    def __str__(self):
        return f"{self.user} - {self.month}/{self.year} ({self.evaluation_type})"

class EvaluationAnswer(models.Model):
    evaluation = models.ForeignKey(DelegateEvaluation, on_delete=models.CASCADE, related_name='answers')
    question_id = models.CharField(max_length=60)
    answer_data = JSONField(blank=True, null=True)

    class Meta:
        unique_together = ('evaluation', 'question_id')

    def __str__(self):
        return f"{self.evaluation} - {self.question_id}"
