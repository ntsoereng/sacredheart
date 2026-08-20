from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("alumni", "0003_alumniprofileupdateverification"),
    ]

    operations = [
        migrations.AlterField(
            model_name="alumnistory",
            name="life_story",
            field=models.TextField(
                help_text=(
                    "Briefly describe your journey, work, studies or community "
                    "contribution."
                ),
                verbose_name="Profile summary",
            ),
        ),
    ]
