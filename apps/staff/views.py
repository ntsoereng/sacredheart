from django.views.generic import DetailView, TemplateView

from .models import StaffMember


class StaffListView(TemplateView):
    template_name = "staff/staff_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        active_staff = StaffMember.objects.filter(is_active=True).prefetch_related(
            "subjects"
        )
        context["principal"] = active_staff.filter(is_principal=True).first()
        context["staff_members"] = active_staff.filter(is_principal=False)

        return context


class StaffDetailView(DetailView):
    model = StaffMember
    context_object_name = "staff_member"
    template_name = "staff/staff_detail.html"

    def get_queryset(self):
        return StaffMember.objects.filter(is_active=True).prefetch_related("subjects")
