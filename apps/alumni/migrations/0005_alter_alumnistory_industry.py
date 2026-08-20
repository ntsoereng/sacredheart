from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("alumni", "0004_alter_alumnistory_life_story"),
    ]

    operations = [
        migrations.AlterField(
            model_name="alumnistory",
            name="industry",
            field=models.CharField(
                help_text=(
                    "For example: engineering, education, health, finance or the arts."
                ),
                max_length=150,
            ),
        ),
    ]
