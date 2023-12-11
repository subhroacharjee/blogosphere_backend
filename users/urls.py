from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from users.views import (
    ProfileView,
    UserActivationView,
    UserChangePasswordView,
    UserForgotPasswordView,
    UserLoginView,
    UserRegisterView,
    UserResendActivationView,
    UserForgetPasswordVerifyView,
)


urlpatterns = [
    path("login/", UserLoginView.as_view(), name="login"),
    path("register/", UserRegisterView.as_view(), name="register"),
    path("activate/", UserActivationView.as_view(), name="activate_user"),
    path("", ProfileView.as_view(), name="profile"),
    path("refresh/", TokenRefreshView.as_view(), name="refresh"),
    path("activate/again/", UserResendActivationView.as_view(), name="refresh_again"),
    path("forget/", UserForgotPasswordView.as_view(), name="forget_password"),
    path(
        "forget/verify/",
        UserForgetPasswordVerifyView.as_view(),
        name="forget_password_verify",
    ),
    path("change/password/", UserChangePasswordView.as_view(), name="change_password"),
]
