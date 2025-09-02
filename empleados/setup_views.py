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
        <html>
        <head><title>Inicializar Datos - Sistema RRHH</title></head>
        <body style="font-family: Arial; padding: 20px;">
            <h2>Estado Actual de la Base de Datos</h2>
            <p><strong>Usuarios existentes:</strong> {usuarios_existentes}</p>
            <p><strong>Empleados existentes:</strong> {empleados_existentes}</p>
            
            <h3>Crear Datos Iniciales</h3>
            <button onclick="inicializar()" style="padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 5px;">
                Crear Empleados y Asociaciones
            </button>
            
            <div id="resultado" style="margin-top: 20px;"></div>
            
            <script>
            function inicializar() {{
                fetch('/setup/inicializar/', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                    }}
                }})
                .then(response => response.json())
                .then(data => {{
                    document.getElementById('resultado').innerHTML = 
                        '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
                }});
            }}
            </script>
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
