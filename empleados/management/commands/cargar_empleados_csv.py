import csv
import os
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.db import transaction
from empleados.models import Empleado
from empleados.views import normalizar_texto_username
import secrets
import string
from datetime import datetime
import pytz


class Command(BaseCommand):
    help = 'Carga empleados desde un archivo CSV'

    def add_arguments(self, parser):
        parser.add_argument(
            'archivo_csv',
            type=str,
            help='Ruta al archivo CSV con los datos de empleados'
        )
        parser.add_argument(
            '--test',
            action='store_true',
            help='Modo de prueba - muestra qué se haría sin guardar cambios'
        )

    def handle(self, *args, **options):
        archivo_csv = options['archivo_csv']
        modo_test = options['test']
        
        if not os.path.exists(archivo_csv):
            raise CommandError(f'El archivo {archivo_csv} no existe.')

        # Configurar timezone peruano
        timezone_peru = pytz.timezone('America/Lima')
        
        empleados_creados = 0
        empleados_actualizados = 0
        errores = []

        try:
            with open(archivo_csv, 'r', encoding='utf-8') as file:
                # Detectar el delimitador
                sample = file.read(1024)
                file.seek(0)
                delimiter = ',' if ',' in sample else ';'
                
                reader = csv.DictReader(file, delimiter=delimiter)
                
                # Validar columnas requeridas
                columnas_requeridas = ['nombre', 'apellido', 'dni', 'email', 'puesto']
                columnas_faltantes = [col for col in columnas_requeridas if col not in reader.fieldnames]
                
                if columnas_faltantes:
                    raise CommandError(f'Columnas faltantes en el CSV: {", ".join(columnas_faltantes)}')

                self.stdout.write(
                    self.style.SUCCESS(f'📁 Archivo CSV cargado correctamente')
                )
                self.stdout.write(f'📋 Columnas encontradas: {", ".join(reader.fieldnames)}')
                self.stdout.write(f'🔧 Delimitador detectado: "{delimiter}"')
                
                if modo_test:
                    self.stdout.write(self.style.WARNING('🧪 MODO DE PRUEBA - No se guardarán cambios'))
                
                self.stdout.write('─' * 50)

                with transaction.atomic():
                    for numero_fila, fila in enumerate(reader, start=2):  # start=2 porque la fila 1 son headers
                        try:
                            resultado = self.procesar_empleado(fila, numero_fila, timezone_peru, modo_test)
                            if resultado['accion'] == 'creado':
                                empleados_creados += 1
                            elif resultado['accion'] == 'actualizado':
                                empleados_actualizados += 1
                                
                        except Exception as e:
                            error_msg = f"Fila {numero_fila}: {str(e)}"
                            errores.append(error_msg)
                            self.stdout.write(
                                self.style.ERROR(f'❌ {error_msg}')
                            )

                    if modo_test:
                        # En modo test, hacer rollback
                        transaction.set_rollback(True)

        except Exception as e:
            raise CommandError(f'Error al procesar el archivo: {str(e)}')

        # Mostrar resumen
        self.stdout.write('─' * 50)
        self.stdout.write(self.style.SUCCESS('📊 RESUMEN:'))
        self.stdout.write(f'✅ Empleados creados: {empleados_creados}')
        self.stdout.write(f'🔄 Empleados actualizados: {empleados_actualizados}')
        
        if errores:
            self.stdout.write(f'❌ Errores: {len(errores)}')
            for error in errores[:5]:  # Mostrar solo los primeros 5 errores
                self.stdout.write(f'   • {error}')
            if len(errores) > 5:
                self.stdout.write(f'   ... y {len(errores) - 5} errores más')
        
        if modo_test:
            self.stdout.write(self.style.WARNING('🧪 Modo de prueba - no se guardaron cambios'))
        else:
            self.stdout.write(self.style.SUCCESS('💾 Cambios guardados exitosamente'))

    def procesar_empleado(self, fila, numero_fila, timezone_peru, modo_test):
        """Procesa una fila del CSV y crea/actualiza el empleado"""
        
        # Limpiar y validar datos básicos
        nombre = fila.get('nombre', '').strip()
        apellido = fila.get('apellido', '').strip()
        dni = fila.get('dni', '').strip()
        email = fila.get('email', '').strip().lower()
        puesto = fila.get('puesto', '').strip()
        
        if not all([nombre, apellido, dni, email, puesto]):
            raise ValueError("Campos requeridos faltantes (nombre, apellido, dni, email, puesto)")

        # Validar DNI
        if len(dni) != 8 or not dni.isdigit():
            raise ValueError(f"DNI inválido: {dni}. Debe tener 8 dígitos numéricos.")

        # Datos opcionales
        area = fila.get('area', '').strip()
        gerencia = fila.get('gerencia', '').strip()
        es_rrhh = fila.get('es_rrhh', '').strip().lower() in ['sí', 'si', 'yes', 'true', '1']
        
        # Mapear jerarquia basado en es_manager (para compatibilidad con la plantilla)
        es_manager_input = fila.get('es_manager', '').strip().lower() in ['sí', 'si', 'yes', 'true', '1']
        jerarquia = 'manager' if es_manager_input else 'auxiliar'
        
        # Procesar fecha de contratación
        fecha_contratacion = None
        fecha_str = fila.get('fecha_contratacion', '').strip()
        if fecha_str:
            try:
                # Intentar varios formatos de fecha
                formatos = ['%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y', '%m/%d/%Y']
                for formato in formatos:
                    try:
                        fecha_contratacion = datetime.strptime(fecha_str, formato).date()
                        break
                    except ValueError:
                        continue
                if not fecha_contratacion:
                    raise ValueError(f"Formato de fecha no reconocido: {fecha_str}")
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'⚠️ Fila {numero_fila}: Fecha inválida "{fecha_str}", se usará None')
                )

        # Generar username
        username = normalizar_texto_username(f"{nombre}.{apellido}")
        
        # Verificar si el usuario ya existe
        usuario_existente = User.objects.filter(username=username).first()
        empleado_existente = None
        
        if usuario_existente:
            try:
                empleado_existente = Empleado.objects.get(user=usuario_existente)
                accion = 'actualizado'
            except Empleado.DoesNotExist:
                accion = 'creado'  # Crear empleado para usuario existente
        else:
            accion = 'creado'

        if modo_test:
            self.stdout.write(
                f'🧪 Fila {numero_fila}: {accion.upper()} - {nombre} {apellido} ({username}) - {puesto}'
            )
            if area:
                self.stdout.write(f'   📍 Área: {area}')
            if jerarquia != 'auxiliar':
                self.stdout.write(f'   👔 Jerarquía: {jerarquia}')
            if es_rrhh:
                self.stdout.write(f'   👥 Personal de RRHH')
            if fecha_contratacion:
                self.stdout.write(f'   📅 Fecha contratación: {fecha_contratacion}')
            return {'accion': accion}

        # Crear o actualizar usuario
        if not usuario_existente:
            # Generar contraseña segura
            password = self.generar_password_seguro()
            
            usuario = User.objects.create_user(
                username=username,
                email=email,
                first_name=nombre,
                last_name=apellido,
                password=password
            )
            
            self.stdout.write(
                f'👤 Usuario creado: {username} (contraseña: {password})'
            )
        else:
            usuario = usuario_existente
            # Actualizar datos del usuario si es necesario
            usuario.email = email
            usuario.first_name = nombre
            usuario.last_name = apellido
            usuario.save()

        # Crear o actualizar empleado
        if empleado_existente:
            # Actualizar empleado existente
            empleado = empleado_existente
            empleado.nombre = nombre
            empleado.apellido = apellido
            empleado.dni = dni
            empleado.email = email
            empleado.puesto = puesto
            empleado.area = area
            empleado.gerencia = gerencia
            empleado.jerarquia = jerarquia
            empleado.es_rrhh = es_rrhh
            if fecha_contratacion:
                empleado.fecha_contratacion = fecha_contratacion
            empleado.save()
            
            self.stdout.write(
                f'🔄 Empleado actualizado: {nombre} {apellido} - {puesto}'
            )
        else:
            # Crear nuevo empleado
            empleado = Empleado.objects.create(
                user=usuario,
                nombre=nombre,
                apellido=apellido,
                dni=dni,
                email=email,
                puesto=puesto,
                area=area,
                gerencia=gerencia,
                jerarquia=jerarquia,
                es_rrhh=es_rrhh,
                fecha_contratacion=fecha_contratacion
            )
            
            self.stdout.write(
                f'✅ Empleado creado: {nombre} {apellido} - {puesto}'
            )

        return {'accion': accion}

    def generar_password_seguro(self):
        """Genera una contraseña segura"""
        caracteres = string.ascii_letters + string.digits
        password = ''.join(secrets.choice(caracteres) for _ in range(8))
        return password
