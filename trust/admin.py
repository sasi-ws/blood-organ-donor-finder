
from django.contrib import admin, messages

from .models import ContactRequest, Report


@admin.register(ContactRequest)
class ContactRequestAdmin(admin.ModelAdmin):
    list_display = (
        "seeker",
        "donor",
        "status",
        "is_flagged",
        "flagged_words",
        "created_at",
    )
    list_filter = ("status", "is_flagged")
    search_fields = ("seeker__username", "donor__full_name", "message")
    readonly_fields = ("created_at",)


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = (
        "reported_user",
        "reason",
        "reporter",
        "status",
        "created_at",
    )
    list_filter = ("status", "reason")
    search_fields = (
        "reported_user__username",
        "reporter__username",
        "details",
    )
    readonly_fields = ("created_at",)
    actions = ["dismiss_reports", "warn_users", "suspend_users"]

    @admin.action(description="Dismiss selected reports")
    def dismiss_reports(self, request, queryset):
        n = queryset.update(status="dismissed")
        self.message_user(request, f"{n} report(s) dismissed.")

    @admin.action(description="Warn the reported users")
    def warn_users(self, request, queryset):
        n = queryset.update(status="warned")
        self.message_user(request, f"{n} report(s) marked as warned.")

    @admin.action(description="Suspend the reported accounts")
    def suspend_users(self, request, queryset):
        users = {
            report.reported_user
            for report in queryset
            if report.reported_user != request.user
            and not report.reported_user.is_superuser
        }

        for user in users:
            user.is_active = False
            user.save(update_fields=["is_active"])

        n = queryset.exclude(
            reported_user__is_superuser=True
        ).exclude(
            reported_user=request.user
        ).update(status="suspended")

        self.message_user(
            request,
            f"{len(users)} account(s) suspended, {n} report(s) closed.",
            messages.SUCCESS,
        )
