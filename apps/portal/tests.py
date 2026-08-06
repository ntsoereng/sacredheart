from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.admissions.models import Application, ApplicationNote
from apps.core.models import ExtracurricularActivity, SiteSettings
from apps.events.models import Event
from apps.posts.models import Post
from apps.academics.models import Subject
from apps.staff.models import StaffMember


class StaffApplicationWorkflowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.staff_user = get_user_model().objects.create_user(
            username="reviewer",
            password="test-password",
            is_staff=True,
        )
        cls.application = Application.objects.create(
            academic_year="2027",
            student_name="Lerato",
            student_surname="Mokoena",
            date_of_birth=date(2012, 5, 10),
            parent_guardian_names="Thabo Mokoena",
            parent_phone_number="+266 5000 0000",
            home_address="Maseru",
            previous_school="Example Primary",
            district="Maseru",
        )

    def setUp(self):
        self.client.force_login(self.staff_user)

    def test_staff_can_update_application_status(self):
        response = self.client.post(
            reverse("application-detail", args=[self.application.pk]),
            {"action": "update_status", "status": "review"},
        )

        self.assertRedirects(
            response,
            reverse("application-detail", args=[self.application.pk]),
        )
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, "review")
        self.assertTrue(self.application.reviewed)
        self.assertEqual(self.application.reviewed_by, self.staff_user)
        self.assertIsNotNone(self.application.reviewed_at)

    def test_staff_can_add_attributed_note(self):
        response = self.client.post(
            reverse("application-detail", args=[self.application.pk]),
            {"action": "add_note", "body": "Guardian documents verified."},
        )

        self.assertRedirects(
            response,
            reverse("application-detail", args=[self.application.pk]),
        )
        note = ApplicationNote.objects.get(application=self.application)
        self.assertEqual(note.author, self.staff_user)
        self.assertEqual(note.body, "Guardian documents verified.")

    def test_dashboard_shows_action_queue(self):
        response = self.client.get(reverse("dashboard"))

        self.assertContains(response, "Lerato Mokoena")
        self.assertEqual(response.context["new_applications"], 1)

    def test_non_staff_user_is_forbidden(self):
        user = get_user_model().objects.create_user(
            username="visitor",
            password="test-password",
        )
        self.client.force_login(user)

        response = self.client.get(reverse("application-list"))

        self.assertEqual(response.status_code, 403)

    def test_staff_can_create_post_with_safe_rich_text(self):
        response = self.client.post(
            reverse("post-create"),
            {
                "title": "School achievement",
                "summary": "Celebrating a school achievement.",
                "content": "<h2>Highlights</h2><ul><li>First item</li></ul><script>alert(1)</script>",
                "is_published": "on",
            },
        )

        self.assertRedirects(response, reverse("content-manager"))
        post = Post.objects.get(title="School achievement")
        self.assertEqual(post.author, self.staff_user)
        self.assertIn("<ul>", post.content)
        self.assertNotIn("<script", post.content)

    def test_staff_can_create_event_and_is_recorded_as_creator(self):
        response = self.client.post(
            reverse("event-create"),
            {
                "title": "Open Day",
                "description": "Meet our school community.",
                "event_date": "2027-04-10",
                "location": "School campus",
                "is_published": "on",
            },
        )

        self.assertRedirects(response, reverse("content-manager"))
        event = Event.objects.get(title="Open Day")
        self.assertEqual(event.created_by, self.staff_user)

    def test_staff_can_create_activity_with_safe_rich_text(self):
        response = self.client.post(
            reverse("activity-create"),
            {
                "name": "Marimba Band",
                "category": "music",
                "short_description": "Music, confidence and teamwork.",
                "description": "<h2>About the band</h2><script>alert(1)</script>",
                "achievements": "<ul><li>Community performance</li></ul>",
                "is_published": "on",
                "is_featured": "on",
                "display_order": 1,
            },
        )

        self.assertRedirects(response, reverse("content-manager"))
        activity = ExtracurricularActivity.objects.get(name="Marimba Band")
        self.assertIn("<h2>", activity.description)
        self.assertNotIn("<script", activity.description)
        self.assertTrue(activity.is_featured)

    def test_staff_can_update_public_announcement(self):
        settings = SiteSettings.objects.create(school_name="Sacred Heart")
        response = self.client.post(
            reverse("announcement-edit"),
            {
                "homepage_announcement": "Applications close on Friday.",
                "show_announcement": "on",
            },
        )

        self.assertRedirects(response, reverse("content-manager"))
        settings.refresh_from_db()
        self.assertEqual(
            settings.homepage_announcement,
            "Applications close on Friday.",
        )
        self.assertTrue(settings.show_announcement)

    def test_staff_can_update_site_info_and_open_applications(self):
        settings = SiteSettings.objects.create(school_name="Sacred Heart")
        response = self.client.post(
            reverse("site-settings"),
            {
                "school_name": "Sacred Heart High School",
                "tagline": "Faith and excellence",
                "admissions_email": "admissions@example.org",
                "admissions_open": "on",
            },
        )

        self.assertRedirects(response, reverse("site-settings"))
        settings.refresh_from_db()
        self.assertEqual(settings.school_name, "Sacred Heart High School")
        self.assertTrue(settings.admissions_open)

    def test_site_settings_page_creates_missing_singleton(self):
        response = self.client.get(reverse("site-settings"))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(SiteSettings.objects.exists())

    def test_site_settings_extracts_google_maps_url_from_iframe(self):
        settings = SiteSettings.objects.create(school_name="Sacred Heart")
        embed_url = "https://www.google.com/maps/embed?pb=test-map"

        response = self.client.post(
            reverse("site-settings"),
            {
                "school_name": "Sacred Heart",
                "google_maps_embed_url": (
                    f'<iframe src="{embed_url}" width="600" height="450"></iframe>'
                ),
            },
        )

        self.assertRedirects(response, reverse("site-settings"))
        settings.refresh_from_db()
        self.assertEqual(settings.google_maps_embed_url, embed_url)

    def test_site_settings_rejects_non_embeddable_maps_share_link(self):
        SiteSettings.objects.create(school_name="Sacred Heart")

        response = self.client.post(
            reverse("site-settings"),
            {
                "school_name": "Sacred Heart",
                "google_maps_embed_url": "https://maps.app.goo.gl/n3dTaH8F4x8SDcHz7",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"],
            "google_maps_embed_url",
            "This is not an embeddable Google Maps URL. In Google Maps, use "
            "Share > Embed a map instead of Copy link.",
        )

    def test_staff_can_create_subject_with_generated_slug(self):
        response = self.client.post(
            reverse("subject-create"),
            {
                "name": "Physical Science",
                "description": "Investigating the physical world.",
                "display_order": 1,
                "is_active": "on",
            },
        )

        self.assertRedirects(response, reverse("content-manager"))
        subject = Subject.objects.get(name="Physical Science")
        self.assertEqual(subject.slug, "physical-science")

    def test_staff_can_create_teacher_and_link_subjects(self):
        subject = Subject.objects.create(
            name="Mathematics",
            description="Logical and numerical reasoning.",
        )
        response = self.client.post(
            reverse("staff-member-create"),
            {
                "full_name": "Lebo Molefe",
                "role": "Teacher",
                "short_bio": "A committed educator.",
                "subjects": [subject.pk],
                "display_order": 0,
                "is_active": "on",
            },
        )

        self.assertRedirects(response, reverse("content-manager"))
        teacher = StaffMember.objects.get(full_name="Lebo Molefe")
        self.assertQuerySetEqual(teacher.subjects.all(), [subject])
