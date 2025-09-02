from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from empleados.models import Empleado
import secrets
import string
import os

class Command(BaseCommand):
    help = 'Configura el sistema para producción con PostgreSQL'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='admin',
            help='Username del superusuario (default: admin)'
        )
        parser.add_argument(
            '--email',
            type=str,
            required=True,
            help='Email del superusuario (requerido)'
        )
        parser.add_argument(
            '--password',
            type=str,
            help='Contraseña del superusuario (se genera automáticamente si no se especifica)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Crear superusuario aunque ya exista uno'
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 CONFIGURANDO SISTEMA PARA PRODUCCIÓN')
        )
        
        # Verificar que estamos usando PostgreSQL
        from django.conf import settings
        db_engine = settings.DATABASES['default']['ENGINE']
        
        if 'postgresql' not in db_engine:
            self.stdout.write(
                self.style.ERROR('❌ No estás usando PostgreSQL. Verifica tu configuración DATABASE_URL.')
            )
            return
        
        self.stdout.write(
            self.style.SUCCESS('✅ PostgreSQL configurado correctamente')
        )
        
        # Verificar si ya existe un superusuario
        if User.objects.filter(is_superuser=True).exists() and not options['force']:
            self.stdout.write(
                self.style.WARNING('⚠️  Ya existe al menos un superusuario')
            )
            self.stdout.write('Usa --force para crear otro superusuario')
            return
        
        username = options['username']
        email = options['email']
        password = options['password']
        
        # Generar contraseña si no se proporcionó
        if not password:
            password = self.generar_password_seguro()
            self.stdout.write(f'🔑 Contraseña generada: {password}')
        
        try:
            # Crear superusuario
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            
            # Crear empleado asociado si no existe
            empleado, created = Empleado.objects.get_or_create(
                user=user,
                defaults={
                    'nombre': username.title(),
                    'apellido': 'Administrador',
                    'dni': '00000000',  # DNI temporal
                    'email': email,
                    'puesto': 'Administrador del Sistema',
                    'area': 'Administración',
                    'es_rrhh': True,
                    'fecha_contratacion': '2024-01-01'
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS('✅ Empleado creado correctamente')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('⚠️  Empleado ya existía')
                )
            
            self.stdout.write(
                self.style.SUCCESS('✅ Superusuario creado correctamente')
            )
            self.stdout.write(f'👤 Usuario: {username}')
            self.stdout.write(f'📧 Email: {email}')
            self.stdout.write(f'🔑 Contraseña: {password}')
            self.stdout.write(f'🆔 ID Empleado: {empleado.id}')
            
            self.stdout.write(
                self.style.SUCCESS('\n🎉 CONFIGURACIÓN COMPLETADA')
            )
            self.stdout.write('Ahora puedes acceder al sistema con estos datos.')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error creando superusuario: {e}')
            )

    def generar_password_seguro(self):
        """Genera una contraseña segura"""
        caracteres = string.ascii_letters + string.digits + "!@#$%"
        password = ''.join(secrets.choice(caracteres) for _ in range(12))
        return password
