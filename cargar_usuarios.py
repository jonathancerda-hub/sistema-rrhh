#!/usr/bin/env python
"""
Script para cargar usuarios desde CSV en la aplicación de RRHH
Uso: python cargar_usuarios.py
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nucleo_rrhh.settings')
django.setup()

from django.core.management import execute_from_command_line

def main():
    print("🚀 CARGADOR DE USUARIOS DESDE CSV")
    print("=" * 50)
    
    # Ruta al archivo CSV
    archivo_csv = input("📁 Ingresa la ruta completa al archivo CSV: ").strip()
    
    if not archivo_csv:
        print("❌ Debes proporcionar la ruta al archivo CSV")
        return
    
    if not os.path.exists(archivo_csv):
        print(f"❌ El archivo {archivo_csv} no existe")
        return
    
    # Preguntar si sobrescribir
    sobrescribir = input("🔄 ¿Sobrescribir usuarios existentes? (s/N): ").strip().lower()
    sobrescribir_flag = sobrescribir in ['s', 'si', 'sí', 'y', 'yes']
    
    # Construir comando
    cmd = ['manage.py', 'cargar_usuarios_csv', '--archivo', archivo_csv]
    if sobrescribir_flag:
        cmd.append('--sobrescribir')
    
    print(f"\n🔧 Ejecutando: python {' '.join(cmd)}")
    print("=" * 50)
    
    # Ejecutar comando
    execute_from_command_line(cmd)

if __name__ == '__main__':
    main()
