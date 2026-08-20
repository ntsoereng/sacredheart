from concurrent.futures import ThreadPoolExecutor
from django.test import TestCase
from django.test import override_settings
from django.test import Client, TransactionTestCase
from django.core import mail
from django.db import IntegrityError, close_old_connections, transaction
from django.urls import reverse
from datetime import date
from threading import Barrier
from unittest.mock import patch

from apps.core.models import SiteSettings

from .forms import ApplicationForm
from .models import Application, ApplicationSubmissionToken
from .protection import create_submission_token


class ApplicationCreateViewTests(TestCase):
    def setUp(self):
        self.url = reverse("application-create")

    def submission_token(self):
        response = self.client.get(self.url)
        return response.context["form"]["submission_token"].value()

    def valid_application_data(self, **overrides):
        data = {
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
            "district": "Maseru",
        }
        data.update(overrides)
        return data

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
        self.assertNotContains(response, "Student candidate number")
        self.assertNotContains(response, 'name="student_candidate_number"')
        self.assertContains(response, '<option value="Other">Other</option>', html=True)
        self.assertContains(response, "Select “Other” if the learner lives outside Lesotho.")
        self.assertContains(response, 'name="website"')
        self.assertContains(response, 'tabindex="-1"')
        self.assertContains(response, 'autocomplete="off"')
        self.assertContains(response, 'aria-hidden="true"')
        self.assertContains(response, 'name="submission_token"')

    def test_previous_school_is_required(self):
        form = ApplicationForm(
            data=self.valid_application_data(previous_school="", submission_token="token")
        )

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["previous_school"], ["This field is required."])
        self.assertTrue(form.fields["previous_school"].required)

    def test_each_render_gets_a_distinct_signed_submission_token(self):
        SiteSettings.objects.create(
            school_name="Sacred Heart High School",
            admissions_open=True,
        )

        first_token = self.submission_token()
        second_token = self.submission_token()

        self.assertNotEqual(first_token, second_token)
        self.assertEqual(ApplicationSubmissionToken.objects.count(), 2)

    def test_open_admissions_displays_the_configured_closing_date(self):
        SiteSettings.objects.create(
            school_name="Sacred Heart High School",
            admissions_open=True,
            admissions_closing_date=date(2026, 9, 18),
        )

        response = self.client.get(self.url)

        self.assertContains(response, "Applications close")
        self.assertContains(response, "Friday, 18 September 2026")
        self.assertContains(response, 'datetime="2026-09-18"')

    def test_closing_date_is_not_shown_when_admissions_are_closed(self):
        SiteSettings.objects.create(
            school_name="Sacred Heart High School",
            admissions_open=False,
            admissions_closing_date=date(2026, 9, 18),
        )

        response = self.client.get(self.url)

        self.assertNotContains(response, "Friday, 18 September 2026")

    def test_admissions_page_has_search_metadata(self):
        SiteSettings.objects.create(school_name="Sacred Heart High School")

        response = self.client.get(self.url, HTTP_HOST="testserver")

        self.assertContains(
            response,
            "<title>Admissions | Apply to Sacred Heart High School</title>",
            html=True,
        )
        self.assertContains(
            response,
            '<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">',
            html=True,
        )
        self.assertContains(
            response,
            '<link rel="canonical" href="http://testserver/admissions/">',
            html=True,
        )

    def test_admissions_page_shows_document_placeholders(self):
        SiteSettings.objects.create(school_name="Sacred Heart High School")

        response = self.client.get(self.url)

        self.assertContains(response, "Admission list will be posted here soon.")
        self.assertNotContains(response, "Prospectus")

    def test_admissions_page_links_uploaded_documents(self):
        SiteSettings.objects.create(
            school_name="Sacred Heart High School",
            admissions_list="admissions/lists/approved-list.pdf",
            prospectus="admissions/prospectuses/prospectus.pdf",
        )

        response = self.client.get(self.url)

        self.assertContains(response, "/media/admissions/lists/approved-list.pdf")
        self.assertContains(response, "View admissions list")
        self.assertNotContains(response, "/media/admissions/prospectuses/prospectus.pdf")
        self.assertNotContains(response, "Browse prospectus")

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
                "district": "Other",
                "submission_token": self.submission_token(),
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
                "district": "Maseru",
                "submission_token": self.submission_token(),
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
                "district": "Maseru",
                "submission_token": self.submission_token(),
            },
            follow=True,
        )

        application = Application.objects.get()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["guardian@example.com"])
        self.assertIn(application.reference_number, mail.outbox[0].body)
        self.assertNotIn("Private home address", mail.outbox[0].body)
        self.assertContains(response, "Confirmation email sent")

    @override_settings(
        ADMISSIONS_RATE_LIMITS={
            "ip": (2, 3600),
            "email": (100, 3600),
            "phone": (100, 3600),
        }
    )
    def test_repeated_invalid_post_attempts_are_rate_limited(self):
        SiteSettings.objects.create(
            school_name="Sacred Heart High School",
            admissions_open=True,
        )

        self.client.post(self.url, {})
        self.client.post(self.url, {})
        response = self.client.post(self.url, {})

        self.assertEqual(response.status_code, 429)
        self.assertContains(response, "Please wait before trying again", status_code=429)
        self.assertEqual(Application.objects.count(), 0)

    @override_settings(
        ADMISSIONS_RATE_LIMITS={
            "ip": (100, 3600),
            "email": (2, 3600),
            "phone": (2, 3600),
        }
    )
    def test_guardian_identifiers_are_normalized_for_rate_limiting(self):
        SiteSettings.objects.create(
            school_name="Sacred Heart High School",
            admissions_open=True,
        )
        attempts = (
            (" Guardian@Example.com ", "+266 5000 0000"),
            ("guardian@example.com", "266-5000-0000"),
            ("GUARDIAN@example.com", "266 5000 0000"),
        )

        responses = [
            self.client.post(
                self.url,
                {
                    "parent_guardian_email": email,
                    "parent_phone_number": phone,
                },
                REMOTE_ADDR=f"192.0.2.{index}",
            )
            for index, (email, phone) in enumerate(attempts, start=1)
        ]

        self.assertEqual(responses[-1].status_code, 429)

    def test_populated_honeypot_is_rejected_without_revealing_the_reason(self):
        SiteSettings.objects.create(
            school_name="Sacred Heart High School",
            admissions_open=True,
        )
        data = self.valid_application_data(
            submission_token=self.submission_token(),
            website="https://spam.example",
        )

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, 400)
        self.assertNotContains(response, "honeypot", status_code=400)
        self.assertEqual(Application.objects.count(), 0)

    def test_reusing_a_consumed_submission_token_is_rejected(self):
        SiteSettings.objects.create(
            school_name="Sacred Heart High School",
            admissions_open=True,
        )
        token = self.submission_token()
        first_response = self.client.post(
            self.url,
            self.valid_application_data(submission_token=token),
        )
        second_response = self.client.post(
            self.url,
            self.valid_application_data(
                student_name="Naledi",
                student_surname="Dlamini",
                date_of_birth="2013-06-11",
                submission_token=token,
            ),
        )

        self.assertEqual(first_response.status_code, 302)
        self.assertEqual(second_response.status_code, 409)
        self.assertContains(
            second_response,
            "form is no longer valid",
            status_code=409,
        )
        self.assertEqual(Application.objects.count(), 1)

    def test_duplicate_application_gets_a_neutral_message(self):
        SiteSettings.objects.create(
            school_name="Sacred Heart High School",
            admissions_open=True,
        )
        first_response = self.client.post(
            self.url,
            self.valid_application_data(submission_token=self.submission_token()),
        )
        duplicate_response = self.client.post(
            self.url,
            self.valid_application_data(submission_token=self.submission_token()),
        )

        self.assertEqual(first_response.status_code, 302)
        self.assertEqual(duplicate_response.status_code, 200)
        self.assertContains(duplicate_response, "may already have been received")
        self.assertEqual(Application.objects.count(), 1)

    def test_validation_failure_does_not_consume_submission_token(self):
        SiteSettings.objects.create(
            school_name="Sacred Heart High School",
            admissions_open=True,
        )
        token = self.submission_token()
        invalid_data = self.valid_application_data(submission_token=token)
        invalid_data.pop("student_surname")

        invalid_response = self.client.post(self.url, invalid_data)
        token_record = ApplicationSubmissionToken.objects.get()

        self.assertEqual(invalid_response.status_code, 200)
        self.assertIsNone(token_record.consumed_at)

        valid_response = self.client.post(
            self.url,
            self.valid_application_data(submission_token=token),
        )
        self.assertEqual(valid_response.status_code, 302)
        token_record.refresh_from_db()
        self.assertIsNotNone(token_record.consumed_at)

    def test_guardian_can_submit_applications_for_different_children(self):
        SiteSettings.objects.create(
            school_name="Sacred Heart High School",
            admissions_open=True,
        )
        first_token = self.submission_token()
        first_response = self.client.post(
            self.url,
            self.valid_application_data(submission_token=first_token),
        )
        second_token = self.submission_token()
        second_response = self.client.post(
            self.url,
            self.valid_application_data(
                student_name="Naledi",
                student_surname="Mokoena",
                date_of_birth="2014-07-12",
                submission_token=second_token,
            ),
        )

        self.assertEqual(first_response.status_code, 302)
        self.assertEqual(second_response.status_code, 302)
        self.assertEqual(Application.objects.count(), 2)


