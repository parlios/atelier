from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.resources.models import Resource

User = get_user_model()


class ResourceViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='test', password='test')
        self.client.login(username='test', password='test')
        self.resource = Resource.objects.create(
            title='R', resource_type=Resource.ResourceType.NOTE,
        )

    def test_list_returns_200(self):
        r = self.client.get(reverse('resources:list'))
        self.assertEqual(r.status_code, 200)

    def test_detail_returns_200(self):
        r = self.client.get(reverse('resources:detail', kwargs={'pk': self.resource.pk}))
        self.assertEqual(r.status_code, 200)

    def test_create_resource(self):
        self.client.post(reverse('resources:create'), {
            'title': 'Nouvelle', 'resource_type': 'prompt', 'content': 'Tu es…',
        })
        self.assertEqual(Resource.objects.count(), 2)

    def test_edit_resource(self):
        self.client.post(
            reverse('resources:detail', kwargs={'pk': self.resource.pk}),
            {'action': 'edit', 'title': 'Modifiée', 'resource_type': 'document', 'content': 'New'},
        )
        self.resource.refresh_from_db()
        self.assertEqual(self.resource.title, 'Modifiée')

    def test_requires_login(self):
        self.client.logout()
        r = self.client.get(reverse('resources:list'))
        self.assertEqual(r.status_code, 302)
