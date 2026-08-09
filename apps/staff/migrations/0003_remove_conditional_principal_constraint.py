from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("staff", "0002_staffmember_subjects"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="staffmember",
            name="only_one_principal",
        ),
    ]
