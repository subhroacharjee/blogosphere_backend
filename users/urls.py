from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from users.views import ProfileView, UserLoginView, UserRegisterView


urlpatterns = [
    path("login/", UserLoginView.as_view(), name="login"),
    path("register/", UserRegisterView.as_view(), name="register"),
    path("", ProfileView.as_view(), name="profile"),
    path("refresh/", TokenRefreshView.as_view(), name="refresh"),
]
