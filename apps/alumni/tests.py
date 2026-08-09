from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

from .models import AlumniStory


class AlumniStoryTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.approved = AlumniStory.objects.create(
            full_name="Mpho Molefe",
            graduation_year=2005,
            email="private@example.com",
            phone="+266 5000 0000",
            occupation="Engineer",
            life_story="A journey in engineering.",
            school_memories="The friendships.",
            consent_to_publish=True,
            status="approved",
        )
        cls.pending = AlumniStory.objects.create(
            full_name="Pending Alumnus",
            graduation_year=2010,
            email="pending@example.com",
            life_story="Not reviewed yet.",
            consent_to_publish=True,
        )

    def test_only_approved_story_is_public(self):
        response = self.client.get(reverse("alumni-list"))
        self.assertContains(response, self.approved.full_name)
        self.assertNotContains(response, self.pending.full_name)
        self.assertEqual(
            self.client.get(reverse("alumni-detail", args=[self.pending.slug])).status_code,
            404,
        )

    def test_contact_details_are_not_published(self):
        response = self.client.get(
            reverse("alumni-detail", args=[self.approved.slug])
        )
        self.assertNotContains(response, self.approved.email)
        self.assertNotContains(response, self.approved.phone)

    def test_staff_can_approve_and_is_recorded_as_reviewer(self):
        staff = get_user_model().objects.create_user(
            username="reviewer",
            password="password",
            is_staff=True,
        )
        staff.user_permissions.add(
            Permission.objects.get(codename="view_alumnistory"),
            Permission.objects.get(codename="change_alumnistory"),
        )
        self.client.force_login(staff)
        response = self.client.post(
            reverse("alumni-review-detail", args=[self.pending.pk]),
            {"status": "approved", "staff_notes": "Identity confirmed."},
        )
        self.assertRedirects(
            response,
            reverse("alumni-review-detail", args=[self.pending.pk]),
        )
        self.pending.refresh_from_db()
        self.assertEqual(self.pending.status, "approved")
        self.assertEqual(self.pending.reviewed_by, staff)
        self.assertIsNotNone(self.pending.reviewed_at)
