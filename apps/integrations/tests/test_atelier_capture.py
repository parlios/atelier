"""Tests pour la commande atelier capture — apps.integrations."""

from __future__ import annotations

import json
import uuid
from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from apps.activity.models import Activity
from apps.inbox.models import InboxItem
from apps.projects.models import Project


class AtelierCaptureCommandTest(TestCase):
    """Tests de la commande ``atelier capture --title ... --idempotency-key ...``."""

    @classmethod
    def setUpTestData(cls):
        cls.project = Project.objects.create(
            name='Mon projet',
            slug='mon-projet',
            status=Project.Status.ACTIVE,
            problem_statement='Pb',
            expected_outcome='Résultat',
        )

    def _run_capture(
        self,
        title='Titre test',
        idempotency_key='key-001',
        notes='',
        suggested_type='',
        project_slug='',
        expect_error=False,
    ):
        args = [
            'atelier', 'capture',
            f'--title={title}',
            f'--idempotency-key={idempotency_key}',
            f'--notes={notes}',
            f'--suggested-type={suggested_type}' if suggested_type else '--suggested-type=',
            f'--project-slug={project_slug}' if project_slug else '--project-slug=',
            '--format=json',
        ]
        out = StringIO()
        err = StringIO()
        if expect_error:
            with self.assertRaises(SystemExit):
                call_command(*args, stdout=out, stderr=err)
        else:
            call_command(*args, stdout=out, stderr=err)
        return json.loads(out.getvalue()), err.getvalue()

    # --- Succès ---

    def test_create_minimal(self):
        """Création minimale : titre + clé d'idempotence."""
        data, stderr = self._run_capture(title='Idée simple', idempotency_key='key-min')
        self.assertEqual(data['status'], 'created')
        self.assertEqual(data['inbox_item']['title'], 'Idée simple')
        self.assertEqual(data['inbox_item']['status'], 'unprocessed')
        self.assertTrue(data['activity_created'])
        self.assertEqual(stderr, '')
        self.assertEqual(InboxItem.objects.count(), 1)

    def test_create_with_notes(self):
        """Création avec notes facultatives."""
        data, _ = self._run_capture(
            title='Avec notes',
            idempotency_key='key-notes',
            notes='Notes importantes',
        )
        self.assertEqual(data['status'], 'created')
        item = InboxItem.objects.get(idempotency_key='key-notes')
        self.assertEqual(item.notes, 'Notes importantes')

    def test_create_with_suggested_type(self):
        """Création avec type suggéré valide."""
        data, _ = self._run_capture(
            title='Tâche suggérée',
            idempotency_key='key-type',
            suggested_type='task',
        )
        self.assertEqual(data['status'], 'created')
        item = InboxItem.objects.get(idempotency_key='key-type')
        self.assertEqual(item.suggested_type, 'task')

    def test_create_with_project_slug(self):
        """Création avec slug de projet valide."""
        data, _ = self._run_capture(
            title='Avec projet',
            idempotency_key='key-proj',
            project_slug='mon-projet',
        )
        self.assertEqual(data['status'], 'created')
        item = InboxItem.objects.get(idempotency_key='key-proj')
        self.assertEqual(item.suggested_project, self.project)

    def test_unicode_title(self):
        """Les caractères Unicode sont acceptés."""
        data, _ = self._run_capture(
            title='Mission déjà accomplie ✓',
            idempotency_key='key-unicode',
        )
        self.assertEqual(data['status'], 'created')
        self.assertIn('✓', data['inbox_item']['title'])

    def test_json_contract_valid(self):
        """Le JSON de succès contient tous les champs attendus."""
        data, stderr = self._run_capture(
            title='Contrat',
            idempotency_key='key-contract',
        )
        self.assertEqual(data['schema_version'], '1.0')
        self.assertIn('status', data)
        self.assertIn('inbox_item', data)
        self.assertIn('activity_created', data)
        self.assertIn('warnings', data)
        self.assertIsInstance(data['inbox_item']['id'], str)
        # UUID valide
        uuid.UUID(data['inbox_item']['id'])
        self.assertIn('T', data['inbox_item']['created_at'])  # ISO 8601

    def test_activity_created(self):
        """Une Activity avec acteur HERMES est créée."""
        self._run_capture(title='Activité', idempotency_key='key-act')
        activity = Activity.objects.filter(event_type='inbox_capture').last()
        self.assertIsNotNone(activity)
        self.assertEqual(activity.actor, Activity.Actor.HERMES)
        self.assertEqual(activity.object_type, 'inbox_item')

    # --- Erreurs ---

    def test_empty_title_refused(self):
        """Titre vide ou whitespace-only refusé."""
        data, _ = self._run_capture(title='  ', idempotency_key='key-empty', expect_error=True)
        self.assertEqual(data['status'], 'error')
        self.assertEqual(data['error']['code'], 'invalid_title')

    def test_title_too_long_refused(self):
        """Titre > 300 refusé."""
        data, _ = self._run_capture(
            title='X' * 301,
            idempotency_key='key-long',
            expect_error=True,
        )
        self.assertEqual(data['status'], 'error')
        self.assertEqual(data['error']['code'], 'title_too_long')

    def test_notes_too_long_refused(self):
        """Notes > 10 000 refusé."""
        data, _ = self._run_capture(
            title='Notes longues',
            idempotency_key='key-notes-long',
            notes='N' * 10001,
            expect_error=True,
        )
        self.assertEqual(data['status'], 'error')
        self.assertEqual(data['error']['code'], 'notes_too_long')

    def test_invalid_suggested_type_default_validation(self):
        """Type suggéré invalide refusé."""
        out = StringIO()
        err = StringIO()
        with self.assertRaises(SystemExit):
            call_command(
                'atelier', 'capture',
                '--title=X', '--idempotency-key=k',
                '--suggested-type=invalid',
                '--format=json',
                stdout=out, stderr=err,
            )

    def test_project_slug_not_found(self):
        """Slug de projet inexistant refusé."""
        data, _ = self._run_capture(
            title='Mauvais projet',
            idempotency_key='key-bad-proj',
            project_slug='inexistant',
            expect_error=True,
        )
        self.assertEqual(data['status'], 'error')
        self.assertEqual(data['error']['code'], 'project_not_found')

    def test_idempotency_key_empty(self):
        """Clé d'idempotence vide refusée."""
        data, _ = self._run_capture(
            title='Sans clé',
            idempotency_key='  ',
            expect_error=True,
        )
        self.assertEqual(data['status'], 'error')
        self.assertEqual(data['error']['code'], 'invalid_idempotency_key')

    # --- Idempotence ---

    def test_idempotency_reuses_existing(self):
        """Même clé d'idempotence → même objet retourné."""
        data1, _ = self._run_capture(title='Doublon', idempotency_key='key-dedup')
        data2, _ = self._run_capture(title='Doublon', idempotency_key='key-dedup')
        self.assertEqual(data1['status'], 'created')
        self.assertEqual(data2['status'], 'reused')
        self.assertEqual(data1['inbox_item']['id'], data2['inbox_item']['id'])
        self.assertEqual(InboxItem.objects.count(), 1)

    def test_stderr_empty_on_success(self):
        """En cas de succès, stderr est vide."""
        data, stderr = self._run_capture(
            title='Silence',
            idempotency_key='key-stderr',
        )
        self.assertEqual(stderr, '')
        self.assertEqual(data['status'], 'created')

    # --- Non-régression ---

    def test_status_still_works(self):
        """``atelier status`` fonctionne toujours après l'ajout de capture."""
        out = StringIO()
        call_command('atelier', 'status', '--format=json', stdout=out)
        data = json.loads(out.getvalue())
        self.assertIn('summary', data)

    def test_default_subcommand_still_works(self):
        """``atelier`` sans sous-commande exécute toujours le statut."""
        out = StringIO()
        call_command('atelier', '--format=json', stdout=out)
        data = json.loads(out.getvalue())
        self.assertIn('summary', data)
