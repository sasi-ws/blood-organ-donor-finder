from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ("donor", "Donor"),
        ("seeker", "Seeker"),
        ("bloodbank", "Blood bank"),
        ("admin", "Admin"),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="seeker")