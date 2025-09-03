"""
Script de emergencia para crear usuario funcional
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nucleo_rrhh.settings')
django.setup()

from django.contrib.auth.models import User
from empleados.models import Empleado

def crear_usuario_emergencia():
    print("🚨 Creando usuario de emergencia...")
    
    # Eliminar usuario existente si hay problemas
    try:
        User.objects.filter(username='admin').delete()
        print("🗑️ Usuario admin anterior eliminado")
    except:
        pass
    
    # Crear superusuario desde cero
    try:
        admin_user = User.objects.create_user(
            username='admin',
            email='admin@empresa.com',
            password='123456',
            first_name='Super',
            last_name='Admin',
            is_staff=True,
            is_superuser=True,
            is_active=True
        )
        admin_user.set_password('123456')
        admin_user.save()
        print("✅ Superusuario creado:")
        print("   Usuario: admin")
        print("   Contraseña: 123456")
    except Exception as e:
        print(f"❌ Error creando superusuario: {e}")
    
    # Crear usuario RRHH simple
    try:
        User.objects.filter(username='rrhh').delete()
    except:
        pass
    
    try:
        rrhh_user = User.objects.create_user(
            username='rrhh',
            email='rrhh@empresa.com',
            password='123456',
            first_name='RRHH',
            last_name='Usuario',
            is_active=True
        )
        rrhh_user.set_password('123456')
        rrhh_user.save()
        
        # Crear empleado RRHH
        empleado_rrhh = Empleado.objects.create(
            user=rrhh_user,
            nombre='RRHH',
            apellido='Usuario',
            dni='99999999',
            email='rrhh@empresa.com',
            puesto='Administrador RRHH',
            fecha_contratacion='2020-01-01',
            es_rrhh=True,
            area='Recursos Humanos',
            gerencia='gerencia_desarrollo_organizacional',
            jerarquia='gerente'
        )
        
        print("✅ Usuario RRHH creado:")
        print("   Usuario: rrhh")
        print("   Contraseña: 123456")
        
    except Exception as e:
        print(f"❌ Error creando usuario RRHH: {e}")
    
    # Crear usuario empleado simple
    try:
        User.objects.filter(username='empleado').delete()
    except:
        pass
    
    try:
        emp_user = User.objects.create_user(
            username='empleado',
            email='empleado@empresa.com',
            password='123456',
            first_name='Juan',
            last_name='Empleado',
            is_active=True
        )
        emp_user.set_password('123456')
        emp_user.save()
        
        # Crear empleado regular
        empleado_regular = Empleado.objects.create(
            user=emp_user,
            nombre='Juan',
            apellido='Empleado',
            dni='88888888',
            email='empleado@empresa.com',
            puesto='Empleado Regular',
            fecha_contratacion='2022-01-01',
            es_rrhh=False,
            area='Ventas',
            gerencia='gerencia_comercial_local',
            jerarquia='asistente'
        )
        
        print("✅ Usuario empleado creado:")
        print("   Usuario: empleado")
        print("   Contraseña: 123456")
        
    except Exception as e:
        print(f"❌ Error creando empleado: {e}")

    print("\n🎯 USUARIOS LISTOS PARA PROBAR:")
    print("🌐 URL: http://127.0.0.1:8000/admin/")
    print("   admin / 123456 (Superusuario)")
    print("\n🌐 URL: http://127.0.0.1:8000/login/")
    print("   rrhh / 123456 (RRHH)")
    print("   empleado / 123456 (Empleado)")

if __name__ == "__main__":
    crear_usuario_emergencia()
