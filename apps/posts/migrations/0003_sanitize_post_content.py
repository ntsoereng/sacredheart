from django.db import migrations


def sanitize_existing_posts(apps, schema_editor):
    from apps.posts.content import sanitize_post_html

    Post = apps.get_model("posts", "Post")
    for post in Post.objects.all().only("pk", "content").iterator():
        cleaned = sanitize_post_html(post.content)
        if cleaned != post.content:
            Post.objects.filter(pk=post.pk).update(content=cleaned)


class Migration(migrations.Migration):
    dependencies = [
        ("posts", "0002_post_featured"),
    ]

    operations = [
        migrations.RunPython(sanitize_existing_posts, migrations.RunPython.noop),
    ]
