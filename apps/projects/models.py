from django.db import models
from django.utils.text import slugify

from apps.core.models import BaseModel


class Project(BaseModel):

    class Status(models.TextChoices):
        EXPLORATION = 'exploration', 'Exploration'
        PLANNED = 'planned', 'Planifié'
        ACTIVE = 'active', 'Actif'
        PAUSED = 'paused', 'En pause'
        COMPLETED = 'completed', 'Terminé'
        ABANDONED = 'abandoned', 'Abandonné'

    class Priority(models.TextChoices):
        HIGH = 'high', 'Haute'
        NORMAL = 'normal', 'Normale'
        LOW = 'low', 'Basse'

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    problem_statement = models.TextField(blank=True)
    expected_outcome = models.TextField(blank=True)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.EXPLORATION,
    )
    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.NORMAL,
    )
    workspace_path = models.CharField(max_length=500, blank=True)
    repository_url = models.URLField(max_length=500, blank=True)
    primary_url = models.URLField(max_length=500, blank=True)
    review_due_on = models.DateField(null=True, blank=True)
    last_reviewed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    abandoned_reason = models.TextField(blank=True)

    class Meta:
        ordering = ['status', '-priority', '-updated_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
