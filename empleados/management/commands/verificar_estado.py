"""
Comando para verificar el estado del sistema RRHH
"""
from django.core.management.base import BaseCommand
from django.db import connection
from django.contrib.auth.models import User
from empleados.models import Empleado
import os

class Command(BaseCommand):
    help = 'Verificar estado del sistema RRHH'

    def handle(self, *args, **options):
        self.stdout.write('🔍 Verificando estado del proyecto RRHH...')
        
        # 1. Verificar conexión a base de datos
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            self.stdout.write('✅ Conexión a base de datos: OK')
            
            # Obtener info de la base de datos
            db_settings = connection.settings_dict
            engine = db_settings['ENGINE']
            if 'postgresql' in engine:
                self.stdout.write(f"🌐 Base de datos: PostgreSQL ({db_settings.get('HOST', 'localhost')})")
            elif 'sqlite' in engine:
                db_name = db_settings.get('NAME', 'Unknown')
                if hasattr(db_name, 'name'):  # Es un Path object
                    db_name = str(db_name)
                self.stdout.write(f"🗄️ Base de datos: SQLite ({os.path.basename(db_name)})")
            else:
                self.stdout.write(f"🔧 Base de datos: {engine}")
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error de conexión: {e}"))
            return
        
        # 2. Verificar usuarios
        try:
            user_count = User.objects.count()
            self.stdout.write(f"👥 Usuarios en sistema: {user_count}")
            
            if user_count > 0:
                users = User.objects.all()[:5]  # Mostrar los primeros 5
                for user in users:
                    self.stdout.write(f"   • {user.username} ({user.first_name} {user.last_name})")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error al consultar usuarios: {e}"))
        
        # 3. Verificar empleados
        try:
            empleado_count = Empleado.objects.count()
            self.stdout.write(f"👔 Empleados en sistema: {empleado_count}")
            
            if empleado_count > 0:
                empleados = Empleado.objects.all()[:5]  # Mostrar los primeros 5
                for emp in empleados:
                    self.stdout.write(f"   • {emp.nombre} {emp.apellido} - {emp.puesto}")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error al consultar empleados: {e}"))
        
        self.stdout.write(self.style.SUCCESS('\n🎉 Verificación completada!'))
