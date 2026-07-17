from django.db import models

from apps.core.models import BaseModel


class Decision(BaseModel):

    class Status(models.TextChoices):
        PROPOSED = 'proposed', 'Proposée'
        ACCEPTED = 'accepted', 'Acceptée'
        REJECTED = 'rejected', 'Rejetée'
        SUPERSEDED = 'superseded', 'Remplacée'

    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.PROTECT,
        related_name='decisions',
    )
    title = models.CharField(max_length=300)
    context = models.TextField()
    question = models.TextField()
    choice = models.TextField(blank=True)
    alternatives = models.TextField(blank=True)
    consequences = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PROPOSED,
    )
    decided_at = models.DateTimeField(null=True, blank=True)
    superseded_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='supersedes',
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
