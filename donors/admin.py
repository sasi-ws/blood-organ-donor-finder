from django.contrib import admin

from .models import DonorProfile


@admin.register(DonorProfile)
class DonorProfileAdmin(admin.ModelAdmin):
    list_display = ("full_name", "blood_group", "city", "is_verified", "hide_profile")
    list_filter = ("blood_group", "is_verified", "hide_profile")