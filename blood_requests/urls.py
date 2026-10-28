from django.urls import path

from . import views

app_name = "blood_requests"

urlpatterns = [
    path("post/", views.post_request, name="post_request"),
]