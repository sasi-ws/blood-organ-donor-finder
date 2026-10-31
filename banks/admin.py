
from django.contrib import admin

from .models import BloodBank, StockLevel


class StockLevelInline(admin.TabularInline):
    model = StockLevel
    extra = 0


@admin.register(BloodBank)
class BloodBankAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "email", "manager")
    search_fields = ("name", "address", "phone")
    inlines = [StockLevelInline]


@admin.register(StockLevel)
class StockLevelAdmin(admin.ModelAdmin):
    list_display = (
        "blood_bank",
        "blood_group",
        "units_available",
        "status",
        "last_updated",
        "is_outdated",
    )
    list_filter = ("blood_group", "blood_bank")
    search_fields = ("blood_bank__name",)
    readonly_fields = ("last_updated",)
