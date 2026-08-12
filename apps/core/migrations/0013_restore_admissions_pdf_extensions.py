from pathlib import PurePosixPath

from django.db import migrations


PDF_HEADER = b"%PDF-"


def restore_pdf_extensions(apps, schema_editor):
    SiteSettings = apps.get_model("core", "SiteSettings")

    for settings in SiteSettings.objects.all():
        changed_fields = []
        for field_name in ("admissions_list", "prospectus"):
            document = getattr(settings, field_name)
            old_name = document.name
            if not old_name or not old_name.lower().endswith(".bin"):
                continue

            storage = document.storage
            try:
                with storage.open(old_name, "rb") as source:
                    if source.read(len(PDF_HEADER)) != PDF_HEADER:
                        continue
                    source.seek(0)
                    path = PurePosixPath(old_name)
                    new_name = str(path.with_suffix(".pdf"))
                    saved_name = storage.save(new_name, source)
            except OSError:
                continue

            setattr(settings, field_name, saved_name)
            changed_fields.append(field_name)
            storage.delete(old_name)

        if changed_fields:
            settings.save(update_fields=changed_fields)


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0012_sitesettings_admissions_documents"),
    ]

    operations = [
        migrations.RunPython(restore_pdf_extensions, migrations.RunPython.noop),
    ]
