# from django.urls import path

# from .views import *
# from .views_excel import (
#     TemplateExportExcel,
#     SalesExportExcel,
#     OrdersExportExcel,
#     UserTargetMonthExcel,
# )
# from .api.urls import urlpatterns as api_urlpatterns

# urlpatterns = [
#     path(
#         "users-with-target-month/",
#         UsersWithTargetMonth.as_view(),
#         name="users_with_target_month",
#     ),
#     # HTML Pages
#     path("target", target, name="target"),
#     path("target/front/", target_front.as_view(), name="target_front"),
#     # HTML Reports
#     path("target_user/", target_front.as_view(), name="taruser"),
#     path("print-sales/<int:id>", sales_report, name="client_print_target"),
#     path("print-target/", target_report, name="target_report"),
#     path("print-target-details/", target_report_details, name="target_report_details"),
#     # Excel Files
#     path("sales/export-excel/", SalesExportExcel.as_view(), name="sales_export_excel"),
#     path(
#         "orders/export-excel/", OrdersExportExcel.as_view(), name="orders_export_excel"
#     ),
#     path(
#         "orders/user-target-month-excel/",
#         UserTargetMonthExcel.as_view(),
#         name="user_target_months_excel",
#     ),
#     path(
#         "template-export-excel/",
#         TemplateExportExcel.as_view(),
#         name="template_export_excel",
#     ),
#     # PRINT
#     path(
#         "usertargetmonth/<int:id>/print/",
#         user_target_month_print,
#         name="usertargetmonth_print",
#     ),
# ]

# # Appending API URLs
# urlpatterns += api_urlpatterns
from django.urls import path

from .views import *
from .views_excel import (
    TemplateExportExcel,
    SalesExportExcel,
    OrdersExportExcel,
    UserTargetMonthExcel,
)
from .api.urls import urlpatterns as api_urlpatterns

urlpatterns = [
    path(
        "users-with-target-month/",
        UsersWithTargetMonth.as_view(),
        name="users_with_target_month",
    ),
    # HTML Pages
    path("target", target, name="target"),
    path("target/front/", target_front, name="target_front"),
    #path("target/front/deux", target_front_2, name="target_front_2"),
    path("target_user/", taruser.as_view(), name="taruser"),
    # HTML Reports
    path("print-sales/<int:id>", sales_report, name="client_print_target"),
    path("print-target/", target_report, name="target_report"),
    path("print-target-details/", target_report_details, name="target_report_details"),
    # Excel Files
    path("sales/export-excel/", SalesExportExcel.as_view(), name="sales_export_excel"),
    path(
        "orders/export-excel/", OrdersExportExcel.as_view(), name="orders_export_excel"
    ),
    path(
        "orders/user-target-month-excel/",
        UserTargetMonthExcel.as_view(),
        name="user_target_months_excel",
    ),
    path(
        "template-export-excel/",
        TemplateExportExcel.as_view(),
        name="template_export_excel",
    ),
    # PRINT
    path(
        "usertargetmonth/<int:id>/print/",
        user_target_month_print,
        name="usertargetmonth_print",
    ),
]

# Appending API URLs
urlpatterns += api_urlpatterns


