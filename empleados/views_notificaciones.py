"""
Vista para configurar las notificaciones de email desde el panel de RRHH
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import Empleado, SolicitudVacaciones


@login_required
def configurar_notificaciones(request):
    """
    Vista para que RRHH configure las notificaciones por email
    """
    try:
        empleado = Empleado.objects.get(email=request.user.email)
        
        # Verificar si es RRHH
        if not empleado.es_rrhh:
            messages.error(request, 'No tienes permisos para acceder a esta configuración.')
            return redirect('inicio_empleado')
        
        if request.method == 'POST':
            accion = request.POST.get('accion')
            
            if accion == 'test_email':
                # Enviar email de prueba
                try:
                    send_mail(
                        subject='🔧 Prueba de Configuración - Sistema RRHH',
                        message='Este es un email de prueba del Sistema de RRHH. Si recibes este mensaje, la configuración está funcionando correctamente.',
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[empleado.email],
                        fail_silently=False
                    )
                    messages.success(request, f'Email de prueba enviado exitosamente a {empleado.email}')
                except Exception as e:
                    messages.error(request, f'Error enviando email de prueba: {str(e)}')
            
            elif accion == 'enviar_recordatorios':
                # Ejecutar comando de recordatorios manualmente
                from django.core.management import call_command
                from io import StringIO
                
                try:
                    output = StringIO()
                    call_command('enviar_recordatorios', stdout=output)
                    result = output.getvalue()
                    messages.success(request, 'Recordatorios enviados. Revisa la terminal para más detalles.')
                except Exception as e:
                    messages.error(request, f'Error enviando recordatorios: {str(e)}')
        
        # Obtener estadísticas
        from .models import SolicitudVacaciones
        from django.utils import timezone
        from datetime import timedelta
        
        # Solicitudes pendientes
        solicitudes_pendientes = SolicitudVacaciones.objects.filter(estado='pendiente')
        
        # Solicitudes pendientes antiguas (más de 2 días)
        fecha_limite = timezone.now() - timedelta(days=2)
        solicitudes_antiguas = solicitudes_pendientes.filter(fecha_solicitud__lte=fecha_limite)
        
        # Personal de RRHH
        personal_rrhh = Empleado.objects.filter(es_rrhh=True)
        
        # Managers y jefes con capacidad de gestión de equipos
        managers = Empleado.objects.filter(
            jerarquia__in=['director', 'gerente', 'sub_gerente', 'jefe']
        )
        
        contexto = {
            'empleado': empleado,
            'user': request.user,
            'solicitudes_pendientes_count': solicitudes_pendientes.count(),
            'solicitudes_antiguas_count': solicitudes_antiguas.count(),
            'personal_rrhh': personal_rrhh,
            'managers': managers,
            'email_backend': settings.EMAIL_BACKEND,
            'from_email': settings.DEFAULT_FROM_EMAIL
        }
        
    except Empleado.DoesNotExist:
        messages.error(request, 'No tienes un perfil de empleado asociado.')
        return redirect('login_empleado')
    
    return render(request, 'empleados/configurar_notificaciones.html', contexto)
