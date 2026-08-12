import re

from django.test import TestCase
from django.urls import reverse

from apps.academics.models import Subject
from apps.pages.models import Page
from apps.posts.models import Post

from .models import ExtracurricularActivity, SiteSettings
from .storage import SafeMediaStorage


class SafeMediaStorageTests(TestCase):
    def test_pdf_uploads_keep_the_pdf_extension(self):
        stored_name = SafeMediaStorage().get_valid_name("School Prospectus.PDF")

        self.assertTrue(stored_name.endswith(".pdf"))
        self.assertNotIn("School Prospectus", stored_name)


class BrowserSecurityHeaderTests(TestCase):
    def test_html_response_has_enforced_nonce_based_csp(self):
        response = self.client.get(reverse("home"))

        policy = response["Content-Security-Policy"]
        self.assertIn("default-src 'self'", policy)
        self.assertIn("object-src 'none'", policy)
        self.assertIn("frame-ancestors 'none'", policy)
        self.assertNotIn("cdn.jsdelivr.net", policy)
        self.assertNotIn("script-src 'unsafe-inline'", policy)
        self.assertNotIn("style-src 'unsafe-inline'", policy)

        nonce_match = re.search(r"'nonce-([^']+)'", policy)
        self.assertIsNotNone(nonce_match)
        self.assertContains(
            response,
            f'nonce="{nonce_match.group(1)}"',
            html=False,
        )

    def test_response_disables_unused_browser_capabilities(self):
        response = self.client.get(reverse("home"))

        policy = response["Permissions-Policy"]
        self.assertIn("camera=()", policy)
        self.assertIn("geolocation=()", policy)
        self.assertIn("microphone=()", policy)
        self.assertIn("payment=()", policy)
        self.assertNotIn(", ", policy)
        self.assertNotIn("publickey-credentials", policy)

    def test_identified_ai_scraper_is_rejected(self):
        response = self.client.get(reverse("home"), HTTP_USER_AGENT="GPTBot/1.0")

        self.assertEqual(response.status_code, 403)

    def test_search_crawler_remains_allowed(self):
        response = self.client.get(reverse("home"), HTTP_USER_AGENT="Googlebot/2.1")

        self.assertEqual(response.status_code, 200)


class AboutViewTests(TestCase):

    def test_about_page_is_available(self):
        response = self.client.get(reverse("about-us"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/about.html")
        self.assertContains(response, "OUR HISTORY")
        self.assertContains(response, "OUR MISSION")
        self.assertContains(response, "OUR VISION")
        self.assertContains(response, "OUR VALUES")


class DonationsViewTests(TestCase):

    def test_donations_page_is_available(self):
        response = self.client.get(reverse("donations"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/donations.html")
        self.assertContains(response, "Financial gifts")
        self.assertContains(response, "Useful items")


class SeoTests(TestCase):

    def test_home_has_core_search_metadata(self):
        response = self.client.get(reverse("home"), HTTP_HOST="testserver")

        self.assertContains(response, '<meta name="description"', html=False)
        self.assertContains(
            response,
            '<link rel="canonical" href="http://testserver/">',
            html=True,
        )
        self.assertContains(response, '"@type": "HighSchool"', html=False)

    def test_robots_points_to_sitemap_and_blocks_private_areas(self):
        response = self.client.get(reverse("robots-txt"), HTTP_HOST="testserver")

        self.assertTrue(response["Content-Type"].startswith("text/plain"))
        self.assertContains(response, "Disallow: /admin/")
        self.assertContains(response, "Disallow: /dashboard/")
        self.assertContains(response, "User-agent: GPTBot")
        self.assertContains(response, "User-agent: ClaudeBot")
        self.assertContains(response, "User-agent: Google-Extended")
        self.assertContains(response, "User-agent: CCBot")
        self.assertContains(response, "Sitemap: http://testserver/sitemap.xml")

    def test_sitemap_is_available(self):
        response = self.client.get("/sitemap.xml", HTTP_HOST="testserver")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/xml")
        self.assertContains(response, "http://testserver/")
        self.assertContains(response, "http://testserver/admissions/")

    def test_configured_social_profiles_appear_in_footer_and_schema(self):
        SiteSettings.objects.create(
            school_name="Sacred Heart",
            facebook_url="https://facebook.com/sacredheart",
            instagram_url="https://instagram.com/sacredheart",
        )

        response = self.client.get(reverse("home"), HTTP_HOST="testserver")

        self.assertContains(response, "Follow the school")
        self.assertContains(response, "https://facebook.com/sacredheart")
        self.assertContains(response, '"sameAs"', html=False)


class ExtracurricularActivityTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.activity = ExtracurricularActivity.objects.create(
            name="Marimba Band",
            category="music",
            short_description="Learners build confidence through music.",
            description="The band rehearses and performs as an ensemble.",
            achievements="Performed at the school celebration.",
            is_featured=True,
            is_published=True,
        )

    def test_published_activity_is_listed_and_has_detail_page(self):
        list_response = self.client.get(reverse("activity-list"))
        detail_response = self.client.get(
            reverse("activity-detail", kwargs={"slug": self.activity.slug})
        )

        self.assertContains(list_response, "Marimba Band")
        self.assertContains(detail_response, "Achievements and highlights")
        self.assertContains(detail_response, "Performed at the school celebration.")

    def test_featured_activity_appears_on_homepage(self):
        response = self.client.get(reverse("home"))

        self.assertContains(response, "Marimba Band")
        self.assertContains(response, "Beyond the classroom")

    def test_unpublished_activity_is_not_public(self):
        self.activity.is_published = False
        self.activity.save()

        response = self.client.get(
            reverse("activity-detail", kwargs={"slug": self.activity.slug})
        )

        self.assertEqual(response.status_code, 404)


class SearchViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.page = Page.objects.create(
            title="School Library",
            content="Browse our reading collection.",
        )
        cls.post = Post.objects.create(
            title="Library Week",
            summary="A week celebrating books.",
            content="Learners visited the library.",
        )
        cls.subject = Subject.objects.create(
            name="Literature",
            description="Study novels, poetry, and drama.",
        )

    def test_search_returns_pages_posts_and_other_public_content_types(self):
        response = self.client.get(reverse("search"), {"q": "library"})

        self.assertContains(response, self.page.title)
        self.assertContains(response, reverse("page-detail", args=[self.page.slug]))
        self.assertContains(response, self.post.title)

        subject_response = self.client.get(reverse("search"), {"q": "poetry"})
        self.assertContains(subject_response, self.subject.name)
        self.assertContains(
            subject_response,
            reverse("subject-detail", args=[self.subject.slug]),
        )

    def test_search_excludes_unpublished_content(self):
        hidden_page = Page.objects.create(
            title="Hidden archive",
            content="Private records",
            is_published=False,
        )

        response = self.client.get(reverse("search"), {"q": "archive"})

        self.assertNotContains(response, hidden_page.title)
