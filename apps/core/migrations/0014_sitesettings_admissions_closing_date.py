from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0013_restore_admissions_pdf_extensions"),
    ]

    operations = [
        migrations.AddField(
            model_name="sitesettings",
            name="admissions_closing_date",
            field=models.DateField(
                blank=True,
                help_text=(
                    "Displayed on the public application form while admissions are open."
                ),
                null=True,
            ),
        ),
    ]
