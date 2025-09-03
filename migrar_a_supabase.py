#!/usr/bin/env python
"""
Script simplificado para migrar de Render PostgreSQL a Supabase
"""

import os
import sys
import django
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nucleo_rrhh.settings')
django.setup()

from django.core.management import execute_from_command_line
from django.contrib.auth.models import User
from empleados.models import Empleado

def main():
    print("🚀 MIGRACIÓN A SUPABASE")
    print("=" * 50)
    
    # Solicitar URL de Supabase
    supabase_url = input("📋 Pega aquí la URL de conexión de Supabase: ").strip()
    
    if not supabase_url:
        print("❌ Debes proporcionar la URL de Supabase")
        return
    
    if not supabase_url.startswith('postgresql://'):
        print("❌ La URL debe empezar con 'postgresql://'")
        return
    
    print("\n🔄 Proceso de migración:")
    print("1. Exportar datos actuales")
    print("2. Configurar Supabase")
    print("3. Crear tablas")
    print("4. Cargar datos")
    
    confirmar = input("\n¿Continuar? (s/N): ").strip().lower()
    if confirmar not in ['s', 'si', 'sí', 'y', 'yes']:
        print("❌ Migración cancelada")
        return
    
    # Mostrar estadísticas actuales
    print(f"\n📊 Datos actuales:")
    try:
        print(f"  - Usuarios: {User.objects.count()}")
        print(f"  - Empleados: {Empleado.objects.count()}")
    except:
        print("  - No se pudieron obtener estadísticas")
    
    # Exportar datos
    print("\n📤 Exportando datos...")
    execute_from_command_line(['manage.py', 'migrar_supabase', '--exportar-datos'])
    
    print(f"\n🔧 Configuración para Render:")
    print(f"Variable: DATABASE_URL")
    print(f"Valor: {supabase_url}")
    print("\n📋 Instrucciones:")
    print("1. Ve al dashboard de Render")
    print("2. Busca la sección Environment Variables")
    print("3. Actualiza DATABASE_URL con el valor de arriba")
    print("4. Haz deploy")
    print("5. Visita /setup/organigrama/ para cargar usuarios")

if __name__ == '__main__':
    main()
