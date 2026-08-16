import re
import unicodedata
import uuid

from django.db import migrations, models


def normalize_value(value):
    value = unicodedata.normalize("NFKC", str(value or ""))
    return re.sub(r"\s+", " ", value).strip().casefold()


def populate_normalized_identity(apps, schema_editor):
    Application = apps.get_model("admissions", "Application")
    seen = set()
    for application in Application.objects.order_by("pk").iterator():
        identity = (
            normalize_value(application.academic_year),
            normalize_value(application.student_name),
            normalize_value(application.student_surname),
            application.date_of_birth,
        )
        if identity in seen:
            # Preserve historical duplicates. Their NULL normalized fields allow the
            # constraint to be introduced while the first record blocks new copies.
            continue
        seen.add(identity)
        Application.objects.filter(pk=application.pk).update(
            normalized_academic_year=identity[0],
            normalized_student_name=identity[1],
            normalized_student_surname=identity[2],
        )


class Migration(migrations.Migration):

    dependencies = [
        ("admissions", "0009_application_parent_guardian_labels_and_other_district"),
    ]

    operations = [
        migrations.AddField(
            model_name="application",
            name="normalized_academic_year",
            field=models.CharField(
                blank=True,
                editable=False,
                max_length=32,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="application",
            name="normalized_student_name",
            field=models.CharField(
                blank=True,
                editable=False,
                max_length=255,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="application",
            name="normalized_student_surname",
            field=models.CharField(
                blank=True,
                editable=False,
                max_length=255,
                null=True,
            ),
        ),
        migrations.CreateModel(
            name="AdmissionRateLimitBucket",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("identifier_hash", models.CharField(max_length=64, unique=True)),
                ("window_started_at", models.DateTimeField()),
                ("attempts", models.PositiveIntegerField(default=0)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Admissions rate-limit bucket",
                "verbose_name_plural": "Admissions rate-limit buckets",
            },
        ),
        migrations.CreateModel(
            name="ApplicationSubmissionToken",
            fields=[
                (
                    "token_id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("consumed_at", models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.RunPython(
            populate_normalized_identity,
            migrations.RunPython.noop,
        ),
        migrations.AddConstraint(
            model_name="application",
            constraint=models.UniqueConstraint(
                fields=(
                    "normalized_academic_year",
                    "normalized_student_name",
                    "normalized_student_surname",
                    "date_of_birth",
                ),
                name="unique_learner_application_per_year",
            ),
        ),
    ]
