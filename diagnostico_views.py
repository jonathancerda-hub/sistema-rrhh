from django.http import JsonResponse, HttpResponse
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.db import connection
from empleados.models import Empleado
import traceback

def diagnostico_produccion(request):
    """Endpoint para diagnosticar problemas en producción"""
    
    diagnostico = {
        'status': 'ok',
        'checks': [],
        'errors': []
    }
    
    try:
        # 1. Verificar conexión a la base de datos
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            diagnostico['checks'].append("✅ Conexión a BD: OK")
    except Exception as e:
        diagnostico['status'] = 'error'
        diagnostico['errors'].append(f"❌ Conexión a BD: {str(e)}")
    
    try:
        # 2. Verificar tabla de sesiones
        count_sessions = Session.objects.count()
        diagnostico['checks'].append(f"✅ Tabla sessions: {count_sessions} registros")
    except Exception as e:
        diagnostico['status'] = 'error'
        diagnostico['errors'].append(f"❌ Tabla sessions: {str(e)}")
    
    try:
        # 3. Verificar usuarios
        count_users = User.objects.count()
        has_admin = User.objects.filter(username='admin').exists()
        diagnostico['checks'].append(f"✅ Usuarios: {count_users} total, admin={'existe' if has_admin else 'NO existe'}")
    except Exception as e:
        diagnostico['status'] = 'error'
        diagnostico['errors'].append(f"❌ Usuarios: {str(e)}")
    
    try:
        # 4. Verificar empleados
        count_empleados = Empleado.objects.count()
        diagnostico['checks'].append(f"✅ Empleados: {count_empleados} registrados")
    except Exception as e:
        diagnostico['status'] = 'error'
        diagnostico['errors'].append(f"❌ Empleados: {str(e)}")
    
    try:
        # 5. Verificar configuración
        from django.conf import settings
        diagnostico['checks'].append(f"✅ Settings: {settings.SETTINGS_MODULE}")
        diagnostico['checks'].append(f"✅ Debug: {settings.DEBUG}")
        diagnostico['checks'].append(f"✅ BD Engine: {settings.DATABASES['default']['ENGINE']}")
    except Exception as e:
        diagnostico['status'] = 'error'
        diagnostico['errors'].append(f"❌ Configuración: {str(e)}")
    
    # Formato de respuesta
    if request.GET.get('format') == 'json':
        return JsonResponse(diagnostico)
    else:
        # HTML simple
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Diagnóstico Sistema RRHH</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .ok {{ color: green; }}
                .error {{ color: red; }}
                .status {{ font-size: 24px; font-weight: bold; }}
                .checks {{ margin: 20px 0; }}
                .check {{ margin: 5px 0; }}
            </style>
        </head>
        <body>
            <h1>🔍 Diagnóstico Sistema RRHH</h1>
            <div class="status {'ok' if diagnostico['status'] == 'ok' else 'error'}">
                Estado: {diagnostico['status'].upper()}
            </div>
            
            <div class="checks">
                <h2>✅ Verificaciones:</h2>
                {''.join([f'<div class="check">{check}</div>' for check in diagnostico['checks']])}
            </div>
            
            {f'''<div class="checks">
                <h2>❌ Errores:</h2>
                {''.join([f'<div class="check error">{error}</div>' for error in diagnostico['errors']])}
            </div>''' if diagnostico['errors'] else ''}
            
            <div class="checks">
                <h2>🔗 Acciones:</h2>
                <div class="check"><a href="/admin/">Panel de Administración</a></div>
                <div class="check"><a href="/empleados/">Sistema de Empleados</a></div>
                <div class="check"><a href="/diagnostico/?format=json">Ver en JSON</a></div>
            </div>
        </body>
        </html>
        """
        return HttpResponse(html)

def forzar_migraciones(request):
    """Endpoint para forzar aplicación de migraciones"""
    
    if request.method == 'POST':
        try:
            from django.core.management import call_command
            
            # Aplicar migraciones
            call_command('migrate', verbosity=2)
            
            # Crear admin si no existe
            if not User.objects.filter(username='admin').exists():
                User.objects.create_superuser('admin', 'admin@empresa.com', 'admin123')
                admin_created = True
            else:
                admin_created = False
            
            return JsonResponse({
                'status': 'success',
                'message': 'Migraciones aplicadas correctamente',
                'admin_created': admin_created
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error aplicando migraciones: {str(e)}',
                'traceback': traceback.format_exc()
            })
    
    # GET - Mostrar formulario
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Aplicar Migraciones</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .button { background: #007cba; color: white; padding: 10px 20px; border: none; cursor: pointer; }
            .warning { background: #ffeb3b; padding: 10px; margin: 10px 0; }
        </style>
    </head>
    <body>
        <h1>🔧 Aplicar Migraciones</h1>
        <div class="warning">
            ⚠️ <strong>Advertencia:</strong> Esta acción aplicará todas las migraciones pendientes y creará el usuario admin si no existe.
        </div>
        <form method="post">
            <button type="submit" class="button">Aplicar Migraciones</button>
        </form>
        <p><a href="/diagnostico/">← Volver al diagnóstico</a></p>
    </body>
    </html>
    """
    return HttpResponse(html)
