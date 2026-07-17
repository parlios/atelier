from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.inbox.models import InboxItem
from apps.projects.models import Project

User = get_user_model()


class InboxViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='test', password='testpass123',
        )
        self.client.login(username='test', password='testpass123')
        self.project = Project.objects.create(name='P', slug='p')

    def test_inbox_list_returns_200(self):
        response = self.client.get(reverse('inbox:list'))
        self.assertEqual(response.status_code, 200)

    def test_capture_creates_item(self):
        self.client.post(reverse('inbox:capture'), {
            'title': 'Nouvelle idée',
            'suggested_type': 'idea',
        })
        self.assertEqual(InboxItem.objects.count(), 1)
        item = InboxItem.objects.first()
        self.assertEqual(item.title, 'Nouvelle idée')
        self.assertEqual(item.status, InboxItem.Status.UNPROCESSED)

    def test_capture_feedback_is_rendered_after_redirect(self):
        response = self.client.post(
            reverse('inbox:capture'),
            {'title': 'Message visible'},
            follow=True,
        )
        self.assertContains(response, 'Élément capturé.')
        self.assertContains(response, 'class="message message--success"')

    def test_capture_requires_title(self):
        self.client.post(reverse('inbox:capture'), {'title': ''})
        self.assertEqual(InboxItem.objects.count(), 0)

    def test_qualify_discard(self):
        item = InboxItem.objects.create(title='À jeter')
        self.client.post(
            reverse('inbox:qualify', kwargs={'pk': item.pk}),
            {'action': 'discard', 'discarded_reason': 'Pas utile.'},
        )
        item.refresh_from_db()
        self.assertEqual(item.status, InboxItem.Status.DISCARDED)

    def test_qualify_to_project(self):
        item = InboxItem.objects.create(title='Nouveau projet')
        self.client.post(
            reverse('inbox:qualify', kwargs={'pk': item.pk}),
            {'action': 'to_project'},
        )
        item.refresh_from_db()
        self.assertEqual(item.status, InboxItem.Status.PROCESSED)
        self.assertIsNotNone(item.destination_project)
        self.assertEqual(item.destination_project.name, 'Nouveau projet')

    def test_qualify_to_task(self):
        item = InboxItem.objects.create(title='Action')
        self.client.post(
            reverse('inbox:qualify', kwargs={'pk': item.pk}),
            {'action': 'to_task', 'project': self.project.pk},
        )
        item.refresh_from_db()
        self.assertEqual(item.status, InboxItem.Status.PROCESSED)
        self.assertIsNotNone(item.destination_task)

    def test_qualify_to_decision(self):
        item = InboxItem.objects.create(title='Choix à faire')
        self.client.post(
            reverse('inbox:qualify', kwargs={'pk': item.pk}),
            {'action': 'to_decision', 'project': self.project.pk},
        )
        item.refresh_from_db()
        self.assertIsNotNone(item.destination_decision)

    def test_qualify_to_resource(self):
        item = InboxItem.objects.create(title='Note utile')
        self.client.post(
            reverse('inbox:qualify', kwargs={'pk': item.pk}),
            {'action': 'to_resource', 'resource_type': 'note'},
        )
        item.refresh_from_db()
        self.assertIsNotNone(item.destination_resource)

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('inbox:list'))
        self.assertEqual(response.status_code, 302)
