from django import forms

from .models import ContactRequest


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