from django.contrib import admin

from .models import Post

    
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "author",
        "is_published",
        "featured",
        "created_at",
    )

    list_editable = (
        "is_published",
        "featured",
    )

    list_filter = (
        "is_published",
    )

    search_fields = (
        "title",
    )

    prepopulated_fields = {
        "slug": ("title",)
    }

    readonly_fields = ("author", "created_at", "updated_at")
    
    
    
    def save_model(self, request, obj, form, change):
        if not obj.author:
            obj.author = request.user

        super().save_model(
            request,
            obj,
            form,
            change
        )
