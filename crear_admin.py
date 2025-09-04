#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nucleo_rrhh.settings')
django.setup()

from django.contrib.auth.models import User

def crear_superusuario():
    """Crear superusuario programáticamente"""
    
    username = 'admin'
    email = 'admin@empresa.com'
    password = 'admin123'
    
    try:
        # Verificar si el usuario ya existe
        if User.objects.filter(username=username).exists():
            print(f"El usuario '{username}' ya existe.")
            user = User.objects.get(username=username)
        else:
            # Crear el superusuario
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            print(f"Superusuario '{username}' creado exitosamente.")
        
        # Mostrar información del usuario
        print(f"Username: {user.username}")
        print(f"Email: {user.email}")
        print(f"Es superusuario: {user.is_superuser}")
        print(f"Es staff: {user.is_staff}")
        print(f"Activo: {user.is_active}")
        
        return True
        
    except Exception as e:
        print(f"Error al crear superusuario: {e}")
        return False

if __name__ == '__main__':
    success = crear_superusuario()
    if success:
        print("\n✅ Superusuario creado correctamente")
        print("Puedes ingresar con:")
        print("Usuario: admin")
        print("Contraseña: admin123")
    else:
        print("\n❌ Error al crear superusuario")
        sys.exit(1)
