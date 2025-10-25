from django.core.management.base import BaseCommand
from decimal import InvalidOperation
from django.db import connection
from django.utils import timezone

class Command(BaseCommand):
    help = 'Diagnose which row in attendance_attendance causes Decimal.InvalidOperation when hydrating via ORM'

    def add_arguments(self, parser):
        parser.add_argument('--table', type=str, default='attendance_attendance', help='Table to diagnose')
        parser.add_argument('--pk-field', type=str, default='id', help='Primary key field name')

    def handle(self, *args, **options):
        table = options['table']
        pk_field = options['pk_field']

        self.stdout.write(f'Diagnosing table {table} pk field {pk_field}')

        # Fetch min and max PK
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT MIN({pk_field}), MAX({pk_field}), COUNT(*) FROM {table}")
            row = cursor.fetchone()
            if not row:
                self.stdout.write('Table empty or not found')
                return
            min_pk, max_pk, total = row

        self.stdout.write(f'Rows: {total}, PK range: {min_pk}..{max_pk}')

        # Binary search over PK range to find smallest PK that causes hydration error using ORM
        low = min_pk
        high = max_pk
        found_pk = None

        try:
            # Quick attempt: try to fetch all via ORM (may raise)
            from attendance.models import Attendance
            self.stdout.write('Attempting to iterate Attendance.objects.all() to trigger converter')
            try:
                for obj in Attendance.objects.all().select_related('employee__user', 'employee__department'):
                    pass
                self.stdout.write('No converter error when iterating all rows via ORM')
                return
            except Exception as exc:
                self.stdout.write(f'Iteration raised: {exc.__class__}: {exc}')

            # Narrow down by PK ranges
            while low <= high:
                mid = (low + high) // 2
                self.stdout.write(f'Testing PK range {low}..{mid}')
                try:
                    # Try to iterate rows up to mid
                    cnt = 0
                    for obj in Attendance.objects.filter(**{f"{pk_field}__gte": low, f"{pk_field}__lte": mid}).select_related('employee__user', 'employee__department'):
                        cnt += 1
                    self.stdout.write(f'OK up to {mid} (rows={cnt})')
                    low = mid + 1
                except Exception as exc:
                    # Error inside this range; shrink high to mid
                    self.stdout.write(f'Error in range {low}..{mid}: {exc.__class__}: {exc}')
                    found_pk = (low, mid)
                    high = mid - 1

            if not found_pk:
                self.stdout.write('Could not isolate a failing PK range')
            else:
                # fetch raw rows in the found range to inspect values
                lo, hi = found_pk
                self.stdout.write(f'Inspecting raw rows in range {lo}..{hi}')
                with connection.cursor() as cursor:
                    cursor.execute(f"SELECT * FROM {table} WHERE {pk_field} BETWEEN %s AND %s", [lo, hi])
                    cols = [c[0] for c in cursor.description]
                    for r in cursor.fetchall():
                        self.stdout.write('ROW:')
                        for c, v in zip(cols, r):
                            self.stdout.write(f'  {c}: {v!r}')
        except Exception as exc:
            self.stdout.write(f'Diagnostic failed: {exc.__class__}: {exc}')
