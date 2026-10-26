
from django.contrib import admin
from .models import OrganPledge


@admin.register(OrganPledge)
class OrganPledgeAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "family_contact_name",
        "family_contact_email",
        "consent_given",
        "created_at",
    )
    list_filter = ("consent_given", "created_at")
    search_fields = ("family_contact_name", "family_contact_email")
