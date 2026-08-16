from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils import timezone
from apps.posts.content import sanitize_post_html


class Event(models.Model):

    class Category(models.TextChoices):
        ACADEMIC = "academic", "Academic"
        ADMISSIONS = "admissions", "Admissions"
        MEETING = "meeting", "Meeting"
        SPORT = "sport", "Sport"
        HOLIDAY = "holiday", "Holiday"
        OTHER = "other", "Other"

    title = models.CharField(
        max_length=200
    )

    slug = models.SlugField(
        unique=True,
        blank=True,
    )

    description = models.TextField()

    event_date = models.DateField(
        verbose_name="start date",
    )

    end_date = models.DateField(
        blank=True,
        null=True,
        help_text="Leave blank for a single-day event.",
    )

    start_time = models.TimeField(
        blank=True,
        null=True,
    )

    end_time = models.TimeField(
        blank=True,
        null=True,
    )

    location = models.CharField(
        max_length=200,
        blank=True
    )

    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.OTHER,
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
        default=False,
        verbose_name="important / featured",
        help_text="Highlight this event in important-date and planning sections.",
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["event_date"]

    def clean(self):
        super().clean()
        if self.end_date and self.end_date < self.event_date:
            raise ValidationError(
                {"end_date": "End date cannot be before the start date."}
            )
        if self.end_time and not self.start_time:
            raise ValidationError(
                {"end_time": "Add a start time before setting an end time."}
            )
        if (
            self.start_time
            and self.end_time
            and (not self.end_date or self.end_date == self.event_date)
            and self.end_time <= self.start_time
        ):
            raise ValidationError(
                {"end_time": "End time must be after the start time."}
            )

    def save(self, *args, **kwargs):
        """
        Auto-generate slug from title.
        """

        if not self.slug:
            base_slug = slugify(
                f"{self.title}-{self.event_date.year}"
            ) or "school-event"
            slug = base_slug
            suffix = 2
            while Event.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{suffix}"
                suffix += 1
            self.slug = slug

        self.description = sanitize_post_html(self.description)
        super().save(*args, **kwargs)
        
    
    @property
    def is_past(self):
        return (self.end_date or self.event_date) < timezone.localdate()
    
    
    @property
    def is_upcoming(self):
        return (self.end_date or self.event_date) >= timezone.localdate()

    @property
    def last_date(self):
        return self.end_date or self.event_date
    

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("event-detail", kwargs={"slug": self.slug})
