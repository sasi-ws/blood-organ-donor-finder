
from django.urls import path
from . import views

app_name = "banks"

urlpatterns = [
    path(
        "",
        views.blood_bank_stock_board,
        name="stock_board",
    ),
    path(
        "update-stock/",
        views.update_stock,
        name="update_stock",
    ),
]
