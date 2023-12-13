from django.urls import path

from user_profile.views import (
    CurrentProfileView,
    UserProfileSearchView,
    UserProfileView,
)


urlpatterns = [
    path("", CurrentProfileView.as_view(), name="profile"),
    path("search/", UserProfileSearchView.as_view(), name="user_search"),
    path("view/<slug:slug>/", UserProfileView.as_view(), name="user_profile"),
]
