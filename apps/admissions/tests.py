from django.test import TestCase
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
        self.assertContains(response, "Admissions are currently not open")
        self.assertContains(response, "Applications will reopen in September.")
        self.assertNotContains(response, "Application Form")

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
        self.assertContains(response, "Application Form")

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
                "parent_guardian_names": "Thabo Mokoena",
                "parent_phone_number": "+266 5000 0000",
                "home_address": "Maseru",
                "previous_school": "Example Primary",
                "district": "Maseru",
            },
            follow=True,
        )

        application = Application.objects.get()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, application.reference_number)
        self.assertContains(response, "Keep this reference number safe")
