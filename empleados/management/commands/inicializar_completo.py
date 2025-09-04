from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth.models import User
from empleados.models import Empleado
from datetime import date
import sys

class Command(BaseCommand):
    help = 'Inicializar completamente la aplicación en producción (optimizado para memoria)'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Iniciando configuración optimizada de producción...')
        )
        
        try:
            # 1. Verificar si ya está inicializado
            if User.objects.exists() and Empleado.objects.exists():
                self.stdout.write(
                    self.style.WARNING('⚠️ Sistema ya inicializado')
                )
                self.mostrar_usuarios_existentes()
                return
            
            # 2. Ejecutar migraciones solo si es necesario
            self.stdout.write('📊 Verificando migraciones...')
            call_command('migrate', '--run-syncdb', verbosity=0)
            self.stdout.write(self.style.SUCCESS('✅ Migraciones verificadas'))
            
            # 3. Crear solo superusuario si no existe
            if not User.objects.filter(is_superuser=True).exists():
                self.stdout.write('👑 Creando superusuario...')
                User.objects.create_superuser(
                    username='admin',
                    email='admin@empresa.com',
                    password='admin123456'
                )
                self.stdout.write(self.style.SUCCESS('✅ Superusuario creado: admin / admin123456'))
            
            # 4. Crear usuarios básicos solo si no existen empleados
            if not Empleado.objects.exists():
                self.crear_usuarios_basicos()
            
            self.stdout.write(
                self.style.SUCCESS('\n🎉 ¡Configuración completada!')
            )
            self.mostrar_resumen()

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error en la configuración: {e}')
            )
            # No hacer sys.exit(1) para evitar problemas en producción

    def crear_usuarios_basicos(self):
        """Crear usuarios básicos del sistema"""
        self.stdout.write('👥 Creando usuarios básicos...')
        
        # Usuario RRHH
        user_rrhh = User.objects.create_user('rrhh', 'rrhh@empresa.com', 'rrhh123456')
        empleado_rrhh = Empleado.objects.create(
            user=user_rrhh,
            nombre='RRHH',
            apellido='Sistema',
            dni='12345678',
            email='rrhh@empresa.com',
            puesto='Recursos Humanos',
            fecha_contratacion=date.today(),
            area='RRHH',
            gerencia='gerencia_desarrollo_organizacional',
            jerarquia='director',
            es_rrhh=True,
            dias_vacaciones_disponibles=30
        )

        # Usuario Manager
        user_manager = User.objects.create_user('manager', 'manager@empresa.com', 'manager123456')
        empleado_manager = Empleado.objects.create(
            user=user_manager,
            nombre='Manager',
            apellido='Prueba',
            dni='87654321',
            email='manager@empresa.com',
            puesto='Gerente',
            fecha_contratacion=date.today(),
            area='Ventas',
            gerencia='gerencia_comercial_local',
            jerarquia='gerente',
            dias_vacaciones_disponibles=30
        )

        # Usuario Empleado
        user_empleado = User.objects.create_user('empleado', 'empleado@empresa.com', 'empleado123456')
        empleado_regular = Empleado.objects.create(
            user=user_empleado,
            nombre='Juan',
            apellido='Pérez',
            dni='11223344',
            email='empleado@empresa.com',
            puesto='Analista',
            fecha_contratacion=date.today(),
            area='Ventas',
            gerencia='gerencia_comercial_local',
            jerarquia='asistente',
            manager=empleado_manager,
            dias_vacaciones_disponibles=30
        )

        self.stdout.write(self.style.SUCCESS('✅ Usuarios básicos creados'))

    def mostrar_usuarios_existentes(self):
        """Mostrar usuarios existentes en el sistema"""
        users = User.objects.all()
        empleados = Empleado.objects.all()
        
        self.stdout.write('\n📋 Usuarios existentes:')
        for user in users:
            tipo = "Admin" if user.is_superuser else "Usuario"
            self.stdout.write(f'   • {user.username} ({tipo})')
        
        self.stdout.write(f'\n👥 Total empleados: {empleados.count()}')

    def mostrar_resumen(self):
        """Mostrar resumen de la configuración"""
        self.stdout.write('\n📝 RESUMEN DE CONFIGURACIÓN:')
        self.stdout.write('━' * 50)
        self.stdout.write('🔑 CREDENCIALES DE ACCESO:')
        self.stdout.write('   Admin: admin / admin123456')
        self.stdout.write('   RRHH: rrhh / rrhh123456')
        self.stdout.write('   Manager: manager / manager123456')
        self.stdout.write('   Empleado: empleado / empleado123456')
        self.stdout.write('\n🌐 URLS IMPORTANTES:')
        self.stdout.write('   • /admin/ - Panel de administración Django')
        self.stdout.write('   • /empleados/ - Sistema RRHH')
        self.stdout.write('   • /empleados/setup/diagnostico/ - Diagnóstico del sistema')
        self.stdout.write('━' * 50)
