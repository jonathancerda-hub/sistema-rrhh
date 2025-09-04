from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.models import User
from empleados.models import Empleado
from django.conf import settings
from django.db import connection

def estado_sistema(request):
    """Vista para mostrar el estado actual del sistema"""
    
    # Información de la base de datos
    db_info = {
        'engine': settings.DATABASES['default']['ENGINE'],
        'name': str(settings.DATABASES['default']['NAME']),
    }
    
    # Contar usuarios
    total_usuarios = User.objects.count()
    total_empleados = Empleado.objects.count()
    
    # Usuarios de AgroVet (filtrar por dominio)
    usuarios_agrovet = User.objects.filter(email__contains='@agrovetmarket.com').count()
    
    # Algunos usuarios de ejemplo
    usuarios_ejemplo = []
    for user in User.objects.all()[:10]:
        usuarios_ejemplo.append({
            'username': user.username,
            'nombre': f"{user.first_name} {user.last_name}",
            'email': user.email,
            'activo': user.is_active,
        })
    
    context = {
        'db_info': db_info,
        'total_usuarios': total_usuarios,
        'total_empleados': total_empleados,
        'usuarios_agrovet': usuarios_agrovet,
        'usuarios_ejemplo': usuarios_ejemplo,
    }
    
    if request.GET.get('format') == 'json':
        return JsonResponse(context)
    
    return render(request, 'empleados/estado_sistema.html', context)

def sistema_no_inicializado(request):
    """
    Vista que se muestra cuando el sistema no está inicializado.
    No depende de ninguna tabla de la base de datos.
    """
    return render(request, 'empleados/sistema_inicializando.html')

def verificar_estado_sistema(request):
    """
    Endpoint para verificar el estado del sistema sin depender de modelos Django
    """
    try:
        with connection.cursor() as cursor:
            # Verificar si existen las tablas principales
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='auth_user';")
            tabla_user = cursor.fetchone()
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='django_session';")
            tabla_session = cursor.fetchone()
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='empleados_empleado';")
            tabla_empleado = cursor.fetchone()
        
        estado = {
            'tablas_django': bool(tabla_user and tabla_session),
            'tabla_empleados': bool(tabla_empleado),
            'sistema_inicializado': bool(tabla_user and tabla_session and tabla_empleado)
        }
        
        if estado['sistema_inicializado']:
            # Si está inicializado, verificar cantidad de usuarios
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT COUNT(*) FROM auth_user;")
                    user_count = cursor.fetchone()[0]
                    estado['usuarios_count'] = user_count
                    estado['tiene_usuarios'] = user_count > 0
            except:
                estado['usuarios_count'] = 0
                estado['tiene_usuarios'] = False
        
        # Respuesta HTML simple
        color = "green" if estado['sistema_inicializado'] else "red"
        status = "✅ INICIALIZADO" if estado['sistema_inicializado'] else "❌ NO INICIALIZADO"
        
        html = f"""
        <html>
        <head>
            <title>Estado del Sistema</title>
            <meta http-equiv="refresh" content="10">
            <style>
                body {{ font-family: Arial; padding: 40px; }}
                .status {{ color: {color}; font-size: 24px; font-weight: bold; }}
                .detail {{ margin: 10px 0; padding: 10px; background: #f5f5f5; }}
            </style>
        </head>
        <body>
            <h1>🔍 Estado del Sistema RRHH</h1>
            <div class="status">{status}</div>
            
            <div class="detail">
                <strong>📊 Detalles:</strong><br>
                • Tablas Django: {'✅' if estado['tablas_django'] else '❌'}<br>
                • Tabla Empleados: {'✅' if estado['tabla_empleados'] else '❌'}<br>
        """
        
        if 'usuarios_count' in estado:
            html += f"• Usuarios registrados: {estado['usuarios_count']}<br>"
        
        html += f"""
            </div>
            
            <div style="margin-top: 30px;">
                <a href="/empleados/setup/emergencia/" style="padding: 10px 20px; background: #f44336; color: white; text-decoration: none; border-radius: 5px;">
                    🚨 Inicializar Sistema
                </a>
                <a href="/" style="padding: 10px 20px; background: #2196f3; color: white; text-decoration: none; border-radius: 5px; margin-left: 10px;">
                    🏠 Ir al Inicio
                </a>
            </div>
            
            <div style="margin-top: 20px; color: #666;">
                <small>🔄 Esta página se actualiza automáticamente cada 10 segundos</small>
            </div>
        </body>
        </html>
        """
        
        return HttpResponse(html)
        
    except Exception as e:
        return HttpResponse(f"""
            <html>
            <head><title>Error de Verificación</title></head>
            <body style="font-family: Arial; padding: 40px;">
                <h1>⚠️ Error al verificar el sistema</h1>
                <p><strong>Error:</strong> {str(e)}</p>
                <p><a href="/empleados/setup/emergencia/">🚨 Ir a Inicialización de Emergencia</a></p>
            </body>
            </html>
        """, status=500)
