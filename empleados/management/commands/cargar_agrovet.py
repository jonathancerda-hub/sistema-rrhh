"""
Comando especializado para cargar organigrama de AgroVet Market
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from empleados.models import Empleado
import csv
import unicodedata
from datetime import datetime

class Command(BaseCommand):
    help = 'Cargar organigrama de AgroVet Market desde CSV'

    def add_arguments(self, parser):
        parser.add_argument(
            '--archivo',
            type=str,
            default='organigrama_agrovet.csv',
            help='Archivo CSV del organigrama',
        )
        parser.add_argument(
            '--preview',
            action='store_true',
            help='Solo mostrar vista previa sin crear usuarios',
        )

    def handle(self, *args, **options):
        archivo = options['archivo']
        
        if options['preview']:
            self.mostrar_preview(archivo)
        else:
            self.cargar_organigrama(archivo)

    def normalizar_texto(self, texto):
        """Normalizar texto removiendo tildes y caracteres especiales"""
        if not texto:
            return ""
        
        # Remover tildes y caracteres especiales
        texto_normalizado = unicodedata.normalize('NFD', texto)
        texto_normalizado = ''.join(c for c in texto_normalizado if unicodedata.category(c) != 'Mn')
        
        return texto_normalizado

    def generar_username(self, nombre, apellido):
        """Generar username en formato nombre.apellido sin tildes"""
        nombre_clean = self.normalizar_texto(nombre).lower().strip()
        apellido_clean = self.normalizar_texto(apellido).lower().strip()
        
        # Limpiar espacios y caracteres especiales
        nombre_clean = ''.join(c for c in nombre_clean if c.isalnum())
        apellido_clean = ''.join(c for c in apellido_clean if c.isalnum())
        
        username = f"{nombre_clean}.{apellido_clean}"
        
        # Si el username es muy largo, truncar
        if len(username) > 30:
            username = username[:30]
        
        return username

    def mapear_jerarquia(self, puesto, es_manager):
        """Mapear puesto a jerarquía del sistema"""
        puesto_lower = puesto.lower()
        
        if 'director' in puesto_lower:
            return 'director'
        elif 'gerente' in puesto_lower:
            return 'gerente'
        elif 'jefe' in puesto_lower:
            return 'jefe'
        elif 'supervisor' in puesto_lower:
            return 'supervisor'
        elif 'asistente' in puesto_lower:
            return 'asistente'
        elif 'practicante' in puesto_lower:
            return 'auxiliar'
        elif es_manager == 'si':
            return 'coordinador'
        else:
            return 'asistente'

    def parsear_fecha(self, fecha_str):
        """Convertir fecha DD-MM-YYYY a formato datetime"""
        try:
            return datetime.strptime(fecha_str, '%d-%m-%Y').date()
        except:
            return datetime(2001, 10, 2).date()  # Fecha por defecto

    def mostrar_preview(self, archivo):
        """Mostrar vista previa de lo que se cargará"""
        self.stdout.write('👀 Vista previa del organigrama AgroVet Market:')
        self.stdout.write('=' * 80)
        
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                count = 0
                for row in reader:
                    count += 1
                    username = self.generar_username(row['nombre'], row['apellido'])
                    jerarquia = self.mapear_jerarquia(row['puesto'], row['es_manager'])
                    
                    self.stdout.write(f"{count:2d}. {username:<25} | {row['nombre']} {row['apellido']:<20} | {row['puesto']:<35} | {jerarquia}")
                
                self.stdout.write('=' * 80)
                self.stdout.write(f'📊 Total empleados: {count}')
                self.stdout.write('🔑 Contraseña para todos: agrovet2025')
                self.stdout.write('\n💡 Para cargar ejecuta: python manage.py cargar_agrovet')
                
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'❌ Archivo no encontrado: {archivo}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error al leer archivo: {e}'))

    def cargar_organigrama(self, archivo):
        """Cargar el organigrama completo"""
        self.stdout.write('🏢 Cargando organigrama AgroVet Market...')
        self.stdout.write('=' * 60)
        
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                creados = 0
                actualizados = 0
                errores = 0
                
                for row in reader:
                    try:
                        # Generar datos
                        username = self.generar_username(row['nombre'], row['apellido'])
                        jerarquia = self.mapear_jerarquia(row['puesto'], row['es_manager'])
                        fecha_contratacion = self.parsear_fecha(row['fecha_contratacion'])
                        es_manager = row['es_manager'].lower() == 'si'
                        es_rrhh = row['es_rrhh'].lower() == 'si'
                        
                        # Crear/actualizar usuario Django
                        user, user_created = User.objects.get_or_create(
                            username=username,
                            defaults={
                                'email': row['email'],
                                'first_name': row['nombre'],
                                'last_name': row['apellido'],
                                'is_active': True,
                                'is_staff': es_rrhh,  # Staff si es RRHH
                            }
                        )
                        
                        # Establecer contraseña
                        user.set_password('agrovet2025')
                        user.save()
                        
                        # Crear/actualizar empleado
                        empleado, emp_created = Empleado.objects.get_or_create(
                            user=user,
                            defaults={
                                'nombre': row['nombre'],
                                'apellido': row['apellido'],
                                'dni': row['dni'],
                                'email': row['email'],
                                'puesto': row['puesto'],
                                'fecha_contratacion': fecha_contratacion,
                                'dias_vacaciones_disponibles': 20,
                                'es_rrhh': es_rrhh,
                                'area': 'Finanzas y T.I',  # Todos son de esta área según el CSV
                                'gerencia': 'gerencia_administracion_finanzas',  # Mapear a las opciones disponibles
                                'jerarquia': jerarquia,
                            }
                        )
                        
                        if user_created or emp_created:
                            creados += 1
                            manager_text = " (MANAGER)" if es_manager else ""
                            rrhh_text = " (RRHH)" if es_rrhh else ""
                            self.stdout.write(f'✅ {username:<25} | {row["nombre"]} {row["apellido"]}{manager_text}{rrhh_text}')
                        else:
                            actualizados += 1
                            self.stdout.write(f'ℹ️ {username:<25} | {row["nombre"]} {row["apellido"]} (actualizado)')
                        
                    except Exception as e:
                        errores += 1
                        self.stdout.write(f'❌ Error con {row.get("nombre", "usuario")}: {e}')
                
                # Resumen
                self.stdout.write('=' * 60)
                self.stdout.write(self.style.SUCCESS(f'🎉 ¡Carga completada!'))
                self.stdout.write(f'✅ Usuarios nuevos: {creados}')
                self.stdout.write(f'ℹ️ Usuarios actualizados: {actualizados}')
                self.stdout.write(f'❌ Errores: {errores}')
                
                # Información de acceso
                self.stdout.write('\n🔑 INFORMACIÓN DE ACCESO:')
                self.stdout.write('👤 Usuarios: nombre.apellido (sin tildes)')
                self.stdout.write('🔐 Contraseña: agrovet2025')
                self.stdout.write('\n📋 Ejemplos de usuarios creados:')
                
                # Mostrar algunos ejemplos
                ejemplos = [
                    ('josé.garcia', 'José García - Director'),
                    ('ena.fernandez', 'Ena Fernández - Gerente'),
                    ('teodoro.balarezo', 'Teodoro Balarezo - Jefe'),
                ]
                
                for username, descripcion in ejemplos:
                    self.stdout.write(f'   • {username} / agrovet2025 ({descripcion})')
                
                self.stdout.write('\n🌐 URLs útiles:')
                self.stdout.write('   • http://127.0.0.1:8000/usuarios/ (Ver todos los usuarios)')
                self.stdout.write('   • http://127.0.0.1:8000/login-debug/ (Probar login)')
                self.stdout.write('   • http://127.0.0.1:8000/admin/ (Panel admin)')
                
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'❌ Archivo no encontrado: {archivo}'))
            self.stdout.write('💡 Asegúrate de que el archivo esté en el directorio del proyecto')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error al procesar archivo: {e}'))
