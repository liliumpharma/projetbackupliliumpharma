from django.urls import path
from . import views

urlpatterns = [
    path('submit/', views.submit_evaluation, name='submit_evaluation'),
    path('medical/', views.medical_evaluation_front, name='medical_evaluation_front'),
    path('commercial/', views.commercial_evaluation_front, name='commercial_evaluation_front'),
    path('landing/', views.landing_page_front, name='landing_page_front'),
    path('print/', views.print_evaluation, name='print_evaluation'),
    path('api/users/', views.evaluations_users_api, name='evaluations_users_api'),
    path('api/view_url/', views.evaluation_view_url_api, name='evaluation_view_url_api'),
    path('api/visits_per_user/', views.evaluations_visits_per_user_api, name='evaluations_visits_per_user_api'),
    path('api/visits_per_user_pharma_gro/', views.evaluations_visits_per_user_pharma_gro_api, name='evaluations_visits_per_user_pharma_gro_api'),
    path('api/visits_supergros/', views.evaluations_visits_supergros_api, name='evaluations_visits_supergros_api'),
    path('api/visits_more_than_once/', views.evaluations_visits_more_than_once_api, name='evaluations_visits_more_than_once_api'),
    path('api/doctors_not_visited/', views.evaluations_doctors_not_visited_api, name='evaluations_doctors_not_visited_api'),
    path('api/doctors_duo/', views.evaluations_doctors_visited_duo_api, name='evaluations_doctors_visited_duo_api'),
    path('api/get_user_products/', views.evaluations_get_user_products_api, name='evaluations_get_user_products_api'),
    path('api/orders_per_product/', views.evaluations_orders_per_product_api, name='evaluations_orders_per_product_api'),
    path('api/similarity/', views.SimilarityAPIView.as_view(), name='api_similarity'),
]
