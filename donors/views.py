from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .forms import DonorProfileForm
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