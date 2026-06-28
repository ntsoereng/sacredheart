from apps.core.models import ContactMessage
from apps.admissions.models import Application


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
    }