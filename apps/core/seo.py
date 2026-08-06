import json

from django.utils.html import strip_tags
from django.utils.safestring import mark_safe


def json_ld(data):
    """Serialize trusted schema data without allowing a script-closing payload."""
    return mark_safe(
        json.dumps(data, ensure_ascii=False)
        .replace("&", "\\u0026")
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
    )


def article_schema(request, post):
    data = {
        "@context": "https://schema.org",
        "@type": "NewsArticle",
        "headline": post.title,
        "description": strip_tags(post.summary),
        "datePublished": post.created_at.isoformat(),
        "dateModified": post.updated_at.isoformat(),
        "mainEntityOfPage": request.build_absolute_uri(),
    }
    if post.featured_image:
        data["image"] = request.build_absolute_uri(post.featured_image.url)
    return json_ld(data)


def event_schema(request, event):
    data = {
        "@context": "https://schema.org",
        "@type": "Event",
        "name": event.title,
        "description": strip_tags(event.description),
        "startDate": event.event_date.isoformat(),
        "url": request.build_absolute_uri(),
        "eventStatus": "https://schema.org/EventScheduled",
        "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
    }
    if event.location:
        data["location"] = {"@type": "Place", "name": event.location}
    if event.image:
        data["image"] = request.build_absolute_uri(event.image.url)
    return json_ld(data)
