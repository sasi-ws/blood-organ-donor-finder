from datetime import date, timedelta

from django.conf import settings


def gap_days(donor_type):
    """Gap in days. Platelet donors use their own setting; blood and both use GAP_DAYS."""
    if donor_type == "platelets":
        return settings.PLATELET_GAP_DAYS
    return settings.GAP_DAYS


def next_eligible_date(last_donation_date, donor_type="blood"):
    """next_eligible_date = last_donation_date + GAP_DAYS (None if never donated)."""
    if not last_donation_date:
        return None
    return last_donation_date + timedelta(days=gap_days(donor_type))


def days_until_eligible(last_donation_date, donor_type="blood", today=None):
    """Days left until the donor can donate again. 0 means eligible now."""
    today = today or date.today()
    next_date = next_eligible_date(last_donation_date, donor_type)
    if next_date is None or next_date <= today:
        return 0
    return (next_date - today).days