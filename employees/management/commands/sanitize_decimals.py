from django.core.management.base import BaseCommand
from decimal import Decimal, InvalidOperation
from django.db import transaction
from django.utils import timezone
import logging

from django.apps import apps

logger = logging.getLogger(__name__)

# We'll dynamically find all DecimalField columns across installed models to scan.
def discover_decimal_fields():
    targets = []
    for model in apps.get_models():
        for field in getattr(model, '_meta').local_fields:
            try:
                if field.get_internal_type() == 'DecimalField':
                    # use the DB column name (attname) for raw SQL
                    targets.append((model, field.attname, f"{model._meta.label}.{field.name}"))
            except Exception:
                continue
    return targets

class Command(BaseCommand):
    help = 'Sanitize Decimal fields across key models. Use --dry-run to only report. Use --apply to write changes.'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Only report problematic rows without changing them')
        parser.add_argument('--apply', action='store_true', help='Apply fixes to the database')
        parser.add_argument('--limit', type=int, default=0, help='Limit number of rows processed per model (0 = all)')

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        apply = options['apply']
        limit = options['limit']

        if not dry_run and not apply:
            self.stdout.write(self.style.WARNING('No action specified. Use --dry-run to inspect or --apply to make changes.'))
            return

        self.stdout.write(self.style.NOTICE(f"Started sanitize_decimals (dry_run={dry_run}, apply={apply}) at {timezone.now()}"))

        from django.db import connection
        for model, field, label in discover_decimal_fields():
            table = model._meta.db_table
            problems = []

            # Use raw SQL to avoid Django's type converters which may raise on malformed values
            with connection.cursor() as cursor:
                sql = f"SELECT id, {field} FROM {table}"
                if limit > 0:
                    sql = sql + f" LIMIT {limit}"
                cursor.execute(sql)
                rows = cursor.fetchall()

            for row in rows:
                pk = row[0]
                val = row[1]
                if val is None:
                    continue
                try:
                    _ = Decimal(str(val))
                except (InvalidOperation, ValueError, TypeError):
                    problems.append((pk, val))

            if not problems:
                self.stdout.write(self.style.SUCCESS(f'OK: {label} — no malformed values found'))
                continue

            self.stdout.write(self.style.WARNING(f'Found {len(problems)} problematic rows for {label}'))
            for pk, bad_val in problems:
                self.stdout.write(f' - PK={pk} value={bad_val!r}')

            if apply:
                self.stdout.write(self.style.NOTICE(f'Applying fixes for {len(problems)} rows in {label}'))
                with connection.cursor() as cursor:
                    for pk, bad_val in problems:
                        try:
                            default_str = '0.00'
                            cursor.execute(f"UPDATE {table} SET {field} = ? WHERE id = ?", [default_str, pk])
                            self.stdout.write(self.style.SUCCESS(f'Fixed {label} pk={pk} -> {default_str}'))
                        except Exception as exc:
                            self.stdout.write(self.style.ERROR(f'Failed to fix pk={pk}: {exc}'))

        self.stdout.write(self.style.NOTICE('sanitize_decimals finished.'))
