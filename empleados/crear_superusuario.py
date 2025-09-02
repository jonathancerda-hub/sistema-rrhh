from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.models import User
from empleados.models import Empleado
from django.views.decorators.csrf import csrf_exempt
from datetime import date

@csrf_exempt
def crear_superusuario(request):
    """Crear un superusuario desde cero"""
    if request.method == 'POST':
        try:
            # Crear o actualizar superusuario admin
            admin_user, created = User.objects.get_or_create(
                username='admin',
                defaults={
                    'email': 'admin@empresa.com',
                    'is_staff': True,
                    'is_superuser': True
                }
            )
            
            if created:
                admin_user.set_password('admin123456')
                admin_user.save()
            else:
                admin_user.is_staff = True
                admin_user.is_superuser = True
                admin_user.set_password('admin123456')
                admin_user.save()

            # También actualizar el usuario rrhh
            try:
                rrhh_user = User.objects.get(username='rrhh')
                rrhh_user.is_staff = True
                rrhh_user.is_superuser = True
                rrhh_user.save()
                rrhh_actualizado = True
            except User.DoesNotExist:
                rrhh_actualizado = False

            return HttpResponse(f"""
            <!DOCTYPE html>
            <html>
            <head><title>Superusuario Creado</title></head>
            <body style="font-family: Arial; padding: 20px; background: #f0f8ff;">
                <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <h2 style="color: #28a745;">✅ ¡Superusuario Creado!</h2>
                    
                    <h3>🔑 Credenciales de Administrador:</h3>
                    <div style="background: #e7f3ff; padding: 15px; border-radius: 5px; margin: 15px 0;">
                        <p><strong>Usuario:</strong> admin</p>
                        <p><strong>Contraseña:</strong> admin123456</p>
                        <p><strong>Permisos:</strong> ✅ Superusuario completo</p>
                    </div>
                    
                    <h3>Usuario RRHH:</h3>
                    <div style="background: {'#d4edda' if rrhh_actualizado else '#f8d7da'}; padding: 15px; border-radius: 5px; margin: 15px 0;">
                        <p><strong>Usuario rrhh:</strong> {'✅ Actualizado con permisos de admin' if rrhh_actualizado else '❌ No encontrado'}</p>
                    </div>
                    
                    <p style="background: #fff3cd; padding: 15px; border-radius: 5px; border-left: 4px solid #ffc107;">
                        <strong>¡Ahora puedes acceder al Django Admin!</strong><br>
                        Usa cualquiera de las dos credenciales para acceder.
                    </p>
                    
                    <div style="margin-top: 20px;">
                        <a href="/admin/" style="display: inline-block; padding: 12px 25px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; margin-right: 10px;">
                            🔐 Django Admin
                        </a>
                        <a href="/login/" style="display: inline-block; padding: 12px 25px; background: #28a745; color: white; text-decoration: none; border-radius: 5px;">
                            🏠 Sistema RRHH
                        </a>
                    </div>
                </div>
            </body>
            </html>
            """)

        except Exception as e:
            return HttpResponse(f"""
            <!DOCTYPE html>
            <html>
            <head><title>Error</title></head>
            <body style="font-family: Arial; padding: 20px;">
                <h2 style="color: red;">❌ Error</h2>
                <p>{str(e)}</p>
                <a href="/setup/superuser/">Intentar de nuevo</a>
            </body>
            </html>
            """)

    # GET request
    return HttpResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Crear Superusuario - Sistema RRHH</title>
        <meta charset="utf-8">
    </head>
    <body style="font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5;">
        <div style="max-width: 500px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            <h2>🔐 Crear Superusuario</h2>
            
            <p>Esta acción creará un usuario administrador con acceso completo al Django Admin.</p>
            
            <form method="post" style="margin-top: 20px;">
                <button type="submit" style="padding: 15px 30px; background: #dc3545; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; width: 100%;">
                    🚀 Crear Superusuario "admin"
                </button>
            </form>
            
            <div style="background: #e7f3ff; padding: 15px; border-radius: 5px; margin-top: 20px;">
                <h4>Se creará:</h4>
                <p><strong>Usuario:</strong> admin</p>
                <p><strong>Contraseña:</strong> admin123456</p>
                <p><strong>Permisos:</strong> Acceso completo al Django Admin</p>
            </div>
        </div>
    </body>
    </html>
    """)
