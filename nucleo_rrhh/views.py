from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.db import connection
from django.core.exceptions import OperationalError

def root_redirect(request):
    """Redirección inteligente desde la raíz de la aplicación"""
    
    try:
        # Verificar si existen las tablas básicas
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='auth_user';")
            tabla_user = cursor.fetchone()
        
        if not tabla_user:
            # Si no existe la tabla de usuarios, redirigir a emergencia
            return redirect('/empleados/setup/emergencia/')
        
        # Intentar contar usuarios
        try:
            user_count = User.objects.count()
            if user_count == 0:
                return redirect('/empleados/setup/emergencia/')
        except OperationalError:
            return redirect('/empleados/setup/emergencia/')
        
        # Si todo está bien, redirigir al sistema principal
        return redirect('/empleados/')
        
    except Exception as e:
        # En caso de cualquier error, redirigir a emergencia
        return redirect('/empleados/setup/emergencia/')

def health_check(request):
    """Endpoint básico de health check para Render"""
    try:
        # Verificar que Django funcione y las tablas existan
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='auth_user';")
            tabla_user = cursor.fetchone()
        
        if not tabla_user:
            return HttpResponse("ERROR: Tablas no inicializadas", status=503)
        
        try:
            user_count = User.objects.count()
            return HttpResponse(f"OK - Sistema RRHH funcionando. Usuarios: {user_count}")
        except OperationalError:
            return HttpResponse("ERROR: Problema con base de datos", status=503)
            
    except Exception as e:
        return HttpResponse(f"ERROR: {str(e)}", status=500)

def vista_simple_root(request):
    """Vista simple sin dependencias para testing"""
    return HttpResponse("""
        <html>
        <head><title>Sistema RRHH</title></head>
        <body style="font-family: Arial; padding: 40px; text-align: center;">
            <h1>🏢 Sistema RRHH</h1>
            <p>Vista simple funcionando</p>
            <div style="margin: 20px;">
                <a href="/empleados/" style="padding: 10px 20px; background: #2196f3; color: white; text-decoration: none; border-radius: 5px;">
                    🏠 Sistema Principal
                </a>
                <a href="/empleados/setup/emergencia/" style="padding: 10px 20px; background: #f44336; color: white; text-decoration: none; border-radius: 5px; margin-left: 10px;">
                    🚨 Inicializar
                </a>
            </div>
        </body>
        </html>
    """)
