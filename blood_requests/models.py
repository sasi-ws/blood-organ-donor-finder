from django.conf import settings
from django.db import models

BLOOD_GROUPS = [(g, g) for g in ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]]


class BloodRequest(models.Model):
    URGENCY = [("normal", "Normal"), ("urgent", "Urgent"), ("critical", "Critical")]
    BLOOD_TYPE = [("whole", "Whole blood"), ("platelets", "Platelets")]
    STATUS = [("open", "Open"), ("fulfilled", "Fulfilled"), ("expired", "Expired")]

    requester = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    patient_name = models.CharField(max_length=100)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUPS)
    units = models.PositiveIntegerField(default=1)
    blood_type = models.CharField(max_length=10, choices=BLOOD_TYPE, default="whole")
    hospital = models.CharField(max_length=150)
    city = models.CharField(max_length=80)
    district = models.CharField(max_length=80)
    urgency = models.CharField(max_length=10, choices=URGENCY, default="normal")
    needed_by = models.DateTimeField()
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS, default="open")
    alert_stage = models.PositiveSmallIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.blood_group} at {self.hospital} ({self.urgency})"


class DonorResponse(models.Model):
    request = models.ForeignKey(BloodRequest, on_delete=models.CASCADE, related_name="responses")
    donor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    can_help = models.BooleanField()
    viewed_at = models.DateTimeField(null=True, blank=True)
    responded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("request", "donor")  # one offer per donor per request

    def __str__(self):
        return f"{self.donor} -> {self.request}"


class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    link = models.CharField(max_length=255, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message