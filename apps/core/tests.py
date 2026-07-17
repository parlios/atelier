import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.activity.models import Activity
from apps.decisions.models import Decision
from apps.inbox.models import InboxItem
from apps.projects.models import Project
from apps.releases.models import Release
from apps.tasks.models import Task

User = get_user_model()


class HomeViewTests(TestCase):

    def test_home_returns_200(self):
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)

    def test_home_uses_correct_template(self):
        response = self.client.get(reverse('core:home'))
        self.assertTemplateUsed(response, 'core/home.html')
        self.assertTemplateUsed(response, 'base.html')


class LoginViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='test', password='testpass123',
        )

    def test_login_page_returns_200(self):
        response = self.client.get(reverse('core:login'))
        self.assertEqual(response.status_code, 200)

    def test_login_success_redirects(self):
        response = self.client.post(reverse('core:login'), {
            'username': 'test',
            'password': 'testpass123',
        })
        self.assertRedirects(response, reverse('core:dashboard'))

    def test_login_failure_stays(self):
        response = self.client.post(reverse('core:login'), {
            'username': 'test',
            'password': 'wrong',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)


class DashboardViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='test', password='testpass123',
        )

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('core:dashboard'))
        self.assertRedirects(
            response, f'{reverse("core:login")}?next={reverse("core:dashboard")}',
        )

    def test_dashboard_authenticated(self):
        self.client.login(username='test', password='testpass123')
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/dashboard.html')

    def test_authenticated_page_uses_application_shell(self):
        self.client.login(username='test', password='testpass123')
        response = self.client.get(reverse('core:dashboard'))
        self.assertContains(response, 'class="app-shell"')
        self.assertContains(response, 'atelier/css/app.css')
        self.assertContains(response, 'aria-current="page"')

    def test_dashboard_shows_operational_context(self):
        project = Project.objects.create(name='Pilotage', slug='pilotage')
        Decision.objects.create(
            project=project,
            title='Choisir la trajectoire',
            context='Contexte',
            question='Quelle suite ?',
        )
        Release.objects.create(
            project=project,
            version_label='MVP-1',
            summary='Première livraison',
        )
        Activity.objects.create(
            id=uuid.uuid4(),
            project=project,
            event_type='project.created',
            object_type='project',
            object_id=project.pk,
            actor=Activity.Actor.MAX,
            message='Projet de pilotage créé',
        )
        self.client.login(username='test', password='testpass123')

        response = self.client.get(reverse('core:dashboard'))

        self.assertContains(response, 'Choisir la trajectoire')
        self.assertContains(response, 'MVP-1')
        self.assertContains(response, 'Projet de pilotage créé')

    def test_navigation_shows_unprocessed_inbox_count(self):
        InboxItem.objects.create(title='À qualifier')
        self.client.login(username='test', password='testpass123')

        response = self.client.get(reverse('core:dashboard'))

        self.assertContains(response, '1 éléments à traiter')


class LogoutViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='test', password='testpass123',
        )

    def test_logout_redirects_home(self):
        self.client.login(username='test', password='testpass123')
        response = self.client.post(reverse('core:logout'))
        self.assertRedirects(response, reverse('core:home'))


class SearchViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='test', password='testpass123',
        )
        self.client.login(username='test', password='testpass123')

    def test_search_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('core:search'))
        self.assertEqual(response.status_code, 302)

    def test_search_page_returns_200(self):
        response = self.client.get(reverse('core:search'))
        self.assertEqual(response.status_code, 200)

    def test_search_finds_project(self):
        Project.objects.create(name='Atelier', slug='atelier')
        response = self.client.get(reverse('core:search') + '?q=Atelier')
        self.assertContains(response, 'Atelier')

    def test_search_finds_task(self):
        p = Project.objects.create(name='P', slug='p')
        Task.objects.create(project=p, title='Déployer le projet')
        response = self.client.get(reverse('core:search') + '?q=Déployer')
        self.assertContains(response, 'Déployer le projet')

    def test_search_no_results(self):
        response = self.client.get(reverse('core:search') + '?q=xyz123')
        self.assertContains(response, 'Aucun résultat')
