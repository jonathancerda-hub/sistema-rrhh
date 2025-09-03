"""
Comando para inicializar Supabase después del deploy
"""
from django.core.management.base import BaseCommand
from django.db import connection
from django.core.management import call_command
import time

class Command(BaseCommand):
    help = 'Inicializar Supabase después del deploy'

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-migrations',
            action='store_true',
            help='Saltar migraciones (solo verificar conexión)',
        )
        parser.add_argument(
            '--create-users',
            action='store_true',
            help='Crear usuarios de prueba',
        )

    def handle(self, *args, **options):
        self.stdout.write("🚀 Inicializando Supabase...")
        
        # Verificar conexión
        if not self.verificar_conexion():
            return
        
        # Aplicar migraciones si es necesario
        if not options['skip_migrations']:
            self.aplicar_migraciones()
        
        # Crear usuarios si se solicita
        if options['create_users']:
            self.crear_usuarios()
        
        self.stdout.write(
            self.style.SUCCESS('🎉 Supabase inicializado correctamente!')
        )

    def verificar_conexion(self):
        """Verificar conexión a Supabase"""
        self.stdout.write("🔍 Verificando conexión a Supabase...")
        
        max_intentos = 5
        for intento in range(1, max_intentos + 1):
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT version();")
                    version = cursor.fetchone()
                    self.stdout.write(
                        self.style.SUCCESS(f"✅ Conectado a PostgreSQL: {version[0]}")
                    )
                    return True
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f"⚠️ Intento {intento}/{max_intentos} falló: {e}")
                )
                if intento < max_intentos:
                    self.stdout.write("🔄 Reintentando en 3 segundos...")
                    time.sleep(3)
        
        self.stdout.write(
            self.style.ERROR("❌ No se pudo conectar a Supabase después de varios intentos")
        )
        return False

    def aplicar_migraciones(self):
        """Aplicar migraciones en Supabase"""
        self.stdout.write("🛠️ Aplicando migraciones...")
        try:
            call_command('migrate', verbosity=1)
            self.stdout.write(self.style.SUCCESS("✅ Migraciones aplicadas correctamente"))
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error aplicando migraciones: {e}")
            )

    def crear_usuarios(self):
        """Crear usuarios de prueba"""
        self.stdout.write("👥 Creando usuarios de prueba...")
        try:
            call_command('crear_usuarios_prueba')
            self.stdout.write(self.style.SUCCESS("✅ Usuarios creados correctamente"))
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f"⚠️ Error creando usuarios: {e}")
            )
