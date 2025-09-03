"""
Vista de login simplificada para debugging
"""
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import HttpResponse
from empleados.models import Empleado

def login_debug(request):
    """
    Login simplificado para debugging
    """
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        
        # Debug: mostrar qué se está intentando
        debug_info = f"Intentando login con: {username} / {password}<br>"
        
        # Verificar si el usuario existe
        try:
            user_obj = User.objects.get(username=username)
            debug_info += f"✅ Usuario encontrado: {user_obj.username}<br>"
            debug_info += f"Activo: {user_obj.is_active}<br>"
            debug_info += f"Staff: {user_obj.is_staff}<br>"
        except User.DoesNotExist:
            debug_info += f"❌ Usuario {username} no existe<br>"
            return HttpResponse(f"<h1>Debug Login</h1>{debug_info}<a href='/login-debug/'>Volver</a>")
        
        # Intentar autenticación
        user = authenticate(request, username=username, password=password)
        debug_info += f"Resultado authenticate: {user}<br>"
        
        if user is not None:
            login(request, user)
            debug_info += f"✅ Login exitoso<br>"
            
            # Verificar si tiene empleado asociado
            try:
                empleado = user.empleado
                debug_info += f"Empleado: {empleado.nombre} {empleado.apellido}<br>"
                if empleado.es_rrhh:
                    return redirect('/admin/')  # Redirigir RRHH al admin
                else:
                    return HttpResponse(f"<h1>✅ Login Exitoso!</h1>{debug_info}<p>Bienvenido {user.first_name}!</p>")
            except:
                debug_info += f"Sin empleado asociado<br>"
                return HttpResponse(f"<h1>✅ Login Exitoso!</h1>{debug_info}<p>Bienvenido {user.username}!</p>")
        else:
            debug_info += f"❌ Autenticación fallida<br>"
            return HttpResponse(f"<h1>❌ Login Fallido</h1>{debug_info}<a href='/login-debug/'>Volver</a>")
    
    # Mostrar formulario de login
    html = """
    <html>
    <head>
        <title>Login Debug</title>
        <style>
            body { font-family: Arial; margin: 20px; }
            form { max-width: 300px; }
            input { width: 100%; padding: 8px; margin: 5px 0; }
            button { padding: 10px 20px; background: #007cba; color: white; border: none; }
        </style>
    </head>
    <body>
        <h1>🔧 Login Debug</h1>
        <form method="post">
            <p>
                <label>Usuario:</label>
                <input type="text" name="username" value="admin" required>
            </p>
            <p>
                <label>Contraseña:</label>
                <input type="password" name="password" value="123456" required>
            </p>
            <button type="submit">🔑 Probar Login</button>
        </form>
        
        <h3>Usuarios disponibles:</h3>
        <ul>
    """
    
    # Listar usuarios disponibles
    try:
        users = User.objects.all()
        for user in users:
            html += f"<li>{user.username} - Activo: {user.is_active}</li>"
    except:
        html += "<li>Error al cargar usuarios</li>"
    
    html += """
        </ul>
        <p><a href="/diagnostico/">🔍 Ver diagnóstico completo</a></p>
    </body>
    </html>
    """
    
    return HttpResponse(html)
