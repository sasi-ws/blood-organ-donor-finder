from django.urls import path

from . import views

app_name = "trust"   # accounts / blood_requests / trust / organs / banks

urlpatterns = [
    path("request/<int:donor_id>/", views.request_contact, name="request_contact"),
]