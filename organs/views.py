
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.http import require_POST

from .models import OrganPledge


def organ_pledge_info(request):
    return render(
        request,
        "organs/organ_pledge_info.html",
    )


def talk_to_family(request):
    return render(
        request,
        "organs/talk_to_family.html",
    )


@login_required
def organ_pledge_view(request):
    if request.method == "POST":
        organs = request.POST.getlist("organs")

        family_contact_name = request.POST.get(
            "family_contact_name", ""
        ).strip()

        family_contact_email = request.POST.get(
            "family_contact_email", ""
        ).strip()

        consent_given = request.POST.get("consent_given") == "on"

        if (
            organs
            and family_contact_name
            and family_contact_email
            and consent_given
        ):
            pledge, created = OrganPledge.objects.update_or_create(
                user=request.user,
                defaults={
                    "organs": organs,
                    "family_contact_name": family_contact_name,
                    "family_contact_email": family_contact_email,
                    "consent_given": consent_given,
                },
            )

            if created:
                try:
                    send_mail(
                        subject="Organ Pledge Information",
                        message=(
                            f"Dear {family_contact_name},\n\n"
                            f"{request.user.username} has recorded an "
                            "intention to pledge the following organs "
                            "or tissues: "
                            f"{', '.join(organs)}.\n\n"
                            "This records an intention only. It does not "
                            "confirm medical eligibility or guarantee "
                            "that donation will occur. Please discuss "
                            "their wishes together.\n"
                        ),
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[family_contact_email],
                        fail_silently=False,
                    )
                except Exception:
                    # The pledge remains saved if email delivery fails.
                    pass

            return redirect("organs:organ_pledge_success")

        return render(
            request,
            "organs/organ_pledge.html",
            {
                "error": (
                    "Please select at least one organ, fill in "
                    "all contact details, and give consent."
                ),
                "selected_organs": organs,
                "pledge": None,
                "organ_choices": OrganPledge.ORGAN_CHOICES,
            },
        )

    existing_pledge = OrganPledge.objects.filter(
        user=request.user
    ).first()

    if existing_pledge:
        return render(
            request,
            "organs/organ_pledge.html",
            {
                "pledge": existing_pledge,
                "selected_organs": existing_pledge.organs,
                "organ_choices": OrganPledge.ORGAN_CHOICES,
            },
        )

    return render(
        request,
        "organs/organ_pledge.html",
        {
            "pledge": None,
            "selected_organs": [],
            "organ_choices": OrganPledge.ORGAN_CHOICES,
        },
    )


@login_required
def edit_organ_pledge(request):
    pledge = get_object_or_404(
        OrganPledge,
        user=request.user,
    )

    if request.method == "POST":
        organs = request.POST.getlist("organs")

        family_contact_name = request.POST.get(
            "family_contact_name", ""
        ).strip()

        family_contact_email = request.POST.get(
            "family_contact_email", ""
        ).strip()

        consent_given = request.POST.get("consent_given") == "on"

        if (
            organs
            and family_contact_name
            and family_contact_email
            and consent_given
        ):
            pledge.organs = organs
            pledge.family_contact_name = family_contact_name
            pledge.family_contact_email = family_contact_email
            pledge.consent_given = consent_given
            pledge.save()

            return redirect("organs:organ_pledge_success")

        return render(
            request,
            "organs/organ_pledge.html",
            {
                "error": (
                    "Please select at least one organ, fill in "
                    "all contact details, and give consent."
                ),
                "selected_organs": organs,
                "pledge": pledge,
                "organ_choices": OrganPledge.ORGAN_CHOICES,
            },
        )

    return render(
        request,
        "organs/organ_pledge.html",
        {
            "pledge": pledge,
            "selected_organs": pledge.organs,
            "organ_choices": OrganPledge.ORGAN_CHOICES,
        },
    )


@login_required
@require_POST
def withdraw_organ_pledge(request):
    pledge = get_object_or_404(
        OrganPledge,
        user=request.user,
    )

    pledge.delete()

    return redirect("organs:organ_pledge_success")


@login_required
def organ_pledge_success(request):
    return render(
        request,
        "organs/organ_pledge_success.html",
    )
