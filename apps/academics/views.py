from django.views.generic import DetailView, ListView

from .models import Subject


class SubjectListView(ListView):
    model = Subject
    context_object_name = "subjects"
    template_name = "academics/subject_list.html"

    def get_queryset(self):
        return Subject.objects.filter(is_active=True)


class SubjectDetailView(DetailView):
    model = Subject
    context_object_name = "subject"
    template_name = "academics/subject_detail.html"

    def get_queryset(self):
        return Subject.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["related_subjects"] = (
            Subject.objects.filter(is_active=True)
            .exclude(pk=self.object.pk)[:3]
        )
        return context
