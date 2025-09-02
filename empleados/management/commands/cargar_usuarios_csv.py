import csv
import os
from datetime import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import models, transaction
from empleados.models import Empleado

class Command(BaseCommand):
    help = 'Carga usuarios desde un archivo CSV'

    def add_arguments(self, parser):
        parser.add_argument(
            '--archivo',
            type=str,
            help='Ruta al archivo CSV con los usuarios',
            required=True
        )
        parser.add_argument(
            '--sobrescribir',
            action='store_true',
            help='Sobrescribe usuarios existentes'
        )

    def handle(self, *args, **options):
        archivo_csv = options['archivo']
        sobrescribir = options['sobrescribir']

        if not os.path.exists(archivo_csv):
            self.stdout.write(
                self.style.ERROR(f'❌ El archivo {archivo_csv} no existe')
            )
            return

        self.stdout.write('🚀 Iniciando carga de usuarios desde CSV...')
        
        usuarios_creados = 0
        usuarios_actualizados = 0
        errores = 0

        try:
            with open(archivo_csv, 'r', encoding='utf-8') as file:
                # Detectar el dialecto del CSV
                sample = file.read(1024)
                file.seek(0)
                sniffer = csv.Sniffer()
                delimiter = ','
                try:
                    delimiter = sniffer.sniff(sample).delimiter
                except:
                    pass

                reader = csv.DictReader(file, delimiter=delimiter)
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        # Limpiar y validar datos
                        nombre = row.get('nombre', '').strip()
                        apellido = row.get('apellido', '').strip()
                        dni = row.get('dni', '').strip()
                        email = row.get('email', '').strip().lower()
                        puesto = row.get('puesto', '').strip()
                        gerencia = row.get('gerencia', '').strip()
                        
                        # Convertir campos booleanos
                        es_manager = row.get('es_manager', '').strip().lower() in ['si', 'sí', 'yes', 'true', '1']
                        es_rrhh = row.get('es_rrhh', '').strip().lower() in ['si', 'sí', 'yes', 'true', '1']
                        
                        # Parsear fecha
                        fecha_str = row.get('fecha_contratacion', '').strip()
                        fecha_contratacion = None
                        if fecha_str:
                            try:
                                # Intentar varios formatos de fecha
                                for fmt in ['%d-%m-%Y', '%d/%m/%Y', '%Y-%m-%d', '%m/%d/%Y']:
                                    try:
                                        fecha_contratacion = datetime.strptime(fecha_str, fmt).date()
                                        break
                                    except ValueError:
                                        continue
                            except:
                                self.stdout.write(
                                    self.style.WARNING(f'⚠️ Fila {row_num}: Fecha inválida "{fecha_str}", usando fecha actual')
                                )
                                fecha_contratacion = datetime.now().date()

                        # Validar campos obligatorios
                        if not all([nombre, apellido, dni, email]):
                            self.stdout.write(
                                self.style.ERROR(f'❌ Fila {row_num}: Faltan campos obligatorios')
                            )
                            errores += 1
                            continue

                        # Crear username único
                        username = self.generar_username(nombre, apellido, dni)
                        
                        # Verificar si el usuario ya existe
                        user_exists = User.objects.filter(
                            models.Q(username=username) | 
                            models.Q(email=email) |
                            models.Q(empleado__dni=dni)
                        ).exists()

                        if user_exists and not sobrescribir:
                            self.stdout.write(
                                self.style.WARNING(f'⚠️ Usuario ya existe: {email} (usa --sobrescribir para actualizar)')
                            )
                            continue

                            # Crear o actualizar usuario
                            if user_exists and sobrescribir:
                                # Actualizar usuario existente
                                try:
                                    user = User.objects.get(email=email)
                                    if not hasattr(user, 'empleado'):
                                        # Crear empleado si no existe
                                        empleado = Empleado.objects.create(
                                            user=user,
                                            nombre=nombre,
                                            apellido=apellido,
                                            dni=dni,
                                            email=email,
                                            puesto=puesto,
                                            gerencia=gerencia,
                                            es_rrhh=es_rrhh,
                                            fecha_contratacion=fecha_contratacion or datetime.now().date(),
                                            dias_vacaciones_disponibles=30
                                        )
                                    else:
                                        empleado = user.empleado
                                except User.DoesNotExist:
                                    try:
                                        empleado = Empleado.objects.get(dni=dni)
                                        user = empleado.user
                                    except Empleado.DoesNotExist:
                                        user = User.objects.get(username=username)
                                        if not hasattr(user, 'empleado'):
                                            empleado = Empleado.objects.create(
                                                user=user,
                                                nombre=nombre,
                                                apellido=apellido,
                                                dni=dni,
                                                email=email,
                                                puesto=puesto,
                                                gerencia=gerencia,
                                                es_rrhh=es_rrhh,
                                                fecha_contratacion=fecha_contratacion or datetime.now().date(),
                                                dias_vacaciones_disponibles=30
                                            )
                                        else:
                                            empleado = user.empleado
                                
                                # Actualizar usuario
                                user.username = username
                                user.first_name = nombre
                                user.last_name = apellido
                                user.email = email
                                user.is_staff = es_manager or es_rrhh
                                user.is_superuser = es_rrhh
                                user.save()
                                
                                # Actualizar empleado
                                empleado.nombre = nombre
                                empleado.apellido = apellido
                                empleado.dni = dni
                                empleado.email = email
                                empleado.puesto = puesto
                                empleado.gerencia = gerencia
                                empleado.es_rrhh = es_rrhh
                                if fecha_contratacion:
                                    empleado.fecha_contratacion = fecha_contratacion
                                empleado.save()
                                
                                usuarios_actualizados += 1
                                self.stdout.write(f'🔄 Actualizado: {nombre} {apellido} ({email})')
                                
                            else:
                                # Crear nuevo usuario
                                user = User.objects.create_user(
                                    username=username,
                                    email=email,
                                    password='agrovet2024',  # Contraseña temporal
                                    first_name=nombre,
                                    last_name=apellido,
                                    is_staff=es_manager or es_rrhh,
                                    is_superuser=es_rrhh
                                )
                                
                                # Crear empleado
                                empleado = Empleado.objects.create(
                                    user=user,
                                    nombre=nombre,
                                    apellido=apellido,
                                    dni=dni,
                                    email=email,
                                    puesto=puesto,
                                    gerencia=gerencia,
                                    es_rrhh=es_rrhh,
                                    fecha_contratacion=fecha_contratacion or datetime.now().date(),
                                    dias_vacaciones_disponibles=30
                                )
                                
                                usuarios_creados += 1
                                self.stdout.write(f'✅ Creado: {nombre} {apellido} ({email})')

                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f'❌ Error en fila {row_num}: {str(e)}')
                        )
                        errores += 1
                        continue

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error al leer el archivo: {str(e)}')
            )
            return

        # Resumen final
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('📊 RESUMEN DE CARGA:'))
        self.stdout.write(f'✅ Usuarios creados: {usuarios_creados}')
        self.stdout.write(f'🔄 Usuarios actualizados: {usuarios_actualizados}')
        self.stdout.write(f'❌ Errores: {errores}')
        self.stdout.write('='*50)
        
        if usuarios_creados > 0 or usuarios_actualizados > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n🎉 ¡Carga completada! '
                    f'Contraseña temporal para todos: "agrovet2024"'
                )
            )

    def generar_username(self, nombre, apellido, dni):
        """Genera un username único basado en nombre, apellido y DNI"""
        # Limpiar caracteres especiales
        nombre_limpio = ''.join(c for c in nombre if c.isalnum()).lower()
        apellido_limpio = ''.join(c for c in apellido if c.isalnum()).lower()
        
        # Crear username base
        username_base = f"{nombre_limpio}.{apellido_limpio}"
        
        # Si es muy largo, usar iniciales + apellido
        if len(username_base) > 25:
            username_base = f"{nombre_limpio[0]}.{apellido_limpio}"
        
        # Si aún es muy largo o ya existe, agregar parte del DNI
        if len(username_base) > 25 or User.objects.filter(username=username_base).exists():
            username_base = f"{nombre_limpio[0]}.{apellido_limpio}{dni[-3:]}"
        
        return username_base[:30]  # Límite de Django para username
