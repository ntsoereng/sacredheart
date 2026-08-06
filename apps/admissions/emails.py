from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from apps.core.models import SiteSettings


def send_application_confirmation(application):
    """Send a privacy-conscious receipt after the application is stored."""
    site_settings = SiteSettings.objects.first()
    school_name = (
        site_settings.school_name
        if site_settings and site_settings.school_name
        else "Sacred Heart High School"
    )
    admissions_email = (
        site_settings.admissions_email
        if site_settings and site_settings.admissions_email
        else ""
    )
    context = {
        "application": application,
        "school_name": school_name,
        "admissions_email": admissions_email,
    }
    message = EmailMultiAlternatives(
        subject=f"Application received — {application.reference_number}",
        body=render_to_string("admissions/email/application_confirmation.txt", context),
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[application.parent_guardian_email],
        reply_to=[admissions_email] if admissions_email else None,
    )
    message.attach_alternative(
        render_to_string("admissions/email/application_confirmation.html", context),
        "text/html",
    )
    return message.send(fail_silently=False) == 1
