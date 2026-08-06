from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("admissions", "0006_application_reviewer_and_notes"),
    ]

    operations = [
        migrations.AddField(
            model_name="application",
            name="parent_guardian_email",
            field=models.EmailField(
                blank=True,
                max_length=254,
                verbose_name="Parent or guardian email",
            ),
        ),
    ]
