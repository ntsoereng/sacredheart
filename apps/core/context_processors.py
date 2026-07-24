import json

from django.utils.safestring import mark_safe

from .models import SiteSettings


def site_settings(request):
    settings = SiteSettings.objects.first()
    school_name = settings.school_name if settings else "Sacred Heart High School"
    description = (
        settings.tagline
        if settings and settings.tagline
        else "Sacred Heart High School nurtures academic excellence, character, faith, and service in a caring school community."
    )
    canonical_url = request.build_absolute_uri(request.path)

    organization = {
        "@context": "https://schema.org",
        "@type": "HighSchool",
        "name": school_name,
        "url": request.build_absolute_uri("/"),
        "description": description,
    }
    if settings:
        if settings.logo:
            organization["logo"] = request.build_absolute_uri(settings.logo.url)
        if settings.email:
            organization["email"] = settings.email
        if settings.phone:
            organization["telephone"] = settings.phone
        if settings.address:
            organization["address"] = {
                "@type": "PostalAddress",
                "streetAddress": settings.address,
                "addressCountry": "LS",
            }

    return {
        "site_settings": settings,
        "seo_school_name": school_name,
        "seo_default_description": description,
        "seo_canonical_url": canonical_url,
        "seo_default_image": (
            request.build_absolute_uri(settings.logo.url)
            if settings and settings.logo
            else ""
        ),
        "organization_schema": mark_safe(
            json.dumps(organization, ensure_ascii=False)
            .replace("&", "\\u0026")
            .replace("<", "\\u003c")
            .replace(">", "\\u003e")
        ),
    }
