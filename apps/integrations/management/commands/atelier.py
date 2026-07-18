from __future__ import annotations

import json
import sys

from django.core.management.base import BaseCommand, CommandError

from apps.integrations.contracts import build_response
from apps.integrations.services.status import get_status


class Command(BaseCommand):
    help = 'Interroger Atelier depuis Hermes (ou tout terminal).'

    SUBCOMMANDS = {'status'}

    def add_arguments(self, parser):
        parser.add_argument('subcommand', nargs='?', default='status')
        parser.add_argument(
            '--format',
            default='json',
            choices=['json'],
            help='Format de sortie (json uniquement pour l\'instant).',
        )

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
            format = options.get('format', 'json')
            if format != 'json':
                self.stderr.write(
                    f'Format « {format} » non supporté.\n'
                )
                sys.exit(1)

            try:
                data = get_status()
            except Exception as exc:
                raise CommandError(
                    f'Erreur lors de la récupération du statut : {exc}'
                ) from exc

            response = build_response(**data)
            self.stdout.write(
                json.dumps(response, indent=2, ensure_ascii=False)
            )
