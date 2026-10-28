
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from .models import OrganPledge


def organ_pledge_info(request):
    return render(request, "organs/organ_pledge_info.html")


@login_required
def organ_pledge_view(request):
    if request.method == "POST":
        organs = request.POST.getlist("organs")
        family_contact_name = request.POST.get("family_contact_name", "").strip()
        family_contact_email = request.POST.get("family_contact_email", "").strip()
        consent_given = request.POST.get("consent_given") == "on"

        if organs and family_contact_name and family_contact_email and consent_given:
            OrganPledge.objects.update_or_create(
                user=request.user,
                defaults={
                    "organs": organs,
                    "family_contact_name": family_contact_name,
                    "family_contact_email": family_contact_email,
                    "consent_given": consent_given,
                },
            )

            send_mail(
                subject="Organ Pledge Information",
                message=(
                    f"Dear {family_contact_name},\n\n"
                    f"{request.user.username} has recorded an intention "
                    "to pledge the following organs or tissues: "
                    f"{', '.join(organs)}.\n\n"
                    "This records an intention only. It does not confirm "
                    "medical eligibility or guarantee that donation will occur. "
                    "Please discuss their wishes together.\n"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[family_contact_email],
                fail_silently=False,
            )

            return redirect("organs:organ_pledge_success")

        return render(request, "organs/organ_pledge.html", {
            "error": "Ella details-um fill panni consent kudunga.",
            "selected_organs": organs,
        })

    return render(request, "organs/organ_pledge.html")


@login_required
def organ_pledge_success(request):
    return render(request, "organs/organ_pledge_success.html")
