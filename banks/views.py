
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Prefetch
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

from .models import BloodBank, StockLevel


def blood_bank_stock_board(request):
    search_query = request.GET.get("q", "").strip()
    selected_blood_group = request.GET.get("blood_group", "").strip()

    valid_blood_groups = dict(StockLevel.BLOOD_GROUP_CHOICES)

    stock_queryset = StockLevel.objects.order_by("blood_group")

    if selected_blood_group in valid_blood_groups:
        stock_queryset = stock_queryset.filter(
            blood_group=selected_blood_group
        )
    else:
        selected_blood_group = ""

    blood_banks = BloodBank.objects.all()

    if search_query:
        blood_banks = blood_banks.filter(
            name__icontains=search_query
        )

    if selected_blood_group:
        blood_banks = blood_banks.filter(
            stock_levels__blood_group=selected_blood_group
        ).distinct()

    blood_banks = blood_banks.prefetch_related(
        Prefetch(
            "stock_levels",
            queryset=stock_queryset,
        )
    ).order_by("name")

    return render(
        request,
        "banks/stock_board.html",
        {
            "blood_banks": blood_banks,
            "search_query": search_query,
            "selected_blood_group": selected_blood_group,
            "blood_group_choices": StockLevel.BLOOD_GROUP_CHOICES,
        },
    )


@login_required
def update_stock(request):
    if request.user.role != "bloodbank":
        return HttpResponseForbidden(
            "Only blood bank users can update stock."
        )

    bank = get_object_or_404(
        BloodBank,
        manager=request.user,
    )

    if request.method == "POST":
        stock_id = request.POST.get("stock_id")
        units = request.POST.get("units_available", "").strip()

        stock = get_object_or_404(
            StockLevel,
            pk=stock_id,
            blood_bank=bank,
        )

        try:
            units = int(units)
            if units < 0:
                raise ValueError
        except (ValueError, TypeError):
            return render(
                request,
                "banks/update_stock.html",
                {
                    "bank": bank,
                    "stocks": bank.stock_levels.all(),
                    "error": "Enter a valid non-negative number.",
                },
            )

        stock.units_available = units
        stock.save()

        return redirect("banks:update_stock")

    return render(
        request,
        "banks/update_stock.html",
        {
            "bank": bank,
            "stocks": bank.stock_levels.all(),
        },
    )
