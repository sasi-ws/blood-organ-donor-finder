from django.urls import path

from . import views

app_name = "blood_requests"

urlpatterns = [
    path("", views.request_list, name="request_list"),
    path("post/", views.post_request, name="post_request"),
    path("<int:pk>/fulfilled/", views.mark_fulfilled, name="mark_fulfilled"),
    path("<int:pk>/help/", views.offer_help, name="offer_help"),
    path("<int:pk>/offers/", views.offers_received, name="offers_received"),
    path("<int:pk>/cancel/", views.cancel_offer, name="cancel_offer"),
    path("<int:pk>/offers/<int:response_id>/done/", views.donation_done, name="donation_done"),
    path("notifications/", views.notification_list, name="notification_list"),
]