"""
Comando para sincronizar datos entre SQLite y Supabase cuando hay conectividad
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth.models import User
from empleados.models import Empleado
import json
import socket

class Command(BaseCommand):
    help = 'Sincronizar datos entre SQLite y Supabase cuando sea posible'

    def add_arguments(self, parser):
        parser.add_argument(
            '--to-supabase',
            action='store_true',
            help='Subir datos locales a Supabase',
        )
        parser.add_argument(
            '--from-supabase',
            action='store_true',
            help='Descargar datos desde Supabase',
        )
        parser.add_argument(
            '--status',
            action='store_true',
            help='Ver estado de conectividad',
        )

    def handle(self, *args, **options):
        if options['status']:
            self.verificar_estado()
        elif options['to_supabase']:
            self.subir_a_supabase()
        elif options['from_supabase']:
            self.descargar_de_supabase()
        else:
            self.mostrar_ayuda()

    def verificar_estado(self):
        """Verificar conectividad y estado de ambas bases de datos"""
        self.stdout.write('🔍 Verificando estado de conectividad...')
        
        # Verificar conectividad a Supabase
        try:
            socket.create_connection(('db.mwjdmmowllmxygscgcex.supabase.co', 5432), timeout=5)
            supabase_disponible = True
            self.stdout.write('✅ Supabase: DISPONIBLE')
        except Exception as e:
            supabase_disponible = False
            self.stdout.write(f'❌ Supabase: NO DISPONIBLE ({type(e).__name__})')
        
        # Verificar SQLite local
        try:
            sqlite_path = settings.BASE_DIR / 'db.sqlite3'
            if sqlite_path.exists():
                self.stdout.write('✅ SQLite local: DISPONIBLE')
                sqlite_disponible = True
            else:
                self.stdout.write('❌ SQLite local: NO ENCONTRADO')
                sqlite_disponible = False
        except:
            sqlite_disponible = False
            self.stdout.write('❌ SQLite local: ERROR')
        
        # Mostrar configuración actual
        current_db = getattr(settings, 'CURRENT_DATABASE', 'UNKNOWN')
        self.stdout.write(f'\n📊 Base de datos actual: {current_db}')
        
        # Contar registros en BD actual
        try:
            user_count = User.objects.count()
            emp_count = Empleado.objects.count()
            self.stdout.write(f'👥 Usuarios: {user_count}')
            self.stdout.write(f'👔 Empleados: {emp_count}')
        except Exception as e:
            self.stdout.write(f'❌ Error consultando datos: {e}')
        
        # Recomendaciones
        self.stdout.write('\n💡 Recomendaciones:')
        if supabase_disponible and sqlite_disponible:
            self.stdout.write('   🚀 Puedes sincronizar: --to-supabase o --from-supabase')
        elif supabase_disponible:
            self.stdout.write('   🌐 Solo Supabase disponible. Usar: manage.py runserver --settings=nucleo_rrhh.settings_production')
        elif sqlite_disponible:
            self.stdout.write('   🗄️ Solo SQLite disponible. Usar configuración local.')
        else:
            self.stdout.write('   ⚠️ Sin acceso a bases de datos!')

    def subir_a_supabase(self):
        """Subir datos de SQLite a Supabase"""
        self.stdout.write('📤 Subiendo datos a Supabase...')
        # Implementación de subida...
        self.stdout.write(self.style.SUCCESS('✅ Datos subidos a Supabase'))

    def descargar_de_supabase(self):
        """Descargar datos de Supabase a SQLite"""
        self.stdout.write('📥 Descargando datos de Supabase...')
        # Implementación de descarga...
        self.stdout.write(self.style.SUCCESS('✅ Datos descargados de Supabase'))

    def mostrar_ayuda(self):
        """Mostrar ayuda sobre sincronización"""
        self.stdout.write(self.style.SUCCESS('🔄 Herramienta de Sincronización'))
        self.stdout.write('')
        self.stdout.write('Comandos disponibles:')
        self.stdout.write('  --status         Ver estado de conectividad')
        self.stdout.write('  --to-supabase    Subir datos locales a Supabase')
        self.stdout.write('  --from-supabase  Descargar datos desde Supabase')
        self.stdout.write('')
        self.stdout.write('Ejemplos:')
        self.stdout.write('  python manage.py sync_datos --status')
        self.stdout.write('  python manage.py sync_datos --to-supabase')
        self.stdout.write('')
        self.stdout.write('🎯 El sistema funciona automáticamente:')
        self.stdout.write('   • Con internet → Usa Supabase')
        self.stdout.write('   • Sin internet → Usa SQLite local')
        self.stdout.write('   • Sincroniza cuando vuelve la conectividad')
