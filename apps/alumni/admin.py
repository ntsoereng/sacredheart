from django.contrib import admin

from .models import AlumniOpportunity, AlumniStory, MentorshipRequest


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
    list_filter = ("status", "mentorship_available", "graduation_year", "consent_to_publish")
    search_fields = ("full_name", "email", "phone", "occupation", "industry", "life_story")
    readonly_fields = ("slug", "submitted_at", "updated_at", "reviewed_by", "reviewed_at")
    fieldsets = (
        ("Alumnus", {"fields": ("full_name", "graduation_year", "profile_photo", "current_location", "occupation", "industry")}),
        ("Private contact details", {"fields": ("email", "phone")}),
        ("Directory profile", {"fields": ("life_story", "school_memories", "message_to_students", "consent_to_publish")}),
        ("Mentorship", {"fields": ("mentorship_available", "mentor_career_guidance", "mentor_university_applications", "mentor_subject_choices", "mentor_entrepreneurship")}),
        ("Review", {"fields": ("status", "staff_notes", "reviewed_by", "reviewed_at")}),
        ("Record information", {"fields": ("slug", "submitted_at", "updated_at")}),
    )

    def save_model(self, request, obj, form, change):
        if "status" in form.changed_data:
            obj.mark_reviewed(request.user)
        super().save_model(request, obj, form, change)


@admin.register(AlumniOpportunity)
class AlumniOpportunityAdmin(admin.ModelAdmin):
    list_display = ("title", "opportunity_type", "alumni", "deadline", "status")
    list_filter = ("status", "opportunity_type", "deadline")
    search_fields = ("title", "provider", "summary", "alumni__full_name")
    readonly_fields = ("submitted_at", "updated_at", "reviewed_by", "reviewed_at")

    def save_model(self, request, obj, form, change):
        if "status" in form.changed_data:
            obj.mark_reviewed(request.user)
        super().save_model(request, obj, form, change)


@admin.register(MentorshipRequest)
class MentorshipRequestAdmin(admin.ModelAdmin):
    list_display = ("full_name", "audience", "focus_area", "mentor", "is_handled", "submitted_at")
    list_filter = ("is_handled", "audience", "focus_area")
    search_fields = ("full_name", "email", "phone", "goals", "mentor__full_name")
    readonly_fields = ("submitted_at",)
