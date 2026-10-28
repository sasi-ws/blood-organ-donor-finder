from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("donors/", include("donors.urls")),
    path("requests/", include("blood_requests.urls")),
    path("trust/", include("trust.urls")),
    path("organs/", include("organs.urls")),
    path("banks/", include("banks.urls")),
    path("", include("core.urls")),
]