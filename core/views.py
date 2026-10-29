from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Q
from django.db.models.functions import TruncMonth
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from blood_requests.models import BloodRequest
from donors.models import DonorProfile
from .models import SiteSetting, is_dengue_mode

BLOOD_GROUPS = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]


def home(request):
    return render(request, "home.html")


def eligible_donors():
    """Visible donors outside the donation gap.
    TODO: replace with P2's eligibility function once it is merged (NFR-MNT-02)."""
    cutoff = timezone.localdate() - timedelta(days=settings.GAP_DAYS)
    return DonorProfile.objects.filter(hide_profile=False, user__is_active=True).filter(
        Q(last_donation_date__isnull=True) | Q(last_donation_date__lte=cutoff))


@staff_member_required
def dashboard(request):
    # Donors per blood group
    per_group = {r["blood_group"]: r["n"] for r in
                 DonorProfile.objects.values("blood_group").annotate(n=Count("id"))}

    # Requests per month (last 6 months)
    since = timezone.now() - timedelta(days=183)
    monthly = (BloodRequest.objects.filter(created_at__gte=since)
               .annotate(m=TruncMonth("created_at")).values("m")
               .annotate(n=Count("id")).order_by("m"))

    open_n = BloodRequest.objects.filter(status="open").count()
    done_n = BloodRequest.objects.filter(status="fulfilled").count()
    total_req = open_n + done_n
    fulfilled_pct = round(100 * done_n / total_req) if total_req else 0

    # Shortages: fewer than 3 eligible donors for a group in a city
    counts = {(r["city"], r["blood_group"]): r["n"] for r in
              eligible_donors().values("city", "blood_group").annotate(n=Count("id"))}
    rows = []
    for city in DonorProfile.objects.values_list("city", flat=True).distinct():
        for g in BLOOD_GROUPS:
            n = counts.get((city, g), 0)
            if n < 3:
                rows.append({"city": city, "group": g, "n": n,
                             "level": "Shortage" if n < 2 else "Low"})
    rows.sort(key=lambda r: (r["n"], r["city"]))

    chart_data = {
        "groups": BLOOD_GROUPS,
        "group_counts": [per_group.get(g, 0) for g in BLOOD_GROUPS],
        "months": [r["m"].strftime("%b") for r in monthly],
        "month_counts": [r["n"] for r in monthly],
    }
    return render(request, "dashboard.html", {
        "total_donors": DonorProfile.objects.count(),
        "verified_donors": DonorProfile.objects.filter(is_verified=True).count(),
        "open_n": open_n, "done_n": done_n, "fulfilled_pct": fulfilled_pct,
        "reports_to_review": 0,  # TODO: P3's Report model (FR-TRU-02)
        "shortages": rows[:6],
        "waiting": DonorProfile.objects.filter(is_verified=False, hide_profile=False)
                   .order_by("-id")[:5],
        "dengue_on": is_dengue_mode(),
        "chart_data": chart_data,
    })


@staff_member_required
@require_POST
def dashboard_verify(request, pk):
    donor = get_object_or_404(DonorProfile, pk=pk)
    donor.is_verified = True
    donor.save(update_fields=["is_verified"])
    messages.success(request, f"{donor.full_name} verified.")
    return redirect("core:dashboard")


@staff_member_required
@require_POST
def dashboard_reject(request, pk):
    donor = get_object_or_404(DonorProfile, pk=pk)
    donor.hide_profile = True
    donor.save(update_fields=["hide_profile"])
    messages.info(request, f"{donor.full_name} hidden from search.")
    return redirect("core:dashboard")


@staff_member_required
@require_POST
def dashboard_dengue(request):
    s, _ = SiteSetting.objects.get_or_create(key="dengue_mode")
    s.value = "off" if s.value == "on" else "on"
    s.save()
    return redirect("core:dashboard")