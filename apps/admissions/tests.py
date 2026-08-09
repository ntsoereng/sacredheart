from django.test import TestCase
from django.test import override_settings
from django.core import mail
from django.urls import reverse
from datetime import date

from apps.core.models import SiteSettings

from .models import Application


class ApplicationCreateViewTests(TestCase):
    def setUp(self):
        self.url = reverse("application-create")

    def test_closed_admissions_shows_only_the_closure_message(self):
        SiteSettings.objects.create(
            school_name="Sacred Heart High School",
            admissions_open=False,
            admissions_message="Applications will reopen in September.",
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Applications are currently closed")
        self.assertContains(response, "Applications will reopen in September.")
        self.assertNotContains(response, "Learner application form")

    def test_closed_admissions_cannot_create_an_application(self):
        SiteSettings.objects.create(school_name="Sacred Heart High School")

        response = self.client.post(self.url, {})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Application.objects.count(), 0)

    def test_open_admissions_shows_the_application_form(self):
        SiteSettings.objects.create(
            school_name="Sacred Heart High School",
            admissions_open=True,
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Learner application form")
        self.assertContains(response, '<option value="Other">Other</option>', html=True)
        self.assertContains(response, "Select “Other” if the learner lives outside Lesotho.")

    def test_application_accepts_other_as_the_home_district(self):
        SiteSettings.objects.create(
            school_name="Sacred Heart High School",
            admissions_open=True,
        )

        response = self.client.post(
            self.url,
            {
                "academic_year": str(date.today().year + 1),
                "student_name": "Naledi",
                "student_surname": "Dlamini",
                "date_of_birth": "2012-05-10",
                "nationality": "South Africa",
                "parent_guardian_names": "Thandi Dlamini",
                "parent_phone_number": "+27 11 555 0100",
                "parent_guardian_email": "parent@example.com",
                "home_address": "Johannesburg",
                "previous_school": "Example Primary",
                "student_candidate_number": "ZA-12345",
                "district": "Other",
            },
        )

        self.assertRedirects(response, reverse("application-success"))
        self.assertEqual(Application.objects.get().district, "Other")

    def test_success_page_shows_generated_reference_number(self):
        SiteSettings.objects.create(
            school_name="Sacred Heart High School",
            admissions_open=True,
        )

        response = self.client.post(
            self.url,
            {
                "academic_year": str(date.today().year + 1),
                "student_name": "Lerato",
                "student_surname": "Mokoena",
                "date_of_birth": "2012-05-10",
                "nationality": "Lesotho",
                "parent_guardian_names": "Thabo Mokoena",
                "parent_phone_number": "+266 5000 0000",
                "parent_guardian_email": "guardian@example.com",
                "home_address": "Maseru",
                "previous_school": "Example Primary",
                "student_candidate_number": "LS-12345",
                "district": "Maseru",
            },
            follow=True,
        )

        application = Application.objects.get()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, application.reference_number)
        self.assertContains(response, "Keep this reference number safe")

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        DEFAULT_FROM_EMAIL="Sacred Heart Admissions <admissions@example.org>",
    )
    def test_submission_sends_privacy_conscious_confirmation_email(self):
        SiteSettings.objects.create(
            school_name="Sacred Heart High School",
            admissions_open=True,
            admissions_email="admissions@example.org",
        )

        response = self.client.post(
            self.url,
            {
                "academic_year": str(date.today().year + 1),
                "student_name": "Lerato",
                "student_surname": "Mokoena",
                "date_of_birth": "2012-05-10",
                "nationality": "South Africa",
                "parent_guardian_names": "Thabo Mokoena",
                "parent_phone_number": "+266 5000 0000",
                "parent_guardian_email": "guardian@example.com",
                "home_address": "Private home address",
                "previous_school": "Example Primary",
                "student_candidate_number": "ZA-98765",
                "district": "Maseru",
            },
            follow=True,
        )

        application = Application.objects.get()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["guardian@example.com"])
        self.assertIn(application.reference_number, mail.outbox[0].body)
        self.assertNotIn("Private home address", mail.outbox[0].body)
        self.assertContains(response, "Confirmation email sent")
