from django.db import models

from apps.core.models import BaseModel


class Asset(BaseModel):

    class AssetType(models.TextChoices):
        APPLICATION = 'application', 'Application'
        AI_AGENT = 'ai_agent', 'Agent IA'
        AUTOMATION = 'automation', 'Automatisation'
        REPOSITORY = 'repository', 'Dépôt'
        EXTERNAL_SERVICE = 'external_service', 'Service externe'
        INFRASTRUCTURE = 'infrastructure', 'Infrastructure'

    class Status(models.TextChoices):
        PLANNED = 'planned', 'Planifié'
        ACTIVE = 'active', 'Actif'
        DEGRADED = 'degraded', 'Dégradé'
        INACTIVE = 'inactive', 'Inactif'
        RETIRED = 'retired', 'Retiré'

    owner_project = models.ForeignKey(
        'projects.Project',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assets',
    )
    name = models.CharField(max_length=200)
    asset_type = models.CharField(max_length=30, choices=AssetType.choices)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PLANNED,
    )
    environment = models.CharField(max_length=50, blank=True)
    url = models.URLField(max_length=2000, blank=True)
    path = models.CharField(max_length=500, blank=True)
    description = models.TextField(blank=True)
    last_verified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['asset_type', 'name']

    def __str__(self):
        return self.name
