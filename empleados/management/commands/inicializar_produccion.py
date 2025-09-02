from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from empleados.models import Empleado

class Command(BaseCommand):
    help = 'Inicializar base de datos con usuarios básicos para producción'

    def handle(self, *args, **options):
        # Verificar si ya existen usuarios
        if User.objects.exists():
            self.stdout.write(
                self.style.WARNING('Ya existen usuarios en la base de datos. Saltando inicialización.')
            )
            return

        try:
            # Crear usuario RRHH
            user_rrhh = User.objects.create_user('rrhh', 'rrhh@empresa.com', 'rrhh123456')
            empleado_rrhh = Empleado.objects.create(
                user=user_rrhh,
                nombre='RRHH',
                apellido='Sistema',
                dni='12345678',
                email='rrhh@empresa.com',
                puesto='Recursos Humanos',
                area='RRHH',
                gerencia='RRHH',
                jerarquia=1,
                es_rrhh=True,
                dias_vacaciones_disponibles=30
            )

            # Crear usuario manager
            user_manager = User.objects.create_user('manager', 'manager@empresa.com', 'manager123456')
            empleado_manager = Empleado.objects.create(
                user=user_manager,
                nombre='Manager',
                apellido='Prueba',
                dni='87654321',
                email='manager@empresa.com',
                puesto='Gerente',
                area='Ventas',
                gerencia='Comercial',
                jerarquia=2,
                dias_vacaciones_disponibles=30
            )

            # Crear usuario empleado
            user_empleado = User.objects.create_user('empleado', 'empleado@empresa.com', 'empleado123456')
            empleado_regular = Empleado.objects.create(
                user=user_empleado,
                nombre='Juan',
                apellido='Pérez',
                dni='11223344',
                email='empleado@empresa.com',
                puesto='Analista',
                area='Ventas',
                gerencia='Comercial',
                jerarquia=7,
                manager=empleado_manager,
                dias_vacaciones_disponibles=30
            )

            self.stdout.write(
                self.style.SUCCESS('✅ Usuarios iniciales creados exitosamente!')
            )
            self.stdout.write('🔑 Credenciales:')
            self.stdout.write('   RRHH: rrhh / rrhh123456')
            self.stdout.write('   Manager: manager / manager123456')
            self.stdout.write('   Empleado: empleado / empleado123456')

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error creando usuarios: {e}')
            )
