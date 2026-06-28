from django.contrib import admin

from .models import Application


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):

    list_display = (
        "student_name",
        "student_surname",
        "academic_year",
        "district",
        "submitted_at",
        "reviewed",
    )

    list_editable = (
        "reviewed",
    )

    search_fields = (
        "student_name",
        "student_surname",
        "parent_guardian_names",
        "previous_school",
        "academic_year"
    )

    list_filter = (
        "district",
        "reviewed",
        "submitted_at",
    )