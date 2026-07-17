from django.db import models

from apps.core.models import BaseModel


class Resource(BaseModel):

    class ResourceType(models.TextChoices):
        NOTE = 'note', 'Note'
        IDEA = 'idea', 'Idée'
        DOCUMENT = 'document', 'Document'
        PROMPT = 'prompt', 'Prompt'
        PROCEDURE = 'procedure', 'Procédure'
        REFERENCE = 'reference', 'Référence'

    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='resources',
    )
    title = models.CharField(max_length=300)
    resource_type = models.CharField(
        max_length=20,
        choices=ResourceType.choices,
    )
    content = models.TextField(blank=True)
    source_url = models.URLField(max_length=2000, blank=True)
    source_path = models.CharField(max_length=500, blank=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return self.title
