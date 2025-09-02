from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.models import User
from empleados.models import Empleado

def ver_datos_existentes(request):
    """Vista para ver todos los datos existentes en la base de datos"""
    
    # Obtener todos los usuarios y empleados
    usuarios = User.objects.all().order_by('username')
    empleados = Empleado.objects.all().order_by('dni')
    
    return HttpResponse(f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Datos Existentes - Sistema RRHH</title>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5; }}
            .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #007bff; color: white; }}
            .dni-usado {{ background-color: #fff3cd; }}
            .btn {{ display: inline-block; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; margin: 5px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>📊 Datos Existentes en la Base de Datos</h2>
            
            <h3>👥 Usuarios Django ({usuarios.count()})</h3>
            <table>
                <thead>
                    <tr>
                        <th>Username</th>
                        <th>Email</th>
                        <th>Staff</th>
                        <th>Superuser</th>
                        <th>Activo</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join([f'''
                    <tr>
                        <td>{user.username}</td>
                        <td>{user.email}</td>
                        <td>{"✅" if user.is_staff else "❌"}</td>
                        <td>{"✅" if user.is_superuser else "❌"}</td>
                        <td>{"✅" if user.is_active else "❌"}</td>
                    </tr>
                    ''' for user in usuarios])}
                </tbody>
            </table>
            
            <h3>🏢 Empleados ({empleados.count()})</h3>
            <table>
                <thead>
                    <tr>
                        <th>DNI</th>
                        <th>Nombre</th>
                        <th>Email</th>
                        <th>Puesto</th>
                        <th>Usuario</th>
                        <th>RRHH</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join([f'''
                    <tr class="dni-usado">
                        <td><strong>{emp.dni}</strong></td>
                        <td>{emp.nombre} {emp.apellido}</td>
                        <td>{emp.email}</td>
                        <td>{emp.puesto}</td>
                        <td>{emp.user.username if emp.user else "Sin usuario"}</td>
                        <td>{"✅" if emp.es_rrhh else "❌"}</td>
                    </tr>
                    ''' for emp in empleados])}
                </tbody>
            </table>
            
            <div style="background: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #ffc107;">
                <h4>⚠️ DNIs ya en uso:</h4>
                <p>Los siguientes DNIs <strong>NO puedes usar</strong> para crear nuevos empleados:</p>
                <ul>
                    {''.join([f'<li><strong>{emp.dni}</strong> - {emp.nombre} {emp.apellido}</li>' for emp in empleados])}
                </ul>
            </div>
            
            <div style="background: #d4edda; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #28a745;">
                <h4>✅ Para crear un nuevo empleado:</h4>
                <p>Usa un DNI diferente, por ejemplo:</p>
                <ul>
                    <li><strong>99887766</strong> - DNI de ejemplo 1</li>
                    <li><strong>55443322</strong> - DNI de ejemplo 2</li>
                    <li><strong>77665544</strong> - DNI de ejemplo 3</li>
                </ul>
            </div>
            
            <div style="margin-top: 30px;">
                <a href="/admin/" class="btn">🔙 Volver al Admin</a>
                <a href="/admin/empleados/empleado/add/" class="btn" style="background: #28a745;">➕ Crear Empleado</a>
                <a href="/" class="btn" style="background: #6c757d;">🏠 Sistema RRHH</a>
            </div>
        </div>
    </body>
    </html>
    """)
