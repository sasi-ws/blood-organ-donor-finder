from django.contrib import admin
from .models import DonorProfile


@admin.register(DonorProfile)
class DonorProfileAdmin(admin.ModelAdmin):
    list_display = ("full_name", "blood_group", "donor_type", "city", "district",
                    "is_verified", "hide_profile", "last_donation_date")
    list_filter = ("blood_group", "donor_type", "is_verified", "hide_profile", "city", "district")
    search_fields = ("full_name", "user__username", "user__email", "city")
    actions = ["verify_donors", "unverify_donors", "hide_donors", "unhide_donors"]

    @admin.action(description="Verify selected donors")
    def verify_donors(self, request, queryset):
        n = queryset.update(is_verified=True)
        self.message_user(request, f"{n} donor(s) verified.")

    @admin.action(description="Remove Verified badge from selected donors")
    def unverify_donors(self, request, queryset):
        n = queryset.update(is_verified=False)
        self.message_user(request, f"{n} donor(s) unverified.")

    @admin.action(description="Hide selected donors from search")
    def hide_donors(self, request, queryset):
        n = queryset.update(hide_profile=True)
        self.message_user(request, f"{n} donor(s) hidden.")

    @admin.action(description="Show selected donors in search again")
    def unhide_donors(self, request, queryset):
        n = queryset.update(hide_profile=False)
        self.message_user(request, f"{n} donor(s) visible again.")