from django.urls import path, re_path, include

from .views import *

urlpatterns = [
    path("api/", PlanAPI.as_view(), name="PlanAPI"),
    path("api/validate/", PlanValidateAPI.as_view(), name="PlanValidateAPI"),
    path(
        "api/validate/request/",
        RequestPlanValidateAPI.as_view(),
        name="RequestPlanValidateAPI",
    ),
    path("api/comment/", PlanCommentAPI.as_view(), name="PlanCommentAPI"),
    path(
        "api/tasks/permute/", PlanTasksPermuteAPI.as_view(), name="PlanTasksPermuteAPI"
    ),
    path("api/tasks/", PlanTasksAPI.as_view(), name="PlanTasksAPI"),
    path("PDF/", PlanPDF, name="PlanPDF"),
    path("PDF/<int:id>", SinglePlanPDF, name="SinglePlanPDF"),
    #path("mServices/monthly_planning/", MsMonthlyPlanning, name="MsMonthlyPlanning"),
]

from django.urls import path, re_path, include

from .views import *

urlpatterns = [
    path("api/", PlanAPI.as_view(), name="PlanAPI"),
    path("api/validate/", PlanValidateAPI.as_view(), name="PlanValidateAPI"),
    path(
        "api/validate/request/",
        RequestPlanValidateAPI.as_view(),
        name="RequestPlanValidateAPI",
    ),
    path("api/comment/", PlanCommentAPI.as_view(), name="PlanCommentAPI"),
    path(
        "api/tasks/permute/", PlanTasksPermuteAPI.as_view(), name="PlanTasksPermuteAPI"
    ),
    path("api/tasks/", PlanTasksAPI.as_view(), name="PlanTasksAPI"),
    path("PDF/", PlanPDF, name="PlanPDF"),
    path("PDF/<int:id>", SinglePlanPDF, name="SinglePlanPDF"),
    path("mServices/monthly_planning/", MsMonthlyPlanning, name="MsMonthlyPlanning"),
]

