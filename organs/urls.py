
from django.urls import path
from . import views

app_name = "organs"

urlpatterns = [
    path(
        "pledge-info/",
        views.organ_pledge_info,
        name="organ_pledge_info",
    ),
    path(
        "pledge/",
        views.organ_pledge_view,
        name="organ_pledge",
    ),
    path(
        "pledge/edit/",
        views.edit_organ_pledge,
        name="edit_organ_pledge",
    ),
    path(
        "pledge/withdraw/",
        views.withdraw_organ_pledge,
        name="withdraw_organ_pledge",
    ),
    path(
        "pledge/success/",
        views.organ_pledge_success,
        name="organ_pledge_success",
    ),

    path(
    "talk-to-family/",
    views.talk_to_family,
    name="talk_to_family",
),
]
