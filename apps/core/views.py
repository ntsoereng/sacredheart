from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic import DetailView, FormView, ListView, TemplateView
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Q
from django.utils import timezone
from apps.alumni.models import AlumniStory
from apps.academics.models import Subject
from apps.core.forms import ContactForm
from apps.posts.models import Post
from apps.events.models import Event
from apps.pages.models import Page
from apps.staff.models import StaffMember
from apps.core.models import ExtracurricularActivity, SiteSettings


def favicon(request):
    site_settings = SiteSettings.objects.only("favicon").first()
    if site_settings and site_settings.favicon:
        return redirect(site_settings.favicon.url)
    return redirect("/")


def robots_txt(request):
    sitemap_url = request.build_absolute_uri("/sitemap.xml")
    content = (
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /admin/\n"
        "Disallow: /dashboard/\n"
        "Disallow: /accounts/\n"
        "Disallow: /search/\n\n"
        f"Sitemap: {sitemap_url}\n"
    )
    return HttpResponse(content, content_type="text/plain")


class HomeView(TemplateView):

    template_name = "core/home.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["latest_posts"] = (
            Post.objects
            .filter(is_published=True)
            [:3]
        )
        
        context["upcoming_events"] = (
            Event.objects
            .filter(
                is_published=True,
                event_date__gte=timezone.localdate(),
            )
            [:3]    
        )
        
        context["featured_event"] = (
            Event.objects.filter(
                is_published=True,
                featured=True,
                event_date__gte=timezone.localdate(),
            )
            .order_by("event_date")
            .first()
        )

        context["principal"] = (
            StaffMember.objects.filter(
                is_active=True,
                is_principal=True,
            ).first()
        )

        context["alumni_stories"] = (
            AlumniStory.objects
            .filter(status="approved", consent_to_publish=True)
            [:3]
        )

        context["featured_activities"] = (
            ExtracurricularActivity.objects
            .filter(is_published=True, is_featured=True)
            [:3]
        )

        return context


class AboutView(TemplateView):

    template_name = "core/about.html"


class DonationsView(TemplateView):

    template_name = "core/donations.html"


class ActivityListView(ListView):
    model = ExtracurricularActivity
    template_name = "core/activity_list.html"
    context_object_name = "activities"
    paginate_by = 12
    queryset = ExtracurricularActivity.objects.filter(is_published=True)


class ActivityDetailView(DetailView):
    model = ExtracurricularActivity
    template_name = "core/activity_detail.html"
    context_object_name = "activity"

    def get_object(self):
        return get_object_or_404(
            ExtracurricularActivity,
            slug=self.kwargs["slug"],
            is_published=True,
        )


class PrivacyPolicyView(TemplateView):
    template_name = "core/privacy_policy.html"


class TermsOfUseView(TemplateView):
    template_name = "core/terms_of_use.html"


class SearchView(TemplateView):

    template_name = "search/results.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        query = self.request.GET.get("q", "").strip()
        context["query"] = query
        
        if not query:
            context["pages"] = Page.objects.none()
            context["posts"] = Post.objects.none()
            context["events"] = Event.objects.none()
            context["activities"] = ExtracurricularActivity.objects.none()
            context["subjects"] = Subject.objects.none()
            context["staff_members"] = StaffMember.objects.none()
            context["alumni_stories"] = AlumniStory.objects.none()

            return context

        context["pages"] = (
            Page.objects
            .filter(
                is_published=True
            )
            .filter(
                Q(title__icontains=query) |
                Q(content__icontains=query)
            )
        )

        context["posts"] = (
            Post.objects
            .filter(
                is_published=True
            )
            .filter(
                Q(title__icontains=query) |
                Q(summary__icontains=query) |
                Q(content__icontains=query)
            )
        )

        context["events"] = (
            Event.objects
            .filter(
                is_published=True
            )
            .filter(
                Q(title__icontains=query) |
                Q(description__icontains=query)
            )
        )

        context["activities"] = (
            ExtracurricularActivity.objects
            .filter(is_published=True)
            .filter(
                Q(name__icontains=query)
                | Q(short_description__icontains=query)
                | Q(description__icontains=query)
                | Q(achievements__icontains=query)
            )
        )

        context["subjects"] = (
            Subject.objects
            .filter(is_active=True)
            .filter(
                Q(name__icontains=query)
                | Q(description__icontains=query)
            )
        )

        context["staff_members"] = (
            StaffMember.objects
            .filter(is_active=True)
            .filter(
                Q(full_name__icontains=query)
                | Q(role__icontains=query)
                | Q(short_bio__icontains=query)
                | Q(motto__icontains=query)
                | Q(subjects__name__icontains=query)
            )
            .distinct()
        )

        context["alumni_stories"] = (
            AlumniStory.objects
            .filter(status="approved", consent_to_publish=True)
            .filter(
                Q(full_name__icontains=query)
                | Q(occupation__icontains=query)
                | Q(current_location__icontains=query)
                | Q(life_story__icontains=query)
                | Q(school_memories__icontains=query)
                | Q(message_to_students__icontains=query)
            )
        )

        return context   
    
    
    
class ContactView(FormView):

    template_name = "core/contact.html"

    form_class = ContactForm

    success_url = reverse_lazy(
        "contact"
    )

    def form_valid(self, form):

        form.save()

        messages.success(
            self.request,
            "Thank you. Your message has been received. We will get back to you shortly."
        )

        return super().form_valid(form)  
    
    
def test_404(request):
    return render(
        request,
        "404.html",
        status=404
    )
