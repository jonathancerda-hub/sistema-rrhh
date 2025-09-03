#!/usr/bin/env python
"""
Script para verificar el estado del proyecto RRHH
"""
import os
import sys
import django

# Añadir el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nucleo_rrhh.settings_local')
django.setup()

from django.db import connection
from django.contrib.auth.models import User
from empleados.models import Empleado

def verificar_estado():
    print("🔍 Verificando estado del proyecto RRHH...")
    
    # 1. Verificar conexión a base de datos
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✅ Conexión a base de datos: OK")
        
        # Obtener info de la base de datos
        db_settings = connection.settings_dict
        engine = db_settings['ENGINE']
        if 'postgresql' in engine:
            print(f"🌐 Base de datos: PostgreSQL ({db_settings['HOST']})")
        elif 'sqlite' in engine:
            print(f"🗄️ Base de datos: SQLite ({db_settings['NAME']})")
        else:
            print(f"🔧 Base de datos: {engine}")
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False
    
    # 2. Verificar usuarios
    try:
        user_count = User.objects.count()
        print(f"👥 Usuarios en sistema: {user_count}")
        
        if user_count > 0:
            users = User.objects.all()[:5]  # Mostrar los primeros 5
            for user in users:
                print(f"   • {user.username} ({user.first_name} {user.last_name})")
        
    except Exception as e:
        print(f"❌ Error al consultar usuarios: {e}")
    
    # 3. Verificar empleados
    try:
        empleado_count = Empleado.objects.count()
        print(f"👔 Empleados en sistema: {empleado_count}")
        
        if empleado_count > 0:
            empleados = Empleado.objects.all()[:5]  # Mostrar los primeros 5
            for emp in empleados:
                print(f"   • {emp.nombre} {emp.apellido} - {emp.puesto}")
        
    except Exception as e:
        print(f"❌ Error al consultar empleados: {e}")
    
    # 4. Verificar archivos importantes
    archivos_importantes = [
        'manage.py',
        'nucleo_rrhh/settings.py',
        'nucleo_rrhh/settings_local.py',
        'nucleo_rrhh/settings_production.py',
        'empleados/models.py',
    ]
    
    print("\n📁 Verificando archivos importantes:")
    for archivo in archivos_importantes:
        if os.path.exists(archivo):
            print(f"   ✅ {archivo}")
        else:
            print(f"   ❌ {archivo} - NO ENCONTRADO")
    
    print("\n🎉 Verificación completada!")
    return True

if __name__ == "__main__":
    verificar_estado()
