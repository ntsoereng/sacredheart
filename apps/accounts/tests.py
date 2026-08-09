from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from apps.staff.models import StaffMember


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

    def test_staff_registration_creates_an_unapproved_account_and_profile(self):
        response = self.client.post(
            reverse("staff-register"),
            {
                "username": "newteacher",
                "email": "teacher@example.org",
                "password1": "A-strong-test-password-482!",
                "password2": "A-strong-test-password-482!",
                "full_name": "Lebo Molefe",
                "role": "Mathematics Teacher",
                "short_bio": "I teach mathematics.",
            },
        )

        self.assertRedirects(response, reverse("staff-registration-complete"))
        user = get_user_model().objects.get(username="newteacher")
        self.assertFalse(user.is_staff)
        profile = StaffMember.objects.get(user=user)
        self.assertEqual(profile.full_name, "Lebo Molefe")
        self.assertFalse(profile.is_active)

    def test_registration_link_is_only_present_on_staff_login_page(self):
        login_response = self.client.get(reverse("staff-login"))
        home_response = self.client.get(reverse("home"))

        self.assertContains(login_response, reverse("staff-register"))
        self.assertNotContains(home_response, reverse("staff-register"))
