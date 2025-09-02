from django.http import JsonResponse
from django.contrib.auth.models import User
from empleados.models import Empleado
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def inicializar_datos_produccion(request):
    """
    Vista temporal para inicializar datos en producción cuando no hay acceso a shell.
    IMPORTANTE: Eliminar esta vista después de usar.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Solo método POST permitido'}, status=405)
    
    # Verificar si ya existen usuarios
    if User.objects.exists():
        return JsonResponse({
            'status': 'warning',
            'message': 'Ya existen usuarios en la base de datos',
            'usuarios_existentes': User.objects.count()
        })
    
    try:
        # Crear usuario RRHH
        user_rrhh = User.objects.create_user('rrhh', 'rrhh@empresa.com', 'rrhh123456')
        empleado_rrhh = Empleado.objects.create(
            user=user_rrhh,
            nombre='RRHH',
            apellido='Sistema',
            dni='12345678',
            email='rrhh@empresa.com',
            puesto='Recursos Humanos',
            area='RRHH',
            gerencia='RRHH',
            jerarquia=1,
            es_rrhh=True,
            dias_vacaciones_disponibles=30
        )

        # Crear usuario manager
        user_manager = User.objects.create_user('manager', 'manager@empresa.com', 'manager123456')
        empleado_manager = Empleado.objects.create(
            user=user_manager,
            nombre='Manager',
            apellido='Prueba',
            dni='87654321',
            email='manager@empresa.com',
            puesto='Gerente',
            area='Ventas',
            gerencia='Comercial',
            jerarquia=2,
            dias_vacaciones_disponibles=30
        )

        # Crear usuario empleado
        user_empleado = User.objects.create_user('empleado', 'empleado@empresa.com', 'empleado123456')
        empleado_regular = Empleado.objects.create(
            user=user_empleado,
            nombre='Juan',
            apellido='Pérez',
            dni='11223344',
            email='empleado@empresa.com',
            puesto='Analista',
            area='Ventas',
            gerencia='Comercial',
            jerarquia=7,
            manager=empleado_manager,
            dias_vacaciones_disponibles=30
        )

        return JsonResponse({
            'status': 'success',
            'message': 'Usuarios creados exitosamente',
            'credenciales': {
                'rrhh': 'rrhh / rrhh123456',
                'manager': 'manager / manager123456',
                'empleado': 'empleado / empleado123456'
            }
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error creando usuarios: {str(e)}'
        }, status=500)
