#!/usr/bin/env python
"""
Script para verificar y cargar usuarios de AgroVet
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nucleo_rrhh.settings_hibrido')
django.setup()

from django.contrib.auth.models import User
from empleados.models import Empleado
import csv
import unicodedata
from datetime import datetime

def normalizar_texto(texto):
    """Normalizar texto removiendo tildes y caracteres especiales"""
    if not texto:
        return ""
    
    # Remover tildes y caracteres especiales
    texto_normalizado = unicodedata.normalize('NFD', texto)
    texto_normalizado = ''.join(c for c in texto_normalizado if unicodedata.category(c) != 'Mn')
    
    return texto_normalizado

def generar_username(nombre, apellido):
    """Generar username en formato nombre.apellido sin tildes"""
    nombre_clean = normalizar_texto(nombre).lower().strip()
    apellido_clean = normalizar_texto(apellido).lower().strip()
    
    # Limpiar espacios y caracteres especiales
    nombre_clean = ''.join(c for c in nombre_clean if c.isalnum())
    apellido_clean = ''.join(c for c in apellido_clean if c.isalnum())
    
    username = f"{nombre_clean}.{apellido_clean}"
    
    # Si el username es muy largo, truncar
    if len(username) > 30:
        username = username[:30]
    
    return username

def mapear_jerarquia(puesto, es_manager):
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

def parsear_fecha(fecha_str):
    """Convertir fecha DD-MM-YYYY a formato datetime"""
    try:
        return datetime.strptime(fecha_str, '%d-%m-%Y').date()
    except:
        return datetime(2001, 10, 2).date()  # Fecha por defecto

def main():
    print("🔍 VERIFICANDO ESTADO ACTUAL...")
    print(f"👥 Total usuarios en la BD: {User.objects.count()}")
    print(f"👤 Total empleados en la BD: {Empleado.objects.count()}")
    
    # Mostrar algunos usuarios existentes
    if User.objects.exists():
        print("\n📋 Usuarios existentes:")
        for user in User.objects.all()[:5]:
            print(f"   • {user.username} ({user.first_name} {user.last_name})")
        if User.objects.count() > 5:
            print(f"   ... y {User.objects.count() - 5} más")
    
    print("\n" + "="*60)
    print("🏢 CARGANDO ORGANIGRAMA AGROVET...")
    
    archivo = 'organigrama_agrovet.csv'
    
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            creados = 0
            actualizados = 0
            errores = 0
            
            for row in reader:
                try:
                    # Generar datos
                    username = generar_username(row['nombre'], row['apellido'])
                    jerarquia = mapear_jerarquia(row['puesto'], row['es_manager'])
                    fecha_contratacion = parsear_fecha(row['fecha_contratacion'])
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
                        print(f'✅ {username:<25} | {row["nombre"]} {row["apellido"]}{manager_text}{rrhh_text}')
                    else:
                        actualizados += 1
                        print(f'ℹ️ {username:<25} | {row["nombre"]} {row["apellido"]} (actualizado)')
                    
                except Exception as e:
                    errores += 1
                    print(f'❌ Error con {row.get("nombre", "usuario")}: {e}')
            
            # Resumen
            print("="*60)
            print(f'🎉 ¡Carga completada!')
            print(f'✅ Usuarios nuevos: {creados}')
            print(f'ℹ️ Usuarios actualizados: {actualizados}')
            print(f'❌ Errores: {errores}')
            print(f'👥 Total usuarios ahora: {User.objects.count()}')
            
            # Información de acceso
            print('\n🔑 INFORMACIÓN DE ACCESO:')
            print('👤 Usuarios: nombre.apellido (sin tildes)')
            print('🔐 Contraseña: agrovet2025')
            print('\n📋 Ejemplos de usuarios creados:')
            
            # Mostrar algunos ejemplos
            ejemplos = [
                ('jose.garcia', 'José García - Director'),
                ('ena.fernandez', 'Ena Fernández - Gerente'),
                ('teodoro.balarezo', 'Teodoro Balarezo - Jefe'),
            ]
            
            for username, descripcion in ejemplos:
                print(f'   • {username} / agrovet2025 ({descripcion})')
            
            print('\n🌐 URLs útiles:')
            print('   • http://127.0.0.1:8000/agrovet/ (Página AgroVet)')
            print('   • http://127.0.0.1:8000/usuarios/ (Ver todos los usuarios)')
            print('   • http://127.0.0.1:8000/login-debug/ (Probar login)')
            
    except FileNotFoundError:
        print(f'❌ Archivo no encontrado: {archivo}')
        print('💡 Asegúrate de que el archivo esté en el directorio del proyecto')
    except Exception as e:
        print(f'❌ Error al procesar archivo: {e}')

if __name__ == '__main__':
    main()
