from django.urls import path

from . import views

app_name = "blood_requests"

urlpatterns = [
    path("", views.request_list, name="request_list"),
    path("post/", views.post_request, name="post_request"),
    path("<int:pk>/fulfilled/", views.mark_fulfilled, name="mark_fulfilled"),
]