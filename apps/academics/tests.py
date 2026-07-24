from django.test import TestCase
from django.urls import reverse

from .models import Subject
from apps.staff.models import StaffMember


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

    def test_subject_detail_lists_only_active_linked_teachers(self):
        teacher = StaffMember.objects.create(
            full_name="Lebo Molefe",
            role="Mathematics Teacher",
            short_bio="A committed educator.",
        )
        inactive_teacher = StaffMember.objects.create(
            full_name="Hidden Teacher",
            short_bio="Not public.",
            is_active=False,
        )
        teacher.subjects.add(self.active_subject)
        inactive_teacher.subjects.add(self.active_subject)

        response = self.client.get(
            reverse("subject-detail", args=[self.active_subject.slug])
        )

        self.assertContains(response, teacher.full_name)
        self.assertNotContains(response, inactive_teacher.full_name)
