from django.conf import settings
from django.db import models
from django.utils.text import slugify
from django.utils import timezone

class Event(models.Model):

    title = models.CharField(
        max_length=200
    )

    slug = models.SlugField(
        unique=True,
        blank=True,
    )

    description = models.TextField()

    event_date = models.DateField()

    location = models.CharField(
        max_length=200,
        blank=True
    )

    image = models.ImageField(
        upload_to="events/",
        blank=True,
        null=True
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    is_published = models.BooleanField(
        default=True
    )
    
    featured = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["event_date"]

    def save(self, *args, **kwargs):
        """
        Auto-generate slug from title.
        """

        if not self.slug:
            self.slug = slugify(f"{self.title}-{self.event_date.year}")

        super().save(*args, **kwargs)
        
    
    @property
    def is_past(self):
        return self.event_date < timezone.now().date()
    
    
    @property
    def is_upcoming(self):
        return self.event_date >= timezone.now().date()
    

    def __str__(self):
        return self.title