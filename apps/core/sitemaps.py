from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from apps.academics.models import Subject
from apps.alumni.models import AlumniStory
from apps.events.models import Event
from apps.pages.models import Page
from apps.posts.models import Post
from apps.core.models import ExtracurricularActivity


class StaticViewSitemap(Sitemap):
    priority = 0.7
    changefreq = "weekly"

    def items(self):
        return [
            "home",
            "about-us",
            "post-list",
            "event-list",
            "subject-list",
            "activity-list",
            "staff-list",
            "alumni-list",
            "contact",
            "donations",
        ]

    def location(self, item):
        return reverse(item)

    def priority(self, item):
        return 1.0 if item == "home" else 0.7


class PostSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.8

    def items(self):
        return Post.objects.filter(is_published=True)

    def lastmod(self, item):
        return item.updated_at

    def location(self, item):
        return reverse("post-detail", kwargs={"slug": item.slug})


class EventSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Event.objects.filter(is_published=True)

    def lastmod(self, item):
        return item.created_at

    def location(self, item):
        return reverse("event-detail", kwargs={"slug": item.slug})


class SubjectSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.7

    def items(self):
        return Subject.objects.filter(is_active=True)

    def lastmod(self, item):
        return item.updated_at

    def location(self, item):
        return reverse("subject-detail", kwargs={"slug": item.slug})


class PageSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return Page.objects.filter(is_published=True)

    def lastmod(self, item):
        return item.updated_at

    def location(self, item):
        return reverse("page-detail", kwargs={"slug": item.slug})


class AlumniSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return AlumniStory.objects.filter(status="approved", consent_to_publish=True)

    def lastmod(self, item):
        return item.updated_at

    def location(self, item):
        return reverse("alumni-detail", kwargs={"slug": item.slug})


class ActivitySitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.7

    def items(self):
        return ExtracurricularActivity.objects.filter(is_published=True)

    def lastmod(self, item):
        return item.updated_at

    def location(self, item):
        return reverse("activity-detail", kwargs={"slug": item.slug})


sitemaps = {
    "static": StaticViewSitemap,
    "news": PostSitemap,
    "events": EventSitemap,
    "subjects": SubjectSitemap,
    "pages": PageSitemap,
    "alumni": AlumniSitemap,
    "activities": ActivitySitemap,
}
