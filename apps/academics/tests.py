from django.test import TestCase
from django.urls import reverse

from .models import Subject


class SubjectViewsTests(TestCase):
    def setUp(self):
        self.active_subject = Subject.objects.create(
            name="Mathematics",
            slug="mathematics",
            description="A foundation for logical thinking.",
            display_order=2,
        )
        Subject.objects.create(
            name="Inactive subject",
            slug="inactive-subject",
            description="Not publicly available.",
            is_active=False,
        )

    def test_subject_list_only_shows_active_subjects_in_display_order(self):
        earlier_subject = Subject.objects.create(
            name="English",
            slug="english",
            description="Language and literature.",
            display_order=1,
        )

        response = self.client.get(reverse("subject-list"))

        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(
            response.context["subjects"],
            [earlier_subject, self.active_subject],
        )

    def test_inactive_subject_detail_is_not_public(self):
        response = self.client.get(reverse("subject-detail", args=["inactive-subject"]))

        self.assertEqual(response.status_code, 404)
