from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Crea un superusuario "admin" con contraseña "admin123" si no existe.'

    def handle(self, *args, **options):
        username = 'admin'
        email = 'admin@empresa.com'
        password = 'admin123'

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            self.stdout.write(self.style.SUCCESS(f"✅ Superusuario '{username}' creado exitosamente."))
        else:
            self.stdout.write(self.style.WARNING(f"ℹ️ El superusuario '{username}' ya existe."))