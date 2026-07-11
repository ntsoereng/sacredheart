from django.views.generic import TemplateView

from .models import StaffMember


class StaffListView(TemplateView):
    template_name = "staff/staff_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        active_staff = StaffMember.objects.filter(is_active=True)
        context["principal"] = active_staff.filter(is_principal=True).first()
        context["staff_members"] = active_staff.filter(is_principal=False)

        return context
