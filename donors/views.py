from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST
from datetime import timedelta

from django.utils import timezone
from django.db.models import Q

from .compatibility import compatible_donor_groups, match_label
from .eligibility import days_until_eligible, next_eligible_date
from .forms import BLOOD_GROUPS, DonorProfileForm
from .models import DonorProfile


@login_required
def edit_profile(request):
    """Create the donor profile, or edit it if it already exists."""
    profile = DonorProfile.objects.filter(user=request.user).first()

    if request.method == "POST":
        form = DonorProfileForm(request.POST, instance=profile)
        if form.is_valid():
            donor = form.save(commit=False)
            donor.user = request.user
            donor.save()
            messages.success(request, "Your profile has been saved.")
            return redirect("donors:edit_profile")
    else:
        form = DonorProfileForm(instance=profile)

    days_left = 0
    next_date = None
    if profile:
        days_left = days_until_eligible(profile.last_donation_date, profile.donor_type)
        next_date = next_eligible_date(profile.last_donation_date, profile.donor_type)

    return render(request, "donors/edit_profile.html", {
        "form": form,
        "profile": profile,
        "days_left": days_left,
        "next_date": next_date,
    })


@login_required
@require_POST
def toggle_pause(request):
    """'Pause my listing' switch: hides or shows the donor in search."""
    profile = DonorProfile.objects.filter(user=request.user).first()
    if profile is None:
        messages.error(request, "Please create your donor profile first.")
        return redirect("donors:edit_profile")

    profile.hide_profile = not profile.hide_profile
    profile.save()
    if profile.hide_profile:
        messages.success(request, "Your listing is paused. You are hidden from search.")
    else:
        messages.success(request, "Your listing is visible again.")
    return redirect("donors:edit_profile")

@login_required
@require_POST
def toggle_available(request):
    """'I can donate today' switch. Turns itself off after 24 hours."""
    profile = DonorProfile.objects.filter(user=request.user).first()
    if profile is None:
        messages.error(request, "Please create your donor profile first.")
        return redirect("donors:edit_profile")

    if profile.is_available_today:
        profile.available_until = None
        messages.success(request, "You are no longer marked as available today.")
    elif days_until_eligible(profile.last_donation_date, profile.donor_type) > 0:
        messages.error(request, "You are still inside your donation gap, so you can't mark yourself available.")
        return redirect("donors:edit_profile")
    else:
        profile.available_until = timezone.now() + timedelta(hours=24)
        messages.success(request, "You are marked available for the next 24 hours.")
    profile.save()
    return redirect("donors:edit_profile")


def search_donors(request):
    """Search donors by blood group and city. Open to everyone (no login)."""
    blood_group = request.GET.get("blood_group", "")
    city = request.GET.get("city", "").strip()
    available_today = request.GET.get("available_today") == "on"
    platelets = request.GET.get("platelets") == "on"
    verified_only = request.GET.get("verified_only") == "on"
    searched = bool(blood_group and city)
    page_obj = None

    if searched:
        donors = list(DonorProfile.objects.filter(
            Q(travel_city__iexact=city) | Q(city__iexact=city, travel_city=""),
            blood_group__in=compatible_donor_groups(blood_group),
            hide_profile=False,
            consent_given=True,
            user__is_active=True,
        ))
        # Hide donors who are still inside their donation gap
        donors = [d for d in donors if days_until_eligible(d.last_donation_date, d.donor_type) == 0]
        # Optional filters
        if available_today:
            donors = [d for d in donors if d.is_available_today]
        if platelets:
            donors = [d for d in donors if d.donor_type in ("platelets", "both")]
        if verified_only:
            donors = [d for d in donors if d.is_verified]
        for donor in donors:
            donor.match_label = match_label(blood_group, donor.blood_group)
        # Exact matches first, then verified, then available today, then by name
        donors.sort(key=lambda d: (
            d.match_label != "Exact match",
            not d.is_verified,
            not d.is_available_today,
            d.full_name,
        ))
        paginator = Paginator(donors, 10)  # 10 per page
        page_obj = paginator.get_page(request.GET.get("page"))

    # Keep the search settings when moving between pages
    params = request.GET.copy()
    params.pop("page", None)

    return render(request, "donors/search.html", {
        "blood_groups": [g for g, _ in BLOOD_GROUPS],
        "blood_group": blood_group,
        "city": city,
        "available_today": available_today,
        "platelets": platelets,
        "verified_only": verified_only,
        "searched": searched,
        "page_obj": page_obj,
        "query_string": params.urlencode(),
    })