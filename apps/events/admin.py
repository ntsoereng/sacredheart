from django.contrib import admin

from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "event_date",
        "end_date",
        "category",
        "is_published",
        "featured"
    )

    list_filter = (
        "is_published",
        "featured",
        "category",
    )

    list_editable = (
        "is_published",
        "featured",
    )

    search_fields = (
        "title",
        "location",
        "description",
    )

    prepopulated_fields = {
        "slug": ("title",)
    }

    readonly_fields = ("created_by", "created_at")

    fieldsets = (
        (None, {"fields": ("title", "slug", "description", "image")}),
        (
            "Date and time",
            {
                "fields": (
                    ("event_date", "end_date"),
                    ("start_time", "end_time"),
                    "location",
                )
            },
        ),
        ("Classification", {"fields": ("category", "featured", "is_published")}),
        ("Record information", {"fields": ("created_by", "created_at")}),
    )
    
    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user

        super().save_model(
            request,
            obj,
            form,
            change
        )
