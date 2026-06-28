from django.contrib import admin

from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "event_date",
        "is_published",
        "featured"
    )

    list_filter = (
        "is_published",
        "featured"
    )

    list_editable = (
        "is_published",
        "featured",
    )

    search_fields = (
        "title",
    )

    prepopulated_fields = {
        "slug": ("title",)
    }
    
    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user

        super().save_model(
            request,
            obj,
            form,
            change
        )