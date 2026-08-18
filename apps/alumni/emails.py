from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import EmailMultiAlternatives, get_connection
from django.template.loader import render_to_string

from apps.core.models import SiteSettings


def send_profile_update_verification(story, verification_url):
    if settings.EMAIL_BACKEND.endswith("smtp.EmailBackend") and (
        not settings.ALUMNI_EMAIL_HOST_USER
        or not settings.ALUMNI_EMAIL_HOST_PASSWORD
    ):
        raise ImproperlyConfigured(
            "Alumni email credentials are required to send profile-update links."
        )

    site_settings = SiteSettings.objects.first()
    school_name = (
        site_settings.school_name
        if site_settings and site_settings.school_name
        else "Sacred Heart High School"
    )
    context = {
        "story": story,
        "school_name": school_name,
        "verification_url": verification_url,
    }
    connection = get_connection(
        backend=settings.EMAIL_BACKEND,
        host=settings.EMAIL_HOST,
        port=settings.EMAIL_PORT,
        username=settings.ALUMNI_EMAIL_HOST_USER,
        password=settings.ALUMNI_EMAIL_HOST_PASSWORD,
        use_tls=settings.EMAIL_USE_TLS,
        use_ssl=settings.EMAIL_USE_SSL,
        timeout=settings.EMAIL_TIMEOUT,
    )
    message = EmailMultiAlternatives(
        subject="Verify your alumni profile update request",
        body=render_to_string(
            "alumni/email/profile_update_verification.txt",
            context,
        ),
        from_email=settings.ALUMNI_DEFAULT_FROM_EMAIL,
        to=[story.email],
        reply_to=(
            [settings.ALUMNI_EMAIL_HOST_USER]
            if settings.ALUMNI_EMAIL_HOST_USER
            else None
        ),
        connection=connection,
    )
    message.attach_alternative(
        render_to_string(
            "alumni/email/profile_update_verification.html",
            context,
        ),
        "text/html",
    )
    return message.send(fail_silently=False) == 1
