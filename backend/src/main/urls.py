from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from health_check import Database, Storage
from health_check.views import HealthCheckView

from api import urls as api_urls

urlpatterns = [
    path(
        "health/",
        HealthCheckView.as_view(checks=(Database, Storage)),
        name="health_check",
    ),
    # OpenAPI Schema
    path("api/schema/swagger-ui/", SpectacularSwaggerView.as_view(url_name="schema")),
    path("api/schema/redoc/", SpectacularRedocView.as_view(url_name="schema")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    # API
    path("api/", include(api_urls)),
    # Admin
    path("djadmin/", admin.site.urls),
    # Headless Account API
    path("api/auth/", include("allauth.headless.urls")),
    # Accounts
    path("account/", include("allauth.urls")),
    # OIDC
    path("", include("allauth.idp.urls")),
    # Hijack
    path("hijack/", include("hijack.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
