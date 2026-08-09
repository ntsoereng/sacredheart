from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("staff", "0003_remove_conditional_principal_constraint"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="staffmember",
            name="user",
            field=models.OneToOneField(
                blank=True,
                help_text="Login account associated with this staff profile.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="staff_profile",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
