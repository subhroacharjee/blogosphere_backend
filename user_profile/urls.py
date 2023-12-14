from django.urls import path

from user_profile.views import (
    BlockListPreviewView,
    CurrentProfileView,
    ToggleBlockProfileView,
    UserProfileSearchView,
    UserProfileToggleFollowView,
    UserProfileView,
)


urlpatterns = [
    path(
        "",
        CurrentProfileView.as_view(),
        name="profile",
    ),
    path(
        "search/",
        UserProfileSearchView.as_view(),
        name="user_search",
    ),
    path(
        "block/",
        BlockListPreviewView.as_view(),
        name="user_block_list",
    ),
    path(
        "view/<slug:slug>/",
        UserProfileView.as_view(),
        name="user_profile",
    ),
    path(
        "follow/<slug:slug>/",
        UserProfileToggleFollowView.as_view(),
        name="user_profile_follow",
    ),
    path(
        "block/<slug:slug>/",
        ToggleBlockProfileView.as_view(),
        name="user_profile_block",
    ),
]
