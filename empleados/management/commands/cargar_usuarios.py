"""
Comando para cargar usuarios masivamente desde diferentes fuentes
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from empleados.models import Empleado
import csv
import json
from datetime import date

class Command(BaseCommand):
    help = 'Cargar usuarios masivamente al sistema'

    def add_arguments(self, parser):
        parser.add_argument(
            '--demo',
            action='store_true',
            help='Crear usuarios de demostración',
        )
        parser.add_argument(
            '--csv',
            type=str,
            help='Cargar desde archivo CSV',
        )
        parser.add_argument(
            '--plantilla',
            action='store_true',
            help='Crear plantilla CSV de ejemplo',
        )

    def handle(self, *args, **options):
        if options['plantilla']:
            self.crear_plantilla_csv()
        elif options['demo']:
            self.crear_usuarios_demo()
        elif options['csv']:
            self.cargar_desde_csv(options['csv'])
        else:
            self.mostrar_ayuda()

    def crear_plantilla_csv(self):
        """Crear plantilla CSV de ejemplo"""
        plantilla = [
            ['username', 'nombre', 'apellido', 'email', 'puesto', 'dni', 'area', 'gerencia', 'jerarquia', 'es_rrhh', 'password'],
            ['juan.perez', 'Juan', 'Pérez', 'juan.perez@empresa.com', 'Analista', '12345678', 'TI', 'gerencia_desarrollo_organizacional', 'asistente', 'False', 'empleado123'],
            ['maria.garcia', 'María', 'García', 'maria.garcia@empresa.com', 'Coordinadora', '87654321', 'Ventas', 'gerencia_comercial_local', 'coordinador', 'False', 'empleado123'],
            ['carlos.lopez', 'Carlos', 'López', 'carlos.lopez@empresa.com', 'Jefe de Ventas', '11223344', 'Ventas', 'gerencia_comercial_local', 'jefe', 'False', 'manager123'],
            ['ana.martinez', 'Ana', 'Martínez', 'ana.martinez@empresa.com', 'Especialista RRHH', '44332211', 'RRHH', 'gerencia_desarrollo_organizacional', 'asistente', 'True', 'rrhh123'],
        ]
        
        with open('plantilla_usuarios.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(plantilla)
        
        self.stdout.write(self.style.SUCCESS('✅ Plantilla creada: plantilla_usuarios.csv'))
        self.stdout.write('📝 Edita el archivo y luego ejecuta:')
        self.stdout.write('   python manage.py cargar_usuarios --csv plantilla_usuarios.csv')

    def crear_usuarios_demo(self):
        """Crear usuarios de demostración variados"""
        self.stdout.write('👥 Creando usuarios de demostración...')
        
        usuarios_demo = [
            {
                'username': 'director.general',
                'nombre': 'Roberto',
                'apellido': 'Valdez',
                'email': 'director@empresa.com',
                'puesto': 'Director General',
                'dni': '10101010',
                'area': 'Dirección',
                'gerencia': 'gerencia_desarrollo_organizacional',
                'jerarquia': 'director',
                'es_rrhh': False,
                'password': 'director123',
                'is_staff': True,
            },
            {
                'username': 'gerente.ventas',
                'nombre': 'Patricia',
                'apellido': 'Morales',
                'email': 'pmorales@empresa.com',
                'puesto': 'Gerente de Ventas',
                'dni': '20202020',
                'area': 'Ventas',
                'gerencia': 'gerencia_comercial_local',
                'jerarquia': 'gerente',
                'es_rrhh': False,
                'password': 'gerente123',
            },
            {
                'username': 'supervisor.ti',
                'nombre': 'Miguel',
                'apellido': 'Reyes',
                'email': 'mreyes@empresa.com',
                'puesto': 'Supervisor de TI',
                'dni': '30303030',
                'area': 'Tecnología',
                'gerencia': 'gerencia_desarrollo_organizacional',
                'jerarquia': 'supervisor',
                'es_rrhh': False,
                'password': 'supervisor123',
            },
            {
                'username': 'asistente.admin',
                'nombre': 'Carmen',
                'apellido': 'Silva',
                'email': 'csilva@empresa.com',
                'puesto': 'Asistente Administrativa',
                'dni': '40404040',
                'area': 'Administración',
                'gerencia': 'gerencia_administracion_finanzas',
                'jerarquia': 'asistente',
                'es_rrhh': False,
                'password': 'asistente123',
            },
            {
                'username': 'analista.finanzas',
                'nombre': 'Diego',
                'apellido': 'Herrera',
                'email': 'dherrera@empresa.com',
                'puesto': 'Analista Financiero',
                'dni': '50505050',
                'area': 'Finanzas',
                'gerencia': 'gerencia_administracion_finanzas',
                'jerarquia': 'asistente',
                'es_rrhh': False,
                'password': 'analista123',
            },
            {
                'username': 'coordinador.logistica',
                'nombre': 'Elena',
                'apellido': 'Vargas',
                'email': 'evargas@empresa.com',
                'puesto': 'Coordinadora de Logística',
                'dni': '60606060',
                'area': 'Logística',
                'gerencia': 'gerencia_comercial_local',
                'jerarquia': 'coordinador',
                'es_rrhh': False,
                'password': 'coordinador123',
            },
            {
                'username': 'especialista.rrhh',
                'nombre': 'Fernando',
                'apellido': 'Castro',
                'email': 'fcastro@empresa.com',
                'puesto': 'Especialista en Compensaciones',
                'dni': '70707070',
                'area': 'Recursos Humanos',
                'gerencia': 'gerencia_desarrollo_organizacional',
                'jerarquia': 'asistente',
                'es_rrhh': True,
                'password': 'rrhh123',
            }
        ]
        
        creados = 0
        actualizados = 0
        
        for user_data in usuarios_demo:
            # Crear o actualizar usuario Django
            user, user_created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data['nombre'],
                    'last_name': user_data['apellido'],
                    'is_staff': user_data.get('is_staff', False),
                    'is_active': True,
                }
            )
            
            if user_created:
                user.set_password(user_data['password'])
                user.save()
                creados += 1
                self.stdout.write(f'✅ Usuario creado: {user.username}')
            else:
                actualizados += 1
                self.stdout.write(f'ℹ️ Usuario ya existe: {user.username}')
            
            # Crear o actualizar empleado
            empleado, emp_created = Empleado.objects.get_or_create(
                user=user,
                defaults={
                    'nombre': user_data['nombre'],
                    'apellido': user_data['apellido'],
                    'dni': user_data['dni'],
                    'email': user_data['email'],
                    'puesto': user_data['puesto'],
                    'fecha_contratacion': date(2022, 1, 1),
                    'dias_vacaciones_disponibles': 20,
                    'es_rrhh': user_data['es_rrhh'],
                    'area': user_data['area'],
                    'gerencia': user_data['gerencia'],
                    'jerarquia': user_data['jerarquia'],
                }
            )
            
            if emp_created:
                self.stdout.write(f'👔 Empleado creado: {empleado.nombre} {empleado.apellido}')
        
        self.stdout.write(self.style.SUCCESS(f'\n🎉 Proceso completado!'))
        self.stdout.write(f'✅ Usuarios nuevos: {creados}')
        self.stdout.write(f'ℹ️ Usuarios existentes: {actualizados}')
        self.stdout.write('\n📝 Credenciales creadas:')
        
        for user_data in usuarios_demo:
            rol = "RRHH" if user_data['es_rrhh'] else user_data['puesto']
            self.stdout.write(f'   • {user_data["username"]} / {user_data["password"]} ({rol})')

    def cargar_desde_csv(self, archivo_csv):
        """Cargar usuarios desde archivo CSV"""
        self.stdout.write(f'📁 Cargando usuarios desde {archivo_csv}...')
        
        try:
            with open(archivo_csv, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                creados = 0
                errores = 0
                
                for row in reader:
                    try:
                        # Crear usuario Django
                        user, created = User.objects.get_or_create(
                            username=row['username'],
                            defaults={
                                'email': row['email'],
                                'first_name': row['nombre'],
                                'last_name': row['apellido'],
                                'is_active': True,
                            }
                        )
                        
                        if created:
                            user.set_password(row.get('password', 'empleado123'))
                            user.save()
                        
                        # Crear empleado
                        empleado, emp_created = Empleado.objects.get_or_create(
                            user=user,
                            defaults={
                                'nombre': row['nombre'],
                                'apellido': row['apellido'],
                                'dni': row['dni'],
                                'email': row['email'],
                                'puesto': row['puesto'],
                                'fecha_contratacion': date(2022, 1, 1),
                                'dias_vacaciones_disponibles': 20,
                                'es_rrhh': row.get('es_rrhh', 'False').lower() == 'true',
                                'area': row.get('area', ''),
                                'gerencia': row.get('gerencia', 'gerencia_desarrollo_organizacional'),
                                'jerarquia': row.get('jerarquia', 'asistente'),
                            }
                        )
                        
                        if created or emp_created:
                            creados += 1
                            self.stdout.write(f'✅ {row["nombre"]} {row["apellido"]} cargado')
                        
                    except Exception as e:
                        errores += 1
                        self.stdout.write(f'❌ Error con {row.get("nombre", "usuario")}: {e}')
                
                self.stdout.write(self.style.SUCCESS(f'\n📊 Resumen: {creados} usuarios procesados, {errores} errores'))
                
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'❌ Archivo no encontrado: {archivo_csv}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error al procesar archivo: {e}'))

    def mostrar_ayuda(self):
        """Mostrar ayuda sobre carga de usuarios"""
        self.stdout.write(self.style.SUCCESS('👥 Herramienta de Carga de Usuarios'))
        self.stdout.write('')
        self.stdout.write('Opciones disponibles:')
        self.stdout.write('  --demo           Crear usuarios de demostración')
        self.stdout.write('  --plantilla      Crear plantilla CSV')
        self.stdout.write('  --csv ARCHIVO    Cargar desde CSV')
        self.stdout.write('')
        self.stdout.write('Ejemplos:')
        self.stdout.write('  python manage.py cargar_usuarios --demo')
        self.stdout.write('  python manage.py cargar_usuarios --plantilla')
        self.stdout.write('  python manage.py cargar_usuarios --csv usuarios.csv')
