from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db.models import Case, Count, IntegerField, Q, Value, When
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from .alerts import send_alerts
from .forms import BloodRequestForm
from .models import BloodRequest, DonorResponse, Notification
from .offers import check_can_offer


@login_required
def post_request(request):
    if request.method == "POST":
        form = BloodRequestForm(request.POST)
        if form.is_valid():
            blood_request = form.save(commit=False)
            blood_request.requester = request.user
            blood_request.save()
            count = send_alerts(blood_request)
            messages.success(request, f"Your request was posted. {count} donor(s) alerted.")
            return redirect("blood_requests:request_list")
    else:
        form = BloodRequestForm(initial={"urgency": "normal"})
    return render(request, "blood_requests/post_request.html", {"form": form})


def request_list(request):
    """Open requests: critical first, then urgent, then normal, then newest."""
    cutoff = timezone.now() - timedelta(hours=48)
    open_requests = (
        BloodRequest.objects.filter(status="open", created_at__gte=cutoff)
        .annotate(
            urgency_rank=Case(
                When(urgency="critical", then=Value(0)),
                When(urgency="urgent", then=Value(1)),
                default=Value(2),
                output_field=IntegerField(),
            ),
            accepted=Count("responses", filter=Q(responses__can_help=True)),
        )
        .order_by("urgency_rank", "-created_at")
    )
    offered_ids = set()
    if request.user.is_authenticated:
        offered_ids = set(
            DonorResponse.objects.filter(donor=request.user, can_help=True)
            .values_list("request_id", flat=True)
        )
    return render(
        request,
        "blood_requests/request_list.html",
        {"open_requests": open_requests, "offered_ids": offered_ids},
    )


@login_required
@require_POST
def mark_fulfilled(request, pk):
    blood_request = get_object_or_404(BloodRequest, pk=pk, requester=request.user)
    blood_request.status = "fulfilled"
    blood_request.save()
    messages.success(request, "Request marked as fulfilled. Thank you!")
    return redirect("blood_requests:request_list")


@login_required
def notification_list(request):
    notes = list(Notification.objects.filter(user=request.user).order_by("-created_at")[:50])
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return render(request, "blood_requests/notification_list.html", {"notifications": notes})


@login_required
def offer_help(request, pk):
    """Confirmation screen for 'I can help'."""
    blood_request = get_object_or_404(BloodRequest, pk=pk, status="open")
    profile, error = check_can_offer(request.user, blood_request)
    if error:
        messages.error(request, error)
        return redirect("blood_requests:request_list")

    already = DonorResponse.objects.filter(
        request=blood_request, donor=request.user, can_help=True
    ).exists()

    if request.method == "POST":
        if not already:
            DonorResponse.objects.update_or_create(
                request=blood_request, donor=request.user, defaults={"can_help": True}
            )
            message = (
                f"A donor can help with your {blood_request.blood_group} request "
                f"at {blood_request.hospital}."
            )
            Notification.objects.create(
                user=blood_request.requester,
                message=message,
                link=reverse("blood_requests:offers_received", args=[blood_request.pk]),
            )
            if blood_request.requester.email:
                send_mail(
                    subject="A donor can help with your blood request",
                    message=message,
                    from_email=None,
                    recipient_list=[blood_request.requester.email],
                    fail_silently=True,
                )
        messages.success(request, "Thank you! The requester has been told you can help.")
        return redirect("blood_requests:request_list")

    return render(
        request,
        "blood_requests/offer_help.html",
        {"r": blood_request, "profile": profile, "already": already},
    )


@login_required
def offers_received(request, pk):
    """Requester only: units covered, donor cards, phone numbers."""
    blood_request = get_object_or_404(BloodRequest, pk=pk, requester=request.user)
    responses = blood_request.responses.filter(can_help=True).select_related(
        "donor", "donor__donorprofile"
    )
    covered = responses.count()
    return render(
        request,
        "blood_requests/offers_received.html",
        {"r": blood_request, "responses": responses, "covered": covered},
    )


@login_required
@require_POST
def cancel_offer(request, pk):
    blood_request = get_object_or_404(BloodRequest, pk=pk)
    response = get_object_or_404(
        DonorResponse, request=blood_request, donor=request.user, can_help=True, donated=False
    )
    response.delete()
    if blood_request.status == "fulfilled":
        blood_request.status = "open"
        blood_request.save()
    Notification.objects.create(
        user=blood_request.requester,
        message=f"A donor cancelled their offer for your {blood_request.blood_group} request.",
        link=reverse("blood_requests:offers_received", args=[blood_request.pk]),
    )
    messages.success(request, "Your offer was cancelled.")
    return redirect("blood_requests:request_list")


@login_required
@require_POST
def donation_done(request, pk, response_id):
    blood_request = get_object_or_404(BloodRequest, pk=pk, requester=request.user)
    response = get_object_or_404(
        DonorResponse, pk=response_id, request=blood_request, can_help=True
    )
    if not response.donated:
        response.donated = True
        response.save()
        profile = response.donor.donorprofile
        profile.last_donation_date = date.today()
        profile.save()
        if blood_request.responses.filter(donated=True).count() >= blood_request.units:
            blood_request.status = "fulfilled"
            blood_request.save()
        messages.success(request, "Donation recorded. The donor is hidden until they can donate again.")
    return redirect("blood_requests:offers_received", pk=pk)