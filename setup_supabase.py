#!/usr/bin/env python
"""
Script para configurar Supabase después del deploy exitoso
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nucleo_rrhh.settings_production')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def verificar_conexion_supabase():
    """Verificar que podemos conectarnos a Supabase"""
    try:
        django.setup()
        from django.db import connection
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"✅ Conexión exitosa a PostgreSQL: {version[0]}")
            return True
    except Exception as e:
        print(f"❌ Error conectando a Supabase: {e}")
        return False

def crear_tablas():
    """Ejecutar migraciones en Supabase"""
    try:
        from django.core.management import execute_from_command_line
        
        print("🔨 Creando tablas en Supabase...")
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Tablas creadas exitosamente")
        return True
    except Exception as e:
        print(f"❌ Error creando tablas: {e}")
        return False

def cargar_usuarios():
    """Cargar usuarios de prueba"""
    try:
        from django.core.management import execute_from_command_line
        
        print("👥 Cargando usuarios de prueba...")
        execute_from_command_line(['manage.py', 'crear_usuarios_prueba'])
        print("✅ Usuarios cargados exitosamente")
        return True
    except Exception as e:
        print(f"❌ Error cargando usuarios: {e}")
        return False

def main():
    print("🚀 Configurando Supabase...")
    
    # Verificar conexión
    if not verificar_conexion_supabase():
        print("❌ No se pudo conectar a Supabase")
        return 1
    
    # Crear tablas
    if not crear_tablas():
        print("❌ No se pudieron crear las tablas")
        return 1
    
    # Cargar usuarios
    if not cargar_usuarios():
        print("⚠️ Error cargando usuarios, pero el setup básico está completo")
    
    print("🎉 Setup de Supabase completado exitosamente!")
    print("💡 Puedes acceder a la aplicación y usar las herramientas de setup web si es necesario")
    return 0

if __name__ == '__main__':
    sys.exit(main())
