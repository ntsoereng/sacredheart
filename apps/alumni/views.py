from django.contrib import messages
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, TemplateView

from apps.core.throttling import RateLimitMixin

from .forms import AlumniStorySubmissionForm
from .models import AlumniStory


class AlumniStoryListView(ListView):
    model = AlumniStory
    template_name = "alumni/story_list.html"
    context_object_name = "stories"
    paginate_by = 9

    def get_queryset(self):
        queryset = AlumniStory.objects.filter(
            status="approved",
            consent_to_publish=True,
        )
        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = queryset.filter(
                Q(full_name__icontains=query)
                | Q(occupation__icontains=query)
                | Q(graduation_year__icontains=query)
            )
        return queryset


class AlumniStoryDetailView(DetailView):
    model = AlumniStory
    template_name = "alumni/story_detail.html"
    context_object_name = "story"

    def get_queryset(self):
        return AlumniStory.objects.filter(
            status="approved",
            consent_to_publish=True,
        )


class AlumniStoryCreateView(RateLimitMixin, CreateView):
    rate_limit_count = 5
    rate_limit_window = 3600
    rate_limit_scope = "alumni-submission"
    model = AlumniStory
    form_class = AlumniStorySubmissionForm
    template_name = "alumni/story_form.html"
    success_url = reverse_lazy("alumni-success")

    def form_valid(self, form):
        response = super().form_valid(form)
        self.request.session["alumni_submission_name"] = self.object.full_name
        messages.success(self.request, "Your alumni story has been submitted.")
        return response


class AlumniStorySuccessView(TemplateView):
    template_name = "alumni/story_success.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["alumni_name"] = self.request.session.get("alumni_submission_name")
        return context
