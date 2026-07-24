from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("academics", "0002_subject_featured_image_alter_subject_slug"),
        ("staff", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="staffmember",
            name="subjects",
            field=models.ManyToManyField(
                blank=True,
                help_text="Optional: select the subjects this staff member teaches.",
                related_name="teachers",
                to="academics.subject",
            ),
        ),
    ]
