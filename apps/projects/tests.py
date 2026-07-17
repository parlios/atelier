from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.projects.models import Project
from apps.tasks.models import Task

User = get_user_model()


class ProjectListViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='test', password='testpass123',
        )
        self.client.login(username='test', password='testpass123')

    def test_list_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('projects:list'))
        self.assertEqual(response.status_code, 302)

    def test_list_returns_200(self):
        response = self.client.get(reverse('projects:list'))
        self.assertEqual(response.status_code, 200)

    def test_list_shows_project(self):
        Project.objects.create(name='Test', slug='test')
        response = self.client.get(reverse('projects:list'))
        self.assertContains(response, 'Test')

    def test_list_filters_by_status(self):
        Project.objects.create(
            name='Active', slug='active',
            status=Project.Status.ACTIVE,
        )
        Project.objects.create(
            name='Done', slug='done',
            status=Project.Status.COMPLETED,
        )
        response = self.client.get(
            reverse('projects:list') + '?status=active',
        )
        self.assertContains(response, 'Active')
        self.assertNotContains(response, 'Done')


class ProjectDetailViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='test', password='testpass123',
        )
        self.client.login(username='test', password='testpass123')
        self.project = Project.objects.create(
            name='Atelier', slug='atelier',
            problem_statement='Problème test',
            expected_outcome='Résultat test',
            status=Project.Status.ACTIVE,
        )

    def test_detail_returns_200(self):
        response = self.client.get(
            reverse('projects:detail', kwargs={'slug': 'atelier'}),
        )
        self.assertEqual(response.status_code, 200)

    def test_detail_shows_name(self):
        response = self.client.get(
            reverse('projects:detail', kwargs={'slug': 'atelier'}),
        )
        self.assertContains(response, 'Atelier')

    def test_detail_shows_next_action(self):
        task = Task.objects.create(
            project=self.project,
            title='Faire ceci',
            is_next_action=True,
        )
        response = self.client.get(
            reverse('projects:detail', kwargs={'slug': 'atelier'}),
        )
        self.assertContains(response, 'Faire ceci')

    def test_detail_requires_login(self):
        self.client.logout()
        response = self.client.get(
            reverse('projects:detail', kwargs={'slug': 'atelier'}),
        )
        self.assertEqual(response.status_code, 302)
