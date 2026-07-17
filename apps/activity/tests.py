import uuid
from django.test import TestCase

from apps.activity.models import Activity
from apps.projects.models import Project


class ActivityModelTests(TestCase):

    def setUp(self):
        self.project = Project.objects.create(name='P', slug='p')

    def test_create_minimal(self):
        a = Activity.objects.create(
            id=uuid.uuid4(),
            event_type='project.created',
            object_type='project',
            object_id=uuid.uuid4(),
            actor=Activity.Actor.SYSTEM,
            message='Projet créé.',
        )
        self.assertEqual(a.event_type, 'project.created')

    def test_project_nullable(self):
        a = Activity.objects.create(
            id=uuid.uuid4(),
            event_type='task.completed',
            object_type='task',
            object_id=uuid.uuid4(),
            actor=Activity.Actor.MAX,
            message='Tâche terminée.',
        )
        self.assertIsNone(a.project)

    def test_activity_with_project(self):
        a = Activity.objects.create(
            id=uuid.uuid4(),
            project=self.project,
            event_type='project.updated',
            object_type='project',
            object_id=self.project.id,
            actor=Activity.Actor.SYSTEM,
            message='Projet mis à jour.',
        )
        self.assertEqual(a.project, self.project)

    def test_occurred_at_auto_set(self):
        a = Activity.objects.create(
            id=uuid.uuid4(),
            event_type='test',
            object_type='project',
            object_id=uuid.uuid4(),
            actor=Activity.Actor.SYSTEM,
            message='Test.',
        )
        self.assertIsNotNone(a.occurred_at)
