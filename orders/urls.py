from django.urls import path,re_path,include
from .views import *
from .export_excel import *

urlpatterns = [
    path('addorder/', addorder.as_view(), name='addorder'),
    path('app/api/',OrderAppAPI.as_view(),name="OrderAppAPI" ),
    path('app/api/v2/front/<int:id>',OrderFrontWebAPI.as_view(),name="OrderFrontWebAPI" ),
    path('app/api/v2/<int:id>',OrderSupervisor.as_view(),name="OrderSupervisor" ),
    path('app/api/v2/',OrderSupervisor.as_view(),name="OrderSupervisor" ),
    path('exits/app/api/v2/<int:id>',ExitOrderSupervisor.as_view(),name="ExitOrderSupervisor" ),
    path('exits/app/api/v2/',ExitOrderSupervisor.as_view(),name="ExitOrderSupervisor" ),
    path('api/',OrderAPI.as_view(),name="OrderAPI"),
    path('api/<int:id>',OrderAPI.as_view(),name="OrderAPI"),
    path('app/api/<int:id>',OrderAppAPI.as_view(),name="OrderAppPostAPI" ),
    path('<int:id>',OrderHTML.as_view(),name="OrderPDF" ),
    path('exits/app/api/',ExitOrderAppAPI.as_view(),name="ExitOrderAppAPI" ),
    path('exits/app/api/<int:id>',ExitOrderAppAPI.as_view(),name="ExitOrderAppPostAPI" ),
    path('exits/<int:id>',ExitOrderPDF.as_view(),name="ExitOrderPDF" ),
    path('exit_orders/<int:id>',ExitOrderPDF.as_view(),name="ExitOrderPDF" ),
    path("front/",MsOrders,name="MsOrders"),
    path("front/exits/",MsExitOrders,name="MsExitOrders"),
    path("share-to-user/<int:id>",ShareUser.as_view(),name="MsExitOrders"),
    path("ordersPerUserPerMonth",ordersPerUserPerMonth.as_view(),name="ordersPerUserPerMonth"),
    path('ordersRepport/<str:username>/<str:order_date>/', OrdersByUserAndDateView.as_view(), name='orders_by_user_and_date'),


    #EXCEL
    path("export_excel",AllExportExcel.as_view(), name="orderExportExcel" ),
    path("exit_orders_export_excel",AllExitOrdersExportExcel.as_view(), name="exitOrderExportExcel" ),
    path("EtatStockClientExcel",EtatStockClientExcel.as_view(), name="EtatStockClientExcel" ),
    path("export-excel", OrdersExportExcel.as_view(), name="orders_export_excel"),
]

