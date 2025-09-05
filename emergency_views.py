from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import traceback
import os

@csrf_exempt
def health_check_simple(request):
    """Health check que no requiere autenticación ni sesiones"""
    
    try:
        # Información básica sin acceso a BD
        info = {
            'status': 'running',
            'django_version': getattr(settings, 'DJANGO_VERSION', 'unknown'),
            'settings_module': os.environ.get('DJANGO_SETTINGS_MODULE', 'not_set'),
            'debug': getattr(settings, 'DEBUG', False),
            'allowed_hosts': getattr(settings, 'ALLOWED_HOSTS', []),
        }
        
        # Intentar obtener info de BD sin hacer queries
        try:
            db_config = settings.DATABASES.get('default', {})
            info['database'] = {
                'engine': db_config.get('ENGINE', 'unknown'),
                'name': db_config.get('NAME', 'unknown')[:50],  # Truncar por seguridad
            }
        except:
            info['database'] = 'error_getting_config'
        
        # HTML simple si no es JSON
        if request.GET.get('format') != 'json':
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Sistema RRHH - Health Check</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
                    .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }}
                    .status {{ font-size: 24px; color: green; font-weight: bold; }}
                    .info {{ margin: 10px 0; padding: 10px; background: #f0f0f0; border-radius: 5px; }}
                    .error {{ color: red; }}
                    .warning {{ color: orange; background: #fff3cd; padding: 15px; border-radius: 5px; margin: 15px 0; }}
                    .solution {{ background: #d4edda; padding: 15px; border-radius: 5px; margin: 15px 0; }}
                    .btn {{ background: #007cba; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 5px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🏥 Sistema RRHH - Health Check</h1>
                    <div class="status">✅ Aplicación funcionando</div>
                    
                    <h2>📊 Información del Sistema</h2>
                    <div class="info"><strong>Settings Module:</strong> {info['settings_module']}</div>
                    <div class="info"><strong>Debug Mode:</strong> {info['debug']}</div>
                    <div class="info"><strong>Allowed Hosts:</strong> {', '.join(map(str, info['allowed_hosts']))}</div>
                    <div class="info"><strong>Database Engine:</strong> {info['database'].get('engine', 'unknown') if isinstance(info['database'], dict) else info['database']}</div>
                    
                    <div class="warning">
                        <h3>⚠️ Error Detectado: django_session</h3>
                        <p>La aplicación está funcionando pero hay un problema con la tabla django_session.</p>
                        <p><strong>Causa probable:</strong> Migraciones no aplicadas en la base de datos.</p>
                    </div>
                    
                    <div class="solution">
                        <h3>🔧 Soluciones Disponibles</h3>
                        <p>1. <strong>Aplicar migraciones manualmente:</strong></p>
                        <code>python manage.py migrate</code>
                        
                        <p>2. <strong>Acceder a endpoints de emergencia:</strong></p>
                        <a href="/emergency-migrate/" class="btn">🚨 Migración de Emergencia</a>
                        <a href="/health/?format=json" class="btn">📊 Ver en JSON</a>
                    </div>
                    
                    <div class="info">
                        <h3>📋 Próximos Pasos</h3>
                        <ol>
                            <li>Verificar que las migraciones se ejecuten durante el build</li>
                            <li>Revisar logs de Render para errores de build</li>
                            <li>Usar el endpoint de migración de emergencia si es necesario</li>
                        </ol>
                    </div>
                </div>
            </body>
            </html>
            """
            return HttpResponse(html)
        else:
            return JsonResponse(info)
            
    except Exception as e:
        error_info = {
            'status': 'error',
            'error': str(e),
            'traceback': traceback.format_exc()
        }
        
        if request.GET.get('format') != 'json':
            html = f"""
            <html><body>
            <h1>❌ Error en Health Check</h1>
            <pre>{traceback.format_exc()}</pre>
            </body></html>
            """
            return HttpResponse(html, status=500)
        else:
            return JsonResponse(error_info, status=500)

@csrf_exempt
def emergency_migrate(request):
    """Endpoint de emergencia para aplicar migraciones sin sesiones"""
    
    if request.method != 'POST':
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Migración de Emergencia</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .btn { background: #dc3545; color: white; padding: 15px 30px; border: none; font-size: 16px; cursor: pointer; border-radius: 5px; }
                .warning { background: #fff3cd; padding: 20px; border-radius: 5px; margin: 20px 0; }
            </style>
        </head>
        <body>
            <h1>🚨 Migración de Emergencia</h1>
            <div class="warning">
                <h3>⚠️ ADVERTENCIA</h3>
                <p>Esta acción aplicará todas las migraciones pendientes a la base de datos.</p>
                <p>Solo úsala si el sistema no está funcionando debido a problemas de migración.</p>
            </div>
            
            <form method="post">
                <button type="submit" class="btn">🔧 APLICAR MIGRACIONES DE EMERGENCIA</button>
            </form>
            
            <p><a href="/health/">← Volver al Health Check</a></p>
        </body>
        </html>
        """
        return HttpResponse(html)
    
    try:
        from django.core.management import call_command
        from io import StringIO
        import sys
        
        # Capturar output de migraciones
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        stdout_capture = StringIO()
        stderr_capture = StringIO()
        
        try:
            sys.stdout = stdout_capture
            sys.stderr = stderr_capture
            
            # Aplicar migraciones
            call_command('migrate', verbosity=2)
            
            # Crear superusuario si no existe
            try:
                from django.contrib.auth.models import User
                if not User.objects.filter(username='admin').exists():
                    User.objects.create_superuser('admin', 'admin@empresa.com', 'admin123')
                    admin_created = True
                else:
                    admin_created = False
            except Exception as user_error:
                admin_created = f"Error: {str(user_error)}"
            
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
        
        stdout_content = stdout_capture.getvalue()
        stderr_content = stderr_capture.getvalue()
        
        result = {
            'status': 'success',
            'message': 'Migraciones aplicadas exitosamente',
            'admin_created': admin_created,
            'stdout': stdout_content,
            'stderr': stderr_content
        }
        
        if request.GET.get('format') == 'json':
            return JsonResponse(result)
        else:
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Migración Completada</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .success {{ background: #d4edda; padding: 20px; border-radius: 5px; color: #155724; }}
                    .output {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0; overflow: auto; }}
                    pre {{ margin: 0; }}
                </style>
            </head>
            <body>
                <h1>✅ Migración Completada</h1>
                <div class="success">
                    <h3>Resultado exitoso</h3>
                    <p>Las migraciones se aplicaron correctamente.</p>
                    <p><strong>Admin creado:</strong> {admin_created}</p>
                </div>
                
                <h3>📋 Output de migraciones:</h3>
                <div class="output">
                    <pre>{stdout_content}</pre>
                </div>
                
                {f'<h3>⚠️ Errores:</h3><div class="output"><pre>{stderr_content}</pre></div>' if stderr_content else ''}
                
                <p><a href="/health/">🔍 Verificar estado del sistema</a></p>
                <p><a href="/admin/">🔐 Ir al panel de administración</a></p>
            </body>
            </html>
            """
            return HttpResponse(html)
            
    except Exception as e:
        error_result = {
            'status': 'error',
            'message': f'Error aplicando migraciones: {str(e)}',
            'traceback': traceback.format_exc()
        }
        
        if request.GET.get('format') == 'json':
            return JsonResponse(error_result, status=500)
        else:
            html = f"""
            <html>
            <head><title>Error en Migración</title></head>
            <body>
                <h1>❌ Error en Migración</h1>
                <p>{str(e)}</p>
                <pre>{traceback.format_exc()}</pre>
                <p><a href="/health/">← Volver</a></p>
            </body>
            </html>
            """
            return HttpResponse(html, status=500)
