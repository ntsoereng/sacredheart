import re
import secrets
import unicodedata
import uuid

from django.conf import settings
from django.db import models


def normalize_identity_value(value):
    value = unicodedata.normalize("NFKC", str(value or ""))
    return re.sub(r"\s+", " ", value).strip().casefold()


class Application(models.Model):

    DISTRICT_CHOICES = [
        ("Berea", "Berea"),
        ("Butha-Buthe", "Butha-Buthe"),
        ("Leribe", "Leribe"),
        ("Mafeteng", "Mafeteng"),
        ("Maseru", "Maseru"),
        ("Mohale's Hoek", "Mohale's Hoek"),
        ("Mokhotlong", "Mokhotlong"),
        ("Qacha's Nek", "Qacha's Nek"),
        ("Quthing", "Quthing"),
        ("Thaba-Tseka", "Thaba-Tseka"),
        ("Other", "Other"),
    ]
    
    STATUS_CHOICES = [
        ("new", "New"),
        ("review", "Under Review"),
        ("accepted", "Accepted"),
        ("declined", "Declined"),
    ]

    academic_year = models.CharField(
        max_length=10
    )

    student_name = models.CharField(
        max_length=100
    )

    student_surname = models.CharField(
        max_length=100
    )

    date_of_birth = models.DateField()

    nationality = models.CharField(
        max_length=100,
        default="Lesotho",
    )

    parent_guardian_names = models.CharField(
        max_length=255,
        verbose_name="Parent/guardian name",
    )

    parent_phone_number = models.CharField(
        max_length=30,
        verbose_name="Parent/guardian phone number",
    )

    parent_guardian_email = models.EmailField(
        blank=True,
        max_length=254,
        verbose_name="Parent/guardian email",
    )

    home_address = models.TextField()

    previous_school = models.CharField(
        max_length=255
    )

    student_candidate_number = models.CharField(
        max_length=100,
        verbose_name="Student candidate number",
    )

    district = models.CharField(
        max_length=50,
        choices=DISTRICT_CHOICES
    )

    submitted_at = models.DateTimeField(
        auto_now_add=True
    )

    reviewed = models.BooleanField(
        default=False
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="new",
    )

    notes = models.TextField(
        blank=True
    )

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="reviewed_applications",
    )

    reviewed_at = models.DateTimeField(
        blank=True,
        null=True,
    )
    
    reference_number = models.CharField(
        max_length=30,
        unique=True,
        blank=True
    )

    normalized_academic_year = models.CharField(
        max_length=32,
        blank=True,
        null=True,
        editable=False,
    )

    normalized_student_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        editable=False,
    )

    normalized_student_surname = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        editable=False,
    )

    class Meta:
        ordering = ["-submitted_at"]
        constraints = [
            models.UniqueConstraint(
                fields=(
                    "normalized_academic_year",
                    "normalized_student_name",
                    "normalized_student_surname",
                    "date_of_birth",
                ),
                name="unique_learner_application_per_year",
            )
        ]

    def __str__(self):
        return (
            f"{self.academic_year} "
            f"{self.student_name} "
            f"{self.student_surname}"
        )
    
    def save(self, *args, **kwargs):
        self.normalized_academic_year = normalize_identity_value(self.academic_year)
        self.normalized_student_name = normalize_identity_value(self.student_name)
        self.normalized_student_surname = normalize_identity_value(
            self.student_surname
        )
        if not self.reference_number:
            self.reference_number = (
                f"SHHS-{self.academic_year}-{secrets.token_hex(5).upper()}"
            )
        super().save(*args, **kwargs)


class AdmissionRateLimitBucket(models.Model):
    identifier_hash = models.CharField(max_length=64, unique=True)
    window_started_at = models.DateTimeField()
    attempts = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Admissions rate-limit bucket"
        verbose_name_plural = "Admissions rate-limit buckets"


class ApplicationSubmissionToken(models.Model):
    token_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    consumed_at = models.DateTimeField(blank=True, null=True)

    @property
    def is_consumed(self):
        return self.consumed_at is not None


class ApplicationNote(models.Model):
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name="review_notes",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
        related_name="application_notes",
    )
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Note on {self.application.reference_number}"
