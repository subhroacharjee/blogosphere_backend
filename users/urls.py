from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from users.views import (
    ProfileView,
    UserActivationView,
    UserLoginView,
    UserRegisterView,
    UserResendActivationView,
)


urlpatterns = [
    path("login/", UserLoginView.as_view(), name="login"),
    path("register/", UserRegisterView.as_view(), name="register"),
    path("activate/", UserActivationView.as_view(), name="activate_user"),
    path("", ProfileView.as_view(), name="profile"),
    path("refresh/", TokenRefreshView.as_view(), name="refresh"),
    path("activate/again/", UserResendActivationView.as_view(), name="refresh_again"),
]
