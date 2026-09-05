from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .models import PersonalPlan, PersonalTask


@override_settings(SECURE_SSL_REDIRECT=False)
class WorkspaceTests(TestCase):
    def setUp(self):
        self.owner = get_user_model().objects.create_user(username='owner')
        self.other = get_user_model().objects.create_superuser(username='other', email='other@example.com', password='test')
        self.task = PersonalTask.objects.create(owner=self.owner, title='Private meeting', due_date=timezone.localdate() - timedelta(days=1))
        PersonalPlan.objects.create(owner=self.owner, notes='Confidential planning')

    def test_login_required_for_every_endpoint(self):
        for name, args in [('workspace', []), ('workspace-task-new', []), ('workspace-task', [self.task.pk]), ('workspace-task-complete', [self.task.pk]), ('workspace-task-reopen', [self.task.pk]), ('workspace-task-delete', [self.task.pk])]:
            self.assertEqual(self.client.get(reverse(name, args=args)).status_code, 302)
            self.assertEqual(self.client.post(reverse(name, args=args)).status_code, 302)

    def test_superuser_cannot_access_other_users_data(self):
        self.client.force_login(self.other)
        response = self.client.get(reverse('workspace'))
        self.assertNotContains(response, 'Private meeting')
        self.assertNotContains(response, 'Confidential planning')
        for name in ['workspace-task', 'workspace-task-complete', 'workspace-task-reopen', 'workspace-task-delete']:
            self.assertEqual(self.client.post(reverse(name, args=[self.task.pk]), {'title': 'Stolen'}).status_code, 404)
        self.assertEqual(self.client.get(reverse('workspace-task', args=[self.task.pk])).status_code, 404)
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, 'Private meeting')

    def test_task_lifecycle_owner_is_not_assignable(self):
        self.client.force_login(self.owner)
        data = {'title': 'New plan', 'due_date': '2026-10-01', 'priority': 'high', 'status': 'in_progress', 'notes': 'Prepare', 'owner': self.other.pk}
        self.assertEqual(self.client.post(reverse('workspace-task-new'), data).status_code, 302)
        task = PersonalTask.objects.get(title='New plan')
        self.assertEqual(task.owner, self.owner)
        self.assertContains(self.client.get(reverse('workspace-task', args=[task.pk])), '2026-10-01')
        data['title'] = 'Updated plan'
        self.client.post(reverse('workspace-task', args=[task.pk]), data)
        task.refresh_from_db()
        self.assertEqual(task.title, 'Updated plan')
        for action, expected in [('complete', 'done'), ('reopen', 'todo')]:
            url = reverse('workspace-task-' + action, args=[task.pk])
            self.assertEqual(self.client.get(url).status_code, 405)
            self.client.post(url)
            task.refresh_from_db()
            self.assertEqual(task.status, expected)
        self.assertEqual(self.client.get(reverse('workspace-task-delete', args=[task.pk])).status_code, 405)
        self.client.post(reverse('workspace-task-delete', args=[task.pk]))
        self.assertFalse(PersonalTask.objects.filter(pk=task.pk).exists())

    def test_dashboard_notes_validation_and_cache(self):
        self.client.force_login(self.owner)
        response = self.client.get(reverse('workspace'))
        self.assertEqual(response.context['counts']['overdue'], 1)
        self.assertIn('no-store', response.headers['Cache-Control'])
        self.assertContains(response, 'Private meeting')
        self.client.post(reverse('workspace'), {'notes': 'My goals', 'owner': self.other.pk})
        self.assertEqual(PersonalPlan.objects.get(owner=self.owner).notes, 'My goals')
        self.assertFalse(PersonalPlan.objects.filter(owner=self.other).exists())
        response = self.client.post(reverse('workspace-task-new'), {'title': 'Bad date', 'due_date': 'invalid', 'priority': 'high', 'status': 'todo'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors)
        self.assertFalse(PersonalTask.objects.filter(title='Bad date').exists())

    def test_csrf_required(self):
        from django.test import Client
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.owner)
        self.assertEqual(client.post(reverse('workspace-task-delete', args=[self.task.pk])).status_code, 403)
