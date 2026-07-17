from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.registry.models import Asset

User = get_user_model()


class AssetViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='test', password='test')
        self.client.login(username='test', password='test')
        self.asset = Asset.objects.create(
            name='A', asset_type=Asset.AssetType.APPLICATION,
        )

    def test_list_returns_200(self):
        r = self.client.get(reverse('registry:list'))
        self.assertEqual(r.status_code, 200)

    def test_detail_returns_200(self):
        r = self.client.get(reverse('registry:detail', kwargs={'pk': self.asset.pk}))
        self.assertEqual(r.status_code, 200)

    def test_create_asset(self):
        self.client.post(reverse('registry:create'), {
            'name': 'B', 'asset_type': 'repository',
        })
        self.assertEqual(Asset.objects.count(), 2)

    def test_verify_asset(self):
        self.client.post(
            reverse('registry:detail', kwargs={'pk': self.asset.pk}),
            {'action': 'verify'},
        )
        self.asset.refresh_from_db()
        self.assertIsNotNone(self.asset.last_verified_at)

    def test_requires_login(self):
        self.client.logout()
        r = self.client.get(reverse('registry:list'))
        self.assertEqual(r.status_code, 302)
