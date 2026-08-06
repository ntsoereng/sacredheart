from django.contrib import admin
from django.utils import timezone

from .models import Application, ApplicationNote


class ApplicationNoteInline(admin.TabularInline):
    model = ApplicationNote
    extra = 0
    readonly_fields = ("author", "created_at")


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):

    readonly_fields = (
        "reference_number",
        "reviewed",
        "reviewed_by",
        "reviewed_at",
        "submitted_at",
    )

    list_display = (
        "student_name",
        "student_surname",
        "academic_year",
        "district",
        "parent_guardian_email",
        "submitted_at",
        "status",
        "reviewed_by",
    )

    inlines = (ApplicationNoteInline,)

    search_fields = (
        "student_name",
        "student_surname",
        "parent_guardian_names",
        "parent_guardian_email",
        "previous_school",
        "academic_year"
    )

    list_filter = (
        "district",
        "status",
        "submitted_at",
    )

    def save_model(self, request, obj, form, change):
        if "status" in form.changed_data:
            obj.reviewed = obj.status != "new"
            obj.reviewed_by = request.user
            obj.reviewed_at = timezone.now()
        super().save_model(request, obj, form, change)
