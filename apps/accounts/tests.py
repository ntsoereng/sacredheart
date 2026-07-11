from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse


class StaffPortalAccessTests(TestCase):
    def setUp(self):
        self.staff_user = get_user_model().objects.create_user(
            username="staffmember",
            password="secure-password",
            is_staff=True,
        )
        self.regular_user = get_user_model().objects.create_user(
            username="parent",
            password="secure-password",
        )

    def test_dashboard_redirects_anonymous_users_to_staff_login(self):
        response = self.client.get(reverse("dashboard"))

        self.assertRedirects(
            response,
            f"{reverse('staff-login')}?next={reverse('dashboard')}",
        )

    def test_regular_users_cannot_sign_in_to_staff_portal(self):
        response = self.client.post(
            reverse("staff-login"),
            {"username": "parent", "password": "secure-password"},
        )

        self.assertContains(response, "does not have access")
        self.assertFalse("_auth_user_id" in self.client.session)

    def test_staff_users_can_sign_in_and_access_dashboard(self):
        response = self.client.post(
            reverse("staff-login"),
            {"username": "staffmember", "password": "secure-password"},
        )

        self.assertRedirects(response, reverse("dashboard"))
        self.assertEqual(self.client.get(reverse("dashboard")).status_code, 200)
