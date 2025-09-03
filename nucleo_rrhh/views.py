from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.http import HttpResponse

def root_redirect(request):
    """Redirección inteligente desde la raíz de la aplicación"""
    
    # Si no hay usuarios, redirigir a inicialización de emergencia
    if User.objects.count() == 0:
        return redirect('/empleados/setup/emergencia/')
    
    # Si hay usuarios, redirigir al sistema principal
    return redirect('/empleados/')

def health_check(request):
    """Endpoint básico de health check para Render"""
    try:
        # Verificar que Django funcione
        user_count = User.objects.count()
        return HttpResponse(f"OK - Sistema RRHH funcionando. Usuarios: {user_count}")
    except Exception as e:
        return HttpResponse(f"ERROR: {str(e)}", status=500)
