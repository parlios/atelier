from __future__ import annotations

import json
import sys

from django.core.management.base import BaseCommand, CommandError

from apps.integrations.contracts import (
    build_capture_error,
    build_capture_success,
    build_response,
)
from apps.integrations.services.capture import CaptureError, capture
from apps.integrations.services.status import get_status


class Command(BaseCommand):
    help = 'Interroger et alimenter Atelier depuis Hermes (ou tout terminal).'

    SUBCOMMANDS = {'status', 'capture'}

    def add_arguments(self, parser):
        parser.add_argument('subcommand', nargs='?', default='status')
        parser.add_argument(
            '--format',
            default='json',
            choices=['json'],
            help='Format de sortie (json uniquement pour l\'instant).',
        )

        # Arguments pour capture
        parser.add_argument('--title', type=str, default='')
        parser.add_argument('--notes', type=str, default='')
        parser.add_argument('--suggested-type', type=str, default='')
        parser.add_argument('--project-slug', type=str, default='')
        parser.add_argument('--idempotency-key', type=str, default='')

    def handle(self, *args, **options):
        subcommand = options['subcommand']

        if subcommand not in self.SUBCOMMANDS:
            self.stderr.write(
                f'Commande inconnue : « {subcommand} ». '
                f'Sous-commandes disponibles : '
                f'{", ".join(sorted(self.SUBCOMMANDS))}\n'
            )
            sys.exit(1)

        if subcommand == 'status':
            self._handle_status(options)
        elif subcommand == 'capture':
            self._handle_capture(options)

    def _handle_status(self, options):
        format = options.get('format', 'json')
        if format != 'json':
            self.stderr.write(f'Format « {format} » non supporté.\n')
            sys.exit(1)

        try:
            data = get_status()
        except Exception as exc:
            raise CommandError(
                f'Erreur lors de la récupération du statut : {exc}'
            ) from exc

        response = build_response(**data)
        self.stdout.write(json.dumps(response, indent=2, ensure_ascii=False))

    def _handle_capture(self, options):
        format = options.get('format', 'json')
        if format != 'json':
            self.stderr.write(f'Format « {format} » non supporté.\n')
            sys.exit(1)

        title = options.get('title', '')
        idempotency_key = options.get('idempotency_key', '')
        notes = options.get('notes', '')
        suggested_type = options.get('suggested_type', '')
        project_slug = options.get('project_slug', '')

        # Validation minimale avant d'appeler le service
        if not title.strip():
            response = build_capture_error(
                'invalid_title',
                'Le titre est obligatoire.',
                {'title': ['Ce champ est obligatoire.']},
            )
            self.stdout.write(json.dumps(response, indent=2, ensure_ascii=False))
            sys.exit(1)

        if not idempotency_key.strip():
            response = build_capture_error(
                'invalid_idempotency_key',
                'La clé d\'idempotence est obligatoire.',
                {'idempotency_key': ['Ce champ est obligatoire.']},
            )
            self.stdout.write(json.dumps(response, indent=2, ensure_ascii=False))
            sys.exit(1)

        try:
            result = capture(
                title=title,
                idempotency_key=idempotency_key,
                notes=notes,
                suggested_type=suggested_type,
                project_slug=project_slug or None,
            )
        except CaptureError as e:
            response = build_capture_error(e.code, e.message, e.fields)
            self.stdout.write(json.dumps(response, indent=2, ensure_ascii=False))
            sys.exit(1)

        item = result.inbox_item
        response = build_capture_success(
            inbox_item_id=str(item.pk),
            title=item.title,
            status=item.status,
            created_at=item.created_at.strftime('%Y-%m-%dT%H:%M:%SZ'),
            created=result.created,
            activity_created=result.activity_created,
            warnings=[],
        )
        self.stdout.write(json.dumps(response, indent=2, ensure_ascii=False))
