from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.projects.models import Project
from apps.tasks.models import Task

User = get_user_model()


class TaskDetailViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='test', password='testpass123',
        )
        self.client.login(username='test', password='testpass123')
        self.project = Project.objects.create(name='P', slug='p')
        self.task = Task.objects.create(
            project=self.project, title='Tâche test',
        )

    def test_list_returns_tasks(self):
        response = self.client.get(reverse('tasks:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Tâche test')

    def test_list_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('tasks:list'))
        self.assertEqual(response.status_code, 302)

    def test_detail_returns_200(self):
        response = self.client.get(
            reverse('tasks:detail', kwargs={'pk': self.task.pk}),
        )
        self.assertEqual(response.status_code, 200)

    def test_start_task(self):
        self.client.post(
            reverse('tasks:detail', kwargs={'pk': self.task.pk}),
            {'action': 'start'},
        )
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, Task.Status.IN_PROGRESS)

    def test_complete_task(self):
        self.task.status = Task.Status.IN_PROGRESS
        self.task.save()
        self.client.post(
            reverse('tasks:detail', kwargs={'pk': self.task.pk}),
            {'action': 'complete', 'result_summary': 'Fait.'},
        )
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, Task.Status.COMPLETED)
        self.assertEqual(self.task.result_summary, 'Fait.')

    def test_complete_removes_next_action(self):
        self.task.status = Task.Status.IN_PROGRESS
        self.task.is_next_action = True
        self.task.save()
        self.client.post(
            reverse('tasks:detail', kwargs={'pk': self.task.pk}),
            {'action': 'complete', 'result_summary': 'Fait.'},
        )
        self.task.refresh_from_db()
        self.assertFalse(self.task.is_next_action)

    def test_block_task(self):
        self.task.status = Task.Status.IN_PROGRESS
        self.task.save()
        self.client.post(
            reverse('tasks:detail', kwargs={'pk': self.task.pk}),
            {'action': 'block', 'blocker_description': 'Bloqué.'},
        )
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, Task.Status.BLOCKED)

    def test_block_removes_next_action(self):
        self.task.status = Task.Status.IN_PROGRESS
        self.task.is_next_action = True
        self.task.save()
        self.client.post(
            reverse('tasks:detail', kwargs={'pk': self.task.pk}),
            {'action': 'block', 'blocker_description': 'Bloqué.'},
        )
        self.task.refresh_from_db()
        self.assertFalse(self.task.is_next_action)

    def test_unblock_task(self):
        self.task.status = Task.Status.BLOCKED
        self.task.blocker_description = 'X'
        self.task.save()
        self.client.post(
            reverse('tasks:detail', kwargs={'pk': self.task.pk}),
            {'action': 'unblock'},
        )
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, Task.Status.TODO)

    def test_toggle_next_action(self):
        self.assertFalse(self.task.is_next_action)
        self.client.post(
            reverse('tasks:detail', kwargs={'pk': self.task.pk}),
            {'action': 'toggle_next'},
        )
        self.task.refresh_from_db()
        self.assertTrue(self.task.is_next_action)

    def test_cancel_task(self):
        self.client.post(
            reverse('tasks:detail', kwargs={'pk': self.task.pk}),
            {'action': 'cancel', 'canceled_reason': 'Plus utile.'},
        )
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, Task.Status.CANCELED)

    def test_edit_task(self):
        self.client.post(
            reverse('tasks:detail', kwargs={'pk': self.task.pk}),
            {'action': 'edit', 'title': 'Nouveau titre', 'priority': 'high'},
        )
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, 'Nouveau titre')
        self.assertEqual(self.task.priority, Task.Priority.HIGH)

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(
            reverse('tasks:detail', kwargs={'pk': self.task.pk}),
        )
        self.assertEqual(response.status_code, 302)
