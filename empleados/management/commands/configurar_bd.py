"""
Comando para cambiar configuración a usar Supabase por defecto
"""
from django.core.management.base import BaseCommand
import os

class Command(BaseCommand):
    help = 'Configurar sistema para usar Supabase por defecto'

    def add_arguments(self, parser):
        parser.add_argument(
            '--local',
            action='store_true',
            help='Volver a configuración local (SQLite)',
        )

    def handle(self, *args, **options):
        if options['local']:
            self.configurar_local()
        else:
            self.configurar_supabase()

    def configurar_supabase(self):
        """Configurar para usar Supabase por defecto"""
        self.stdout.write('🌐 Configurando para usar Supabase...')
        
        # Crear/actualizar settings_local.py para usar Supabase
        settings_content = '''# Configuración local para desarrollo con Supabase
from .settings import *
import os

# Configuración directa a Supabase
DATABASES = {
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

print("🌐 Conectado a Supabase PostgreSQL")

# Debug activado para desarrollo local
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Archivos estáticos para desarrollo
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Email backend para desarrollo
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'Sistema RRHH <noreply@empresa.com>'
'''
        
        with open('nucleo_rrhh/settings_local.py', 'w', encoding='utf-8') as f:
            f.write(settings_content)
        
        self.stdout.write('✅ settings_local.py actualizado para Supabase')
        
        # Crear manage_supabase.py para usar siempre Supabase
        manage_content = '''#!/usr/bin/env python
"""Django's command-line utility for administrative tasks with Supabase."""
import os
import sys

if __name__ == '__main__':
    """Run administrative tasks with Supabase configuration."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nucleo_rrhh.settings_local')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
'''
        
        with open('manage_supabase.py', 'w', encoding='utf-8') as f:
            f.write(manage_content)
        
        self.stdout.write('✅ manage_supabase.py creado')
        
        self.stdout.write(self.style.SUCCESS('\n🎉 ¡Configuración completada!'))
        self.stdout.write('🚀 Comandos para usar Supabase:')
        self.stdout.write('   python manage_supabase.py runserver')
        self.stdout.write('   python manage_supabase.py migrate')
        self.stdout.write('   python manage_supabase.py createsuperuser')

    def configurar_local(self):
        """Volver a configuración local SQLite"""
        self.stdout.write('🏠 Configurando para uso local...')
        
        settings_content = '''# Configuración local para desarrollo
from .settings import *

# Base de datos SQLite local
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

print("🗄️ Usando SQLite local")

# Debug activado para desarrollo local
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Archivos estáticos para desarrollo
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
'''
        
        with open('nucleo_rrhh/settings_local.py', 'w', encoding='utf-8') as f:
            f.write(settings_content)
        
        self.stdout.write(self.style.SUCCESS('✅ Configuración local restaurada'))
