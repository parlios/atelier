from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.projects.models import Project
from apps.releases.models import Release

User = get_user_model()


class ReleaseViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='test', password='test')
        self.client.login(username='test', password='test')
        self.project = Project.objects.create(name='P', slug='p')
        self.release = Release.objects.create(
            project=self.project, version_label='0.1', summary='S',
        )

    def test_list_returns_releases(self):
        response = self.client.get(reverse('releases:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '0.1')

    def test_list_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('releases:list'))
        self.assertEqual(response.status_code, 302)

    def test_detail_returns_200(self):
        r = self.client.get(reverse('releases:detail', kwargs={'pk': self.release.pk}))
        self.assertEqual(r.status_code, 200)

    def test_release(self):
        self.client.post(
            reverse('releases:detail', kwargs={'pk': self.release.pk}),
            {'action': 'release'},
        )
        self.release.refresh_from_db()
        self.assertEqual(self.release.status, Release.Status.RELEASED)

    def test_validate(self):
        self.client.post(
            reverse('releases:detail', kwargs={'pk': self.release.pk}),
            {'action': 'validate', 'validation_result': 'OK'},
        )
        self.release.refresh_from_db()
        self.assertEqual(self.release.status, Release.Status.VALIDATED)

    def test_fail(self):
        self.client.post(
            reverse('releases:detail', kwargs={'pk': self.release.pk}),
            {'action': 'fail', 'validation_result': 'Erreur'},
        )
        self.release.refresh_from_db()
        self.assertEqual(self.release.status, Release.Status.FAILED)

    def test_create_release(self):
        self.client.post(
            reverse('releases:create', kwargs={'project_slug': 'p'}),
            {'version_label': '0.2', 'summary': 'Next'},
        )
        self.assertEqual(Release.objects.count(), 2)

    def test_requires_login(self):
        self.client.logout()
        r = self.client.get(reverse('releases:detail', kwargs={'pk': self.release.pk}))
        self.assertEqual(r.status_code, 302)
