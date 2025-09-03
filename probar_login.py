"""
Script simple para probar login de usuarios
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nucleo_rrhh.settings')
django.setup()

from django.contrib.auth import authenticate
from django.contrib.auth.models import User

def probar_usuarios():
    print("🔑 Probando autenticación de usuarios...")
    
    usuarios_probar = [
        ('admin', 'admin123'),
        ('admin_rrhh', 'admin123'),
        ('manager_ventas', 'manager123'),
        ('ana_garcia', 'empleado123'),
    ]
    
    for username, password in usuarios_probar:
        print(f"\n👤 Probando: {username}")
        
        # Verificar si el usuario existe
        try:
            user = User.objects.get(username=username)
            print(f"   ✅ Usuario existe: {user.first_name} {user.last_name}")
            
            # Resetear contraseña para asegurar que esté correcta
            user.set_password(password)
            user.save()
            print(f"   🔄 Contraseña reseteada")
            
            # Probar autenticación
            auth_user = authenticate(username=username, password=password)
            if auth_user:
                print(f"   ✅ Autenticación exitosa!")
                if hasattr(auth_user, 'empleado'):
                    empleado = auth_user.empleado
                    print(f"   👔 Empleado: {empleado.nombre} {empleado.apellido}")
                    if empleado.es_rrhh:
                        print(f"   🔴 ACCESO RRHH")
                    elif empleado.es_manager:
                        print(f"   🔵 MANAGER")
                    else:
                        print(f"   👤 EMPLEADO")
            else:
                print(f"   ❌ Autenticación fallida")
                
        except User.DoesNotExist:
            print(f"   ❌ Usuario no existe")
            
            # Crear el usuario si no existe
            if username == 'admin':
                User.objects.create_superuser(
                    username='admin',
                    email='admin@empresa.com',
                    password='admin123'
                )
                print(f"   ✅ Usuario admin creado")

if __name__ == "__main__":
    probar_usuarios()
    print("\n🎯 Prueba completada!")
    print("\n📝 Credenciales verificadas:")
    print("   • admin / admin123 (Superusuario)")
    print("   • admin_rrhh / admin123 (RRHH)")
    print("   • manager_ventas / manager123 (Manager)")
    print("   • ana_garcia / empleado123 (Empleado)")
    print("\n🌐 Accede a: http://127.0.0.1:8000/")
