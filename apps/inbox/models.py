from django.db import models

from apps.core.models import BaseModel


class InboxItem(BaseModel):

    class Status(models.TextChoices):
        UNPROCESSED = 'unprocessed', 'À traiter'
        PROCESSED = 'processed', 'Traité'
        DISCARDED = 'discarded', 'Écarté'

    class SuggestedType(models.TextChoices):
        IDEA = 'idea', 'Idée'
        TASK = 'task', 'Tâche'
        DECISION = 'decision', 'Décision'
        RESOURCE = 'resource', 'Ressource'
        OTHER = 'other', 'Autre'

    title = models.CharField(max_length=300)
    notes = models.TextField(blank=True)
    suggested_type = models.CharField(
        max_length=20,
        choices=SuggestedType.choices,
        blank=True,
    )
    suggested_project = models.ForeignKey(
        'projects.Project',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inbox_suggestions',
    )
    source_url = models.URLField(max_length=2000, blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.UNPROCESSED,
    )
    discarded_reason = models.TextField(blank=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    destination_project = models.ForeignKey(
        'projects.Project',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inbox_processed',
    )
    destination_task = models.ForeignKey(
        'tasks.Task',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inbox_origin',
    )
    destination_decision = models.ForeignKey(
        'decisions.Decision',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inbox_origin',
    )
    destination_resource = models.ForeignKey(
        'resources.Resource',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inbox_origin',
    )
    idempotency_key = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
