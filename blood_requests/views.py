from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Case, Count, IntegerField, Q, Value, When
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .alerts import send_alerts
from .forms import BloodRequestForm
from .models import BloodRequest
from .models import BloodRequest, Notification

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
    cutoff = timezone.now() - timedelta(hours=48)  # auto-expiry
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
    return render(request, "blood_requests/request_list.html", {"open_requests": open_requests})


@login_required
@require_POST
def mark_fulfilled(request, pk):
    # Only the person who posted the request can close it.
    blood_request = get_object_or_404(BloodRequest, pk=pk, requester=request.user)
    blood_request.status = "fulfilled"
    blood_request.save()
    messages.success(request, "Request marked as fulfilled. Thank you!")
    return redirect("blood_requests:request_list")


@login_required
def notification_list(request):
    notes = list(Notification.objects.filter(user=request.user).order_by("-created_at")[:50])
    # Mark as read after we built the list, so new ones still show as "new" this time.
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return render(request, "blood_requests/notification_list.html", {"notifications": notes})