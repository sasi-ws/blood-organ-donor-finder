from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import SeekerProfile, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("Role", {"fields": ("role",)}),)
    list_display = ("username", "email", "role", "is_active")

@admin.register(SeekerProfile)
class SeekerProfileAdmin(admin.ModelAdmin):
    list_display = ("full_name", "user", "seeker_type", "phone", "city", "district")
    list_filter = ("seeker_type", "district")
    search_fields = ("full_name", "user__username", "phone", "city")