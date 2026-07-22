from apps.core.models import ContactMessage
from apps.admissions.models import Application
from apps.alumni.models import AlumniStory


def portal_stats(request):
    """
    Portal-wide statistics available in all portal templates.
    """

    return {
        "portal_unread_messages": (
            ContactMessage.objects
            .filter(is_read=False)
            .count()
        ),

        "portal_total_messages": (
            ContactMessage.objects
            .count()
        ),

        "portal_total_applications": (
            Application.objects
            .count()
        ),

        "portal_new_applications": (
            Application.objects
            .filter(status="new")
            .count()
        ),

        "portal_pending_alumni": (
            AlumniStory.objects
            .filter(status="pending")
            .count()
        ),
    }
