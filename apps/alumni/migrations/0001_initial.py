import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(
            name="AlumniStory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("full_name", models.CharField(max_length=200)),
                ("graduation_year", models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1900), django.core.validators.MaxValueValidator(2100)])),
                ("email", models.EmailField(help_text="Kept private and used only for follow-up.", max_length=254)),
                ("phone", models.CharField(blank=True, help_text="Kept private and used only for follow-up.", max_length=30)),
                ("current_location", models.CharField(blank=True, max_length=150)),
                ("occupation", models.CharField(blank=True, max_length=200)),
                ("profile_photo", models.ImageField(blank=True, null=True, upload_to="alumni/")),
                ("life_story", models.TextField(help_text="Tell us about your journey since leaving Sacred Heart.")),
                ("school_memories", models.TextField(blank=True, help_text="Share a favourite memory from your time at Sacred Heart.")),
                ("message_to_students", models.TextField(blank=True, help_text="Optional advice or encouragement for current learners.")),
                ("consent_to_publish", models.BooleanField(default=False, help_text="I consent to my story and photo being published on this website.")),
                ("status", models.CharField(choices=[("pending", "Pending review"), ("approved", "Approved"), ("rejected", "Not approved")], default="pending", max_length=20)),
                ("staff_notes", models.TextField(blank=True)),
                ("reviewed_at", models.DateTimeField(blank=True, null=True)),
                ("slug", models.SlugField(blank=True, max_length=240, unique=True)),
                ("submitted_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("reviewed_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="reviewed_alumni_stories", to=settings.AUTH_USER_MODEL)),
            ],
            options={"verbose_name_plural": "Alumni stories", "ordering": ("-submitted_at",)},
        ),
    ]
