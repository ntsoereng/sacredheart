from django.db import models
from django.utils.text import slugify


class Page(models.Model):
    title = models.CharField(
        max_length=200
    )

    slug = models.SlugField(
        unique=True,
        blank=True
    )

    content = models.TextField()

    hero_image = models.ImageField(
        upload_to="pages/",
        blank=True,
        null=True
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

    class Meta:
        ordering = ["title"]

    def save(self, *args, **kwargs):
        """
        Auto-generate slug if one has not
        been supplied manually.
        """

        if not self.slug:
            self.slug = slugify(self.title)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title