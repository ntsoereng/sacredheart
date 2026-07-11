from django.contrib import admin

from .models import ContactMessage, SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):

    readonly_fields = ("updated_at",)

    fieldsets = (
        ("School identity", {
            "fields": (
                "school_name",
                "tagline",
                "logo",
                "favicon",
            ),
        }),
        ("Contact details", {
            "fields": (
                "email",
                "phone",
                "address",
                "office_hours",
                "google_maps_embed_url",
            ),
        }),
        ("Homepage", {
            "fields": (
                "hero_title",
                "hero_subtitle",
                "hero_image",
            ),
        }),
        ("About Us", {
            "fields": (
                "about_history",
                "about_mission",
                "about_vision",
                "about_values",
            ),
        }),
        ("Admissions", {
            "fields": (
                "admissions_email",
                "admissions_open",
                "admissions_message",
            ),
        }),
        ("Announcement bar", {
            "fields": (
                "show_announcement",
                "homepage_announcement",
            ),
        }),
        ("Record information", {
            "fields": ("updated_at",),
        }),
    )

    def has_add_permission(self, request):

        return not SiteSettings.objects.exists()
    
    
@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "email",
        "subject",
        "created_at",
        "is_read",
    )

    list_editable = (
        "is_read",
    )

    search_fields = (
        "name",
        "email",
        "subject",
    )
