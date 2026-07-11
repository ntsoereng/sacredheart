from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic import FormView, TemplateView
from django.shortcuts import render
from django.db.models import Q
from apps.core.forms import ContactForm
from apps.posts.models import Post
from apps.events.models import Event
from apps.pages.models import Page
from apps.staff.models import StaffMember


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
            .filter(is_published=True)
            [:3]    
        )
        
        context["featured_event"] = (
            Event.objects.filter(
                is_published=True,
                featured=True
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


        return context


class AboutView(TemplateView):

    template_name = "core/about.html"


class DonationsView(TemplateView):

    template_name = "core/donations.html"


class SearchView(TemplateView):

    template_name = "search/results.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        query = self.request.GET.get("q", "").strip()
        
        if not query:
            context["pages"] = Page.objects.none()
            context["posts"] = Post.objects.none()
            context["events"] = Event.objects.none()

            return context

        context["query"] = query

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