class ApplicationDuplicateConstraintTests(TestCase):
    def application_values(self, **overrides):
        values = {
            "academic_year": "2027",
            "student_name": "Lerato",
            "student_surname": "Mokoena",
            "date_of_birth": date(2012, 5, 10),
            "nationality": "Lesotho",
            "parent_guardian_names": "Thabo Mokoena",
            "parent_phone_number": "+266 5000 0000",
            "parent_guardian_email": "guardian@example.com",
            "home_address": "Maseru",
            "previous_school": "Example Primary",
            "district": "Maseru",
        }
        values.update(overrides)
        return values

    def test_database_constraint_blocks_normalized_duplicate(self):
        Application.objects.create(
            **self.application_values(
                academic_year=" 2027 ",
                student_name="Lerato  Anne",
                student_surname="MOKOENA",
            )
        )

        with self.assertRaises(IntegrityError), transaction.atomic():
            Application.objects.create(
                **self.application_values(
                    academic_year="2027",
                    student_name=" lerato anne ",
                    student_surname="mokoena",
                )
            )


class ConcurrentApplicationSubmissionTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        SiteSettings.objects.create(
            school_name="Sacred Heart High School",
            admissions_open=True,
        )
        self.url = reverse("application-create")

    def application_data(self, token):
        return {
            "academic_year": "2027",
            "student_name": "Lerato",
            "student_surname": "Mokoena",
            "date_of_birth": "2012-05-10",
            "nationality": "Lesotho",
            "parent_guardian_names": "Thabo Mokoena",
            "parent_phone_number": "+266 5000 0000",
            "parent_guardian_email": "guardian@example.com",
            "home_address": "Maseru",
            "previous_school": "Example Primary",
            "district": "Maseru",
            "submission_token": token,
        }

    def test_two_simultaneous_identical_submissions_create_one_application(self):
        tokens = [create_submission_token(), create_submission_token()]
        save_barrier = Barrier(2)
        original_save = Application.save

        def synchronized_save(instance, *args, **kwargs):
            if instance._state.adding:
                save_barrier.wait(timeout=5)
            return original_save(instance, *args, **kwargs)

        def submit(index):
            close_old_connections()
            client = Client(raise_request_exception=False)
            try:
                return client.post(
                    self.url,
                    self.application_data(tokens[index]),
                    REMOTE_ADDR=f"192.0.2.{index + 1}",
                ).status_code
            finally:
                close_old_connections()

        with self.assertLogs("apps.admissions.views", level="WARNING"):
            with (
                patch(
                    "apps.admissions.views.admission_attempt_is_limited",
                    return_value=False,
                ),
                patch.object(Application, "save", synchronized_save),
                patch(
                    "apps.admissions.views.send_application_confirmation",
                    return_value=False,
                ),
                ThreadPoolExecutor(max_workers=2) as executor,
            ):
                statuses = list(executor.map(submit, range(2)))

        self.assertEqual(Application.objects.count(), 1)
        self.assertIn(302, statuses)
        self.assertEqual(sorted(statuses), [302, 409])
