#!/usr/bin/env python
"""
Script para forzar la migración de sesiones en producción
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nucleo_rrhh.settings_production_final')
django.setup()

from django.core.management import execute_from_command_line
from django.db import connection
from django.contrib.sessions.models import Session

def verificar_y_migrar():
    """Verificar y aplicar migraciones necesarias"""
    
    print("🔍 Verificando estado de la base de datos...")
    
    try:
        # Intentar acceder a la tabla de sesiones
        count = Session.objects.count()
        print(f"✅ Tabla django_session existe con {count} registros")
        return True
        
    except Exception as e:
        print(f"❌ Error con tabla django_session: {e}")
        print("🔧 Aplicando migraciones...")
        
        try:
            # Aplicar migraciones de sessions específicamente
            execute_from_command_line(['manage.py', 'migrate', 'sessions', '--verbosity=2'])
            print("✅ Migraciones de sessions aplicadas")
            
            # Aplicar todas las migraciones
            execute_from_command_line(['manage.py', 'migrate', '--verbosity=2'])
            print("✅ Todas las migraciones aplicadas")
            
            return True
            
        except Exception as migrate_error:
            print(f"❌ Error aplicando migraciones: {migrate_error}")
            return False

def crear_superusuario_si_no_existe():
    """Crear superusuario admin si no existe"""
    from django.contrib.auth.models import User
    
    try:
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@empresa.com', 'admin123')
            print("✅ Superusuario admin creado")
        else:
            print("ℹ️ Superusuario admin ya existe")
            
        print(f"👥 Total usuarios: {User.objects.count()}")
        
    except Exception as e:
        print(f"❌ Error creando superusuario: {e}")

if __name__ == '__main__':
    print("🚀 SCRIPT DE MIGRACIÓN PARA PRODUCCIÓN")
    print("=" * 50)
    
    # Verificar configuración
    from django.conf import settings
    print(f"📍 Settings module: {settings.SETTINGS_MODULE}")
    print(f"🗄️ Base de datos: {settings.DATABASES['default']['ENGINE']}")
    
    # Aplicar migraciones
    if verificar_y_migrar():
        print("\n👤 Configurando usuario administrador...")
        crear_superusuario_si_no_existe()
        
        print("\n✅ CONFIGURACIÓN COMPLETADA")
        print("🌐 El sistema está listo para usar")
    else:
        print("\n❌ CONFIGURACIÓN FALLÓ")
        sys.exit(1)
