"""Service de capture Inbox pour la sous-commande atelier capture."""

from __future__ import annotations

import uuid

from django.db import transaction

from apps.activity.models import Activity
from apps.inbox.models import InboxItem
from apps.projects.models import Project


class CaptureResult:
    """Résultat structuré d'une opération de capture."""

    def __init__(
        self,
        inbox_item: InboxItem,
        created: bool,
        activity_created: bool,
    ):
        self.inbox_item = inbox_item
        self.created = created
        self.activity_created = activity_created


class CaptureError(Exception):
    """Erreur métier contrôlée lors de la capture."""

    def __init__(self, code: str, message: str, fields: dict | None = None):
        self.code = code
        self.message = message
        self.fields = fields or {}
        super().__init__(self.message)


def capture(
    *,
    title: str,
    idempotency_key: str | None = None,
    notes: str = '',
    suggested_type: str = '',
    project_slug: str | None = None,
) -> CaptureResult:
    """Crée un InboxItem (et une Activity) avec idempotence.

    Retourne ``CaptureResult``.
    Lève ``CaptureError`` pour les erreurs métier contrôlées.
    """
    title = title.strip()
    if not title:
        raise CaptureError(
            'invalid_title',
            'Le titre est obligatoire.',
            {'title': ['Ce champ est obligatoire.']},
        )
    if len(title) > 300:
        raise CaptureError(
            'title_too_long',
            'Le titre ne peut pas dépasser 300 caractères.',
            {'title': [f'{len(title)}/300 caractères.']},
        )
    if len(notes) > 10000:
        raise CaptureError(
            'notes_too_long',
            'Les notes ne peuvent pas dépasser 10 000 caractères.',
            {'notes': [f'{len(notes)}/10000 caractères.']},
        )

    # Valider suggested_type si fourni
    valid_types = set(InboxItem.SuggestedType.values)
    if suggested_type and suggested_type not in valid_types:
        raise CaptureError(
            'invalid_suggested_type',
            f'Type suggéré invalide. Valeurs acceptées : {", ".join(sorted(valid_types))}.',
            {'suggested_type': [f'Reçu : {suggested_type!r}.']},
        )

    # Résoudre le projet si slug fourni
    project = None
    if project_slug:
        try:
            project = Project.objects.get(slug=project_slug, archived_at__isnull=True)
        except Project.DoesNotExist:
            raise CaptureError(
                'project_not_found',
                f'Projet « {project_slug} » introuvable ou archivé.',
                {'project_slug': [f'Aucun projet avec ce slug.']},
            )

    # Idempotence
    if idempotency_key:
        existing = InboxItem.objects.filter(
            idempotency_key=idempotency_key,
        ).first()
        if existing:
            return CaptureResult(
                inbox_item=existing,
                created=False,
                activity_created=False,
            )

    with transaction.atomic():
        item = InboxItem.objects.create(
            title=title,
            notes=notes,
            suggested_type=suggested_type,
            suggested_project=project,
            idempotency_key=idempotency_key,
        )

        Activity.objects.create(
            id=uuid.uuid4(),
            event_type='inbox_capture',
            object_type='inbox_item',
            object_id=item.pk,
            actor=Activity.Actor.HERMES,
            message="Élément capturé par Hermes dans l'Inbox.",
            project=project,
        )

    return CaptureResult(
        inbox_item=item,
        created=True,
        activity_created=True,
    )
