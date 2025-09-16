#!/usr/bin/env python
import os
import csv
from datetime import datetime
import unicodedata
import re
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from empleados.models import Empleado


def limpiar_texto(texto):
    """Remover tildes, ñ y caracteres especiales para usernames"""
    # Convertir a minúsculas
    texto = texto.lower()
    # Remover tildes y caracteres especiales
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
    # Reemplazar ñ por n
    texto = texto.replace('ñ', 'n')
    # Mantener solo letras, números y puntos
    texto = re.sub(r'[^a-z0-9.]', '', texto)
    return texto

def generar_username(nombre, apellido):
    """Generar username en formato nombre.apellido"""
    nombre_limpio = limpiar_texto(nombre.strip())
    apellido_limpio = limpiar_texto(apellido.strip())
    
    # Tomar primera palabra de cada campo
    nombre_parte = nombre_limpio.split()[0] if nombre_limpio.split() else nombre_limpio
    apellido_parte = apellido_limpio.split()[0] if apellido_limpio.split() else apellido_limpio
    
    username = f"{nombre_parte}.{apellido_parte}"
    return username

def convertir_fecha(fecha_str):
    """Convertir fecha de formato DD-MM-YYYY a objeto datetime"""
    try:
        return datetime.strptime(fecha_str.strip(), '%d-%m-%Y').date()
    except:
        return datetime.now().date()

class Command(BaseCommand):
    help = 'Carga empleados desde un archivo CSV especificado.'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='La ruta al archivo CSV para cargar.')

    def handle(self, *args, **options):
        archivo_csv = options['csv_file']

        if not os.path.exists(archivo_csv):
            self.stdout.write(self.style.ERROR(f"❌ Error: No se encuentra el archivo {archivo_csv}"))
            return

        empleados_creados = 0
        empleados_actualizados = 0
        errores = []

        with open(archivo_csv, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for fila in reader:
                try:
                    # Extraer datos
                    nombre = fila['nombre'].strip()
                    apellido = fila['apellido'].strip()
                    dni = fila['dni'].strip()
                    email = fila['email'].strip()
                    puesto = fila['puesto'].strip()
                    gerencia = fila['gerencia'].strip()
                    es_manager = fila['es_manager'].strip().lower() == 'si'
                    es_rrhh = fila['es_rrhh'].strip().lower() == 'si'
                    fecha_contratacion = convertir_fecha(fila['fecha_contratacion'])
                    
                    # Generar username
                    username = generar_username(nombre, apellido)
                    password = "Agrovet2025"
                    
                    self.stdout.write(f"\n📝 Procesando: {nombre} {apellido}")
                    self.stdout.write(f"   Username: {username}")
                    self.stdout.write(f"   Email: {email}")
                    self.stdout.write(f"   DNI: {dni}")
                    
                    # Crear o actualizar usuario Django
                    user, user_created = User.objects.get_or_create(
                        username=username,
                        defaults={
                            'email': email,
                            'first_name': nombre,
                            'last_name': apellido,
                            'is_active': True,
                            'is_staff': es_manager or es_rrhh,  # Staff si es manager o RRHH
                        }
                    )
                    
                    if user_created:
                        user.set_password(password)
                        user.save()
                        self.stdout.write(self.style.SUCCESS(f"   ✅ Usuario Django creado"))
                    else:
                        # Actualizar datos del usuario existente
                        user.email = email
                        user.first_name = nombre
                        user.last_name = apellido
                        user.is_staff = es_manager or es_rrhh
                        user.set_password(password)  # Actualizar contraseña
                        user.save()
                        self.stdout.write(self.style.WARNING(f"   🔄 Usuario Django actualizado"))
                    
                    # Mapear gerencia a valores válidos
                    gerencia_map = {
                        'Gerencia Finanzas y T.I': 'gerencia_administracion_finanzas',
                        'Gerencia Comercial Local': 'gerencia_comercial_local',
                        'Gerencia Comercial Internacional': 'gerencia_comercial_internacional',
                        'Gerencia de Desarrollo Organizacional': 'gerencia_desarrollo_organizacional',
                    }
                    gerencia_valor = gerencia_map.get(gerencia, None)
                    
                    # Crear o actualizar empleado
                    empleado, emp_created = Empleado.objects.get_or_create(
                        dni=dni,
                        defaults={
                            'user': user,
                            'nombre': nombre,
                            'apellido': apellido,
                            'email': email,
                            'puesto': puesto,
                            'gerencia': gerencia_valor,
                            'area': gerencia,  # Guardar el nombre completo en area
                            'es_rrhh': es_rrhh,
                            'fecha_contratacion': fecha_contratacion,
                        }
                    )
                    
                    if emp_created:
                        empleados_creados += 1
                        self.stdout.write(self.style.SUCCESS(f"   ✅ Empleado creado"))
                    else:
                        # Actualizar empleado existente
                        empleado.user = user
                        empleado.nombre = nombre
                        empleado.apellido = apellido
                        empleado.email = email
                        empleado.puesto = puesto
                        empleado.gerencia = gerencia_valor
                        empleado.area = gerencia
                        empleado.es_rrhh = es_rrhh
                        empleado.fecha_contratacion = fecha_contratacion
                        empleado.save()
                        empleados_actualizados += 1
                        self.stdout.write(self.style.WARNING(f"   🔄 Empleado actualizado"))
                        
                except Exception as e:
                    error_msg = f"Error con {nombre} {apellido}: {str(e)}"
                    errores.append(error_msg)
                    self.stdout.write(self.style.ERROR(f"   ❌ {error_msg}"))
                    continue
        
        # Resumen final
        self.stdout.write(self.style.SUCCESS(f"\n{'='*50}"))
        self.stdout.write(self.style.SUCCESS(f"📊 RESUMEN DE CARGA"))
        self.stdout.write(self.style.SUCCESS(f"{'='*50}"))
        self.stdout.write(f"✅ Empleados nuevos creados: {empleados_creados}")
        self.stdout.write(f"🔄 Empleados actualizados: {empleados_actualizados}")
        self.stdout.write(f"📝 Total procesados: {empleados_creados + empleados_actualizados}")
        
        if errores:
            self.stdout.write(self.style.ERROR(f"\n❌ Errores encontrados ({len(errores)}):"))
            for error in errores:
                self.stdout.write(f"   - {error}")
        
        # Mostrar estadísticas finales
        total_users = User.objects.count()
        total_empleados = Empleado.objects.count()
        managers = Empleado.objects.filter(user__is_staff=True, es_rrhh=False).count()
        rrhh = Empleado.objects.filter(es_rrhh=True).count()
        
        self.stdout.write(f"\n📈 ESTADÍSTICAS DEL SISTEMA:")
        self.stdout.write(f"👥 Total usuarios Django: {total_users}")
        self.stdout.write(f"👨‍💼 Total empleados: {total_empleados}")
        self.stdout.write(f"👨‍💼 Managers: {managers}")
        self.stdout.write(f"🏢 Personal RRHH: {rrhh}")
