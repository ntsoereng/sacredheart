from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0010_alter_sitesettings_google_maps_embed_url"),
    ]

    operations = [
        migrations.AddField(
            model_name="sitesettings",
            name="facebook_url",
            field=models.URLField(blank=True, max_length=500, verbose_name="Facebook page URL"),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="instagram_url",
            field=models.URLField(blank=True, max_length=500, verbose_name="Instagram profile URL"),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="youtube_url",
            field=models.URLField(blank=True, max_length=500, verbose_name="YouTube channel URL"),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="tiktok_url",
            field=models.URLField(blank=True, max_length=500, verbose_name="TikTok profile URL"),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="x_url",
            field=models.URLField(blank=True, max_length=500, verbose_name="X (Twitter) profile URL"),
        ),
    ]
