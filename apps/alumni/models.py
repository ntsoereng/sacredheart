import hashlib
import secrets
from datetime import timedelta

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
    industry = models.CharField(
        max_length=150,
        blank=True,
        help_text="For example: engineering, education, health, finance or the arts.",
    )
    profile_photo = models.ImageField(upload_to="alumni/", blank=True, null=True)
    life_story = models.TextField(
        blank=True,
        verbose_name="Profile summary",
        help_text="Briefly describe your journey, work, studies or community contribution.",
    )
    school_memories = models.TextField(
        blank=True,
        help_text="Share a favourite memory from your time at Sacred Heart.",
    )
    message_to_students = models.TextField(
        blank=True,
        help_text="Optional advice or encouragement for current learners.",
    )
    mentorship_available = models.BooleanField(
        default=False,
        help_text="I am open to being contacted by the school about mentoring.",
    )
    mentor_career_guidance = models.BooleanField(default=False)
    mentor_university_applications = models.BooleanField(default=False)
    mentor_subject_choices = models.BooleanField(default=False)
    mentor_entrepreneurship = models.BooleanField(default=False)
    consent_to_publish = models.BooleanField(
        default=False,
        help_text="I consent to my directory profile and photo being published on this website.",
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
        verbose_name = "Alumni profile"
        verbose_name_plural = "Alumni profiles"

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

    @property
    def mentorship_areas(self):
        areas = []
        if self.mentor_career_guidance:
            areas.append("Career guidance")
        if self.mentor_university_applications:
            areas.append("University applications")
        if self.mentor_subject_choices:
            areas.append("Subject and career choices")
        if self.mentor_entrepreneurship:
            areas.append("Entrepreneurship advice")
        return areas


class AlumniProfileUpdateVerification(models.Model):
    alumni = models.ForeignKey(
        AlumniStory,
        on_delete=models.CASCADE,
        related_name="profile_update_verifications",
    )
    token_digest = models.CharField(max_length=64, unique=True, editable=False)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [models.Index(fields=("alumni", "expires_at"))]
        verbose_name = "Alumni profile update verification"
        verbose_name_plural = "Alumni profile update verifications"

    @staticmethod
    def digest_token(raw_token):
        return hashlib.sha256(str(raw_token).encode()).hexdigest()

    @classmethod
    def issue(cls, alumni, lifetime=timedelta(hours=1)):
        raw_token = secrets.token_urlsafe(32)
        verification = cls.objects.create(
            alumni=alumni,
            token_digest=cls.digest_token(raw_token),
            expires_at=timezone.now() + lifetime,
        )
        return verification, raw_token

    @property
    def is_available(self):
        return self.used_at is None and self.expires_at > timezone.now()

    def __str__(self):
        return f"Profile update verification for {self.alumni}"


class AlumniOpportunity(models.Model):
    TYPE_CHOICES = (
        ("scholarship", "Scholarship"),
        ("competition", "Competition"),
        ("training", "Training opportunity"),
    )
    STATUS_CHOICES = AlumniStory.STATUS_CHOICES

    alumni = models.ForeignKey(
        AlumniStory,
        on_delete=models.CASCADE,
        related_name="opportunities",
        limit_choices_to={"status": "approved", "consent_to_publish": True},
    )
    opportunity_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    title = models.CharField(max_length=200)
    provider = models.CharField(max_length=200, blank=True)
    summary = models.TextField(help_text="Explain who is eligible and what is offered.")
    application_url = models.URLField(blank=True)
    deadline = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    staff_notes = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="reviewed_alumni_opportunities",
    )
    reviewed_at = models.DateTimeField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("deadline", "-submitted_at")
        verbose_name_plural = "Alumni opportunities"

    @property
    def is_published(self):
        return (
            self.status == "approved"
            and self.alumni.is_published
            and (self.deadline is None or self.deadline >= timezone.localdate())
        )

    def mark_reviewed(self, user):
        self.reviewed_by = user
        self.reviewed_at = timezone.now()

    def __str__(self):
        return self.title


class MentorshipRequest(models.Model):
    AUDIENCE_CHOICES = (
        ("learner", "Current Sacred Heart learner"),
        ("graduate", "Recent Sacred Heart graduate"),
    )
    FOCUS_CHOICES = (
        ("career", "Career guidance"),
        ("university", "University applications"),
        ("subjects", "Subject and career choices"),
        ("entrepreneurship", "Entrepreneurship advice"),
    )

    mentor = models.ForeignKey(
        AlumniStory,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="mentorship_requests",
        limit_choices_to={"status": "approved", "mentorship_available": True},
    )
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    audience = models.CharField(max_length=20, choices=AUDIENCE_CHOICES)
    focus_area = models.CharField(max_length=20, choices=FOCUS_CHOICES)
    goals = models.TextField(help_text="Tell us what support you are looking for.")
    consent_to_contact = models.BooleanField(default=False)
    is_handled = models.BooleanField(default=False)
    staff_notes = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-submitted_at",)

    def __str__(self):
        return f"{self.full_name} — {self.get_focus_area_display()}"
