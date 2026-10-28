from django.urls import path

from . import views

app_name = "donors"

urlpatterns = [
    path("profile/", views.edit_profile, name="edit_profile"),
    path("profile/pause/", views.toggle_pause, name="toggle_pause"),
    path("profile/available/", views.toggle_available, name="toggle_available"),
    path("search/", views.search_donors, name="search"),
    path("quiz/", views.eligibility_quiz, name="quiz"),
]