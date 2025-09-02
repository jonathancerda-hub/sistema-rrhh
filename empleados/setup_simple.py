from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.models import User
from empleados.models import Empleado
from django.views.decorators.csrf import csrf_exempt
from datetime import date

@csrf_exempt
def setup_simple(request):
    """Vista ultra simple para crear empleados"""
    if request.method == 'POST':
        try:
            # Crear usuario RRHH si no existe
            user_rrhh, created = User.objects.get_or_create(
                username='rrhh',
                defaults={
                    'email': 'rrhh@empresa.com',
                    'is_staff': True,
                    'is_superuser': True
                }
            )
            if created:
                user_rrhh.set_password('rrhh123456')
                user_rrhh.save()

            # Crear empleado RRHH
            empleado_rrhh, created_emp = Empleado.objects.get_or_create(
                user=user_rrhh,
                defaults={
                    'nombre': 'RRHH',
                    'apellido': 'Sistema',
                    'dni': '12345678',
                    'email': 'rrhh@empresa.com',
                    'puesto': 'Recursos Humanos',
                    'fecha_contratacion': date.today(),  # ✅ Campo obligatorio agregado
                    'area': 'RRHH',
                    'gerencia': 'gerencia_desarrollo_organizacional',
                    'jerarquia': 'director',
                    'es_rrhh': True,
                    'dias_vacaciones_disponibles': 30
                }
            )

            return HttpResponse(f"""
            <!DOCTYPE html>
            <html>
            <head><title>Empleados Creados</title></head>
            <body style="font-family: Arial; padding: 20px; background: #f0f8ff;">
                <div style="max-width: 500px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <h2 style="color: #28a745;">✅ ¡Empleados creados exitosamente!</h2>
                    <p><strong>Usuario RRHH:</strong> {'Creado' if created else 'Ya existía'}</p>
                    <p><strong>Empleado RRHH:</strong> {'Creado' if created_emp else 'Ya existía'}</p>
                    
                    <h3>🔑 Credenciales:</h3>
                    <ul>
                        <li><strong>Usuario:</strong> rrhh</li>
                        <li><strong>Contraseña:</strong> rrhh123456</li>
                    </ul>
                    
                    <p style="background: #d4edda; padding: 15px; border-radius: 5px; border-left: 4px solid #28a745;">
                        ¡Ya puedes hacer login con estas credenciales!
                    </p>
                    
                    <a href="/login/" style="display: inline-block; padding: 12px 25px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; margin-top: 15px;">
                        Ir al Login →
                    </a>
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
                <a href="/setup/simple/">Intentar de nuevo</a>
            </body>
            </html>
            """)

    # GET request - mostrar formulario
    usuarios_count = User.objects.count()
    empleados_count = Empleado.objects.count()
    
    return HttpResponse(f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Setup Simple - Sistema RRHH</title>
        <meta charset="utf-8">
    </head>
    <body style="font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5;">
        <div style="max-width: 500px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            <h2>Setup Simple - Sistema RRHH</h2>
            
            <p><strong>Usuarios existentes:</strong> {usuarios_count}</p>
            <p><strong>Empleados existentes:</strong> {empleados_count}</p>
            
            <form method="post" style="margin-top: 20px;">
                <button type="submit" style="padding: 15px 30px; background: #28a745; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; width: 100%;">
                    🚀 Crear Usuario RRHH
                </button>
            </form>
            
            <p style="margin-top: 20px; color: #666; font-size: 14px;">
                Esto creará el usuario 'rrhh' con contraseña 'rrhh123456' y su perfil de empleado asociado.
            </p>
        </div>
    </body>
    </html>
    """)
