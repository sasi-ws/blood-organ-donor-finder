from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import SeekerProfile, User, phone_validator

SEEKER_REQUIRED = ["full_name", "seeker_type", "phone", "city", "district"]


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(
        label="I am registering as",
        choices=[
            ("donor", "Donor"),
            ("seeker", "Seeker (patient, family, hospital staff)"),
        ],
    )

    # Seeker details: only required when role == "seeker" (checked in clean)
    full_name = forms.CharField(label="Full name", max_length=100, required=False)
    seeker_type = forms.ChoiceField(
        label="I am a",
        required=False,
        choices=[("", "Select...")] + SeekerProfile.TYPE_CHOICES,
    )
    hospital = forms.CharField(label="Hospital (optional)", max_length=120, required=False)
    phone = forms.CharField(
        label="Phone number",
        max_length=20,
        required=False,
        validators=[phone_validator],
        help_text="Only the admin can see this. Donors never see it.",
    )
    city = forms.CharField(label="City", max_length=60, required=False)
    district = forms.CharField(label="District", max_length=60, required=False)

    agree = forms.BooleanField(
        label="I will give accurate information, I will never ask a donor "
              "for money, and I have read the privacy policy."
    )

    class Meta:
        model = User
        fields = ("username", "email", "role")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs["class"] = "form-check-input"
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs["class"] = "form-select"
            else:
                field.widget.attrs["class"] = "form-control"

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("role") == "seeker":
            for name in SEEKER_REQUIRED:
                if not cleaned.get(name):
                    self.add_error(name, "This field is required for seekers.")
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit and user.role == "seeker":
            SeekerProfile.objects.create(
                user=user,
                full_name=self.cleaned_data["full_name"],
                seeker_type=self.cleaned_data["seeker_type"],
                hospital=self.cleaned_data.get("hospital", ""),
                phone=self.cleaned_data["phone"],
                city=self.cleaned_data["city"],
                district=self.cleaned_data["district"],
            )
        return user