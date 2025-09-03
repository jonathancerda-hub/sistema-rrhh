"""
Vista de diagnóstico simple
"""
from django.http import HttpResponse
from django.contrib.auth.models import User
from empleados.models import Empleado

def diagnostico_simple(request):
    """
    Página de diagnóstico simple para verificar usuarios
    """
    html = """
    <html>
    <head>
        <title>Diagnóstico Sistema RRHH</title>
        <style>
            body { font-family: Arial; margin: 20px; }
            .success { color: green; }
            .error { color: red; }
            .info { color: blue; }
        </style>
    </head>
    <body>
        <h1>🔍 Diagnóstico Sistema RRHH</h1>
        
        <h2>👥 Usuarios en el sistema:</h2>
        <ul>
    """
    
    try:
        users = User.objects.all()
        for user in users:
            html += f'<li class="success">✅ {user.username} - {user.first_name} {user.last_name} - Activo: {user.is_active}</li>'
    except Exception as e:
        html += f'<li class="error">❌ Error al obtener usuarios: {e}</li>'
    
    html += """
        </ul>
        
        <h2>👔 Empleados en el sistema:</h2>
        <ul>
    """
    
    try:
        empleados = Empleado.objects.all()
        for emp in empleados:
            html += f'<li class="success">✅ {emp.nombre} {emp.apellido} - {emp.puesto} - RRHH: {emp.es_rrhh}</li>'
    except Exception as e:
        html += f'<li class="error">❌ Error al obtener empleados: {e}</li>'
    
    html += f"""
        </ul>
        
        <h2>🔑 Credenciales para probar:</h2>
        <div class="info">
            <h3>Panel Admin:</h3>
            <p><strong>URL:</strong> <a href="/admin/">http://127.0.0.1:8000/admin/</a></p>
            <p><strong>Usuario:</strong> admin</p>
            <p><strong>Contraseña:</strong> 123456</p>
            
            <h3>Login Empleados:</h3>
            <p><strong>URL:</strong> <a href="/login/">http://127.0.0.1:8000/login/</a></p>
            <p><strong>RRHH:</strong> rrhh / 123456</p>
            <p><strong>Empleado:</strong> empleado / 123456</p>
        </div>
        
        <h2>🔄 Acciones:</h2>
        <p><a href="/crear-usuario-emergencia/">🚨 Crear usuarios de emergencia</a></p>
        <p><a href="/admin/">🔧 Ir al panel de administración</a></p>
        <p><a href="/login/">👤 Ir al login de empleados</a></p>
        
        <hr>
        <p><small>🕐 Generado: {request.META.get('HTTP_HOST', 'localhost')} - Puerto: {request.META.get('SERVER_PORT', '8000')}</small></p>
    </body>
    </html>
    """
    
    return HttpResponse(html)
