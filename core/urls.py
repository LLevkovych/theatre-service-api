from debug_toolbar.toolbar import debug_toolbar_urls
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)

urlpatterns = [
    path(
        "admin/",
        admin.site.urls
    ),

    path(
        "api/v1/theatre/",
        include(("theatre.urls", "theatre"),
        namespace="theatre")
    ),

    path(
        "api/v1/user/",
        include(("user.urls", "user"),
        namespace="user")
    ),

    path(
        "api/v1/token/",
        TokenObtainPairView.as_view(),
        name="token_obtain_pair"
    ),

    path(
        "api/v1/token/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh"
    ),

    path("api/schema/",
         SpectacularAPIView.as_view(),
         name="schema"
    ),

    path(
        "api/docs/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui"
    ),

    path(
        "api/docs/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc"
    ),

] + debug_toolbar_urls()
