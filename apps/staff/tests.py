from django.test import TestCase
from django.urls import reverse

from .models import StaffMember


class StaffListViewTests(TestCase):
    def test_principal_is_featured_before_active_staff_members(self):
        principal = StaffMember.objects.create(
            full_name="Mpho Mokoena",
            role="Principal",
            short_bio="An experienced school leader.",
            motto="Every learner matters.",
            is_principal=True,
            welcome_remarks="Welcome to our school community.",
        )
        teacher = StaffMember.objects.create(
            full_name="Lebo Molefe",
            role="Mathematics Teacher",
            short_bio="A committed mathematics teacher.",
        )
        StaffMember.objects.create(
            full_name="Inactive Teacher",
            short_bio="Not publicly visible.",
            is_active=False,
        )

        response = self.client.get(reverse("staff-list"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["principal"], principal)
        self.assertQuerySetEqual(response.context["staff_members"], [teacher])
        self.assertContains(response, "Welcome to our school community.")
        self.assertNotContains(response, "Inactive Teacher")
