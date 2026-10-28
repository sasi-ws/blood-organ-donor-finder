from django import forms
from django.utils import timezone

from .models import BloodRequest


class BloodRequestForm(forms.ModelForm):
    needed_by = forms.DateTimeField(
        input_formats=["%Y-%m-%dT%H:%M"],
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"
        ),
    )

    class Meta:
        model = BloodRequest
        fields = [
            "patient_name", "blood_group", "blood_type", "units",
            "hospital", "city", "district", "needed_by", "urgency", "notes",
        ]
        widgets = {
            "urgency": forms.RadioSelect,
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name == "urgency":
                continue
            field.widget.attrs["class"] = (
                "form-select" if isinstance(field.widget, forms.Select) else "form-control"
            )

    def clean_needed_by(self):
        value = self.cleaned_data["needed_by"]
        if value < timezone.now():
            raise forms.ValidationError("The needed-by time cannot be in the past.")
        return value

    def clean_units(self):
        units = self.cleaned_data["units"]
        if units < 1:
            raise forms.ValidationError("At least 1 unit is needed.")
        return units