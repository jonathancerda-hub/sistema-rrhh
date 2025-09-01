# empleados/management/commands/crear_usuario_rrhh.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from empleados.models import Empleado
from datetime import date

class Command(BaseCommand):
    help = 'Crea un usuario de RRHH independiente con acceso total al sistema'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='rrhh.admin',
            help='Nombre de usuario para el RRHH (default: rrhh.admin)'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='rrhh123',
            help='Contraseña para el usuario RRHH (default: rrhh123)'
        )
        parser.add_argument(
            '--email',
            type=str,
            default='rrhh.admin@empresa.com',
            help='Email para el usuario RRHH'
        )

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        email = options['email']
        
        self.stdout.write(
            self.style.SUCCESS('🔴 CREANDO USUARIO DE RRHH INDEPENDIENTE')
        )
        self.stdout.write('=' * 60)
        
        # Verificar si ya existe un usuario RRHH
        if Empleado.objects.filter(es_rrhh=True).exists():
            self.stdout.write(
                self.style.WARNING('⚠️  Ya existe un usuario de RRHH en el sistema')
            )
            rrhh_existente = Empleado.objects.get(es_rrhh=True)
            self.stdout.write(f'   • Usuario existente: {rrhh_existente.nombre} {rrhh_existente.apellido}')
            self.stdout.write(f'   • Email: {rrhh_existente.email}')
            self.stdout.write(f'   • Puesto: {rrhh_existente.puesto}')
            return
        
        # Crear usuario Django
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.ERROR(f'❌ El usuario Django "{username}" ya existe')
            )
            return
        
        if User.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.ERROR(f'❌ El email "{email}" ya está en uso')
            )
            return
        
        # Crear usuario Django
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name='Sofía Alejandra',
            last_name='Hernández Morales'
        )
        
        # Crear perfil de empleado RRHH
        empleado_rrhh = Empleado.objects.create(
            nombre='Sofía Alejandra',
            apellido='Hernández Morales',
            email=email,
            puesto='Directora de RRHH',
            fecha_contratacion=date(2020, 5, 15),
            dias_vacaciones_disponibles=25,
            es_rrhh=True  # Marcar como RRHH
        )
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ Usuario RRHH creado exitosamente!')
        )
        self.stdout.write('=' * 60)
        self.stdout.write(f'👤 Nombre: {empleado_rrhh.nombre} {empleado_rrhh.apellido}')
        self.stdout.write(f'🔑 Usuario: {username}')
        self.stdout.write(f'🔒 Contraseña: {password}')
        self.stdout.write(f'📧 Email: {email}')
        self.stdout.write(f'💼 Puesto: {empleado_rrhh.puesto}')
        self.stdout.write(f'📅 Fecha contratación: {empleado_rrhh.fecha_contratacion}')
        self.stdout.write(f'🔴 Tipo: Usuario RRHH Independiente')
        
        self.stdout.write('\n🎯 FUNCIONALIDADES DISPONIBLES:')
        self.stdout.write('   • 📊 Dashboard RRHH: http://127.0.0.1:8000/rrhh/')
        self.stdout.write('   • 👀 Ver TODAS las solicitudes de vacaciones')
        self.stdout.write('   • ✅ Aprobar/Rechazar según políticas')
        self.stdout.write('   • 📈 Estadísticas completas del sistema')
        self.stdout.write('   • 🎯 Acceso independiente (sin restricciones)')
        
        self.stdout.write('\n🚀 Para acceder:')
        self.stdout.write('   1. Inicia el servidor: python manage.py runserver')
        self.stdout.write('   2. Ve a: http://127.0.0.1:8000/login/')
        self.stdout.write('   3. Inicia sesión con las credenciales de arriba')
        self.stdout.write('   4. Navega a: http://127.0.0.1:8000/rrhh/')
        
        self.stdout.write(
            self.style.SUCCESS('\n✅ ¡Usuario RRHH listo para usar!')
        )
