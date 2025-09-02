from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.models import User
from empleados.models import Empleado
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def hacer_admin(request):
    """Vista específica para dar permisos de admin al usuario rrhh"""
    if request.method == 'POST':
        try:
            # Buscar usuario rrhh
            user_rrhh = User.objects.get(username='rrhh')
            
            # Dar permisos de administrador
            user_rrhh.is_staff = True
            user_rrhh.is_superuser = True
            user_rrhh.save()

            return HttpResponse(f"""
            <!DOCTYPE html>
            <html>
            <head><title>Permisos de Admin Otorgados</title></head>
            <body style="font-family: Arial; padding: 20px; background: #f0f8ff;">
                <div style="max-width: 500px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <h2 style="color: #28a745;">✅ ¡Permisos de Administrador Otorgados!</h2>
                    <p><strong>Usuario:</strong> rrhh</p>
                    <p><strong>is_staff:</strong> ✅ True</p>
                    <p><strong>is_superuser:</strong> ✅ True</p>
                    
                    <p style="background: #d4edda; padding: 15px; border-radius: 5px; border-left: 4px solid #28a745;">
                        ¡Ahora puedes acceder al Admin de Django!
                    </p>
                    
                    <a href="/admin/" style="display: inline-block; padding: 12px 25px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; margin-top: 15px;">
                        Ir al Admin de Django →
                    </a>
                    
                    <a href="/login/" style="display: inline-block; padding: 12px 25px; background: #28a745; color: white; text-decoration: none; border-radius: 5px; margin-top: 15px; margin-left: 10px;">
                        Ir al Sistema RRHH →
                    </a>
                </div>
            </body>
            </html>
            """)

        except User.DoesNotExist:
            return HttpResponse(f"""
            <!DOCTYPE html>
            <html>
            <head><title>Error</title></head>
            <body style="font-family: Arial; padding: 20px;">
                <h2 style="color: red;">❌ Error</h2>
                <p>El usuario 'rrhh' no existe. Primero crea el usuario usando la vista de setup simple.</p>
                <a href="/setup/simple/">Crear Usuario RRHH</a>
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
                <a href="/setup/admin/">Intentar de nuevo</a>
            </body>
            </html>
            """)

    # GET request - mostrar formulario
    try:
        user_rrhh = User.objects.get(username='rrhh')
        user_exists = True
        is_staff = user_rrhh.is_staff
        is_superuser = user_rrhh.is_superuser
    except User.DoesNotExist:
        user_exists = False
        is_staff = False
        is_superuser = False
    
    return HttpResponse(f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Hacer Admin - Sistema RRHH</title>
        <meta charset="utf-8">
    </head>
    <body style="font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5;">
        <div style="max-width: 500px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            <h2>🔒 Permisos de Administrador</h2>
            
            <h3>Estado Actual del Usuario 'rrhh':</h3>
            <p><strong>Usuario existe:</strong> {'✅ Sí' if user_exists else '❌ No'}</p>
            {f'''
            <p><strong>is_staff:</strong> {'✅ Sí' if is_staff else '❌ No'}</p>
            <p><strong>is_superuser:</strong> {'✅ Sí' if is_superuser else '❌ No'}</p>
            ''' if user_exists else ''}
            
            {f'''
            <form method="post" style="margin-top: 20px;">
                <button type="submit" style="padding: 15px 30px; background: #dc3545; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; width: 100%;">
                    🔑 Otorgar Permisos de Administrador
                </button>
            </form>
            ''' if user_exists else '''
            <p style="background: #f8d7da; padding: 15px; border-radius: 5px; color: #721c24;">
                Primero necesitas crear el usuario 'rrhh'. Ve a la vista de setup simple.
            </p>
            <a href="/setup/simple/" style="display: inline-block; padding: 15px 30px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; margin-top: 15px;">
                Crear Usuario RRHH
            </a>
            '''}
            
            <p style="margin-top: 20px; color: #666; font-size: 14px;">
                Esto dará permisos de is_staff=True e is_superuser=True al usuario 'rrhh'.
            </p>
        </div>
    </body>
    </html>
    """)
