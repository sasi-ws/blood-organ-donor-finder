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
    is_flagged = models.BooleanField(default=False)   # money words found (FR-TRU-05)
    flagged_words = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ["-created_at"]  # newest first

    def __str__(self):
        return f"{self.seeker} -> {self.donor} ({self.status})"

class Report(models.Model):
    """A user reports a suspicious donor profile (FR-TRU-02)."""

    REASON_CHOICES = [
        ("fake", "Fake profile"),
        ("money", "Asked for money"),
        ("harassment", "Harassment"),
        ("other", "Other"),
    ]
    STATUS_CHOICES = [
        ("open", "Open"),
        ("dismissed", "Dismissed"),
        ("warned", "User warned"),
        ("suspended", "Account suspended"),
    ]

    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reports_made",
    )
    reported_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reports_received",
    )
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    details = models.TextField(blank=True, max_length=500)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="open")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Report on {self.reported_user} ({self.get_reason_display()}, {self.status})"