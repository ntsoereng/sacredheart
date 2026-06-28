from django.contrib import admin

from .models import ContactMessage, SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):

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