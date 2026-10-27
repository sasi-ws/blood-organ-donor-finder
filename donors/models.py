from django.db import models
from django.conf import settings
from django.utils import timezone


class DonorProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10)
    blood_group = models.CharField(max_length=3)
    donor_type = models.CharField(max_length=10)  # blood, platelets, both
    city = models.CharField(max_length=50)
    district = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    last_donation_date = models.DateField(null=True, blank=True)
    hide_profile = models.BooleanField(default=False)
    available_until = models.DateTimeField(null=True, blank=True)
    travel_city = models.CharField(max_length=50, blank=True)
    is_verified = models.BooleanField(default=False)
    consent_given = models.BooleanField(default=False)
    consent_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.full_name
    @property
    def is_available_today(self):
        """True while the 'I can donate today' switch is still within its 24 hours."""
        return bool(self.available_until and self.available_until > timezone.now())