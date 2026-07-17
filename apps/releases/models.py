from django.db import models

from apps.core.models import BaseModel


class Release(BaseModel):

    class Status(models.TextChoices):
        PREPARED = 'prepared', 'Préparée'
        RELEASED = 'released', 'Livrée'
        VALIDATED = 'validated', 'Validée'
        FAILED = 'failed', 'Échouée'
        WITHDRAWN = 'withdrawn', 'Retirée'

    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.PROTECT,
        related_name='releases',
    )
    asset = models.ForeignKey(
        'registry.Asset',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='releases',
    )
    version_label = models.CharField(max_length=100)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PREPARED,
    )
    summary = models.TextField()
    reference_url = models.URLField(max_length=2000, blank=True)
    released_at = models.DateTimeField(null=True, blank=True)
    validation_result = models.TextField(blank=True)
    validated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-released_at', '-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['project', 'version_label'],
                name='unique_version_per_project',
            ),
        ]

    def __str__(self):
        return f'{self.project.name} — {self.version_label}'
