import re
from datetime import date

from django import forms
from django.utils import timezone

from .models import DonorProfile

BLOOD_GROUPS = [(g, g) for g in ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]]
GENDERS = [("Female", "Female"), ("Male", "Male"), ("Other", "Other")]
DONOR_TYPES = [("blood", "Blood"), ("platelets", "Platelets"), ("both", "Both")]


def calculate_age(dob):
    """Work out age in years from date of birth."""
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))


class DonorProfileForm(forms.ModelForm):
    gender = forms.ChoiceField(choices=GENDERS)
    blood_group = forms.ChoiceField(choices=BLOOD_GROUPS)
    donor_type = forms.ChoiceField(choices=DONOR_TYPES, label="I can donate")

    # Self-declaration (FR-PRO-13). Not saved in the database, only checked.
    self_declaration = forms.BooleanField(
        required=True,
        label="I am aged 18 to 60, I weigh more than 50 kg, and I feel healthy. "
              "I understand the blood bank will screen me privately before any donation.",
        error_messages={"required": "Please tick the self-declaration box."},
    )

    class Meta:
        model = DonorProfile
        fields = [
            "full_name", "date_of_birth", "gender", "blood_group", "donor_type",
            "city", "district", "phone", "last_donation_date", "travel_city", "consent_given",
        ]
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
            "last_donation_date": forms.DateInput(attrs={"type": "date"}),
        }
        labels = {
            "consent_given": "I agree to be listed as a donor. I understand I can hide "
                             "or delete my profile at any time.",
            "travel_city": "Travel mode: temporary city (optional). Clear it to turn off.",
        }

    def clean_consent_given(self):
        consent = self.cleaned_data.get("consent_given")
        if not consent:
            raise forms.ValidationError("You must agree to be listed before saving.")
        return consent

    def clean_date_of_birth(self):
        dob = self.cleaned_data["date_of_birth"]
        if dob > date.today():
            raise forms.ValidationError("Date of birth cannot be in the future.")
        return dob

    def clean_last_donation_date(self):
        last = self.cleaned_data.get("last_donation_date")
        if last and last > date.today():
            raise forms.ValidationError("Last donation date cannot be in the future.")
        return last

    def clean_phone(self):
        phone = re.sub(r"[\s-]", "", self.cleaned_data["phone"])
        # Sri Lankan numbers: 0771110001 or +94771110001
        if not re.fullmatch(r"(\+94|0)\d{9}", phone):
            raise forms.ValidationError("Enter a valid phone number, e.g. 077 111 0001.")
        return phone

    def clean(self):
        cleaned = super().clean()
        dob = cleaned.get("date_of_birth")
        if dob:
            age = calculate_age(dob)
            first_time = not cleaned.get("last_donation_date")
            max_age = 55 if first_time else 60
            if age < 18 or age > max_age:
                self.add_error(
                    "date_of_birth",
                    f"Donors must be 18 to {max_age} years old"
                    + (" for a first donation." if first_time else "."),
                )
        return cleaned

    def save(self, commit=True):
        profile = super().save(commit=False)
        if not profile.consent_date:
            profile.consent_date = timezone.now()
        if commit:
            profile.save()
        return profile