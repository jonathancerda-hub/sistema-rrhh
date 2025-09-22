from django.core.management.base import BaseCommand
from empleados.models import Empleado

class Command(BaseCommand):
    help = 'Backfill director/gerente/jefe fields for all Empleado records'

    def handle(self, *args, **options):
        qs = Empleado.objects.all()
        total = qs.count()
        self.stdout.write(f'Procesando {total} empleados...')
        for i, emp in enumerate(qs, start=1):
            emp._recompute_and_propagate()
            if i % 50 == 0:
                self.stdout.write(f'  Procesados {i}/{total}')
        self.stdout.write('Backfill completo.')
