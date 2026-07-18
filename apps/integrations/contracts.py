"""Structure du contrat JSON de sortie pour les commandes atelier.

Chaque dictionnaire est construit sans dépendance à DRF.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any


def build_project_summary(
    name: str,
    slug: str,
    status: str,
    priority: str,
    next_action_title: str | None,
    next_action_status: str | None,
    review_due_on: str | None,
) -> dict[str, Any]:
    return {
        "name": name,
        "slug": slug,
        "status": status,
        "priority": priority,
        "next_action_title": next_action_title,
        "next_action_status": next_action_status,
        "review_due_on": review_due_on,
    }


def build_activity_entry(
    occurred_at: str,
    actor: str,
    event_type: str,
    message: str,
    project_name: str | None,
) -> dict[str, Any]:
    return {
        "occurred_at": occurred_at,
        "actor": actor,
        "event_type": event_type,
        "message": message,
        "project_name": project_name,
    }


def build_response(
    summary: dict[str, int],
    projects: list[dict[str, Any]],
    recent_activity: list[dict[str, Any]],
    warnings: list[str],
) -> dict[str, Any]:
    """Construit la réponse JSON complète avec version et horodatage."""
    return {
        "schema_version": "1.0",
        "generated_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "summary": summary,
        "projects": projects,
        "recent_activity": recent_activity,
        "warnings": warnings,
    }


def build_capture_success(
    inbox_item_id: str,
    title: str,
    status: str,
    created_at: str,
    created: bool,
    activity_created: bool,
    warnings: list[str],
) -> dict[str, Any]:
    """Construit la réponse JSON pour une capture réussie."""
    return {
        "schema_version": "1.0",
        "status": "created" if created else "reused",
        "inbox_item": {
            "id": inbox_item_id,
            "title": title,
            "status": status,
            "created_at": created_at,
        },
        "activity_created": activity_created,
        "warnings": warnings,
    }


def build_capture_error(
    code: str,
    message: str,
    fields: dict[str, list[str]] | None = None,
) -> dict[str, Any]:
    """Construit la réponse JSON pour une erreur de capture contrôlée."""
    return {
        "schema_version": "1.0",
        "status": "error",
        "error": {
            "code": code,
            "message": message,
            "fields": fields or {},
        },
    }
