from apps.core.models import ContactMessage
from apps.admissions.models import Application
from apps.alumni.models import AlumniStory


def portal_stats(request):
    """
    Portal-wide statistics available in all portal templates.
    """

    user = getattr(request, "user", None)
    if not user or not user.is_authenticated or not user.is_staff:
        return {}

    context = {}
    if user.has_perm("core.view_contactmessage"):
        context["portal_unread_messages"] = ContactMessage.objects.filter(
            is_read=False
        ).count()
        context["portal_total_messages"] = ContactMessage.objects.count()
    if user.has_perm("admissions.view_application"):
        context["portal_total_applications"] = Application.objects.count()
        context["portal_new_applications"] = Application.objects.filter(
            status="new"
        ).count()
    if user.has_perm("alumni.view_alumnistory"):
        context["portal_pending_alumni"] = AlumniStory.objects.filter(
            status="pending"
        ).count()
    return context
