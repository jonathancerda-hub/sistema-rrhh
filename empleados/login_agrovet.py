"""
Página especial para probar login de usuarios AgroVet
"""
from django.http import HttpResponse
from django.contrib.auth.models import User
from empleados.models import Empleado

def login_agrovet(request):
    """
    Página de login específica para AgroVet con lista de usuarios
    """
    html = """
    <html>
    <head>
        <title>🏢 Login AgroVet Market</title>
        <style>
            body { font-family: Arial; margin: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
            .container { background: rgba(255,255,255,0.95); color: #333; padding: 30px; border-radius: 15px; max-width: 1200px; margin: 0 auto; }
            .login-section { background: #f8f9fa; padding: 20px; border-radius: 10px; margin-bottom: 30px; }
            .usuarios-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 15px; margin-top: 20px; }
            .usuario-card { background: white; padding: 15px; border-radius: 8px; border-left: 4px solid #007cba; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .usuario-card:hover { transform: translateY(-2px); box-shadow: 0 4px 8px rgba(0,0,0,0.15); transition: all 0.3s; }
            .director { border-left-color: #dc3545; }
            .gerente { border-left-color: #fd7e14; }
            .jefe { border-left-color: #198754; }
            .supervisor { border-left-color: #0dcaf0; }
            form { display: flex; gap: 10px; align-items: center; margin-bottom: 20px; }
            input[type="text"], input[type="password"] { padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
            button { padding: 10px 20px; background: #007cba; color: white; border: none; border-radius: 5px; cursor: pointer; }
            button:hover { background: #0056b3; }
            .badge { padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: bold; color: white; }
            .badge-director { background: #dc3545; }
            .badge-gerente { background: #fd7e14; }
            .badge-jefe { background: #198754; }
            .badge-supervisor { background: #0dcaf0; }
            .badge-asistente { background: #6c757d; }
            .copy-btn { background: #28a745; color: white; border: none; padding: 2px 6px; border-radius: 3px; font-size: 10px; cursor: pointer; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏢 AgroVet Market - Sistema RRHH</h1>
            
            <div class="login-section">
                <h2>🔑 Acceso al Sistema</h2>
                <form action="/login-debug/" method="post">
                    <input type="text" name="username" placeholder="Usuario (ej: jose.garcia)" required>
                    <input type="password" name="password" value="agrovet2025" required>
                    <button type="submit">🚀 Ingresar</button>
                </form>
                <p><strong>💡 Contraseña para todos:</strong> <code>agrovet2025</code></p>
            </div>
            
            <h2>👥 Usuarios Disponibles - Organigrama AgroVet</h2>
            <div class="usuarios-grid">
    """
    
    # Obtener usuarios de AgroVet (filtrar por dominio de email)
    usuarios_agrovet = User.objects.filter(email__contains='agrovetmarket.com').order_by('empleado__jerarquia', 'first_name')
    
    jerarquia_colors = {
        'director': 'director',
        'gerente': 'gerente', 
        'jefe': 'jefe',
        'supervisor': 'supervisor',
        'asistente': 'asistente',
        'auxiliar': 'asistente'
    }
    
    for user in usuarios_agrovet:
        try:
            empleado = user.empleado
            jerarquia_class = jerarquia_colors.get(empleado.jerarquia, 'asistente')
            badge_class = f"badge-{jerarquia_class}"
            
            # Username sin tildes
            username = user.username
            
            html += f"""
                <div class="usuario-card {jerarquia_class}">
                    <div style="display: flex; justify-content: between; align-items: center;">
                        <div style="flex: 1;">
                            <h4 style="margin: 0 0 5px 0;">{empleado.nombre} {empleado.apellido}</h4>
                            <p style="margin: 0; font-size: 12px; color: #666;">{empleado.puesto}</p>
                            <p style="margin: 5px 0; font-weight: bold;">👤 {username}</p>
                        </div>
                        <span class="badge {badge_class}">{empleado.get_jerarquia_display()}</span>
                    </div>
                    <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid #eee;">
                        <small>📧 {user.email}</small><br>
                        <small>🏢 {empleado.area}</small>
                        {"<br><small>👑 MANAGER</small>" if empleado.es_manager else ""}
                        {"<br><small>👥 RRHH</small>" if empleado.es_rrhh else ""}
                    </div>
                    <button class="copy-btn" onclick="copyUsername('{username}')">📋 Copiar usuario</button>
                </div>
            """
        except:
            # Usuario sin perfil de empleado
            html += f"""
                <div class="usuario-card">
                    <h4>{user.first_name} {user.last_name}</h4>
                    <p>👤 {user.username}</p>
                    <p>📧 {user.email}</p>
                    <button class="copy-btn" onclick="copyUsername('{user.username}')">📋 Copiar usuario</button>
                </div>
            """
    
    html += f"""
            </div>
            
            <div style="margin-top: 30px; padding: 20px; background: #e8f5e8; border-radius: 10px;">
                <h3>📊 Estadísticas del Organigrama</h3>
                <p>👥 <strong>Total empleados AgroVet:</strong> {usuarios_agrovet.count()}</p>
                <p>🔑 <strong>Contraseña universal:</strong> agrovet2025</p>
                <p>👤 <strong>Formato usuario:</strong> nombre.apellido (sin tildes)</p>
            </div>
            
            <div style="margin-top: 20px; padding: 20px; background: #fff3cd; border-radius: 10px;">
                <h3>🔗 Enlaces útiles:</h3>
                <ul>
                    <li><a href="/usuarios/">👥 Ver todos los usuarios del sistema</a></li>
                    <li><a href="/admin/">⚙️ Panel de administración</a></li>
                    <li><a href="/diagnostico/">🔍 Diagnóstico del sistema</a></li>
                </ul>
            </div>
        </div>
        
        <script>
            function copyUsername(username) {{
                navigator.clipboard.writeText(username).then(function() {{
                    alert('✅ Usuario copiado: ' + username);
                }}).catch(function(err) {{
                    alert('❌ Error al copiar: ' + err);
                }});
            }}
        </script>
    </body>
    </html>
    """
    
    return HttpResponse(html)
