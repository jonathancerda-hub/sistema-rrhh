from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.models import User
from empleados.models import Empleado
from django.conf import settings

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
