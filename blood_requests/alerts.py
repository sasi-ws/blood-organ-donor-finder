from datetime import timedelta

from django.core.mail import send_mail
from django.urls import reverse
from django.utils import timezone

from donors.compatibility import compatible_donor_groups
from donors.eligibility import days_until_eligible
from donors.models import DonorProfile

from .models import Notification
from .nearby import nearby_cities


def eligible_donors(blood_request, stage=1):
    """Donors who can safely help and are allowed to be alerted.

    stage 1 = same city, stage 2 = same or nearby cities, stage 3 = whole district.
    """
    groups = compatible_donor_groups(blood_request.blood_group)
    if blood_request.blood_type == "platelets":
        wanted_types = ["platelets", "both"]
    else:
        wanted_types = ["blood", "both"]

    profiles = (
        DonorProfile.objects.select_related("user")
        .filter(
            blood_group__in=groups,
            donor_type__in=wanted_types,
            hide_profile=False,
            consent_given=True,
            user__is_active=True,
        )
        .exclude(user=blood_request.requester)
    )

    request_city = blood_request.city.strip().lower()
    request_district = blood_request.district.strip().lower()

    result = []
    for profile in profiles:
        # Donors inside the donation gap are never alerted.
        if days_until_eligible(profile.last_donation_date, profile.donor_type) > 0:
            continue

        donor_city = profile.current_city.strip().lower()
        if stage <= 1:
            if donor_city != request_city:
                continue
        elif stage == 2:
            if donor_city != request_city and donor_city not in nearby_cities(request_city):
                continue
        else:
            if profile.district.strip().lower() != request_district:
                continue
        result.append(profile)
    return result


def notify(blood_request, profile):
    """Create the in-app notification and the console email for one donor."""
    message = (
        f"{blood_request.get_urgency_display()}: {blood_request.blood_group} "
        f"{blood_request.get_blood_type_display().lower()} needed at "
        f"{blood_request.hospital}, {blood_request.city}. (#{blood_request.pk})"
    )
    Notification.objects.create(
        user=profile.user,
        message=message,
        link=reverse("blood_requests:request_list"),
    )
    if blood_request.urgency in ("urgent", "critical") and profile.user.email:
        send_mail(
            subject=f"{blood_request.get_urgency_display()} blood request near you",
            message=message + "\n\nLog in to Donor Finder to respond.",
            from_email=None,
            recipient_list=[profile.user.email],
            fail_silently=True,
        )


def send_alerts(blood_request, stage=1):
    """Alert every eligible donor for this stage. Returns how many were alerted."""
    donors = eligible_donors(blood_request, stage)
    for profile in donors:
        notify(blood_request, profile)
    return len(donors)


def current_stage(blood_request):
    """0-15 min = stage 1, 15-30 min = stage 2, 30+ min = stage 3 (BR-08)."""
    age = timezone.now() - blood_request.created_at
    if age < timedelta(minutes=15):
        return 1
    if age < timedelta(minutes=30):
        return 2
    return 3


def escalate_if_needed(blood_request):
    """Alert the next ring of donors if the request moved to a new stage
    and nobody has offered help yet. Donors already alerted are skipped."""
    stage = current_stage(blood_request)
    if blood_request.status != "open" or stage <= blood_request.alert_stage:
        return 0
    if blood_request.responses.filter(can_help=True).exists():
        return 0

    already = set(
        Notification.objects.filter(message__contains=f"(#{blood_request.pk})")
        .values_list("user_id", flat=True)
    )
    count = 0
    for profile in eligible_donors(blood_request, stage):
        if profile.user_id in already:
            continue
        notify(blood_request, profile)
        count += 1

    blood_request.alert_stage = stage
    blood_request.save(update_fields=["alert_stage"])
    return count