from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("awareness/", views.awareness, name="awareness"),
    path("staff/dashboard/", views.dashboard, name="dashboard"),
    path("staff/dashboard/verify/<int:pk>/", views.dashboard_verify, name="dashboard_verify"),
    path("staff/dashboard/reject/<int:pk>/", views.dashboard_reject, name="dashboard_reject"),
    path("staff/dashboard/dengue/", views.dashboard_dengue, name="dashboard_dengue"),
]