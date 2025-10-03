from django.contrib import admin
from django.urls import path, include, re_path
from . import views
from .export_excel import *
from .views import *

from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)
from .api.api import *

urlpatterns = [
    re_path(r"^$", views.HomeAccount.as_view(), name="account"),
    re_path(
        r"^login/", LoginView.as_view(template_name="accounts/login.html"), name="login"
    ),
    path("logout/", LogoutView.as_view(template_name="home.html"), name="logout"),
    # path('register/', views.Register.as_view(),name='register'),
    # path('profile/', views.Profile.as_view(),name='profile'),
    # path('activate/<str:username>/<str:activate>', views.ActivateAccount,name='activate_account'),
    # path('activate/form', views.ActivateAccountForm.as_view(),name='activate_account_form'),
    # re_path(r'^profile/edit', views.EditProfile.as_view(),name='edit_profile'),
    re_path(
        r"^profile/change-password$",
        views.ChangePassword.as_view(),
        name="change_password",
    ),
    re_path(
        r"^profile/reset-password$",
        PasswordResetView.as_view(template_name="accounts/password_reset_form.html"),
        name="password_reset",
    ),
    path(
        "profile/reset-password/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(
            template_name="accounts/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    re_path(
        r"^profile/reset-password/done",
        PasswordResetDoneView.as_view(
            template_name="accounts/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    re_path(
        r"^profile/reset-password/complete",
        PasswordResetCompleteView.as_view(
            template_name="accounts/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    path("all/", AllUsersApi.as_view(), name="AllUsersApi"),
    path("api/", UserProfileApi.as_view(), name="Usersapi"),
    path("api/admin", UserProfileAdminApi.as_view(), name="Usersapiadmin"),
    path("api/current", AccountApi.as_view(), name="AccountApi"),
    path("api/app/current", AccountAppApi.as_view(), name="AccountAppApi"),
    path("api/specialite/", SpecialiteApi.as_view(), name="UserSpecialitesapi"),
    path(
        "api/classifications/", ClassificationsApi.as_view(), name="ClassificationsApi"
    ),
    # path('api/edit/', EditProfileApi.as_view(),name='EditProfileApi'),
    # path('api/edit/user/', EditUserApi.as_view(),name='EditUserApi'),
    path(
        "transfer_task_users",
        TransferTaskUsersApi.as_view(),
        name="transfer task users",
    ),
    path("export_excel", AllExportExcel.as_view(), name="Export Excel"),
    path("checklist/", views.check_list_new_delegate, name="check_list_new_delegate"),
    path(
        "report_details/",
        views.get_monthly_report_details,
        name="get_monthly_report_details",
    ),
    path("families/", views.get_families, name="get_families"),
    path(
        "api/users-by-family/", UsersByFamilyAPIView.as_view(), name="users-by-family"
    ),
]
