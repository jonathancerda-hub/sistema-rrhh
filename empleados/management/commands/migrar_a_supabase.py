"""
Comando para migrar datos de SQLite local a Supabase
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth.models import User
from empleados.models import Empleado
import json

class Command(BaseCommand):
    help = 'Migrar datos de SQLite local a Supabase'

    def add_arguments(self, parser):
        parser.add_argument(
            '--exportar',
            action='store_true',
            help='Solo exportar datos sin migrar',
        )

    def handle(self, *args, **options):
        if options['exportar']:
            self.exportar_datos()
        else:
            self.migrar_a_supabase()

    def exportar_datos(self):
        """Exportar datos locales a JSON"""
        self.stdout.write('📤 Exportando datos locales...')
        
        # Exportar usuarios
        usuarios = []
        for user in User.objects.all():
            usuarios.append({
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
                'is_active': user.is_active,
                'password_hash': user.password,  # Hash de la contraseña
            })
        
        # Exportar empleados
        empleados = []
        for emp in Empleado.objects.all():
            empleados.append({
                'username': emp.user.username,
                'nombre': emp.nombre,
                'apellido': emp.apellido,
                'dni': emp.dni,
                'email': emp.email,
                'puesto': emp.puesto,
                'fecha_contratacion': str(emp.fecha_contratacion),
                'dias_vacaciones_disponibles': emp.dias_vacaciones_disponibles,
                'es_rrhh': emp.es_rrhh,
                'area': emp.area,
                'gerencia': emp.gerencia,
                'jerarquia': emp.jerarquia,
            })
        
        datos = {
            'usuarios': usuarios,
            'empleados': empleados
        }
        
        # Guardar en archivo
        with open('datos_exportados.json', 'w', encoding='utf-8') as f:
            json.dump(datos, f, indent=2, ensure_ascii=False)
        
        self.stdout.write(self.style.SUCCESS('✅ Datos exportados a datos_exportados.json'))

    def migrar_a_supabase(self):
        """Migrar datos a Supabase"""
        self.stdout.write('🚀 Migrando datos a Supabase...')
        
        # Configuración temporal para Supabase
        original_databases = settings.DATABASES
        settings.DATABASES = {
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
        
        try:
            # Obtener datos de SQLite
            usuarios_sqlite = []
            empleados_sqlite = []
            
            # Restaurar configuración original para leer SQLite
            settings.DATABASES = original_databases
            
            for user in User.objects.all():
                usuarios_sqlite.append({
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'is_staff': user.is_staff,
                    'is_superuser': user.is_superuser,
                    'is_active': user.is_active,
                    'password_hash': user.password,
                })
            
            for emp in Empleado.objects.all():
                empleados_sqlite.append({
                    'username': emp.user.username,
                    'nombre': emp.nombre,
                    'apellido': emp.apellido,
                    'dni': emp.dni,
                    'email': emp.email,
                    'puesto': emp.puesto,
                    'fecha_contratacion': emp.fecha_contratacion,
                    'dias_vacaciones_disponibles': emp.dias_vacaciones_disponibles,
                    'es_rrhh': emp.es_rrhh,
                    'area': emp.area,
                    'gerencia': emp.gerencia,
                    'jerarquia': emp.jerarquia,
                })
            
            self.stdout.write(f'📊 Datos a migrar: {len(usuarios_sqlite)} usuarios, {len(empleados_sqlite)} empleados')
            
            # Cambiar a Supabase
            settings.DATABASES = {
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
            
            # Importar usuarios a Supabase
            for user_data in usuarios_sqlite:
                user, created = User.objects.get_or_create(
                    username=user_data['username'],
                    defaults={
                        'email': user_data['email'],
                        'first_name': user_data['first_name'],
                        'last_name': user_data['last_name'],
                        'is_staff': user_data['is_staff'],
                        'is_superuser': user_data['is_superuser'],
                        'is_active': user_data['is_active'],
                    }
                )
                # Mantener el hash de contraseña original
                user.password = user_data['password_hash']
                user.save()
                
                if created:
                    self.stdout.write(f'✅ Usuario creado: {user.username}')
                else:
                    self.stdout.write(f'ℹ️ Usuario actualizado: {user.username}')
            
            # Importar empleados a Supabase
            for emp_data in empleados_sqlite:
                try:
                    user = User.objects.get(username=emp_data['username'])
                    empleado, created = Empleado.objects.get_or_create(
                        user=user,
                        defaults={
                            'nombre': emp_data['nombre'],
                            'apellido': emp_data['apellido'],
                            'dni': emp_data['dni'],
                            'email': emp_data['email'],
                            'puesto': emp_data['puesto'],
                            'fecha_contratacion': emp_data['fecha_contratacion'],
                            'dias_vacaciones_disponibles': emp_data['dias_vacaciones_disponibles'],
                            'es_rrhh': emp_data['es_rrhh'],
                            'area': emp_data['area'],
                            'gerencia': emp_data['gerencia'],
                            'jerarquia': emp_data['jerarquia'],
                        }
                    )
                    
                    if created:
                        self.stdout.write(f'✅ Empleado creado: {empleado.nombre} {empleado.apellido}')
                    else:
                        self.stdout.write(f'ℹ️ Empleado actualizado: {empleado.nombre} {empleado.apellido}')
                        
                except User.DoesNotExist:
                    self.stdout.write(f'❌ Usuario no encontrado: {emp_data["username"]}')
            
            self.stdout.write(self.style.SUCCESS('\n🎉 ¡Migración completada exitosamente!'))
            self.stdout.write('🌐 Los datos están ahora en Supabase')
            self.stdout.write('💡 Puedes usar settings_production.py para conectar siempre a Supabase')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error en migración: {e}'))
        finally:
            # Restaurar configuración original
            settings.DATABASES = original_databases
