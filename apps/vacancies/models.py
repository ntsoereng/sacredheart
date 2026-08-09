from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from apps.posts.content import sanitize_post_html


class VacancyQuerySet(models.QuerySet):
    def publicly_visible(self):
        return self.filter(
            is_published=True,
            status="open",
            application_deadline__gte=timezone.localdate(),
        )


class Vacancy(models.Model):
    EMPLOYMENT_TYPES = (
        ("full_time", "Full-time"),
        ("part_time", "Part-time"),
        ("temporary", "Temporary"),
        ("contract", "Contract"),
    )
    STATUS_CHOICES = (
        ("open", "Open"),
        ("closed", "Closed"),
        ("filled", "Filled"),
    )

    job_title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=240, unique=True, blank=True)
    department = models.CharField(max_length=200, verbose_name="Department / subject")
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPES)
    location = models.CharField(max_length=200, default="Sacred Heart High School")
    application_deadline = models.DateField()
    expected_start_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="open")
    reference_number = models.CharField(max_length=100, blank=True)
    short_summary = models.TextField(help_text="A 1–3 sentence overview for listings.")
    job_description = models.TextField()
    minimum_qualifications = models.TextField()
    experience_requirements = models.TextField()
    skills_competencies = models.TextField(verbose_name="Skills / competencies")
    additional_requirements = models.TextField(blank=True)
    application_instructions = models.TextField()
    contact_email = models.EmailField(default="careers@sacredheart.ac.ls")
    contact_person = models.CharField(max_length=200, blank=True)
    is_published = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="created_vacancies",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = VacancyQuerySet.as_manager()

    class Meta:
        ordering = ("application_deadline", "job_title")
        verbose_name_plural = "vacancies"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.job_title) or "vacancy"
            slug = base_slug
            suffix = 2
            while Vacancy.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{suffix}"
                suffix += 1
            self.slug = slug
        rich_fields = (
            "job_description",
            "minimum_qualifications",
            "experience_requirements",
            "skills_competencies",
            "additional_requirements",
            "application_instructions",
        )
        for field in rich_fields:
            setattr(self, field, sanitize_post_html(getattr(self, field)))
        super().save(*args, **kwargs)

    @property
    def is_accepting_applications(self):
        return (
            self.is_published
            and self.status == "open"
            and self.application_deadline >= timezone.localdate()
        )

    def __str__(self):
        return self.job_title
