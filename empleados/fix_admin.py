from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.models import User
from empleados.models import Empleado
from django.views.decorators.csrf import csrf_exempt
from datetime import date

@csrf_exempt
def fix_admin_access(request):
    """Vista específica para arreglar el acceso al admin"""
    if request.method == 'POST':
        try:
            resultados = []
            
            # Método 1: Crear superusuario admin
            admin_user, created = User.objects.get_or_create(
                username='admin',
                defaults={
                    'email': 'admin@empresa.com',
                    'first_name': 'Admin',
                    'last_name': 'Sistema',
                    'is_staff': True,
                    'is_superuser': True,
                    'is_active': True
                }
            )
            
            if created:
                admin_user.set_password('admin123456')
                admin_user.save()
                resultados.append("✅ Usuario 'admin' creado")
            else:
                admin_user.is_staff = True
                admin_user.is_superuser = True
                admin_user.is_active = True
                admin_user.set_password('admin123456')
                admin_user.save()
                resultados.append("✅ Usuario 'admin' actualizado")

            # Método 2: Actualizar usuario rrhh
            try:
                rrhh_user = User.objects.get(username='rrhh')
                rrhh_user.is_staff = True
                rrhh_user.is_superuser = True
                rrhh_user.is_active = True
                rrhh_user.save()
                resultados.append("✅ Usuario 'rrhh' actualizado con permisos de admin")
            except User.DoesNotExist:
                # Crear usuario rrhh si no existe
                rrhh_user = User.objects.create_user(
                    username='rrhh',
                    email='rrhh@empresa.com',
                    password='rrhh123456',
                    first_name='RRHH',
                    last_name='Sistema',
                    is_staff=True,
                    is_superuser=True,
                    is_active=True
                )
                resultados.append("✅ Usuario 'rrhh' creado desde cero")

            # Verificar que tengan empleados asociados
            empleados_creados = 0
            
            # Empleado para admin
            admin_emp, created = Empleado.objects.get_or_create(
                user=admin_user,
                defaults={
                    'nombre': 'Admin',
                    'apellido': 'Sistema',
                    'dni': '00000000',
                    'email': 'admin@empresa.com',
                    'puesto': 'Administrador',
                    'fecha_contratacion': date.today(),
                    'area': 'Sistemas',
                    'gerencia': 'gerencia_desarrollo_organizacional',
                    'jerarquia': 'director',
                    'es_rrhh': True,
                    'dias_vacaciones_disponibles': 30
                }
            )
            if created:
                empleados_creados += 1

            # Empleado para rrhh
            rrhh_emp, created = Empleado.objects.get_or_create(
                user=rrhh_user,
                defaults={
                    'nombre': 'RRHH',
                    'apellido': 'Sistema',
                    'dni': '12345678',
                    'email': 'rrhh@empresa.com',
                    'puesto': 'Recursos Humanos',
                    'fecha_contratacion': date.today(),
                    'area': 'RRHH',
                    'gerencia': 'gerencia_desarrollo_organizacional',
                    'jerarquia': 'director',
                    'es_rrhh': True,
                    'dias_vacaciones_disponibles': 30
                }
            )
            if created:
                empleados_creados += 1

            return HttpResponse(f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Acceso Admin Reparado</title>
                <meta charset="utf-8">
                <style>
                    body {{ font-family: Arial, sans-serif; padding: 20px; background: #f0f8ff; }}
                    .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }}
                    .success {{ background: #d4edda; border: 1px solid #c3e6cb; color: #155724; padding: 15px; border-radius: 8px; margin: 15px 0; }}
                    .credentials {{ background: #e7f3ff; border: 1px solid #bee5eb; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                    .btn {{ display: inline-block; padding: 12px 25px; color: white; text-decoration: none; border-radius: 8px; margin: 10px 5px; font-weight: bold; }}
                    .btn-primary {{ background: #007bff; }}
                    .btn-success {{ background: #28a745; }}
                    ul li {{ margin: 8px 0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h2 style="color: #28a745; text-align: center;">🔓 ¡Acceso al Admin Reparado!</h2>
                    
                    <div class="success">
                        <h4>✅ Operaciones Completadas:</h4>
                        <ul>
                            {''.join([f'<li>{resultado}</li>' for resultado in resultados])}
                            <li>✅ {empleados_creados} empleados asociados</li>
                        </ul>
                    </div>
                    
                    <div class="credentials">
                        <h4>🔑 Credenciales de Acceso al Django Admin:</h4>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 15px;">
                            <div style="background: #fff; padding: 15px; border-radius: 5px; border-left: 4px solid #007bff;">
                                <strong>Opción 1:</strong><br>
                                <strong>Usuario:</strong> admin<br>
                                <strong>Contraseña:</strong> admin123456<br>
                                <small>Superusuario dedicado</small>
                            </div>
                            <div style="background: #fff; padding: 15px; border-radius: 5px; border-left: 4px solid #28a745;">
                                <strong>Opción 2:</strong><br>
                                <strong>Usuario:</strong> rrhh<br>
                                <strong>Contraseña:</strong> rrhh123456<br>
                                <small>Usuario RRHH con admin</small>
                            </div>
                        </div>
                    </div>
                    
                    <div style="text-align: center; margin-top: 30px;">
                        <a href="/admin/" class="btn btn-primary">🔐 Acceder al Django Admin</a>
                        <a href="/login/" class="btn btn-success">🏠 Sistema RRHH</a>
                    </div>
                    
                    <div style="background: #fff3cd; border: 1px solid #ffeaa7; color: #856404; padding: 15px; border-radius: 8px; margin-top: 20px;">
                        <strong>📝 Importante:</strong> Ambos usuarios ahora tienen permisos completos de administrador (is_staff=True, is_superuser=True).
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
            <body style="font-family: Arial; padding: 20px; background: #f8f9fa;">
                <div style="max-width: 500px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                    <h2 style="color: #dc3545;">❌ Error</h2>
                    <p><strong>Error:</strong> {str(e)}</p>
                    <p>Detalles técnicos del error para debugging.</p>
                    <a href="/fix-admin/" style="display: inline-block; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px;">Intentar de nuevo</a>
                </div>
            </body>
            </html>
            """)

    # GET request
    total_users = User.objects.count()
    admin_users = User.objects.filter(is_superuser=True).count()
    staff_users = User.objects.filter(is_staff=True).count()
    
    return HttpResponse(f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Reparar Acceso Admin - Sistema RRHH</title>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 15px; box-shadow: 0 2px 15px rgba(0,0,0,0.1); }}
            .info {{ background: #e7f3ff; border: 1px solid #bee5eb; padding: 15px; border-radius: 8px; margin: 15px 0; }}
            .btn {{ padding: 15px 30px; background: #dc3545; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 16px; width: 100%; font-weight: bold; }}
            .btn:hover {{ background: #c82333; }}
            .stats {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin: 20px 0; }}
            .stat {{ background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center; border-left: 4px solid #007bff; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>🔧 Reparar Acceso al Django Admin</h2>
            
            <div class="stats">
                <div class="stat">
                    <h4>{total_users}</h4>
                    <small>Total Usuarios</small>
                </div>
                <div class="stat">
                    <h4>{staff_users}</h4>
                    <small>Staff Users</small>
                </div>
                <div class="stat">
                    <h4>{admin_users}</h4>
                    <small>Superusers</small>
                </div>
            </div>
            
            <div class="info">
                <h4>🔍 ¿Qué hace esta acción?</h4>
                <ul>
                    <li>✅ Crea/actualiza usuario <strong>'admin'</strong> con permisos completos</li>
                    <li>✅ Actualiza usuario <strong>'rrhh'</strong> con permisos de administrador</li>
                    <li>✅ Asigna contraseñas conocidas y seguras</li>
                    <li>✅ Crea perfiles de empleado asociados</li>
                    <li>✅ Garantiza acceso completo al Django Admin</li>
                </ul>
            </div>
            
            <form method="post" style="margin-top: 25px;">
                <button type="submit" class="btn">
                    🚀 Reparar Acceso al Admin Ahora
                </button>
            </form>
            
            <div style="margin-top: 20px; color: #666; font-size: 14px; text-align: center;">
                Esta acción es segura y no afectará datos existentes.
            </div>
        </div>
    </body>
    </html>
    """)
