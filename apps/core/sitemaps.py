from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from apps.academics.models import Subject
from apps.alumni.models import AlumniStory
from apps.events.models import Event
from apps.pages.models import Page
from apps.posts.models import Post
from apps.core.models import ExtracurricularActivity
from apps.staff.models import StaffMember
from apps.vacancies.models import Vacancy


class StaticViewSitemap(Sitemap):
    """Only canonical, indexable public landing pages belong here."""

    public_views = {
        "home": ("daily", 1.0),
        "application-create": ("weekly", 0.9),
        "about-us": ("monthly", 0.8),
        "post-list": ("daily", 0.8),
        "event-list": ("daily", 0.8),
        "subject-list": ("monthly", 0.8),
        "activity-list": ("monthly", 0.7),
        "staff-list": ("monthly", 0.7),
        "alumni-list": ("weekly", 0.8),
        "alumni-opportunity-list": ("weekly", 0.7),
        "vacancy-list": ("daily", 0.8),
        "contact": ("monthly", 0.6),
        "donations": ("monthly", 0.6),
        "privacy-policy": ("yearly", 0.3),
        "terms-of-use": ("yearly", 0.3),
    }

    def items(self):
        return tuple(self.public_views)

    def location(self, item):
        return reverse(item)

    def priority(self, item):
        return self.public_views[item][1]

    def changefreq(self, item):
        return self.public_views[item][0]


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
    priority = 0.7

    def items(self):
        return AlumniStory.objects.filter(status="approved", consent_to_publish=True)

    def lastmod(self, item):
        return item.updated_at

    def location(self, item):
        return reverse("alumni-detail", kwargs={"slug": item.slug})


class AlumniClassSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return (
            AlumniStory.objects.filter(
                status="approved",
                consent_to_publish=True,
            )
            .values_list("graduation_year", flat=True)
            .distinct()
            .order_by("-graduation_year")
        )

    def location(self, item):
        return reverse("alumni-class", kwargs={"year": item})


class ActivitySitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.7

    def items(self):
        return ExtracurricularActivity.objects.filter(is_published=True)

    def lastmod(self, item):
        return item.updated_at

    def location(self, item):
        return reverse("activity-detail", kwargs={"slug": item.slug})


class StaffSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return StaffMember.objects.filter(is_active=True)

    def lastmod(self, item):
        return item.updated_at

    def location(self, item):
        return reverse("staff-detail", kwargs={"pk": item.pk})


class VacancySitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return Vacancy.objects.publicly_visible()

    def lastmod(self, item):
        return item.updated_at

    def location(self, item):
        return reverse("vacancy-detail", kwargs={"slug": item.slug})


sitemaps = {
    "static": StaticViewSitemap,
    "news": PostSitemap,
    "events": EventSitemap,
    "subjects": SubjectSitemap,
    "pages": PageSitemap,
    "alumni": AlumniSitemap,
    "alumni-classes": AlumniClassSitemap,
    "activities": ActivitySitemap,
    "staff": StaffSitemap,
    "vacancies": VacancySitemap,
}
