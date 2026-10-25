from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from .compatibility import compatible_donor_groups, match_label

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

    return render(request, "donors/edit_profile.html", {"form": form, "profile": profile})


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

def search_donors(request):
    """Search donors by blood group and city. Open to everyone (no login)."""
    blood_group = request.GET.get("blood_group", "")
    city = request.GET.get("city", "").strip()
    searched = bool(blood_group and city)
    page_obj = None

    if searched:
        donors = list(DonorProfile.objects.filter(
            blood_group__in=compatible_donor_groups(blood_group),
            city__iexact=city,
            hide_profile=False,
            consent_given=True,
            user__is_active=True,
        ))
        for donor in donors:
            donor.match_label = match_label(blood_group, donor.blood_group)
        # Exact matches first, then verified donors, then by name
        donors.sort(key=lambda d: (d.match_label != "Exact match", not d.is_verified, d.full_name))
        paginator = Paginator(donors, 10)  # 10 per page
        page_obj = paginator.get_page(request.GET.get("page"))

    return render(request, "donors/search.html", {
        "blood_groups": [g for g, _ in BLOOD_GROUPS],
        "blood_group": blood_group,
        "city": city,
        "searched": searched,
        "page_obj": page_obj,
    })