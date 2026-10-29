from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from datetime import timedelta
from django.utils import timezone
from donors.models import DonorProfile

from .forms import ContactRequestForm
from .models import ContactRequest

DAILY_REQUEST_LIMIT = 10  # FR-CON-04: one place to change the limit
@login_required  # visitors who are not logged in are sent to the login page (FR-SRC-09)
def request_contact(request, donor_id):
    """A seeker writes a message and asks one donor for contact (FR-CON-01)."""
    donor = get_object_or_404(
        DonorProfile,
        pk=donor_id,
        hide_profile=False,
        consent_given=True,
        user__is_active=True,
    )

    # Only seekers can send requests, and nobody can ask themselves
    if request.user.role != "seeker":
        messages.error(request, "Only seeker accounts can request contact.")
        return redirect("donors:search")
    if donor.user == request.user:
        messages.error(request, "You can't send a request to yourself.")
        return redirect("donors:search")
    # Rate limit: at most 10 requests in the last 24 hours (FR-CON-04)
    sent_today = ContactRequest.objects.filter(
        seeker=request.user,
        created_at__gte=timezone.now() - timedelta(days=1),
    ).count()
    if sent_today >= DAILY_REQUEST_LIMIT:
        messages.error(request, f"You can send at most {DAILY_REQUEST_LIMIT} requests per day. Please try again tomorrow.")
        return redirect("donors:search")
    # Don't allow a second pending request to the same donor
    already_pending = ContactRequest.objects.filter(
        seeker=request.user, donor=donor, status="pending"
    ).exists()
    if already_pending:
        messages.info(request, "You already sent this donor a request. Please wait for their reply.")
        return redirect("donors:search")

    if request.method == "POST":
        form = ContactRequestForm(request.POST)
        if form.is_valid():
            contact = form.save(commit=False)
            contact.seeker = request.user
            contact.donor = donor
            contact.save()
            messages.success(request, "Your request was sent. The donor will see it on their dashboard.")
            return redirect("donors:search")
    else:
        form = ContactRequestForm()

    return render(request, "trust/request_contact.html", {"form": form, "donor": donor})

@login_required
def my_requests(request):
    """The donor sees contact requests sent to them (FR-CON-02)."""
    profile = DonorProfile.objects.filter(user=request.user).first()
    if profile is None:
        messages.error(request, "Please create your donor profile first.")
        return redirect("donors:edit_profile")

    all_requests = ContactRequest.objects.filter(donor=profile).select_related("seeker")
    return render(request, "trust/my_requests.html", {
        "pending": all_requests.filter(status="pending"),
        "answered": all_requests.exclude(status="pending"),
    })


@login_required
@require_POST  # changing data must never happen through a plain link
def respond_to_request(request, request_id, decision):
    """The donor accepts or declines one request."""
    # donor__user=request.user means a donor can only answer requests sent to THEM
    contact = get_object_or_404(ContactRequest, pk=request_id, donor__user=request.user)

    if contact.status != "pending":
        messages.info(request, "You already answered this request.")
        return redirect("trust:my_requests")

    contact.status = decision  # "accepted" or "declined"
    contact.save()

    if decision == "accepted":
        messages.success(request, "You accepted the request.")
    else:
        messages.success(request, "You declined the request.")
    return redirect("trust:my_requests")
@login_required
def sent_requests(request):
    """The seeker sees their own requests. The phone shows only if accepted (FR-CON-03)."""
    # seeker=request.user means nobody can see another person's requests
    my_sent = ContactRequest.objects.filter(seeker=request.user).select_related("donor")
    return render(request, "trust/sent_requests.html", {"requests_sent": my_sent})