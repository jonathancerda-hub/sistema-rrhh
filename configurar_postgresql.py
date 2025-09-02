#!/usr/bin/env python3
"""
Script para configurar PostgreSQL en Render.com

INSTRUCCIONES:
1. Ve a https://dashboard.render.com
2. Inicia sesión con tu cuenta
3. Ve a "New +" -> "PostgreSQL"
4. Configura la base de datos:
   - Name: sistema-rrhh-db
   - Database: sistema_rrhh
   - User: sistema_rrhh_user
   - Region: Oregon (US West) - es más barato
   - PostgreSQL Version: 15
   - Plan: Free (para desarrollo)

5. Una vez creada, copia la "External Database URL" 
6. Ve a tu Web Service "sistema-rrhh"
7. Ve a "Environment"
8. Agrega la variable de entorno:
   - Key: DATABASE_URL
   - Value: [la URL que copiaste]

9. Ejecuta este script para generar las migraciones necesarias
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nucleo_rrhh.settings_production')
django.setup()

from django.core.management import execute_from_command_line
from django.contrib.auth.models import User
from empleados.models import Empleado
import secrets
import string

def generar_password_seguro():
    """Genera una contraseña segura"""
    caracteres = string.ascii_letters + string.digits + "!@#$%"
    password = ''.join(secrets.choice(caracteres) for _ in range(12))
    return password

def main():
    print("🔧 CONFIGURACIÓN DE POSTGRESQL PARA RENDER.COM")
    print("=" * 50)
    
    print("\n📋 PASOS A SEGUIR:")
    print("1. ✅ Crear base de datos PostgreSQL en Render.com")
    print("2. ✅ Configurar variable DATABASE_URL")
    print("3. 🔄 Ejecutar migraciones")
    print("4. 👤 Crear superusuario")
    
    response = input("\n¿Ya configuraste la base de datos PostgreSQL en Render.com? (s/n): ")
    
    if response.lower() != 's':
        print("\n⚠️  CONFIGURACIÓN PENDIENTE")
        print("Ve a https://dashboard.render.com y sigue las instrucciones del comentario en este script.")
        print("Luego ejecuta este script nuevamente.")
        return
    
    print("\n🔄 Ejecutando migraciones...")
    try:
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Migraciones ejecutadas correctamente")
    except Exception as e:
        print(f"❌ Error en migraciones: {e}")
        return
    
    print("\n👤 Creando superusuario...")
    
    # Verificar si ya existe un superusuario
    if User.objects.filter(is_superuser=True).exists():
        print("⚠️  Ya existe al menos un superusuario")
        response = input("¿Crear otro superusuario? (s/n): ")
        if response.lower() != 's':
            print("✅ Configuración completada")
            return
    
    # Datos del superusuario
    username = input("Username del superusuario (ej: admin): ") or "admin"
    email = input("Email del superusuario: ")
    
    if not email:
        print("❌ El email es obligatorio")
        return
    
    # Generar contraseña segura o permitir al usuario ingresarla
    response = input("¿Generar contraseña automáticamente? (s/n): ")
    
    if response.lower() == 's':
        password = generar_password_seguro()
        print(f"🔑 Contraseña generada: {password}")
    else:
        password = input("Ingresa la contraseña: ")
        if len(password) < 8:
            print("❌ La contraseña debe tener al menos 8 caracteres")
            return
    
    try:
        # Crear superusuario
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        
        # Crear empleado asociado
        empleado = Empleado.objects.create(
            user=user,
            nombre=username.title(),
            apellido="Administrador",
            dni="00000000",  # DNI temporal
            email=email,
            puesto="Administrador del Sistema",
            area="Administración",
            es_rrhh=True,
            fecha_contratacion="2024-01-01"
        )
        
        print("✅ Superusuario creado correctamente")
        print(f"👤 Usuario: {username}")
        print(f"📧 Email: {email}")
        print(f"🔑 Contraseña: {password}")
        print(f"🆔 ID Empleado: {empleado.id}")
        
        print("\n🚀 CONFIGURACIÓN COMPLETADA")
        print("Ahora puedes acceder a tu sistema en producción:")
        print("1. Ve a https://sistema-rrhh.onrender.com/admin/")
        print(f"2. Inicia sesión con {username} / {password}")
        print("3. ¡Tu sistema ya tiene persistencia de datos!")
        
    except Exception as e:
        print(f"❌ Error creando superusuario: {e}")

if __name__ == "__main__":
    main()
