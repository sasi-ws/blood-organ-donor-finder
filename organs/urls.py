
from django.urls import path
from . import views

app_name = "organs"

urlpatterns = [
    path("pledge-info/", views.organ_pledge_info, name="organ_pledge_info"),
    path("pledge/", views.organ_pledge_view, name="organ_pledge"),
    path("pledge/success/", views.organ_pledge_success, name="organ_pledge_success"),
]
