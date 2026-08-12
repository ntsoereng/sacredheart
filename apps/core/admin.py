from django.contrib import admin

from .models import ContactMessage, ExtracurricularActivity, SiteSettings

admin.site.site_header = "Sacred Heart Administration"
admin.site.site_title = "Sacred Heart Admin"
admin.site.index_title = "School management"


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
        ("Social media", {
            "fields": (
                "facebook_url",
                "instagram_url",
                "youtube_url",
                "tiktok_url",
                "x_url",
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
                "admissions_list",
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


@admin.register(ExtracurricularActivity)
class ExtracurricularActivityAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "display_order",
        "is_featured",
        "is_published",
        "updated_at",
    )
    list_editable = ("display_order", "is_featured", "is_published")
    list_filter = ("category", "is_featured", "is_published")
    search_fields = (
        "name",
        "short_description",
        "description",
        "achievements",
    )
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("Activity", {
            "fields": (
                "name",
                "slug",
                "category",
                "short_description",
                "description",
                "featured_image",
            ),
        }),
        ("Achievements", {"fields": ("achievements",)}),
        ("Publishing", {
            "fields": (
                "is_published",
                "is_featured",
                "display_order",
            ),
        }),
        ("Record information", {
            "fields": ("created_at", "updated_at"),
        }),
    )
