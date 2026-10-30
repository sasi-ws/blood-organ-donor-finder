from donors.compatibility import compatible_donor_groups
from donors.eligibility import days_until_eligible


def check_can_offer(user, blood_request):
    """Return (profile, error). error is None when the donor may offer help."""
    profile = getattr(user, "donorprofile", None)
    if profile is None:
        return None, "Register as a donor to help."
    if blood_request.requester_id == user.id:
        return profile, "You cannot offer help on your own request."
    if profile.hide_profile or not profile.consent_given or not user.is_active:
        return profile, "Your profile is hidden or inactive, so you cannot offer help right now."
    if profile.blood_group not in compatible_donor_groups(blood_request.blood_group):
        return profile, "Your blood group cannot be given to this patient."
    if blood_request.blood_type == "platelets" and profile.donor_type not in ("platelets", "both"):
        return profile, "This request needs platelets, and your profile is set to whole blood only."
    if blood_request.blood_type == "whole" and profile.donor_type not in ("blood", "both"):
        return profile, "This request needs whole blood, and your profile is set to platelets only."
    days = days_until_eligible(profile.last_donation_date, profile.donor_type)
    if days > 0:
        return profile, f"You can donate again in {days} days, so you cannot offer help yet."
    return profile, None