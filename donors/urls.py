from django.urls import path

from . import views

app_name = "donors"

urlpatterns = [
    path("profile/", views.edit_profile, name="edit_profile"),
    path("profile/pause/", views.toggle_pause, name="toggle_pause"),
]