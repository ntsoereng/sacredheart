from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("admissions", "0007_application_parent_guardian_email"),
    ]

    operations = [
        migrations.AddField(
            model_name="application",
            name="nationality",
            field=models.CharField(default="Lesotho", max_length=100),
        ),
        migrations.AddField(
            model_name="application",
            name="student_candidate_number",
            field=models.CharField(max_length=100, verbose_name="Student candidate number"),
        ),
    ]
