import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("alumni", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="alumnistory",
            options={
                "ordering": ("-submitted_at",),
                "verbose_name": "Alumni profile",
                "verbose_name_plural": "Alumni profiles",
            },
        ),
        migrations.AlterField(
            model_name="alumnistory",
            name="life_story",
            field=models.TextField(
                blank=True,
                help_text="Briefly describe your journey, work, studies or community contribution.",
                verbose_name="Profile summary",
            ),
        ),
        migrations.AlterField(
            model_name="alumnistory",
            name="consent_to_publish",
            field=models.BooleanField(
                default=False,
                help_text="I consent to my directory profile and photo being published on this website.",
            ),
        ),
        migrations.AddField(
            model_name="alumnistory",
            name="industry",
            field=models.CharField(
                blank=True,
                help_text="For example: engineering, education, health, finance or the arts.",
                max_length=150,
            ),
        ),
        migrations.AddField(
            model_name="alumnistory",
            name="mentorship_available",
            field=models.BooleanField(
                default=False,
                help_text="I am open to being contacted by the school about mentoring.",
            ),
        ),
        migrations.AddField(
            model_name="alumnistory",
            name="mentor_career_guidance",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="alumnistory",
            name="mentor_university_applications",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="alumnistory",
            name="mentor_subject_choices",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="alumnistory",
            name="mentor_entrepreneurship",
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name="MentorshipRequest",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("full_name", models.CharField(max_length=200)),
                ("email", models.EmailField(max_length=254)),
                ("phone", models.CharField(blank=True, max_length=30)),
                ("audience", models.CharField(choices=[("learner", "Current Sacred Heart learner"), ("graduate", "Recent Sacred Heart graduate")], max_length=20)),
                ("focus_area", models.CharField(choices=[("career", "Career guidance"), ("university", "University applications"), ("subjects", "Subject and career choices"), ("entrepreneurship", "Entrepreneurship advice")], max_length=20)),
                ("goals", models.TextField(help_text="Tell us what support you are looking for.")),
                ("consent_to_contact", models.BooleanField(default=False)),
                ("is_handled", models.BooleanField(default=False)),
                ("staff_notes", models.TextField(blank=True)),
                ("submitted_at", models.DateTimeField(auto_now_add=True)),
                ("mentor", models.ForeignKey(blank=True, limit_choices_to={"mentorship_available": True, "status": "approved"}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="mentorship_requests", to="alumni.alumnistory")),
            ],
            options={"ordering": ("-submitted_at",)},
        ),
        migrations.CreateModel(
            name="AlumniOpportunity",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("opportunity_type", models.CharField(choices=[("scholarship", "Scholarship"), ("competition", "Competition"), ("training", "Training opportunity")], max_length=20)),
                ("title", models.CharField(max_length=200)),
                ("provider", models.CharField(blank=True, max_length=200)),
                ("summary", models.TextField(help_text="Explain who is eligible and what is offered.")),
                ("application_url", models.URLField(blank=True)),
                ("deadline", models.DateField(blank=True, null=True)),
                ("status", models.CharField(choices=[("pending", "Pending review"), ("approved", "Approved"), ("rejected", "Not approved")], default="pending", max_length=20)),
                ("staff_notes", models.TextField(blank=True)),
                ("reviewed_at", models.DateTimeField(blank=True, null=True)),
                ("submitted_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("alumni", models.ForeignKey(limit_choices_to={"consent_to_publish": True, "status": "approved"}, on_delete=django.db.models.deletion.CASCADE, related_name="opportunities", to="alumni.alumnistory")),
                ("reviewed_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="reviewed_alumni_opportunities", to=settings.AUTH_USER_MODEL)),
            ],
            options={"verbose_name_plural": "Alumni opportunities", "ordering": ("deadline", "-submitted_at")},
        ),
    ]
