from django.contrib import admin, messages

from .models import ContactRequest, Report


@admin.register(ContactRequest)
class ContactRequestAdmin(admin.ModelAdmin):
    list_display = ("seeker", "donor", "status", "created_at")
    list_filter = ("status",)


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("reported_user", "reason", "reporter", "status", "created_at")
    list_filter = ("status", "reason")
    actions = ["dismiss_reports", "warn_users", "suspend_users"]

    @admin.action(description="Dismiss selected reports")
    def dismiss_reports(self, request, queryset):
        queryset.update(status="dismissed")

    @admin.action(description="Warn the reported users")
    def warn_users(self, request, queryset):
        # Later this can also send the user a notification
        queryset.update(status="warned")

    @admin.action(description="Suspend the reported accounts")
    def suspend_users(self, request, queryset):
        for report in queryset:
            user = report.reported_user
            if user.is_superuser:
                self.message_user(request, f"{user} is an admin and was not suspended.", messages.WARNING)
                continue
            user.is_active = False  # a suspended donor disappears from search
            user.save()
            report.status = "suspended"
            report.save()