"""
Vista para mostrar todos los usuarios del sistema
"""
from django.http import HttpResponse
from django.contrib.auth.models import User
from empleados.models import Empleado

def listar_usuarios(request):
    """
    Página para listar todos los usuarios del sistema
    """
    html = """
    <html>
    <head>
        <title>👥 Usuarios del Sistema RRHH</title>
        <style>
            body { font-family: Arial; margin: 20px; background: #f5f5f5; }
            .container { background: white; padding: 20px; border-radius: 8px; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
            th { background: #007cba; color: white; }
            tr:hover { background: #f0f8ff; }
            .badge { padding: 4px 8px; border-radius: 4px; font-size: 12px; }
            .rrhh { background: #ff6b6b; color: white; }
            .manager { background: #4ecdc4; color: white; }
            .empleado { background: #95e1d3; color: #333; }
            .admin { background: #fce38a; color: #333; }
            .stats { display: flex; gap: 20px; margin-bottom: 20px; }
            .stat-card { background: #007cba; color: white; padding: 15px; border-radius: 8px; text-align: center; flex: 1; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>👥 Usuarios del Sistema RRHH</h1>
            
            <div class="stats">
    """
    
    # Estadísticas
    total_users = User.objects.count()
    total_empleados = Empleado.objects.count()
    usuarios_rrhh = Empleado.objects.filter(es_rrhh=True).count()
    admins = User.objects.filter(is_superuser=True).count()
    
    html += f"""
                <div class="stat-card">
                    <h3>{total_users}</h3>
                    <p>Total Usuarios</p>
                </div>
                <div class="stat-card">
                    <h3>{total_empleados}</h3>
                    <p>Empleados</p>
                </div>
                <div class="stat-card">
                    <h3>{usuarios_rrhh}</h3>
                    <p>Personal RRHH</p>
                </div>
                <div class="stat-card">
                    <h3>{admins}</h3>
                    <p>Administradores</p>
                </div>
            </div>
            
            <table>
                <thead>
                    <tr>
                        <th>👤 Usuario</th>
                        <th>📧 Email</th>
                        <th>🏢 Puesto</th>
                        <th>🏛️ Área</th>
                        <th>🔱 Jerarquía</th>
                        <th>🏷️ Tipo</th>
                        <th>✅ Estado</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    # Listar usuarios
    users = User.objects.all().order_by('first_name', 'last_name')
    for user in users:
        try:
            empleado = user.empleado
            puesto = empleado.puesto
            area = empleado.area or 'Sin área'
            jerarquia = empleado.get_jerarquia_display()
            
            # Determinar tipo de usuario
            if user.is_superuser:
                tipo = '<span class="badge admin">👑 ADMIN</span>'
            elif empleado.es_rrhh:
                tipo = '<span class="badge rrhh">🔴 RRHH</span>'
            elif empleado.es_manager:
                tipo = '<span class="badge manager">🔵 MANAGER</span>'
            else:
                tipo = '<span class="badge empleado">👤 EMPLEADO</span>'
                
        except:
            puesto = 'Sin perfil'
            area = '-'
            jerarquia = '-'
            if user.is_superuser:
                tipo = '<span class="badge admin">👑 ADMIN</span>'
            else:
                tipo = '<span class="badge empleado">👤 USUARIO</span>'
        
        estado = '✅ Activo' if user.is_active else '❌ Inactivo'
        nombre_completo = f"{user.first_name} {user.last_name}" if user.first_name else user.username
        
        html += f"""
                    <tr>
                        <td><strong>{nombre_completo}</strong><br><small>@{user.username}</small></td>
                        <td>{user.email}</td>
                        <td>{puesto}</td>
                        <td>{area}</td>
                        <td>{jerarquia}</td>
                        <td>{tipo}</td>
                        <td>{estado}</td>
                    </tr>
        """
    
    html += """
                </tbody>
            </table>
            
            <div style="margin-top: 30px; padding: 20px; background: #f8f9fa; border-radius: 8px;">
                <h3>🔧 Acciones disponibles:</h3>
                <p><a href="/crear-usuarios/">➕ Crear más usuarios</a></p>
                <p><a href="/login-debug/">🔑 Probar login</a></p>
                <p><a href="/diagnostico/">🔍 Diagnóstico del sistema</a></p>
                <p><a href="/admin/">⚙️ Panel de administración</a></p>
            </div>
            
            <div style="margin-top: 20px; padding: 15px; background: #e8f5e8; border-radius: 8px;">
                <h4>💡 Credenciales comunes:</h4>
                <ul>
                    <li><strong>Administradores:</strong> admin123, director123</li>
                    <li><strong>RRHH:</strong> rrhh123, 123456</li>
                    <li><strong>Managers:</strong> manager123, gerente123</li>
                    <li><strong>Empleados:</strong> empleado123</li>
                </ul>
            </div>
        </div>
    </body>
    </html>
    """
    
    return HttpResponse(html)
