#!/usr/bin/env python
# Script para cargar empleados de AgroVet Market

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nucleo_rrhh.settings')
django.setup()

from django.contrib.auth.models import User
from empleados.models import Empleado
from datetime import datetime
import unicodedata

def normalizar_texto(texto):
    """Normalizar texto eliminando tildes y caracteres especiales"""
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

# Lista de empleados AgroVet Market
empleados_agrovet = [
    {"nombre": "María José", "apellido": "González", "email": "maria.gonzalez@agrovetmarket.com", "dni": "12345678", "puesto": "Gerente RRHH", "area": "Recursos Humanos", "gerencia": "gerencia_desarrollo_organizacional"},
    {"nombre": "Juan Carlos", "apellido": "Pérez", "email": "juan.perez@agrovetmarket.com", "dni": "23456789", "puesto": "Asistente Comercial", "area": "Ventas", "gerencia": "gerencia_comercial"},
    {"nombre": "Ana Sofía", "apellido": "Rodríguez", "email": "ana.rodriguez@agrovetmarket.com", "dni": "34567890", "puesto": "Coordinadora de Finanzas", "area": "Finanzas", "gerencia": "gerencia_administracion_finanzas"},
    {"nombre": "Luis Fernando", "apellido": "Martínez", "email": "luis.martinez@agrovetmarket.com", "dni": "45678901", "puesto": "Supervisor de Operaciones", "area": "Operaciones", "gerencia": "gerencia_operaciones"},
    {"nombre": "Carmen Elena", "apellido": "López", "email": "carmen.lopez@agrovetmarket.com", "dni": "56789012", "puesto": "Asistente de RRHH", "area": "Recursos Humanos", "gerencia": "gerencia_desarrollo_organizacional"},
    {"nombre": "Miguel Ángel", "apellido": "García", "email": "miguel.garcia@agrovetmarket.com", "dni": "67890123", "puesto": "Jefe de Ventas", "area": "Ventas", "gerencia": "gerencia_comercial"},
    {"nombre": "Patricia Isabel", "apellido": "Hernández", "email": "patricia.hernandez@agrovetmarket.com", "dni": "78901234", "puesto": "Analista Financiero", "area": "Finanzas", "gerencia": "gerencia_administracion_finanzas"},
    {"nombre": "Roberto Carlos", "apellido": "Jiménez", "email": "roberto.jimenez@agrovetmarket.com", "dni": "89012345", "puesto": "Operario Senior", "area": "Operaciones", "gerencia": "gerencia_operaciones"},
    {"nombre": "Diana Marcela", "apellido": "Torres", "email": "diana.torres@agrovetmarket.com", "dni": "90123456", "puesto": "Especialista en Selección", "area": "Recursos Humanos", "gerencia": "gerencia_desarrollo_organizacional"},
    {"nombre": "Andrés Felipe", "apellido": "Vargas", "email": "andres.vargas@agrovetmarket.com", "dni": "01234567", "puesto": "Ejecutivo Comercial", "area": "Ventas", "gerencia": "gerencia_comercial"},
    {"nombre": "Sandra Milena", "apellido": "Ruiz", "email": "sandra.ruiz@agrovetmarket.com", "dni": "12340567", "puesto": "Contadora", "area": "Finanzas", "gerencia": "gerencia_administracion_finanzas"},
    {"nombre": "Carlos Eduardo", "apellido": "Morales", "email": "carlos.morales@agrovetmarket.com", "dni": "23450678", "puesto": "Coordinador de Logística", "area": "Operaciones", "gerencia": "gerencia_operaciones"},
    {"nombre": "Liliana Patricia", "apellido": "Castro", "email": "liliana.castro@agrovetmarket.com", "dni": "34560789", "puesto": "Asistente Administrativa", "area": "Administración", "gerencia": "gerencia_administracion_finanzas"},
    {"nombre": "Fernando José", "apellido": "Ramírez", "email": "fernando.ramirez@agrovetmarket.com", "dni": "45670890", "puesto": "Supervisor de Ventas", "area": "Ventas", "gerencia": "gerencia_comercial"},
    {"nombre": "Gloria Inés", "apellido": "Mendoza", "email": "gloria.mendoza@agrovetmarket.com", "dni": "56780901", "puesto": "Auxiliar Contable", "area": "Finanzas", "gerencia": "gerencia_administracion_finanzas"},
    {"nombre": "Javier Augusto", "apellido": "Ortega", "email": "javier.ortega@agrovetmarket.com", "dni": "67890012", "puesto": "Operario de Almacén", "area": "Operaciones", "gerencia": "gerencia_operaciones"},
    {"nombre": "Mónica Andrea", "apellido": "Silva", "email": "monica.silva@agrovetmarket.com", "dni": "78900123", "puesto": "Practicante RRHH", "area": "Recursos Humanos", "gerencia": "gerencia_desarrollo_organizacional"},
    {"nombre": "Oscar David", "apellido": "Gutiérrez", "email": "oscar.gutierrez@agrovetmarket.com", "dni": "89010234", "puesto": "Asesor Comercial", "area": "Ventas", "gerencia": "gerencia_comercial"},
    {"nombre": "Beatriz Elena", "apellido": "Vásquez", "email": "beatriz.vasquez@agrovetmarket.com", "dni": "90120345", "puesto": "Directora Administrativa", "area": "Administración", "gerencia": "gerencia_administracion_finanzas"}
]

def cargar_empleados():
    """Cargar empleados de AgroVet Market"""
    print("🚀 Iniciando carga de empleados AgroVet Market...")
    print("=" * 50)
    
    usuarios_creados = 0
    usuarios_actualizados = 0
    errores = 0
    
    for empleado_data in empleados_agrovet:
        try:
            nombre = empleado_data['nombre']
            apellido = empleado_data['apellido']
            email = empleado_data['email']
            dni = empleado_data['dni']
            puesto = empleado_data['puesto']
            area = empleado_data['area']
            gerencia = empleado_data['gerencia']
            
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
                    'es_rrhh': 'rrhh' in puesto.lower(),
                    'area': area,
                    'gerencia': gerencia,
                    'jerarquia': mapear_jerarquia(puesto),
                }
            )
            
            if created or emp_created:
                usuarios_creados += 1
                status = '✅ CREADO'
            else:
                usuarios_actualizados += 1
                status = '🔄 ACTUALIZADO'
            
            print(f"{status} - {username} | {nombre} {apellido} | {puesto}")
            
        except Exception as e:
            errores += 1
            print(f"❌ ERROR - {empleado_data.get('nombre', 'N/A')} {empleado_data.get('apellido', 'N/A')}: {str(e)}")
    
    print("=" * 50)
    print(f"📊 RESUMEN DE CARGA:")
    print(f"   ✅ Usuarios creados: {usuarios_creados}")
    print(f"   🔄 Usuarios actualizados: {usuarios_actualizados}")
    print(f"   ❌ Errores: {errores}")
    print(f"   📊 Total usuarios en DB: {User.objects.count()}")
    print(f"   👥 Total empleados en DB: {Empleado.objects.count()}")
    print("=" * 50)
    print("🎉 ¡Carga completada exitosamente!")

if __name__ == "__main__":
    cargar_empleados()
