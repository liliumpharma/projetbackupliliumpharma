from django.urls import path,re_path,include
from .views import *

urlpatterns = [
    path('count_medecins_visites_per_user/',CountMedecinsVisitesPerUser.as_view(),name="CountMedecinsVisitesPerUser" ),
    path('AddMonthlyEvaluation/',AddMonthlyEvaluation.as_view(),name="AddMonthlyEvaluation" ),
    path('get-monthly-evaluation/', MonthlyEvaluationView.as_view(), name='monthly_evaluation'),
    path('MonthlyEvaluationFrontSupToDirection/', MonthlyEvaluationFrontSupToDirection.as_view(), name='MonthlyEvaluationFrontSupToDirection'),


    # COMMERCIAL EVALUATION
    path('AddCommercialeMonthlyEvaluation/',AddCommercialeMonthlyEvaluation.as_view(),name="AddMonthlyEvaluation" ),

    #PRINT SECTION
    path('monthly_evaluations/<int:id>/', MEPDF.as_view(), name='pdf_view'),
    path('print_evaluation/', print_evaluation.as_view(), name='print_evaluation'),

    #SUPERVISOR EVALUATION
    path('AddMonthlyEvaluationSup/',AddMonthlyEvaluationSup.as_view(),name="AddMonthlyEvaluationSup" ),

    #SUPERVISOR EVALUATION TO DIRECTION
    path('AddMonthlyEvaluationSupToDirection/',AddMonthlyEvaluationSupToDirection.as_view(),name="AddMonthlyEvaluationSupToDirection" ),
    path('MonthlyEvaluationSupToDirectionView/',MonthlyEvaluationSupToDirectionView.as_view(),name="MonthlyEvaluationSupToDirectionView" ),
    path('monthly_evaluations_sup_to_direction/<int:id>/', MonthlyEvaluationSupToDirection.as_view(), name='get-monthly-evaluation-sup-to-direction'),


    #DIRECTION EVALUATION TO SUP
    path('AddMonthlyEvaluationDirectionToSup/',AddMonthlyEvaluationDirectionToSup.as_view(),name="AddMonthlyEvaluationDirectionToSup" ),
    path('DirectionToSup/',DirectionToSup.as_view(),name="DirectionToSup" ),
    path('AddMonthlyEvaluationDirectionToDelegate/',AddMonthlyEvaluationDir.as_view(),name="AddMonthlyEvaluationDir" ),




]
