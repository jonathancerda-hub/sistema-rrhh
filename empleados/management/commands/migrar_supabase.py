import os
import subprocess
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
from django.db import connection

class Command(BaseCommand):
    help = 'Migrar a Supabase: crear tablas y migrar datos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--supabase-url',
            type=str,
            help='URL de conexión de Supabase',
            required=True
        )
        parser.add_argument(
            '--exportar-datos',
            action='store_true',
            help='Solo exportar datos de la base actual sin migrar'
        )

    def handle(self, *args, **options):
        supabase_url = options['supabase_url']
        solo_exportar = options['exportar_datos']

        self.stdout.write('🚀 Iniciando migración a Supabase...')
        
        if solo_exportar:
            self.exportar_datos_actuales()
            return

        # Paso 1: Exportar datos actuales
        self.stdout.write('\n📤 Paso 1: Exportando datos actuales...')
        self.exportar_datos_actuales()

        # Paso 2: Configurar nueva base de datos
        self.stdout.write('\n🔧 Paso 2: Configurando conexión a Supabase...')
        self.configurar_supabase(supabase_url)

        # Paso 3: Crear tablas en Supabase
        self.stdout.write('\n🏗️ Paso 3: Creando tablas en Supabase...')
        self.crear_tablas_supabase()

        # Paso 4: Importar datos
        self.stdout.write('\n📥 Paso 4: Importando datos...')
        self.importar_datos()

        self.stdout.write(
            self.style.SUCCESS('\n✅ ¡Migración completada exitosamente!')
        )

    def exportar_datos_actuales(self):
        """Exporta los datos actuales a archivos JSON"""
        try:
            # Crear directorio para los datos
            backup_dir = 'backup_datos'
            os.makedirs(backup_dir, exist_ok=True)

            # Exportar datos de cada modelo
            modelos = [
                'auth.User',
                'empleados.Empleado',
                'empleados.SolicitudVacaciones',
                'empleados.SolicitudNuevoColaborador',
            ]

            for modelo in modelos:
                archivo = f"{backup_dir}/{modelo.replace('.', '_')}.json"
                try:
                    call_command('dumpdata', modelo, 
                               output=archivo, 
                               format='json', 
                               indent=2)
                    self.stdout.write(f'  ✅ Exportado: {modelo} -> {archivo}')
                except Exception as e:
                    self.stdout.write(f'  ⚠️ Error exportando {modelo}: {str(e)}')

        except Exception as e:
            self.stdout.write(f'❌ Error en exportación: {str(e)}')

    def configurar_supabase(self, supabase_url):
        """Configura la conexión a Supabase temporalmente"""
        # Guardar configuración actual
        self.db_backup = settings.DATABASES['default'].copy()
        
        # Configurar Supabase
        import dj_database_url
        nueva_config = dj_database_url.parse(supabase_url)
        settings.DATABASES['default'] = nueva_config
        
        # Reiniciar conexión
        connection.close()
        
        self.stdout.write('  ✅ Conexión a Supabase configurada')

    def crear_tablas_supabase(self):
        """Crea todas las tablas en Supabase"""
        try:
            # Ejecutar migraciones
            call_command('migrate', verbosity=1)
            self.stdout.write('  ✅ Tablas creadas en Supabase')
        except Exception as e:
            self.stdout.write(f'  ❌ Error creando tablas: {str(e)}')
            raise

    def importar_datos(self):
        """Importa los datos exportados a Supabase"""
        try:
            backup_dir = 'backup_datos'
            
            # Orden de importación (respetando dependencias)
            archivos_orden = [
                'auth_User.json',
                'empleados_Empleado.json',
                'empleados_SolicitudVacaciones.json',
                'empleados_SolicitudNuevoColaborador.json',
            ]

            for archivo in archivos_orden:
                ruta_archivo = os.path.join(backup_dir, archivo)
                if os.path.exists(ruta_archivo):
                    try:
                        call_command('loaddata', ruta_archivo, verbosity=1)
                        self.stdout.write(f'  ✅ Importado: {archivo}')
                    except Exception as e:
                        self.stdout.write(f'  ⚠️ Error importando {archivo}: {str(e)}')
                else:
                    self.stdout.write(f'  ⚠️ Archivo no encontrado: {archivo}')

        except Exception as e:
            self.stdout.write(f'❌ Error en importación: {str(e)}')

    def restaurar_configuracion(self):
        """Restaura la configuración de base de datos original"""
        if hasattr(self, 'db_backup'):
            settings.DATABASES['default'] = self.db_backup
            connection.close()
