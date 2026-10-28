from django.contrib import admin
from .models import BloodBank, StockLevel


class StockLevelInline(admin.TabularInline):
    model = StockLevel
    extra = 1


@admin.register(BloodBank)
class BloodBankAdmin(admin.ModelAdmin):
    list_display = ("name", "manager", "phone", "email")
    search_fields = ("name", "address")
    inlines = [StockLevelInline]


@admin.register(StockLevel)
class StockLevelAdmin(admin.ModelAdmin):
    list_display = (
        "blood_bank",
        "blood_group",
        "units_available",
        "last_updated",
    )
    list_filter = ("blood_group", "blood_bank")