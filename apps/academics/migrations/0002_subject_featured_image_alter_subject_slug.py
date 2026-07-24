from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("academics", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="subject",
            name="featured_image",
            field=models.ImageField(
                blank=True,
                help_text="A wide image used on subject cards and the subject detail page.",
                null=True,
                upload_to="subjects/",
            ),
        ),
        migrations.AlterField(
            model_name="subject",
            name="slug",
            field=models.SlugField(blank=True, unique=True),
        ),
    ]
