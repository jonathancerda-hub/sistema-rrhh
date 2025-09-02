from django.http import JsonResponse, HttpResponse
from django.contrib.auth.models import User
from empleados.models import Empleado
from django.views.decorators.csrf import csrf_exempt
import json

def inicializar_datos_produccion(request):
    """
    Vista temporal para inicializar datos en producción cuando no hay acceso a shell.
    IMPORTANTE: Eliminar esta vista después de usar.
    Acepta tanto GET como POST para facilidad de uso.
    """
    
    # Verificar si ya existen empleados
    empleados_existentes = Empleado.objects.count()
    usuarios_existentes = User.objects.count()
    
    if request.method == 'GET':
        return HttpResponse(f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Inicializar Datos - Sistema RRHH</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .btn {{ padding: 15px 30px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }}
                .btn:hover {{ background: #0056b3; }}
                .resultado {{ margin-top: 20px; padding: 15px; border-radius: 5px; }}
                .success {{ background: #d4edda; border: 1px solid #c3e6cb; color: #155724; }}
                .error {{ background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; }}
                .loading {{ background: #fff3cd; border: 1px solid #ffeaa7; color: #856404; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Estado Actual de la Base de Datos</h2>
                <p><strong>Usuarios existentes:</strong> {usuarios_existentes}</p>
                <p><strong>Empleados existentes:</strong> {empleados_existentes}</p>
                
                <h3>Crear Datos Iniciales</h3>
                <button onclick="inicializar()" class="btn" id="btnInicializar">
                    Crear Empleados y Asociaciones
                </button>
                
                <div id="resultado"></div>
                
                <script>
                function inicializar() {{
                    const btn = document.getElementById('btnInicializar');
                    const resultado = document.getElementById('resultado');
                    
                    btn.disabled = true;
                    btn.innerHTML = 'Procesando...';
                    resultado.innerHTML = '<div class="loading">Creando empleados y asociaciones...</div>';
                    
                    fetch(window.location.href, {{
                        method: 'POST',
                        headers: {{
                            'Content-Type': 'application/json',
                            'X-Requested-With': 'XMLHttpRequest'
                        }},
                        credentials: 'same-origin'
                    }})
                    .then(response => {{
                        if (!response.ok) {{
                            throw new Error('Error en el servidor: ' + response.status);
                        }}
                        return response.json();
                    }})
                    .then(data => {{
                        btn.disabled = false;
                        btn.innerHTML = 'Completado ✓';
                        
                        if (data.status === 'success') {{
                            resultado.innerHTML = `
                                <div class="success">
                                    <h4>✅ ${{data.message}}</h4>
                                    <p><strong>Resultados:</strong></p>
                                    <ul>${{data.resultados.map(r => '<li>' + r + '</li>').join('')}}</ul>
                                    <p><strong>Total usuarios:</strong> ${{data.total_usuarios}}</p>
                                    <p><strong>Total empleados:</strong> ${{data.total_empleados}}</p>
                                    <h4>🔑 Credenciales de acceso:</h4>
                                    <ul>
                                        <li>RRHH: ${{data.credenciales.rrhh}}</li>
                                        <li>Manager: ${{data.credenciales.manager}}</li>
                                        <li>Empleado: ${{data.credenciales.empleado}}</li>
                                    </ul>
                                    <p><strong>¡Ya puedes hacer login!</strong></p>
                                    <a href="/login/" style="display: inline-block; padding: 10px 20px; background: #28a745; color: white; text-decoration: none; border-radius: 5px; margin-top: 10px;">Ir al Login</a>
                                </div>
                            `;
                        }} else {{
                            resultado.innerHTML = `<div class="error">❌ ${{data.message}}</div>`;
                        }}
                    }})
                    .catch(error => {{
                        btn.disabled = false;
                        btn.innerHTML = 'Reintentar';
                        resultado.innerHTML = `<div class="error">❌ Error: ${{error.message}}</div>`;
                        console.error('Error completo:', error);
                    }});
                }}
                </script>
            </div>
        </body>
        </html>
        """)
    
    if request.method == 'POST':
        try:
            # Crear o actualizar empleados para usuarios existentes
            resultados = []
            
            # Usuario RRHH
            user_rrhh, created_user = User.objects.get_or_create(
                username='rrhh',
                defaults={
                    'email': 'rrhh@empresa.com',
                    'is_staff': True,
                    'is_superuser': True
                }
            )
            if created_user:
                user_rrhh.set_password('rrhh123456')
                user_rrhh.save()
                
            empleado_rrhh, created_emp = Empleado.objects.get_or_create(
                user=user_rrhh,
                defaults={
                    'nombre': 'RRHH',
                    'apellido': 'Sistema',
                    'dni': '12345678',
                    'email': 'rrhh@empresa.com',
                    'puesto': 'Recursos Humanos',
                    'area': 'RRHH',
                    'gerencia': 'RRHH',
                    'jerarquia': 1,
                    'es_rrhh': True,
                    'dias_vacaciones_disponibles': 30
                }
            )
            resultados.append(f"RRHH: {'creado' if created_emp else 'ya existía'}")

            # Usuario Manager
            user_manager, created_user = User.objects.get_or_create(
                username='manager',
                defaults={
                    'email': 'manager@empresa.com'
                }
            )
            if created_user:
                user_manager.set_password('manager123456')
                user_manager.save()
                
            empleado_manager, created_emp = Empleado.objects.get_or_create(
                user=user_manager,
                defaults={
                    'nombre': 'Manager',
                    'apellido': 'Prueba',
                    'dni': '87654321',
                    'email': 'manager@empresa.com',
                    'puesto': 'Gerente',
                    'area': 'Ventas',
                    'gerencia': 'Comercial',
                    'jerarquia': 2,
                    'dias_vacaciones_disponibles': 30
                }
            )
            resultados.append(f"Manager: {'creado' if created_emp else 'ya existía'}")

            # Usuario Empleado
            user_empleado, created_user = User.objects.get_or_create(
                username='empleado',
                defaults={
                    'email': 'empleado@empresa.com'
                }
            )
            if created_user:
                user_empleado.set_password('empleado123456')
                user_empleado.save()
                
            empleado_regular, created_emp = Empleado.objects.get_or_create(
                user=user_empleado,
                defaults={
                    'nombre': 'Juan',
                    'apellido': 'Pérez',
                    'dni': '11223344',
                    'email': 'empleado@empresa.com',
                    'puesto': 'Analista',
                    'area': 'Ventas',
                    'gerencia': 'Comercial',
                    'jerarquia': 7,
                    'manager': empleado_manager,
                    'dias_vacaciones_disponibles': 30
                }
            )
            resultados.append(f"Empleado: {'creado' if created_emp else 'ya existía'}")

            return JsonResponse({
                'status': 'success',
                'message': 'Proceso completado exitosamente',
                'resultados': resultados,
                'total_usuarios': User.objects.count(),
                'total_empleados': Empleado.objects.count(),
                'credenciales': {
                    'rrhh': 'rrhh / rrhh123456',
                    'manager': 'manager / manager123456',
                    'empleado': 'empleado / empleado123456'
                }
            })

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error en el proceso: {str(e)}'
            }, status=500)
