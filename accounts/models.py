from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ("donor", "Donor"),
        ("seeker", "Seeker"),
        ("bloodbank", "Blood bank"),
        ("admin", "Admin"),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="seeker")


phone_validator = RegexValidator(
    regex=r"^\+?[0-9 ]{9,15}$",
    message="Enter a valid phone number, for example 077 111 0001.",
)


class SeekerProfile(models.Model):
    """Extra details for people who look for donors (FR-ACC-01, design: 'About you')."""

    TYPE_CHOICES = [
        ("patient", "Patient"),
        ("family", "Family member"),
        ("hospital", "Hospital staff"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,   # deleting the account removes this too
        related_name="seeker_profile",
    )
    full_name = models.CharField(max_length=100)
    seeker_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="patient")
    hospital = models.CharField(max_length=120, blank=True)
    phone = models.CharField(max_length=20, validators=[phone_validator])
    city = models.CharField(max_length=60)
    district = models.CharField(max_length=60)

    def __str__(self):
        return f"{self.full_name} ({self.get_seeker_type_display()})"