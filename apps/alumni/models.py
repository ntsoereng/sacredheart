from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class AlumniStory(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending review"),
        ("approved", "Approved"),
        ("rejected", "Not approved"),
    )

    full_name = models.CharField(max_length=200)
    graduation_year = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1900), MaxValueValidator(2100)]
    )
    email = models.EmailField(help_text="Kept private and used only for follow-up.")
    phone = models.CharField(
        max_length=30,
        blank=True,
        help_text="Kept private and used only for follow-up.",
    )
    current_location = models.CharField(max_length=150, blank=True)
    occupation = models.CharField(max_length=200, blank=True)
    profile_photo = models.ImageField(upload_to="alumni/", blank=True, null=True)
    life_story = models.TextField(
        help_text="Tell us about your journey since leaving Sacred Heart."
    )
    school_memories = models.TextField(
        blank=True,
        help_text="Share a favourite memory from your time at Sacred Heart.",
    )
    message_to_students = models.TextField(
        blank=True,
        help_text="Optional advice or encouragement for current learners.",
    )
    consent_to_publish = models.BooleanField(
        default=False,
        help_text="I consent to my story and photo being published on this website.",
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    staff_notes = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="reviewed_alumni_stories",
    )
    reviewed_at = models.DateTimeField(blank=True, null=True)
    slug = models.SlugField(max_length=240, unique=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-submitted_at",)
        verbose_name_plural = "Alumni stories"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(
                f"{self.full_name}-class-of-{self.graduation_year}"
            ) or "alumni-story"
            slug = base_slug
            suffix = 2
            while AlumniStory.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{suffix}"
                suffix += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def is_published(self):
        return self.status == "approved" and self.consent_to_publish

    def mark_reviewed(self, user):
        self.reviewed_by = user
        self.reviewed_at = timezone.now()

    def __str__(self):
        return f"{self.full_name} — Class of {self.graduation_year}"
