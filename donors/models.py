from django.db import models
from django.conf import settings


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
    is_verified = models.BooleanField(default=False)
    consent_given = models.BooleanField(default=False)
    consent_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.full_name