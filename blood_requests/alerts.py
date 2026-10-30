from django.core.mail import send_mail
from django.urls import reverse

from donors.compatibility import compatible_donor_groups
from donors.eligibility import days_until_eligible
from donors.models import DonorProfile

from .models import Notification


def eligible_donors(blood_request, stage=1):
    """Donors who can safely help and are allowed to be alerted.

    stage 1 = same city. Stage 3 = whole district.
    (Stage 2, nearby cities, comes later with the escalation task.)
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

    result = []
    for profile in profiles:
        # Donors inside the donation gap are never alerted.
        if days_until_eligible(profile.last_donation_date, profile.donor_type) > 0:
            continue
        if stage <= 1:
            if profile.current_city.strip().lower() != blood_request.city.strip().lower():
                continue
        elif profile.district.strip().lower() != blood_request.district.strip().lower():
            continue
        result.append(profile)
    return result


def send_alerts(blood_request, stage=1):
    """Create one Notification per eligible donor. Returns how many were alerted."""
    donors = eligible_donors(blood_request, stage)
    for profile in donors:
        message = (
            f"{blood_request.get_urgency_display()}: {blood_request.blood_group} "
            f"{blood_request.get_blood_type_display().lower()} needed at "
            f"{blood_request.hospital}, {blood_request.city}."
        )
        Notification.objects.create(
            user=profile.user,
            message=message,
            link=reverse("blood_requests:request_list"),
        )

        # Console email for urgent and critical requests (FR-NOT-03).
        if blood_request.urgency in ("urgent", "critical") and profile.user.email:
            send_mail(
                subject=f"{blood_request.get_urgency_display()} blood request near you",
                message=message + "\n\nLog in to Donor Finder to respond.",
                from_email=None,
                recipient_list=[profile.user.email],
                fail_silently=True,
            )
    return len(donors)