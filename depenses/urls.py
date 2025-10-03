from django.urls import path,re_path,include
from .views import *

urlpatterns = [
    path("/", depenses_front, name="depenses_front"),
    path("spends/", get_spends.as_view(), name="spends"),
    path('api/confirm_spend/<int:spend_id>/', ConfirmSpend.as_view(), name='confirm_spend'),    
    path('api/AddSpend', AddSpend.as_view(), name='AddSpend'),  
    path('api/AddSpendComment', AddSpendComment.as_view(), name='AddSpendComment'),
    path('api/GetSpendComment/', GetSpendComment.as_view(), name='GetSpendComment'),
    path('printSpend/<int:id>/', SpendPDF.as_view(), name='SpendPDF'),
    path('getting_users_under/', getting_users_under.as_view(), name='getting_users_under'),
    path('print/', print_spend.as_view(), name='print_spend'),

    # Excel
    path('export/excel',AllExportExcel.as_view(),name="AllDepensesExportExcel"),
]
