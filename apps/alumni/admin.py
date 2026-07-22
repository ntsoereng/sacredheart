from django.contrib import admin

from .models import AlumniStory


@admin.register(AlumniStory)
class AlumniStoryAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "graduation_year",
        "occupation",
        "status",
        "submitted_at",
        "reviewed_by",
    )
    list_filter = ("status", "graduation_year", "consent_to_publish")
    search_fields = ("full_name", "email", "phone", "occupation", "life_story")
    readonly_fields = ("slug", "submitted_at", "updated_at", "reviewed_by", "reviewed_at")
    fieldsets = (
        ("Alumnus", {"fields": ("full_name", "graduation_year", "profile_photo", "current_location", "occupation")}),
        ("Private contact details", {"fields": ("email", "phone")}),
        ("Story", {"fields": ("life_story", "school_memories", "message_to_students", "consent_to_publish")}),
        ("Review", {"fields": ("status", "staff_notes", "reviewed_by", "reviewed_at")}),
        ("Record information", {"fields": ("slug", "submitted_at", "updated_at")}),
    )

    def save_model(self, request, obj, form, change):
        if "status" in form.changed_data:
            obj.mark_reviewed(request.user)
        super().save_model(request, obj, form, change)
