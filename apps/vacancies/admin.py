from django.contrib import admin

from .models import Vacancy


@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ("job_title", "department", "employment_type", "application_deadline", "status", "is_published")
    list_filter = ("status", "is_published", "employment_type", "application_deadline")
    search_fields = ("job_title", "department", "reference_number", "short_summary")
    readonly_fields = ("created_by", "created_at", "updated_at")

    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
