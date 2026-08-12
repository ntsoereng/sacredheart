from django.core.validators import FileExtensionValidator
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0011_sitesettings_social_media"),
    ]

    operations = [
        migrations.AddField(
            model_name="sitesettings",
            name="admissions_list",
            field=models.FileField(
                blank=True,
                help_text="Upload the approved admissions list as a PDF when it is ready.",
                upload_to="admissions/lists/",
                validators=[FileExtensionValidator(allowed_extensions=["pdf"])],
            ),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="prospectus",
            field=models.FileField(
                blank=True,
                help_text="Upload the current school prospectus as a PDF.",
                upload_to="admissions/prospectuses/",
                validators=[FileExtensionValidator(allowed_extensions=["pdf"])],
            ),
        ),
    ]
