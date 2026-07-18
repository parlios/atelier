from __future__ import annotations

from datetime import date, datetime
from typing import Any

from django.utils import timezone

from apps.activity.models import Activity
from apps.decisions.models import Decision
from apps.inbox.models import InboxItem
from apps.projects.models import Project
from apps.tasks.models import Task

from apps.integrations.contracts import (
    build_activity_entry,
    build_project_summary,
)


def get_status() -> dict[str, Any]:
    """Retourne les données structurées pour la commande atelier status.

    Entièrement en lecture seule — aucun objet n'est créé ni modifié.
    """
    projects = _load_active_projects_with_tasks()
    active_projects = [p for p in projects if p.status == Project.Status.ACTIVE]
    paused_projects = [p for p in projects if p.status == Project.Status.PAUSED]
    blocked_tasks_count = Task.objects.filter(
        status=Task.Status.BLOCKED,
        archived_at__isnull=True,
    ).count()
    inbox_pending = InboxItem.objects.filter(
        status=InboxItem.Status.UNPROCESSED,
    ).count()
    decisions_pending = Decision.objects.filter(
        status=Decision.Status.PROPOSED,
    ).count()

    today = timezone.localdate()
    projects_to_review = [
        p for p in active_projects + paused_projects
        if p.review_due_on and p.review_due_on <= today
    ]

    next_actions: dict[str, str | None] = {}
    for p in projects:
        next_action = getattr(p, '_next_action', None)
        next_actions[p.slug] = next_action.title if next_action else None

    project_list = [
        build_project_summary(
            name=p.name,
            slug=p.slug,
            status=p.status,
            priority=p.priority,
            next_action_title=next_actions.get(p.slug),
            next_action_status=_next_action_status(p),
            review_due_on=p.review_due_on.isoformat() if p.review_due_on else None,
        )
        for p in projects
    ]

    recent = _load_recent_activity()

    warnings: list[str] = []
    for p in active_projects:
        if not next_actions.get(p.slug):
            warnings.append(
                f"Le projet « {p.name} » est actif mais n'a pas de prochaine action."
            )

    summary = {
        "active_projects": len(active_projects),
        "paused_projects": len(paused_projects),
        "projects_to_review": len(projects_to_review),
        "inbox_pending": inbox_pending,
        "decisions_pending": decisions_pending,
        "blocked_tasks": blocked_tasks_count,
    }

    return {
        "summary": summary,
        "projects": project_list,
        "recent_activity": recent,
        "warnings": warnings,
    }


def _load_active_projects_with_tasks() -> list[Project]:
    """Charge les projets non archivés avec leur prochaine action."""
    projects = list(
        Project.objects.filter(archived_at__isnull=True)
        .exclude(status__in=[
            Project.Status.COMPLETED,
            Project.Status.ABANDONED,
        ])
        .select_related()
        .order_by('status', '-priority', '-updated_at')
    )
    # Prefetch la prochaine action pour chaque projet en une seule requête
    project_ids = [p.pk for p in projects]
    next_actions = {
        na.project_id: na
        for na in Task.objects.filter(
            project_id__in=project_ids,
            is_next_action=True,
        ).only('title', 'status', 'project_id')
    }
    for p in projects:
        p._next_action = next_actions.get(p.pk)
    return projects


def _next_action_status(project: Project) -> str | None:
    na = getattr(project, '_next_action', None)
    return na.status if na else None


def _load_recent_activity(limit: int = 10) -> list[dict[str, Any]]:
    entries = Activity.objects.order_by('-occurred_at')[:limit]
    return [
        build_activity_entry(
            occurred_at=e.occurred_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
            actor=e.actor,
            event_type=e.event_type,
            message=e.message,
            project_name=str(e.project) if e.project else None,
        )
        for e in entries
    ]
