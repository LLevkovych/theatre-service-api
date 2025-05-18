from django.urls import path
from user.views import (
    RegisterView,
    ProfileView,
    ChangePasswordView, LogoutView
)


app_name = "user"

urlpatterns = [
    path(
        "register/",
        RegisterView.as_view(),
        name="register"
    ),
    path(
        "me/",
        ProfileView.as_view(),
        name="profile"
    ),
    path(
        "change-password/",
        ChangePasswordView.as_view(),
        name="change-password"
    ),
    path(
        "logout/",
        LogoutView.as_view(),
        name="logout"
    ),
]
