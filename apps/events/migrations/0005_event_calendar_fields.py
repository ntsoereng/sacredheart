from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0004_event_featured"),
    ]

    operations = [
        migrations.AlterField(
            model_name="event",
            name="event_date",
            field=models.DateField(verbose_name="start date"),
        ),
        migrations.AddField(
            model_name="event",
            name="end_date",
            field=models.DateField(
                blank=True,
                help_text="Leave blank for a single-day event.",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="event",
            name="start_time",
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="event",
            name="end_time",
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="event",
            name="category",
            field=models.CharField(
                choices=[
                    ("academic", "Academic"),
                    ("admissions", "Admissions"),
                    ("meeting", "Meeting"),
                    ("sport", "Sport"),
                    ("holiday", "Holiday"),
                    ("other", "Other"),
                ],
                default="other",
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="event",
            name="featured",
            field=models.BooleanField(
                default=False,
                help_text="Highlight this event in important-date and planning sections.",
                verbose_name="important / featured",
            ),
        ),
    ]
