from django.conf import settings
from django.db import models

from donors.models import DonorProfile


class ContactRequest(models.Model):
    """A seeker asks a donor to share their phone number (FR-CON-01)."""

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("declined", "Declined"),
    ]

    seeker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_contact_requests",
    )
    donor = models.ForeignKey(
        DonorProfile,
        on_delete=models.CASCADE,
        related_name="contact_requests",
    )
    message = models.CharField(max_length=300)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]  # newest first

    def __str__(self):
        return f"{self.seeker} -> {self.donor} ({self.status})"