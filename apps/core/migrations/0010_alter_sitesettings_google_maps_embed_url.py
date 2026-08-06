from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0009_extracurricularactivity"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sitesettings",
            name="google_maps_embed_url",
            field=models.URLField(
                blank=True,
                help_text=(
                    "Paste the Google Maps embed URL or the complete iframe code from "
                    "Share > Embed a map. Ordinary maps.app.goo.gl share links cannot be embedded."
                ),
                max_length=2000,
            ),
        ),
    ]
