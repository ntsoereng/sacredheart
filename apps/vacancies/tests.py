from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Vacancy


def vacancy_data(**overrides):
    data = {
        "job_title": "English Teacher",
        "department": "Languages Department",
        "employment_type": "full_time",
        "location": "Sacred Heart High School",
        "application_deadline": timezone.localdate() + timedelta(days=14),
        "status": "open",
        "short_summary": "Teach English in a supportive school community.",
        "job_description": "<p>Teach English.</p>",
        "minimum_qualifications": "<ul><li>Teaching qualification</li></ul>",
        "experience_requirements": "<p>Two years preferred.</p>",
        "skills_competencies": "<ul><li>Communication</li></ul>",
        "application_instructions": "<p>Email a CV and certificates.</p>",
        "contact_email": "careers@sacredheart.ac.ls",
        "is_published": True,
    }
    data.update(overrides)
    return data


class PublicVacancyTests(TestCase):
    def test_only_open_published_unexpired_vacancies_are_visible(self):
        visible = Vacancy.objects.create(**vacancy_data())
        Vacancy.objects.create(**vacancy_data(job_title="Draft Role", is_published=False))
        Vacancy.objects.create(**vacancy_data(job_title="Filled Role", status="filled"))
        Vacancy.objects.create(**vacancy_data(
            job_title="Expired Role",
            application_deadline=timezone.localdate() - timedelta(days=1),
        ))

        response = self.client.get(reverse("vacancy-list"))

        self.assertContains(response, visible.job_title)
        self.assertNotContains(response, "Draft Role")
        self.assertNotContains(response, "Filled Role")
        self.assertNotContains(response, "Expired Role")

    def test_expired_vacancy_detail_is_not_public(self):
        vacancy = Vacancy.objects.create(**vacancy_data(
            application_deadline=timezone.localdate() - timedelta(days=1),
        ))
        response = self.client.get(reverse("vacancy-detail", args=[vacancy.slug]))
        self.assertEqual(response.status_code, 404)


class StaffVacancyTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="recruiter", password="test-password", is_staff=True
        )
        self.user.user_permissions.add(
            Permission.objects.get(codename="view_vacancy"),
            Permission.objects.get(codename="add_vacancy"),
            Permission.objects.get(codename="change_vacancy"),
        )
        self.client.force_login(self.user)

    def test_authorised_staff_can_create_a_vacancy(self):
        data = vacancy_data(
            application_deadline=(timezone.localdate() + timedelta(days=14)).isoformat(),
            job_description="<p>Teach.</p><script>alert(1)</script>",
        )
        response = self.client.post(reverse("vacancy-create"), data)

        self.assertRedirects(response, reverse("content-manager"))
        vacancy = Vacancy.objects.get()
        self.assertEqual(vacancy.created_by, self.user)
        self.assertNotIn("<script", vacancy.job_description)
        self.assertEqual(vacancy.contact_email, "careers@sacredheart.ac.ls")

    def test_staff_without_vacancy_permission_is_forbidden(self):
        user = get_user_model().objects.create_user(
            username="restricted-vacancy-user", password="test-password", is_staff=True
        )
        self.client.force_login(user)
        self.assertEqual(self.client.get(reverse("vacancy-create")).status_code, 403)
