import csv
import os
from datetime import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import models
from empleados.models import Empleado

class Command(BaseCommand):
    help = 'Carga usuarios desde un archivo CSV - Versión simplificada'

    def add_arguments(self, parser):
        parser.add_argument(
            '--archivo',
            type=str,
            help='Ruta al archivo CSV con los usuarios',
            required=True
        )

    def handle(self, *args, **options):
        archivo_csv = options['archivo']

        if not os.path.exists(archivo_csv):
            self.stdout.write(
                self.style.ERROR(f'❌ El archivo {archivo_csv} no existe')
            )
            return

        self.stdout.write('🚀 Iniciando carga de usuarios desde CSV...')
        
        usuarios_procesados = 0
        usuarios_creados = 0
        usuarios_actualizados = 0
        errores = 0

        try:
            with open(archivo_csv, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        # Extraer datos
                        nombre = row.get('nombre', '').strip()
                        apellido = row.get('apellido', '').strip()
                        dni = row.get('dni', '').strip()
                        email = row.get('email', '').strip().lower()
                        puesto = row.get('puesto', '').strip()
                        gerencia = row.get('gerencia', '').strip()
                        
                        # Campos booleanos
                        es_rrhh = row.get('es_rrhh', '').strip().lower() in ['si', 'sí', 'yes', 'true', '1']
                        
                        # Fecha
                        fecha_str = row.get('fecha_contratacion', '').strip()
                        try:
                            fecha_contratacion = datetime.strptime(fecha_str, '%d-%m-%Y').date()
                        except:
                            fecha_contratacion = datetime.now().date()

                        # Validar campos obligatorios
                        if not all([nombre, apellido, dni, email]):
                            self.stdout.write(f'❌ Fila {row_num}: Faltan campos obligatorios')
                            errores += 1
                            continue

                        # Buscar usuario existente
                        usuario_existente = None
                        try:
                            usuario_existente = User.objects.get(email=email)
                        except User.DoesNotExist:
                            try:
                                empleado_existente = Empleado.objects.get(dni=dni)
                                usuario_existente = empleado_existente.user
                            except Empleado.DoesNotExist:
                                pass

                        if usuario_existente:
                            # Actualizar usuario existente
                            username = self.generar_username(nombre, apellido, dni)
                            usuario_existente.username = username
                            usuario_existente.first_name = nombre
                            usuario_existente.last_name = apellido
                            usuario_existente.email = email
                            usuario_existente.is_staff = es_rrhh
                            usuario_existente.is_superuser = es_rrhh
                            usuario_existente.save()

                            # Actualizar o crear empleado
                            if hasattr(usuario_existente, 'empleado'):
                                empleado = usuario_existente.empleado
                                empleado.nombre = nombre
                                empleado.apellido = apellido
                                empleado.dni = dni
                                empleado.email = email
                                empleado.puesto = puesto
                                empleado.gerencia = gerencia
                                empleado.es_rrhh = es_rrhh
                                empleado.fecha_contratacion = fecha_contratacion
                                empleado.save()
                            else:
                                Empleado.objects.create(
                                    user=usuario_existente,
                                    nombre=nombre,
                                    apellido=apellido,
                                    dni=dni,
                                    email=email,
                                    puesto=puesto,
                                    gerencia=gerencia,
                                    es_rrhh=es_rrhh,
                                    fecha_contratacion=fecha_contratacion,
                                    dias_vacaciones_disponibles=30
                                )

                            usuarios_actualizados += 1
                            self.stdout.write(f'🔄 Actualizado: {nombre} {apellido}')

                        else:
                            # Crear nuevo usuario
                            username = self.generar_username(nombre, apellido, dni)
                            
                            nuevo_user = User.objects.create_user(
                                username=username,
                                email=email,
                                password='agrovet2024',
                                first_name=nombre,
                                last_name=apellido,
                                is_staff=es_rrhh,
                                is_superuser=es_rrhh
                            )

                            Empleado.objects.create(
                                user=nuevo_user,
                                nombre=nombre,
                                apellido=apellido,
                                dni=dni,
                                email=email,
                                puesto=puesto,
                                gerencia=gerencia,
                                es_rrhh=es_rrhh,
                                fecha_contratacion=fecha_contratacion,
                                dias_vacaciones_disponibles=30
                            )

                            usuarios_creados += 1
                            self.stdout.write(f'✅ Creado: {nombre} {apellido}')

                        usuarios_procesados += 1

                    except Exception as e:
                        self.stdout.write(f'❌ Error en fila {row_num}: {str(e)}')
                        errores += 1

        except Exception as e:
            self.stdout.write(f'❌ Error al leer archivo: {str(e)}')
            return

        # Resumen
        self.stdout.write('\n' + '='*50)
        self.stdout.write('📊 RESUMEN:')
        self.stdout.write(f'👥 Usuarios procesados: {usuarios_procesados}')
        self.stdout.write(f'✅ Usuarios creados: {usuarios_creados}')
        self.stdout.write(f'🔄 Usuarios actualizados: {usuarios_actualizados}')
        self.stdout.write(f'❌ Errores: {errores}')
        self.stdout.write('='*50)
        
        if usuarios_creados > 0 or usuarios_actualizados > 0:
            self.stdout.write('🎉 ¡Carga completada! Contraseña temporal: "agrovet2024"')

    def generar_username(self, nombre, apellido, dni):
        """Genera username único"""
        base = f"{nombre.lower()}.{apellido.lower()}"
        base = ''.join(c for c in base if c.isalnum() or c == '.')
        
        if len(base) > 25:
            base = f"{nombre[0].lower()}.{apellido.lower()}"
        
        if User.objects.filter(username=base).exists():
            base = f"{base}{dni[-3:]}"
        
        return base[:30]
