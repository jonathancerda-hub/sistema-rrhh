#!/usr/bin/env python
import os
import sys
import django
import csv
from datetime import datetime
import unicodedata
import re

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nucleo_rrhh.settings_production')
django.setup()

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

def cargar_empleados_desde_csv():
    """Cargar empleados desde el archivo CSV"""
    
    archivo_csv = r"c:\Users\jcerda\Downloads\organigrama - Hoja 1.csv"
    
    if not os.path.exists(archivo_csv):
        print(f"❌ Error: No se encuentra el archivo {archivo_csv}")
        return False
    
    empleados_creados = 0
    empleados_actualizados = 0
    errores = []
    
    try:
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
                    
                    print(f"\n📝 Procesando: {nombre} {apellido}")
                    print(f"   Username: {username}")
                    print(f"   Email: {email}")
                    print(f"   DNI: {dni}")
                    
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
                        print(f"   ✅ Usuario Django creado")
                    else:
                        # Actualizar datos del usuario existente
                        user.email = email
                        user.first_name = nombre
                        user.last_name = apellido
                        user.is_staff = es_manager or es_rrhh
                        user.set_password(password)  # Actualizar contraseña
                        user.save()
                        print(f"   🔄 Usuario Django actualizado")
                    
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
                        print(f"   ✅ Empleado creado")
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
                        print(f"   🔄 Empleado actualizado")
                        
                except Exception as e:
                    error_msg = f"Error con {nombre} {apellido}: {str(e)}"
                    errores.append(error_msg)
                    print(f"   ❌ {error_msg}")
                    continue
                    
    except Exception as e:
        print(f"❌ Error al leer archivo CSV: {e}")
        return False
    
    # Resumen final
    print(f"\n{'='*50}")
    print(f"📊 RESUMEN DE CARGA")
    print(f"{'='*50}")
    print(f"✅ Empleados nuevos creados: {empleados_creados}")
    print(f"🔄 Empleados actualizados: {empleados_actualizados}")
    print(f"📝 Total procesados: {empleados_creados + empleados_actualizados}")
    
    if errores:
        print(f"\n❌ Errores encontrados ({len(errores)}):")
        for error in errores:
            print(f"   - {error}")
    
    # Mostrar estadísticas finales
    total_users = User.objects.count()
    total_empleados = Empleado.objects.count()
    managers = Empleado.objects.filter(user__is_staff=True, es_rrhh=False).count()
    rrhh = Empleado.objects.filter(es_rrhh=True).count()
    
    print(f"\n📈 ESTADÍSTICAS DEL SISTEMA:")
    print(f"👥 Total usuarios Django: {total_users}")
    print(f"👨‍💼 Total empleados: {total_empleados}")
    print(f"👨‍💼 Managers: {managers}")
    print(f"🏢 Personal RRHH: {rrhh}")
    
    print(f"\n🔑 CREDENCIALES DE ACCESO:")
    print(f"Contraseña para todos: Agrovet2025")
    print(f"Formato username: nombre.apellido (sin tildes)")
    
    return True

if __name__ == '__main__':
    print("🚀 INICIANDO CARGA DE EMPLEADOS DESDE CSV")
    print("=" * 50)
    
    success = cargar_empleados_desde_csv()
    
    if success:
        print(f"\n✅ CARGA COMPLETADA EXITOSAMENTE")
    else:
        print(f"\n❌ CARGA FALLÓ")
        sys.exit(1)
