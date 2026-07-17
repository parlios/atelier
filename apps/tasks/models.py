from django.db import models

from apps.core.models import BaseModel


class Task(BaseModel):

    class Status(models.TextChoices):
        TODO = 'todo', 'À faire'
        IN_PROGRESS = 'in_progress', 'En cours'
        WAITING = 'waiting', 'En attente'
        BLOCKED = 'blocked', 'Bloquée'
        COMPLETED = 'completed', 'Terminée'
        CANCELED = 'canceled', 'Annulée'

    class Priority(models.TextChoices):
        HIGH = 'high', 'Haute'
        NORMAL = 'normal', 'Normale'
        LOW = 'low', 'Basse'

    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.PROTECT,
        related_name='tasks',
    )
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.TODO,
    )
    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.NORMAL,
    )
    is_next_action = models.BooleanField(default=False)
    due_on = models.DateField(null=True, blank=True)
    review_on = models.DateField(null=True, blank=True)
    blocker_description = models.TextField(blank=True)
    unblock_action = models.TextField(blank=True)
    result_summary = models.TextField(blank=True)
    evidence_url = models.URLField(max_length=2000, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    canceled_reason = models.TextField(blank=True)

    class Meta:
        ordering = ['-is_next_action', '-priority', 'due_on', '-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['project'],
                condition=models.Q(is_next_action=True),
                name='unique_next_action_per_project',
            ),
        ]

    def __str__(self):
        return self.title
