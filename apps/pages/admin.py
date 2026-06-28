from django.contrib import admin
from .models import Page


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "is_published",
        "updated_at",
    )

    prepopulated_fields = {
        "slug": ("title",)
    }

    list_filter = (
        "is_published",
    )
    
    list_editable = (
        "is_published",
    )

    search_fields = (
        "title",
    )