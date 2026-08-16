from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

from .models import AlumniOpportunity, AlumniStory, MentorshipRequest


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

    def test_directory_can_filter_available_mentors(self):
        response = self.client.get(reverse("alumni-list"), {"mentors": "yes"})
        self.assertContains(response, self.approved.full_name)
        self.assertNotContains(response, self.pending.full_name)

    def test_mentorship_request_is_stored_privately(self):
        response = self.client.post(
            reverse("alumni-mentorship-request"),
            {
                "mentor": self.approved.pk,
                "full_name": "Current Learner",
                "email": "learner@example.com",
                "phone": "+266 5000 1111",
                "audience": "learner",
                "focus_area": "career",
                "goals": "I want to understand engineering careers.",
                "consent_to_contact": True,
                "submission_token": self.submission_token(
                    "alumni-mentorship-request"
                ),
            },
        )
        self.assertRedirects(response, reverse("alumni-mentorship-success"))
        request = MentorshipRequest.objects.get()
        self.assertEqual(request.mentor, self.approved)
        self.assertEqual(request.email, "learner@example.com")

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
