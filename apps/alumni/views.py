import hmac
import logging
from datetime import timedelta

from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponseGone
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DetailView, FormView, ListView, TemplateView

from apps.core.models import ContactMessage
from apps.core.throttling import PublicFormProtectionMixin

from .emails import send_profile_update_verification
from .forms import (
    AlumniOpportunitySubmissionForm,
    AlumniProfileUpdateRequestForm,
    AlumniProfileUpdateVerificationForm,
    AlumniStorySubmissionForm,
)
from .models import (
    AlumniOpportunity,
    AlumniProfileUpdateVerification,
    AlumniStory,
)


logger = logging.getLogger(__name__)


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
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["opportunities"] = AlumniOpportunity.objects.filter(
            Q(deadline__isnull=True) | Q(deadline__gte=timezone.localdate()),
            status="approved",
            alumni__status="approved",
            alumni__consent_to_publish=True,
        ).select_related("alumni")[:6]
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


class AlumniProfileUpdateRequestView(PublicFormProtectionMixin, FormView):
    rate_limit_count = 5
    rate_limit_window = 3600
    rate_limit_scope = "alumni-profile-update-request"
    form_class = AlumniProfileUpdateVerificationForm
    template_name = "alumni/profile_update_verify_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.story = get_object_or_404(
            AlumniStory,
            slug=kwargs["slug"],
            status="approved",
            consent_to_publish=True,
        )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["story"] = self.story
        return context

    def get_success_url(self):
        return reverse(
            "alumni-profile-update-sent",
            kwargs={"slug": self.story.slug},
        )

    def protected_form_valid(self, form):
        supplied_email = form.cleaned_data["email"].strip().casefold()
        stored_email = self.story.email.strip().casefold()
        email_matches = hmac.compare_digest(
            supplied_email.encode("utf-8"),
            stored_email.encode("utf-8"),
        )
        recent_cutoff = timezone.now() - timedelta(minutes=10)
        daily_cutoff = timezone.now() - timedelta(days=1)
        recent_verification_exists = (
            AlumniProfileUpdateVerification.objects.filter(
                alumni=self.story,
                created_at__gte=recent_cutoff,
            ).exists()
        )
        daily_verification_count = (
            AlumniProfileUpdateVerification.objects.filter(
                alumni=self.story,
                created_at__gte=daily_cutoff,
            ).count()
        )

        if (
            email_matches
            and not recent_verification_exists
            and daily_verification_count < 5
        ):
            verification, raw_token = AlumniProfileUpdateVerification.issue(
                self.story
            )
            verification_url = self.request.build_absolute_uri(
                reverse(
                    "alumni-profile-update-confirm",
                    kwargs={"slug": self.story.slug, "token": raw_token},
                )
            )

            def deliver_verification_email():
                try:
                    delivered = send_profile_update_verification(
                        self.story,
                        verification_url,
                    )
                except Exception:
                    logger.exception(
                        "Could not send an alumni profile update verification email."
                    )
                    delivered = False
                if not delivered:
                    AlumniProfileUpdateVerification.objects.filter(
                        pk=verification.pk
                    ).delete()

            transaction.on_commit(deliver_verification_email)

        return super().protected_form_valid(form)


class AlumniProfileUpdateSentView(TemplateView):
    template_name = "alumni/profile_update_verification_sent.html"

    def dispatch(self, request, *args, **kwargs):
        self.story = get_object_or_404(
            AlumniStory,
            slug=kwargs["slug"],
            status="approved",
            consent_to_publish=True,
        )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["story"] = self.story
        return context


class AlumniVerifiedProfileUpdateView(PublicFormProtectionMixin, FormView):
    rate_limit_count = 5
    rate_limit_window = 3600
    rate_limit_scope = "verified-alumni-profile-update"
    form_class = AlumniProfileUpdateRequestForm
    template_name = "alumni/profile_update_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.story = get_object_or_404(
            AlumniStory,
            slug=kwargs["slug"],
            status="approved",
            consent_to_publish=True,
        )
        token_digest = AlumniProfileUpdateVerification.digest_token(
            kwargs["token"]
        )
        self.verification = (
            AlumniProfileUpdateVerification.objects.filter(
                alumni=self.story,
                token_digest=token_digest,
            ).first()
        )
        response = super().dispatch(request, *args, **kwargs)
        response["Referrer-Policy"] = "no-referrer"
        response["X-Robots-Tag"] = "noindex, nofollow, noarchive"
        return response

    def protected_dispatch(self, request, *args, **kwargs):
        if not self.verification or not self.verification.is_available:
            return render(
                request,
                "alumni/profile_update_link_invalid.html",
                {"story": self.story},
                status=410,
            )
        return super().protected_dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["story"] = self.story
        context["seo_canonical_url"] = self.request.build_absolute_uri(
            reverse("alumni-detail", kwargs={"slug": self.story.slug})
        )
        return context

    def get_success_url(self):
        return reverse("alumni-detail", kwargs={"slug": self.story.slug})

    def protected_form_valid(self, form):
        consumed = AlumniProfileUpdateVerification.objects.filter(
            pk=self.verification.pk,
            used_at__isnull=True,
            expires_at__gt=timezone.now(),
        ).update(used_at=timezone.now())
        if consumed != 1:
            return HttpResponseGone("This verification link is no longer available.")

        update_label = dict(form.fields["update_type"].choices)[
            form.cleaned_data["update_type"]
        ]
        profile_url = self.request.build_absolute_uri(
            reverse("alumni-detail", kwargs={"slug": self.story.slug})
        )
        ContactMessage.objects.create(
            name=self.story.full_name,
            email=self.story.email,
            subject=(
                f"Verified alumni profile update: {self.story.full_name} "
                f"(Class of {self.story.graduation_year})"
            ),
            message=(
                f"Email ownership verified by a single-use link.\n"
                f"Profile: {self.story.full_name}, Class of "
                f"{self.story.graduation_year}\n"
                f"Public profile: {profile_url}\n"
                f"Update category: {update_label}\n\n"
                f"Requested change:\n{form.cleaned_data['message']}"
            ),
        )
        messages.success(
            self.request,
            "Your verified profile update request has been sent for staff review.",
        )
        return super().protected_form_valid(form)


class AlumniStoryCreateView(PublicFormProtectionMixin, CreateView):
    rate_limit_count = 5
    rate_limit_window = 3600
    rate_limit_scope = "alumni-submission"
    model = AlumniStory
    form_class = AlumniStorySubmissionForm
    template_name = "alumni/story_form.html"
    success_url = reverse_lazy("alumni-success")

    def form_valid(self, form):
        response = super().form_valid(form)
        if response.status_code < 400:
            self.request.session["alumni_submission_name"] = self.object.full_name
            messages.success(
                self.request,
                "Your alumni directory profile has been submitted.",
            )
        return response


class AlumniStorySuccessView(TemplateView):
    template_name = "alumni/story_success.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["alumni_name"] = self.request.session.get("alumni_submission_name")
        return context


class AlumniOpportunityCreateView(PublicFormProtectionMixin, CreateView):
    rate_limit_count = 5
    rate_limit_window = 3600
    rate_limit_scope = "alumni-opportunity-submission"
    model = AlumniOpportunity
    form_class = AlumniOpportunitySubmissionForm
    template_name = "alumni/opportunity_form.html"
    success_url = reverse_lazy("alumni-opportunity-success")

    def form_valid(self, form):
        response = super().form_valid(form)
        if response.status_code < 400:
            messages.success(self.request, "The opportunity has been sent for review.")
        return response


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


class AlumniActionSuccessView(TemplateView):
    template_name = "alumni/action_success.html"
