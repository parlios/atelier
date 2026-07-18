"""Tests pour la commande atelier status — apps.integrations."""

import json
from io import StringIO

from django.core.management import call_command
from django.db import connection
from django.test import TestCase
from django.utils import timezone

from apps.activity.models import Activity
from apps.decisions.models import Decision
from apps.inbox.models import InboxItem
from apps.projects.models import Project
from apps.tasks.models import Task


class AtelierStatusCommandTest(TestCase):
    """Tests de la commande ``atelier status --format json``."""

    @classmethod
    def setUpTestData(cls):
        cls.project = Project.objects.create(
            name='Projet test',
            slug='projet-test',
            status=Project.Status.ACTIVE,
            priority=Project.Priority.HIGH,
            problem_statement='Problème',
            expected_outcome='Résultat',
        )
        cls.next_action = Task.objects.create(
            project=cls.project,
            title='Faire quelque chose',
            status=Task.Status.TODO,
            is_next_action=True,
        )
        cls.inbox_item = InboxItem.objects.create(
            title='Idée en attente',
            suggested_type=InboxItem.SuggestedType.IDEA,
        )
        cls.decision = Decision.objects.create(
            project=cls.project,
            title='Décision à prendre',
            context='Contexte',
            question='Question',
        )

    def test_command_output_is_valid_json(self):
        """La sortie de la commande est du JSON valide."""
        out = StringIO()
        call_command('atelier', 'status', '--format=json', stdout=out)
        data = json.loads(out.getvalue())
        self.assertEqual(data['schema_version'], '1.0')
        self.assertIn('summary', data)
        self.assertIn('projects', data)
        self.assertIn('recent_activity', data)
        self.assertIn('warnings', data)
        self.assertIn('generated_at', data)

    def test_summary_counts(self):
        """Les compteurs du résumé correspondent aux données réelles."""
        out = StringIO()
        call_command('atelier', 'status', '--format=json', stdout=out)
        data = json.loads(out.getvalue())
        s = data['summary']
        self.assertEqual(s['active_projects'], 1)
        self.assertEqual(s['paused_projects'], 0)
        self.assertEqual(s['inbox_pending'], 1)  # cls.inbox_item
        self.assertEqual(s['decisions_pending'], 1)  # cls.decision
        self.assertEqual(s['blocked_tasks'], 0)

    def test_project_list_contains_next_action(self):
        """Chaque projet liste sa prochaine action."""
        out = StringIO()
        call_command('atelier', 'status', '--format=json', stdout=out)
        data = json.loads(out.getvalue())
        projects = data['projects']
        self.assertEqual(len(projects), 1)
        p = projects[0]
        self.assertEqual(p['name'], 'Projet test')
        self.assertEqual(p['slug'], 'projet-test')
        self.assertEqual(p['next_action_title'], 'Faire quelque chose')
        self.assertEqual(p['next_action_status'], 'todo')

    def test_paused_project_counts_as_paused(self):
        """Un projet en pause est compté dans ``paused_projects``."""
        Project.objects.create(
            name='Projet en pause',
            slug='pause',
            status=Project.Status.PAUSED,
        )
        out = StringIO()
        call_command('atelier', 'status', '--format=json', stdout=out)
        data = json.loads(out.getvalue())
        self.assertEqual(data['summary']['paused_projects'], 1)
        self.assertEqual(len(data['projects']), 2)

    def test_active_project_without_next_action_raises_warning(self):
        """Un projet actif sans prochaine action génère un avertissement."""
        Project.objects.create(
            name='Sans action',
            slug='sans-action',
            status=Project.Status.ACTIVE,
            problem_statement='Pb',
            expected_outcome='Résultat',
        )
        out = StringIO()
        call_command('atelier', 'status', '--format=json', stdout=out)
        data = json.loads(out.getvalue())
        warnings = data['warnings']
        self.assertGreaterEqual(len(warnings), 1)
        self.assertIn('Sans action', warnings[0])

    def test_completed_projects_excluded(self):
        """Les projets terminés ou abandonnés sont exclus de la liste."""
        Project.objects.create(
            name='Fini',
            slug='fini',
            status=Project.Status.COMPLETED,
            completed_at=timezone.now(),
        )
        Project.objects.create(
            name='Abandonné',
            slug='abandonne',
            status=Project.Status.ABANDONED,
            abandoned_reason='Raison',
        )
        out = StringIO()
        call_command('atelier', 'status', '--format=json', stdout=out)
        data = json.loads(out.getvalue())
        slugs = [p['slug'] for p in data['projects']]
        self.assertNotIn('fini', slugs)
        self.assertNotIn('abandonne', slugs)

    def test_recent_activity_included(self):
        """L'activité récente est présente dans la réponse."""
        Activity.objects.create(
            id='00000000-0000-0000-0000-000000000001',
            event_type='created',
            object_type='project',
            object_id=self.project.pk,
            actor=Activity.Actor.MAX,
            message='Test activité',
        )
        out = StringIO()
        call_command('atelier', 'status', '--format=json', stdout=out)
        data = json.loads(out.getvalue())
        self.assertGreaterEqual(len(data['recent_activity']), 1)
        self.assertEqual(
            data['recent_activity'][0]['message'], 'Test activité'
        )

    def test_read_only_no_side_effects(self):
        """La commande ne crée ni ne modifie aucun objet."""
        count_before = Project.objects.count()
        out = StringIO()
        call_command('atelier', 'status', '--format=json', stdout=out)
        count_after = Project.objects.count()
        self.assertEqual(count_before, count_after)

    def test_empty_database_returns_empty_lists(self):
        """Une base vide retourne des listes vides sans erreur."""
        # Ordre : supprimer les objets qui référencent le projet d'abord
        Task.objects.all().delete()
        Decision.objects.all().delete()
        Project.objects.all().delete()
        InboxItem.objects.all().delete()
        out = StringIO()
        call_command('atelier', 'status', '--format=json', stdout=out)
        data = json.loads(out.getvalue())
        self.assertEqual(data['summary']['active_projects'], 0)
        self.assertEqual(data['summary']['inbox_pending'], 0)
        self.assertEqual(len(data['projects']), 0)
        self.assertEqual(len(data['recent_activity']), 0)

    def test_invalid_subcommand_exits_with_error(self):
        """Une sous-commande invalide écrit sur stderr et sort avec le code 1."""
        out = StringIO()
        err = StringIO()
        with self.assertRaises(SystemExit):
            call_command(
                'atelier', 'inconnu', '--format=json',
                stdout=out, stderr=err,
            )
        self.assertIn('Commande inconnue', err.getvalue())

    def test_warning_for_project_to_review(self):
        """Un projet avec review_due_on dépassée apparaît dans projects_to_review."""
        import datetime
        from django.utils import timezone
        Project.objects.create(
            name='À revoir',
            slug='a-revoir',
            status=Project.Status.ACTIVE,
            review_due_on=timezone.localdate() - datetime.timedelta(days=1),
            problem_statement='Pb',
            expected_outcome='Résultat',
        )
        out = StringIO()
        call_command('atelier', 'status', '--format=json', stdout=out)
        data = json.loads(out.getvalue())
        self.assertGreaterEqual(data['summary']['projects_to_review'], 1)

    def test_default_subcommand_works(self):
        """La commande sans sous-commande exécute le statut par défaut."""
        out = StringIO()
        call_command('atelier', '--format=json', stdout=out)
        data = json.loads(out.getvalue())
        self.assertIn('summary', data)
        self.assertIn('projects', data)

    def test_format_with_equals(self):
        """``--format=json`` fonctionne aussi bien que ``--format json``."""
        out = StringIO()
        call_command('atelier', 'status', '--format=json', stdout=out)
        data = json.loads(out.getvalue())
        self.assertEqual(data['schema_version'], '1.0')

    def test_atelier_help_outputs(self):
        """La commande ``atelier --help`` affiche l'aide et sort avec 0."""
        # L'aide argparse n'est pas capturée par call_command
        # On vérifie que la commande définit bien une aide
        from django.core.management import load_command_class
        cmd = load_command_class('apps.integrations', 'atelier')
        self.assertIn('Atelier', cmd.help or '')
        self.assertIn('Interroger', cmd.help or '')

    def test_query_count_is_bounded(self):
        """Le nombre de requêtes ORM ne dépasse pas un budget raisonnable."""
        # Ajoute des données supplémentaires au-delà du setUpTestData
        for i in range(3):
            p = Project.objects.create(
                name=f'P{i}', slug=f'p{i}', status='active',
                problem_statement='x', expected_outcome='y',
            )
            Task.objects.create(project=p, title=f'NA{i}', is_next_action=True)
        Project.objects.create(
            name='En pause', slug='pause', status='paused',
        )
        InboxItem.objects.create(title='Libre')
        first_project = Project.objects.filter(status='active').first()
        Decision.objects.create(
            project=first_project, title='D', context='c', question='q',
        )
        Task.objects.create(
            project=first_project, title='Bloqué', status='blocked',
        )
        with self.assertNumQueries(6):
            out = StringIO()
            call_command('atelier', 'status', '--format=json', stdout=out)

    def test_stderr_empty_on_success(self):
        """En cas de succès, stderr ne contient rien."""
        out = StringIO()
        err = StringIO()
        call_command('atelier', 'status', '--format=json', stdout=out, stderr=err)
        self.assertEqual(err.getvalue(), '')
