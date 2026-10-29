from django.db import models


class SiteSetting(models.Model):
    """Simple key/value switches the admin can change (for example dengue_mode)."""
    key = models.CharField(max_length=50, unique=True)
    value = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.key} = {self.value}"


def is_dengue_mode():
    """True when the admin has switched Dengue season mode on."""
    return SiteSetting.objects.filter(key="dengue_mode", value="on").exists()