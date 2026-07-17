from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.decisions.models import Decision
from apps.projects.models import Project

User = get_user_model()


class DecisionViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='test', password='test')
        self.client.login(username='test', password='test')
        self.project = Project.objects.create(name='P', slug='p')
        self.decision = Decision.objects.create(
            project=self.project, title='D',
            context='C', question='Q',
        )

    def test_list_returns_decisions(self):
        response = self.client.get(reverse('decisions:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'D')

    def test_list_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('decisions:list'))
        self.assertEqual(response.status_code, 302)

    def test_detail_returns_200(self):
        r = self.client.get(reverse('decisions:detail', kwargs={'pk': self.decision.pk}))
        self.assertEqual(r.status_code, 200)

    def test_accept_decision(self):
        self.client.post(reverse('decisions:detail', kwargs={'pk': self.decision.pk}), {
            'action': 'accept', 'choice': 'Oui', 'consequences': 'Ok',
        })
        self.decision.refresh_from_db()
        self.assertEqual(self.decision.status, Decision.Status.ACCEPTED)
        self.assertEqual(self.decision.choice, 'Oui')

    def test_supersede_decision(self):
        self.decision.status = Decision.Status.ACCEPTED
        self.decision.choice = 'Oui'
        self.decision.consequences = 'Ok'
        self.decision.save()
        self.client.post(reverse('decisions:detail', kwargs={'pk': self.decision.pk}), {
            'action': 'supersede', 'new_choice': 'Non', 'consequences': 'Autre',
        })
        self.decision.refresh_from_db()
        self.assertEqual(self.decision.status, Decision.Status.SUPERSEDED)
        self.assertIsNotNone(self.decision.superseded_by)

    def test_create_decision(self):
        self.client.post(
            reverse('decisions:create', kwargs={'project_slug': 'p'}),
            {'title': 'Nouvelle', 'context': 'C', 'question': 'Q?'},
        )
        self.assertEqual(Decision.objects.count(), 2)

    def test_requires_login(self):
        self.client.logout()
        r = self.client.get(reverse('decisions:detail', kwargs={'pk': self.decision.pk}))
        self.assertEqual(r.status_code, 302)
