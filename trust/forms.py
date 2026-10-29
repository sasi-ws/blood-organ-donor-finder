from django import forms

from .models import ContactRequest, Report


class ContactRequestForm(forms.ModelForm):
    """The short message a seeker writes to a donor."""

    class Meta:
        model = ContactRequest
        fields = ["message"]
        widgets = {
            "message": forms.Textarea(attrs={
                "rows": 3,
                "maxlength": 300,
                "class": "form-control",
                "placeholder": "For example: I need O- blood for my father at General Hospital.",
            }),
        }
        labels = {"message": "Your message to the donor"}

class ReportForm(forms.ModelForm):
    """Reason and optional details for reporting a profile."""

    class Meta:
        model = Report
        fields = ["reason", "details"]
        widgets = {
            "reason": forms.Select(attrs={"class": "form-select"}),
            "details": forms.Textarea(attrs={
                "rows": 3,
                "maxlength": 500,
                "class": "form-control",
                "placeholder": "Optional: tell the admin what happened.",
            }),
        }
        labels = {"reason": "Why are you reporting this profile?", "details": "Details"}