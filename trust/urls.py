from django.urls import path

from . import views

app_name = "trust"   # accounts / blood_requests / trust / organs / banks

urlpatterns = [
    path("request/<int:donor_id>/", views.request_contact, name="request_contact"),
    path("requests/", views.my_requests, name="my_requests"),
    path("requests/<int:request_id>/accept/", views.respond_to_request,
         {"decision": "accepted"}, name="accept_request"),
    path("requests/<int:request_id>/decline/", views.respond_to_request,
         {"decision": "declined"}, name="decline_request"),
]