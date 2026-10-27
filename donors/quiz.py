from .eligibility import days_until_eligible


def check_quiz(age, weight_kg, last_donation_date, feeling_ill, travelled_abroad, recent_tattoo, today=None):
    """Return a list of general notes. An empty list means no problem was found."""
    notes = []

    max_age = 55 if last_donation_date is None else 60
    if age < 18 or age > max_age:
        notes.append(f"Donors are usually aged 18 to {max_age}.")
    if weight_kg <= 50:
        notes.append("Donors usually weigh more than 50 kg.")

    days_left = days_until_eligible(last_donation_date, "blood", today)
    if days_left > 0:
        notes.append(f"You usually need to wait between donations. About {days_left} more days.")

    if feeling_ill:
        notes.append("Please wait until you feel well.")
    if travelled_abroad:
        notes.append("Returning from abroad less than 3 months ago usually means a wait.")
    if recent_tattoo:
        notes.append("A recent tattoo or piercing usually means a wait.")

    return notes