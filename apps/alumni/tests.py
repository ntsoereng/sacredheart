import re
from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core import mail
from django.core.mail import get_connection
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.core.models import ContactMessage

from .models import (
    AlumniOpportunity,
    AlumniProfileUpdateVerification,
    AlumniStory,
    MentorshipRequest,
)


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
            mentorship_available=True,
            mentor_career_guidance=True,
        )
        cls.pending = AlumniStory.objects.create(
            full_name="Pending Alumnus",
            graduation_year=2010,
            email="pending@example.com",
            life_story="Not reviewed yet.",
            consent_to_publish=True,
        )

    def submission_token(self, url_name):
        response = self.client.get(reverse(url_name))
        return response.context["form"]["submission_token"].value()

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

    @override_settings(
        EMAIL_HOST_USER="admissions@example.com",
        EMAIL_HOST_PASSWORD="admissions-secret",
        ALUMNI_EMAIL_HOST_USER="alumni@sacredheart.ac.ls",
        ALUMNI_EMAIL_HOST_PASSWORD="alumni-secret",
    )
    def test_profile_update_requires_the_private_email_magic_link(self):
        update_url = reverse(
            "alumni-profile-update",
            args=[self.approved.slug],
        )
        form_response = self.client.get(update_url)

        self.assertEqual(form_response.status_code, 200)
        self.assertContains(form_response, "Verify your private email")
        self.assertContains(form_response, "data-protected-form")
        self.assertNotContains(form_response, self.approved.email)

        with patch(
            "apps.alumni.emails.get_connection",
            wraps=get_connection,
        ) as connection_factory:
            with self.captureOnCommitCallbacks(execute=True):
                response = self.client.post(
                    update_url,
                    {
                        "email": "private@example.com",
                        "submission_token": form_response.context["form"][
                            "submission_token"
                        ].value(),
                    },
                )

        connection_kwargs = connection_factory.call_args.kwargs
        self.assertEqual(
            connection_kwargs["username"],
            "alumni@sacredheart.ac.ls",
        )
        self.assertEqual(connection_kwargs["password"], "alumni-secret")

        self.assertRedirects(
            response,
            reverse("alumni-profile-update-sent", args=[self.approved.slug]),
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.approved.email])
        self.assertEqual(
            mail.outbox[0].from_email,
            "Sacred Heart Alumni Association <alumni@sacredheart.ac.ls>",
        )
        self.assertEqual(mail.outbox[0].reply_to, ["alumni@sacredheart.ac.ls"])
        self.assertEqual(AlumniProfileUpdateVerification.objects.count(), 1)

        verification_url = re.search(
            r"http://testserver(?P<path>/alumni/\S+)",
            mail.outbox[0].body,
        ).group("path")
        verification = AlumniProfileUpdateVerification.objects.get()
        raw_token = verification_url.rstrip("/").rsplit("/", 1)[-1]
        self.assertNotEqual(verification.token_digest, raw_token)

        correction_form = self.client.get(verification_url)
        self.assertEqual(correction_form.status_code, 200)
        self.assertContains(correction_form, "Email verified")
        self.assertNotContains(correction_form, self.approved.email)
        self.assertEqual(correction_form["Referrer-Policy"], "no-referrer")
        self.assertEqual(
            correction_form["X-Robots-Tag"],
            "noindex, nofollow, noarchive",
        )

        response = self.client.post(
            verification_url,
            {
                "update_type": "work",
                "message": "Please update my occupation to Senior Engineer.",
                "submission_token": correction_form.context["form"][
                    "submission_token"
                ].value(),
            },
        )
        self.assertRedirects(
            response,
            reverse("alumni-detail", args=[self.approved.slug]),
        )
        update_request = ContactMessage.objects.get()
        self.assertEqual(update_request.name, "Mpho Molefe")
        self.assertIn("Verified alumni profile update", update_request.subject)
        self.assertIn("Occupation, studies, or industry", update_request.message)
        self.assertIn("Senior Engineer", update_request.message)
        verification.refresh_from_db()
        self.assertIsNotNone(verification.used_at)
        self.assertEqual(self.client.get(verification_url).status_code, 410)

    def test_wrong_update_email_gets_the_same_response_without_a_link(self):
        update_url = reverse("alumni-profile-update", args=[self.approved.slug])
        form_response = self.client.get(update_url)

        response = self.client.post(
            update_url,
            {
                "email": "imposter@example.com",
                "submission_token": form_response.context["form"][
                    "submission_token"
                ].value(),
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Secure instructions will be sent to the private contact address",
        )
        self.assertNotContains(response, "does not match")
        self.assertEqual(len(mail.outbox), 0)
        self.assertFalse(AlumniProfileUpdateVerification.objects.exists())

    def test_profile_update_email_resend_has_a_cooldown(self):
        update_url = reverse("alumni-profile-update", args=[self.approved.slug])

        for _attempt in range(2):
            form_response = self.client.get(update_url)
            with self.captureOnCommitCallbacks(execute=True):
                response = self.client.post(
                    update_url,
                    {
                        "email": self.approved.email,
                        "submission_token": form_response.context["form"][
                            "submission_token"
                        ].value(),
                    },
                )
            self.assertRedirects(
                response,
                reverse(
                    "alumni-profile-update-sent",
                    args=[self.approved.slug],
                ),
            )

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(AlumniProfileUpdateVerification.objects.count(), 1)

    def test_expired_profile_update_link_is_rejected(self):
        verification, raw_token = AlumniProfileUpdateVerification.issue(
            self.approved,
            lifetime=timedelta(seconds=-1),
        )
        verification_url = reverse(
            "alumni-profile-update-confirm",
            args=[self.approved.slug, raw_token],
        )

        response = self.client.get(verification_url)

        self.assertEqual(response.status_code, 410)
        self.assertContains(response, "expired or already been used", status_code=410)

    def test_unpublished_profile_cannot_receive_an_update_request(self):
        response = self.client.get(
            reverse("alumni-profile-update", args=[self.pending.slug])
        )

        self.assertEqual(response.status_code, 404)

    def test_mentorship_feature_is_not_public(self):
        public_responses = (
            self.client.get(reverse("home")),
            self.client.get(reverse("alumni-list")),
            self.client.get(reverse("alumni-create")),
            self.client.get(reverse("alumni-detail", args=[self.approved.slug])),
            self.client.get(reverse("privacy-policy")),
            self.client.get(reverse("terms-of-use")),
        )

        for response in public_responses:
            with self.subTest(path=response.request["PATH_INFO"]):
                self.assertEqual(response.status_code, 200)
                self.assertNotIn("mentor", response.content.decode().lower())
        self.assertEqual(
            self.client.get("/alumni/mentorship/request/").status_code,
            404,
        )
        self.assertEqual(
            self.client.get("/alumni/mentorship/thank-you/").status_code,
            404,
        )

    def test_verified_alumnus_can_submit_opportunity(self):
        response = self.client.post(
            reverse("alumni-opportunity-create"),
            {
                "alumni": self.approved.pk,
                "verification_email": self.approved.email,
                "opportunity_type": "scholarship",
                "title": "Engineering scholarship",
                "provider": "Example Foundation",
                "summary": "Support for eligible secondary school graduates.",
                "application_url": "https://example.com/apply",
                "deadline": "2030-12-31",
                "submission_token": self.submission_token(
                    "alumni-opportunity-create"
                ),
            },
        )
        self.assertRedirects(response, reverse("alumni-opportunity-success"))
        opportunity = AlumniOpportunity.objects.get()
        self.assertEqual(opportunity.status, "pending")
        self.assertEqual(opportunity.alumni, self.approved)

    def test_opportunity_submission_rejects_wrong_profile_email(self):
        response = self.client.post(
            reverse("alumni-opportunity-create"),
            {
                "alumni": self.approved.pk,
                "verification_email": "not-the-alumnus@example.com",
                "opportunity_type": "training",
                "title": "Skills workshop",
                "summary": "A useful workshop.",
                "submission_token": self.submission_token(
                    "alumni-opportunity-create"
                ),
            },
        )
        self.assertContains(response, "does not match the selected verified profile")
        self.assertFalse(AlumniOpportunity.objects.exists())

    def test_only_current_approved_opportunities_are_public(self):
        AlumniOpportunity.objects.create(
            alumni=self.approved,
            opportunity_type="competition",
            title="Science competition",
            summary="Open to current learners.",
            status="approved",
        )
        AlumniOpportunity.objects.create(
            alumni=self.approved,
            opportunity_type="training",
            title="Unreviewed workshop",
            summary="Pending staff checks.",
        )
        response = self.client.get(reverse("alumni-list"))
        self.assertContains(response, "Science competition")
        self.assertNotContains(response, "Unreviewed workshop")
        opportunity_response = self.client.get(
            reverse("alumni-opportunity-list"), {"type": "competition"}
        )
        self.assertContains(opportunity_response, "Science competition")
        self.assertNotContains(opportunity_response, "Unreviewed workshop")

    def test_staff_can_review_opportunity_and_handle_mentorship(self):
        opportunity = AlumniOpportunity.objects.create(
            alumni=self.approved,
            opportunity_type="training",
            title="Career workshop",
            summary="A workshop for recent graduates.",
        )
        mentorship_request = MentorshipRequest.objects.create(
            mentor=self.approved,
            full_name="Recent Graduate",
            email="graduate@example.com",
            audience="graduate",
            focus_area="career",
            goals="Prepare for a first job.",
            consent_to_contact=True,
        )
        staff = get_user_model().objects.create_user(
            username="programme-reviewer",
            password="password",
            is_staff=True,
        )
        staff.user_permissions.add(
            Permission.objects.get(codename="view_alumniopportunity"),
            Permission.objects.get(codename="change_alumniopportunity"),
            Permission.objects.get(codename="view_mentorshiprequest"),
            Permission.objects.get(codename="change_mentorshiprequest"),
        )
        self.client.force_login(staff)
        response = self.client.post(
            reverse("alumni-opportunity-review-detail", args=[opportunity.pk]),
            {"status": "approved", "staff_notes": "Provider checked."},
        )
        self.assertRedirects(
            response,
            reverse("alumni-opportunity-review-detail", args=[opportunity.pk]),
        )
        opportunity.refresh_from_db()
        self.assertEqual(opportunity.status, "approved")
        self.assertEqual(opportunity.reviewed_by, staff)

        response = self.client.post(
            reverse("mentorship-request-detail", args=[mentorship_request.pk]),
            {"is_handled": True, "staff_notes": "Introduction arranged."},
        )
        self.assertRedirects(
            response,
            reverse("mentorship-request-detail", args=[mentorship_request.pk]),
        )
        mentorship_request.refresh_from_db()
        self.assertTrue(mentorship_request.is_handled)

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
