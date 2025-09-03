#!/usr/bin/env python
import os
import sys
import django
import csv
import unicodedata
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nucleo_rrhh.settings')
django.setup()

from django.contrib.auth.models import User
from empleados.models import Empleado

def normalizar_texto(texto):
    """Normalizar texto removiendo tildes y caracteres especiales"""
    texto_normalizado = unicodedata.normalize('NFD', texto)
    return ''.join(c for c in texto_normalizado if unicodedata.category(c) != 'Mn')

def generar_username(nombre, apellido):
    """Generar username normalizado"""
    nombre_clean = normalizar_texto(nombre).lower()
    apellido_clean = normalizar_texto(apellido).lower()
    
    # Limpiar caracteres especiales
    nombre_clean = ''.join(c for c in nombre_clean if c.isalnum())
    apellido_clean = ''.join(c for c in apellido_clean if c.isalnum())
    
    return f"{nombre_clean}.{apellido_clean}"

def mapear_jerarquia(puesto):
    """Mapear puesto a jerarquía"""
    puesto_lower = puesto.lower()
    
    if 'director' in puesto_lower:
        return 'director'
    elif 'gerente' in puesto_lower:
        return 'gerente'
    elif 'jefe' in puesto_lower:
        return 'jefe'
    elif 'supervisor' in puesto_lower:
        return 'supervisor'
    elif 'coordinador' in puesto_lower:
        return 'coordinador'
    elif 'asistente' in puesto_lower:
        return 'asistente'
    elif 'practicante' in puesto_lower:
        return 'auxiliar'
    else:
        return 'asistente'

def mapear_gerencia(gerencia):
    """Mapear gerencia a opciones válidas"""
    gerencia_lower = gerencia.lower()
    
    if 'finanzas' in gerencia_lower or 'ti' in gerencia_lower or 'tecnologia' in gerencia_lower:
        return 'gerencia_administracion_finanzas'
    elif 'rrhh' in gerencia_lower or 'recursos humanos' in gerencia_lower:
        return 'gerencia_desarrollo_organizacional'
    elif 'comercial' in gerencia_lower or 'ventas' in gerencia_lower:
        return 'gerencia_comercial'
    elif 'operaciones' in gerencia_lower:
        return 'gerencia_operaciones'
    else:
        return 'gerencia_administracion_finanzas'

def cargar_usuarios():
    """Cargar usuarios de AgroVet Market"""
    archivo_csv = 'empleados_agrovet_organigrama.csv'
    
    print(f"🚀 Iniciando carga de empleados AgroVet Market...")
    print(f"📁 Archivo: {archivo_csv}")
    
    if not os.path.exists(archivo_csv):
        print(f"❌ Error: No se encuentra el archivo {archivo_csv}")
        return
    
    usuarios_creados = 0
    usuarios_actualizados = 0
    errores = 0
    
    try:
        with open(archivo_csv, 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            
            for row_num, row in enumerate(reader, 1):
                try:
                    # Campos del CSV
                    nombre = row.get('nombre', '').strip()
                    apellido = row.get('apellido', '').strip()
                    dni = row.get('dni', '').strip()
                    email = row.get('email', '').strip()
                    puesto = row.get('puesto', '').strip()
                    area = row.get('area', 'Sin asignar').strip()
                    gerencia = row.get('gerencia', '').strip()
                    
                    if not all([nombre, apellido, email]):
                        print(f"⚠️  Fila {row_num}: Faltan campos obligatorios")
                        errores += 1
                        continue
                    
                    # Generar username
                    username = generar_username(nombre, apellido)
                    
                    # Crear o actualizar usuario
                    user, created = User.objects.get_or_create(
                        username=username,
                        defaults={
                            'email': email,
                            'first_name': nombre,
                            'last_name': apellido,
                            'is_active': True,
                        }
                    )
                    
                    # Establecer contraseña por defecto
                    user.set_password('agrovet2025')
                    user.save()
                    
                    # Crear o actualizar empleado
                    empleado, emp_created = Empleado.objects.get_or_create(
                        user=user,
                        defaults={
                            'nombre': nombre,
                            'apellido': apellido,
                            'dni': dni,
                            'email': email,
                            'puesto': puesto,
                            'fecha_contratacion': datetime.now().date(),
                            'dias_vacaciones_disponibles': 20,
                            'es_rrhh': False,
                            'area': area,
                            'gerencia': mapear_gerencia(gerencia),
                            'jerarquia': mapear_jerarquia(puesto),
                        }
                    )
                    
                    if created or emp_created:
                        usuarios_creados += 1
                        status = 'CREADO'
                    else:
                        usuarios_actualizados += 1
                        status = 'ACTUALIZADO'
                    
                    print(f"✅ {username} - {nombre} {apellido} ({status})")
                    
                except Exception as e:
                    errores += 1
                    print(f"❌ Fila {row_num}: Error - {str(e)}")
    
    except Exception as e:
        print(f"❌ Error al leer archivo: {str(e)}")
        return
    
    print(f"\n📊 RESUMEN:")
    print(f"✅ Usuarios creados: {usuarios_creados}")
    print(f"🔄 Usuarios actualizados: {usuarios_actualizados}")
    print(f"❌ Errores: {errores}")
    
    # Verificar estado final
    total_usuarios = User.objects.count()
    total_empleados = Empleado.objects.count()
    print(f"\n🎯 ESTADO ACTUAL:")
    print(f"👥 Total usuarios en sistema: {total_usuarios}")
    print(f"🏢 Total empleados: {total_empleados}")
    
    # Mostrar algunos usuarios creados
    print(f"\n👨‍💼 ÚLTIMOS USUARIOS:")
    for user in User.objects.order_by('-id')[:10]:
        print(f"- {user.username} ({user.first_name} {user.last_name})")

if __name__ == '__main__':
    cargar_usuarios()
