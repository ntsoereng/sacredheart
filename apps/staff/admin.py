from django.contrib import admin

from .models import StaffMember


@admin.register(StaffMember)
class StaffMemberAdmin(admin.ModelAdmin):
    filter_horizontal = ("subjects",)
    list_display = (
        "full_name",
        "user",
        "role",
        "is_principal",
        "display_order",
        "is_active",
    )
    list_editable = ("display_order", "is_active")
    list_filter = ("is_principal", "is_active")
    search_fields = ("full_name", "role", "short_bio", "user__username", "user__email")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("Profile", {
            "fields": (
                "full_name",
                "user",
                "role",
                "profile_picture",
                "short_bio",
                "motto",
                "started_at_shhs",
                "subjects",
            ),
        }),
        ("Principal welcome", {
            "fields": ("is_principal", "welcome_remarks"),
        }),
        ("Display", {
            "fields": ("display_order", "is_active"),
        }),
        ("Record information", {
            "fields": ("created_at", "updated_at"),
        }),
    )
