
from django.conf import settings
from django.db import models
from django.utils import timezone


class BloodBank(models.Model):
    manager = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="managed_blood_bank",
        limit_choices_to={"role": "bloodbank"},
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=150)
    address = models.TextField()
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)

    def __str__(self):
        return self.name


class StockLevel(models.Model):
    BLOOD_GROUP_CHOICES = [
        ("A+", "A+"),
        ("A-", "A-"),
        ("B+", "B+"),
        ("B-", "B-"),
        ("AB+", "AB+"),
        ("AB-", "AB-"),
        ("O+", "O+"),
        ("O-", "O-"),
    ]

    STATUS_CHOICES = [
        ("Low", "Low"),
        ("OK", "OK"),
        ("Full", "Full"),
    ]

    blood_bank = models.ForeignKey(
        BloodBank,
        on_delete=models.CASCADE,
        related_name="stock_levels",
    )
    blood_group = models.CharField(
        max_length=3,
        choices=BLOOD_GROUP_CHOICES,
    )
    units_available = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("blood_bank", "blood_group")
        ordering = ["blood_group"]

    @property
    def status(self):
        if self.units_available < 5:
            return "Low"
        elif self.units_available < 15:
            return "OK"
        return "Full"

    @property
    def is_outdated(self):
        return (timezone.now() - self.last_updated).days > 3

    def __str__(self):
        return f"{self.blood_bank.name} - {self.blood_group}"
