from django.contrib import messages
from django.db.models import Q
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DetailView, ListView, TemplateView

from apps.core.throttling import RateLimitMixin

from .forms import (
    AlumniOpportunitySubmissionForm,
    AlumniStorySubmissionForm,
    MentorshipRequestForm,
)
from .models import AlumniOpportunity, AlumniStory, MentorshipRequest


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
                | Q(industry__icontains=query)
                | Q(current_location__icontains=query)
                | Q(graduation_year__icontains=query)
            )
        if self.request.GET.get("mentors") == "yes":
            queryset = queryset.filter(mentorship_available=True)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["opportunities"] = AlumniOpportunity.objects.filter(
            Q(deadline__isnull=True) | Q(deadline__gte=timezone.localdate()),
            status="approved",
            alumni__status="approved",
            alumni__consent_to_publish=True,
        ).select_related("alumni")[:6]
        context["mentor_count"] = AlumniStory.objects.filter(
            status="approved",
            consent_to_publish=True,
            mentorship_available=True,
        ).count()
        return context


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
        messages.success(self.request, "Your alumni directory profile has been submitted.")
        return response


class AlumniStorySuccessView(TemplateView):
    template_name = "alumni/story_success.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["alumni_name"] = self.request.session.get("alumni_submission_name")
        return context


class AlumniOpportunityCreateView(RateLimitMixin, CreateView):
    rate_limit_count = 5
    rate_limit_window = 3600
    rate_limit_scope = "alumni-opportunity-submission"
    model = AlumniOpportunity
    form_class = AlumniOpportunitySubmissionForm
    template_name = "alumni/opportunity_form.html"
    success_url = reverse_lazy("alumni-opportunity-success")

    def form_valid(self, form):
        messages.success(self.request, "The opportunity has been sent for review.")
        return super().form_valid(form)


class AlumniOpportunityListView(ListView):
    model = AlumniOpportunity
    template_name = "alumni/opportunity_list.html"
    context_object_name = "opportunities"
    paginate_by = 12

    def get_queryset(self):
        queryset = AlumniOpportunity.objects.filter(
            Q(deadline__isnull=True) | Q(deadline__gte=timezone.localdate()),
            status="approved",
            alumni__status="approved",
            alumni__consent_to_publish=True,
        ).select_related("alumni")
        opportunity_type = self.request.GET.get("type", "").strip()
        valid_types = {value for value, _ in AlumniOpportunity.TYPE_CHOICES}
        if opportunity_type in valid_types:
            queryset = queryset.filter(opportunity_type=opportunity_type)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["opportunity_types"] = AlumniOpportunity.TYPE_CHOICES
        return context


class MentorshipRequestCreateView(RateLimitMixin, CreateView):
    rate_limit_count = 5
    rate_limit_window = 3600
    rate_limit_scope = "alumni-mentorship-request"
    model = MentorshipRequest
    form_class = MentorshipRequestForm
    template_name = "alumni/mentorship_form.html"
    success_url = reverse_lazy("alumni-mentorship-success")

    def get_initial(self):
        initial = super().get_initial()
        mentor_id = self.request.GET.get("mentor", "").strip()
        if mentor_id.isdigit():
            initial["mentor"] = mentor_id
        return initial

    def form_valid(self, form):
        messages.success(self.request, "Your mentorship request has been sent privately to the school.")
        return super().form_valid(form)


class AlumniActionSuccessView(TemplateView):
    template_name = "alumni/action_success.html"
