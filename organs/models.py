
from django.conf import settings
from django.db import models


class OrganPledge(models.Model):
    ORGAN_CHOICES = [
        ("kidneys", "Kidneys"),
        ("liver", "Liver"),
        ("heart", "Heart"),
        ("lungs", "Lungs"),
        ("pancreas", "Pancreas"),
        ("corneas", "Corneas"),
        ("tissues", "Other tissues"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="organ_pledges",
    )
    organs = models.JSONField(default=list)
    family_contact_name = models.CharField(max_length=100)
    family_contact_email = models.EmailField()
    consent_given = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Organ pledge by {self.user}"
