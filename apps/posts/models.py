from pathlib import PurePosixPath

from django.conf import settings
from django.db import models
from django.utils.text import slugify

from .content import sanitize_post_html


class Post(models.Model):

    title = models.CharField(
        max_length=200
    )

    slug = models.SlugField(
        unique=True,
        blank=True
    )

    summary = models.TextField(
        help_text="Short summary shown on cards."
    )

    content = models.TextField()

    featured_image = models.ImageField(
        upload_to="posts/",
        blank=True,
        null=True
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    is_published = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )
    
    featured = models.BooleanField(
        default=False
    )

    class Meta:
        ordering = ["-created_at"]

    @property
    def featured_image_url(self):
        """Use the converted WebP when it exists, otherwise use the upload."""
        if not self.featured_image:
            return ""

        webp_name = str(PurePosixPath(self.featured_image.name).with_suffix(".webp"))
        if self.featured_image.storage.exists(webp_name):
            return self.featured_image.storage.url(webp_name)
        return self.featured_image.url

    def save(self, *args, **kwargs):

        if not self.slug:
            base_slug = slugify(self.title) or "news-story"
            slug = base_slug
            suffix = 2
            while Post.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{suffix}"
                suffix += 1
            self.slug = slug

        self.content = sanitize_post_html(self.content)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
