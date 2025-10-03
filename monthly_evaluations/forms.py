from django.forms import ModelForm
from .models import *

class MonthlyEvaluationModelForm(ModelForm):
    class Meta:
        model=Monthly_Evaluation
        fields = '__all__'
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.user_sup_evaluation = True
        if commit:
            instance.save()
        return instance
    

class Commercial_Monthly_EvaluationModelForm(ModelForm):
    class Meta:
        model=Commercial_Monthly_Evaluation
        fields = '__all__'
        
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.user_sup_evaluation = True
        if commit:
            instance.save()
        return instance
    
class SupMonthlyEvaluationModelForm(ModelForm):
    class Meta:
        model=SupEvaluation
        fields = '__all__'

class SupMonthlyEvaluationToDirectionModelForm(ModelForm):
    class Meta:
        model=SupEvaluationToDirection
        fields = '__all__'
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.sup_evaluate_direction = True
        if commit:
            instance.save()
        return instance

class DirectionEvaluationToSupModelForm(ModelForm):
    class Meta:
        model=DirectionEvaluationToSup
        fields = '__all__'


class DirectionToDelegateEvaluationModelForm(ModelForm):
    class Meta:
        model=DirectionToDelegateEvaluation
        fields = '__all__'
        