from django.contrib import admin
from .models import BloodRequest, DonorResponse, Notification


@admin.register(BloodRequest)
class BloodRequestAdmin(admin.ModelAdmin):
    list_display = ("blood_group", "blood_type", "units", "hospital", "city",
                    "urgency", "status", "alert_stage", "needed_by", "created_at")
    list_filter = ("urgency", "status", "blood_group", "blood_type", "city", "district")
    search_fields = ("patient_name", "hospital", "city", "notes", "requester__username")
    actions = ["mark_fulfilled", "mark_expired"]

    @admin.action(description="Mark selected requests as fulfilled")
    def mark_fulfilled(self, request, queryset):
        n = queryset.update(status="fulfilled")
        self.message_user(request, f"{n} request(s) marked fulfilled.")

    @admin.action(description="Hide selected requests (mark expired)")
    def mark_expired(self, request, queryset):
        n = queryset.update(status="expired")
        self.message_user(request, f"{n} request(s) hidden.")


@admin.register(DonorResponse)
class DonorResponseAdmin(admin.ModelAdmin):
    list_display = ("request", "donor", "can_help", "viewed_at", "responded_at")
    list_filter = ("can_help",)
    search_fields = ("donor__username", "request__hospital")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "message", "is_read", "created_at")
    list_filter = ("is_read",)
    search_fields = ("user__username", "message")