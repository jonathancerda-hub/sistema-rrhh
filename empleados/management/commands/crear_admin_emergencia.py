from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from empleados.models import Empleado

class Command(BaseCommand):
    help = 'Crea usuario administrador de emergencia'

    def handle(self, *args, **options):
        # Crear superusuario
        username = 'admin'
        email = 'admin@empresa.com'
        password = 'Admin123!'
        
        # Verificar si ya existe
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'Usuario {username} ya existe')
            )
            user = User.objects.get(username=username)
        else:
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            self.stdout.write(
                self.style.SUCCESS(f'Usuario {username} creado')
            )
        
        # Crear empleado asociado
        empleado, created = Empleado.objects.get_or_create(
            user=user,
            defaults={
                'nombre': 'Administrador',
                'apellido': 'Sistema',
                'dni': '00000000',
                'email': email,
                'puesto': 'Administrador del Sistema',
                'area': 'Administración',
                'es_rrhh': True,
                'fecha_contratacion': '2024-01-01'
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS('Empleado creado')
            )
        
        self.stdout.write(
            self.style.SUCCESS('=== CREDENCIALES ===')
        )
        self.stdout.write(f'Usuario: {username}')
        self.stdout.write(f'Email: {email}')
        self.stdout.write(f'Contraseña: {password}')
        self.stdout.write(
            self.style.SUCCESS('==================')
        )
