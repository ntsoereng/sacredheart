import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(
            name="Vacancy",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("job_title", models.CharField(max_length=200)),
                ("slug", models.SlugField(blank=True, max_length=240, unique=True)),
                ("department", models.CharField(max_length=200, verbose_name="Department / subject")),
                ("employment_type", models.CharField(choices=[("full_time", "Full-time"), ("part_time", "Part-time"), ("temporary", "Temporary"), ("contract", "Contract")], max_length=20)),
                ("location", models.CharField(default="Sacred Heart High School", max_length=200)),
                ("application_deadline", models.DateField()),
                ("expected_start_date", models.DateField(blank=True, null=True)),
                ("status", models.CharField(choices=[("open", "Open"), ("closed", "Closed"), ("filled", "Filled")], default="open", max_length=20)),
                ("reference_number", models.CharField(blank=True, max_length=100)),
                ("short_summary", models.TextField(help_text="A 1–3 sentence overview for listings.")),
                ("job_description", models.TextField()),
                ("minimum_qualifications", models.TextField()),
                ("experience_requirements", models.TextField()),
                ("skills_competencies", models.TextField(verbose_name="Skills / competencies")),
                ("additional_requirements", models.TextField(blank=True)),
                ("application_instructions", models.TextField()),
                ("contact_email", models.EmailField(default="careers@sacredheart.ac.ls", max_length=254)),
                ("contact_person", models.CharField(blank=True, max_length=200)),
                ("is_published", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="created_vacancies", to=settings.AUTH_USER_MODEL)),
            ],
            options={"verbose_name_plural": "vacancies", "ordering": ("application_deadline", "job_title")},
        )
    ]
