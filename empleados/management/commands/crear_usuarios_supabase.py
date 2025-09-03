"""
Comando para crear usuarios de prueba directamente en Supabase
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth.models import User
from empleados.models import Empleado
import sys

class Command(BaseCommand):
    help = 'Crear usuarios de prueba en Supabase'

    def handle(self, *args, **options):
        # Configuración temporal para Supabase
        original_databases = settings.DATABASES
        settings.DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': 'postgres',
                'USER': 'postgres',
                'PASSWORD': '3jbxqfv$2gyW$yG',
                'HOST': 'db.mwjdmmowllmxygscgcex.supabase.co',
                'PORT': '5432',
                'CONN_MAX_AGE': 600,
            }
        }
        
        try:
            self.stdout.write('👥 Creando usuarios de prueba en Supabase...')
            
            # Usuario Admin
            user_admin, created = User.objects.get_or_create(
                username='admin_rrhh',
                defaults={
                    'first_name': 'Admin',
                    'last_name': 'RRHH',
                    'email': 'admin@empresa.com',
                    'is_staff': True,
                    'is_superuser': True
                }
            )
            if created:
                user_admin.set_password('admin123')
                user_admin.save()
                self.stdout.write('✅ Usuario admin_rrhh creado')
            else:
                self.stdout.write('ℹ️ Usuario admin_rrhh ya existe')

            # Empleado RRHH
            empleado_rrhh, created = Empleado.objects.get_or_create(
                user=user_admin,
                defaults={
                    'nombre': 'Admin',
                    'apellido': 'RRHH',
                    'dni': '12345678',
                    'email': 'admin@empresa.com',
                    'puesto': 'Administrador RRHH',
                    'fecha_contratacion': '2020-01-01',
                    'dias_vacaciones_disponibles': 30,
                    'es_rrhh': True,
                    'area': 'Recursos Humanos',
                    'gerencia': 'gerencia_desarrollo_organizacional',
                    'jerarquia': 'gerente'
                }
            )
            if created:
                self.stdout.write('✅ Empleado RRHH creado')
            else:
                self.stdout.write('ℹ️ Empleado RRHH ya existe')

            # Manager de Ventas
            user_manager, created = User.objects.get_or_create(
                username='manager_ventas',
                defaults={
                    'first_name': 'Carlos',
                    'last_name': 'Rodríguez',
                    'email': 'carlos@empresa.com'
                }
            )
            if created:
                user_manager.set_password('manager123')
                user_manager.save()
                self.stdout.write('✅ Usuario manager_ventas creado')
            else:
                self.stdout.write('ℹ️ Usuario manager_ventas ya existe')

            empleado_manager, created = Empleado.objects.get_or_create(
                user=user_manager,
                defaults={
                    'nombre': 'Carlos',
                    'apellido': 'Rodríguez',
                    'dni': '87654321',
                    'email': 'carlos@empresa.com',
                    'puesto': 'Manager de Ventas',
                    'fecha_contratacion': '2021-03-15',
                    'dias_vacaciones_disponibles': 25,
                    'es_rrhh': False,
                    'area': 'Ventas',
                    'gerencia': 'gerencia_comercial_local',
                    'jerarquia': 'jefe'
                }
            )
            if created:
                self.stdout.write('✅ Empleado Manager creado')
            else:
                self.stdout.write('ℹ️ Empleado Manager ya existe')

            # Empleado Regular
            user_empleado, created = User.objects.get_or_create(
                username='ana_garcia',
                defaults={
                    'first_name': 'Ana',
                    'last_name': 'García',
                    'email': 'ana@empresa.com'
                }
            )
            if created:
                user_empleado.set_password('empleado123')
                user_empleado.save()
                self.stdout.write('✅ Usuario ana_garcia creado')
            else:
                self.stdout.write('ℹ️ Usuario ana_garcia ya existe')

            empleado_regular, created = Empleado.objects.get_or_create(
                user=user_empleado,
                defaults={
                    'nombre': 'Ana',
                    'apellido': 'García',
                    'dni': '11223344',
                    'email': 'ana@empresa.com',
                    'puesto': 'Ejecutiva de Ventas',
                    'fecha_contratacion': '2022-06-01',
                    'dias_vacaciones_disponibles': 20,
                    'manager': empleado_manager,  # Ana reporta a Carlos
                    'es_rrhh': False,
                    'area': 'Ventas',
                    'gerencia': 'gerencia_comercial_local',
                    'jerarquia': 'asistente'
                }
            )
            if created:
                self.stdout.write('✅ Empleado Regular creado')
            else:
                self.stdout.write('ℹ️ Empleado Regular ya existe')

            self.stdout.write(
                self.style.SUCCESS('\n🎉 ¡Usuarios de prueba creados en Supabase!')
            )
            self.stdout.write('📝 Credenciales de acceso:')
            self.stdout.write('  👑 admin_rrhh / admin123 (RRHH)')
            self.stdout.write('  👨‍💼 manager_ventas / manager123 (Manager)')
            self.stdout.write('  👩‍💻 ana_garcia / empleado123 (Empleado)')

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error: {e}')
            )
        finally:
            # Restaurar configuración original
            settings.DATABASES = original_databases
