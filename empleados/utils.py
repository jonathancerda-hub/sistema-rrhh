"""
Utilidades para el envío de notificaciones por email
"""
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def enviar_notificacion_nueva_solicitud_vacaciones(solicitud):
    """
    Envía notificación por email cuando se crea una nueva solicitud de vacaciones
    """
    try:
        empleado = solicitud.empleado
        manager = empleado.manager
        
        # Lista de destinatarios
        destinatarios = []
        
        # Agregar manager si existe
        if manager and manager.email:
            destinatarios.append(manager.email)
        
        # Agregar personal de RRHH
        from .models import Empleado
        empleados_rrhh = Empleado.objects.filter(es_rrhh=True)
        for rrhh in empleados_rrhh:
            if rrhh.email and rrhh.email not in destinatarios:
                destinatarios.append(rrhh.email)
        
        if not destinatarios:
            logger.warning(f"No se encontraron destinatarios para la solicitud {solicitud.id}")
            return False
        
        # Preparar el contexto para el template
        contexto = {
            'solicitud': solicitud,
            'empleado': empleado,
            'manager': manager,
            'dias_solicitados': solicitud.dias_solicitados,
            'url_procesar': f"http://127.0.0.1:8000/empleados/manager/solicitud/{solicitud.id}/procesar/"
        }
        
        # Renderizar el email HTML
        html_message = render_to_string('empleados/emails/nueva_solicitud_vacaciones.html', contexto)
        plain_message = strip_tags(html_message)
        
        # Asunto del email
        asunto = f"📋 Nueva Solicitud de Vacaciones - {empleado.nombre} {empleado.apellido}"
        
        # Enviar email
        send_mail(
            subject=asunto,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=destinatarios,
            html_message=html_message,
            fail_silently=False
        )
        
        logger.info(f"Notificación enviada para solicitud {solicitud.id} a {destinatarios}")
        return True
        
    except Exception as e:
        logger.error(f"Error enviando notificación para solicitud {solicitud.id}: {str(e)}")
        return False


def enviar_notificacion_cambio_estado_solicitud(solicitud, estado_anterior):
    """
    Envía notificación cuando cambia el estado de una solicitud
    """
    try:
        empleado = solicitud.empleado
        
        # El destinatario es el empleado que hizo la solicitud
        if not empleado.email:
            logger.warning(f"Empleado {empleado.id} no tiene email configurado")
            return False
        
        # Preparar contexto
        contexto = {
            'solicitud': solicitud,
            'empleado': empleado,
            'estado_anterior': estado_anterior,
            'estado_actual': solicitud.estado,
        }
        
        # Renderizar email
        html_message = render_to_string('empleados/emails/cambio_estado_solicitud.html', contexto)
        plain_message = strip_tags(html_message)
        
        # Asunto según el estado
        estados_asunto = {
            'aprobado': f"✅ Tu solicitud de vacaciones ha sido APROBADA",
            'rechazado': f"❌ Tu solicitud de vacaciones ha sido RECHAZADA", 
            'cancelado': f"🚫 Tu solicitud de vacaciones ha sido CANCELADA"
        }
        
        asunto = estados_asunto.get(solicitud.estado, f"📄 Actualización de tu solicitud de vacaciones")
        
        # Enviar email
        send_mail(
            subject=asunto,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[empleado.email],
            html_message=html_message,
            fail_silently=False
        )
        
        logger.info(f"Notificación de cambio de estado enviada a {empleado.email} para solicitud {solicitud.id}")
        return True
        
    except Exception as e:
        logger.error(f"Error enviando notificación de cambio de estado para solicitud {solicitud.id}: {str(e)}")
        return False


def enviar_notificacion_recordatorio_aprobacion(solicitud):
    """
    Envía recordatorio para solicitudes pendientes de aprobación
    """
    try:
        empleado = solicitud.empleado
        manager = empleado.manager
        
        # Lista de destinatarios (manager y RRHH)
        destinatarios = []
        
        if manager and manager.email:
            destinatarios.append(manager.email)
        
        from .models import Empleado
        empleados_rrhh = Empleado.objects.filter(es_rrhh=True)
        for rrhh in empleados_rrhh:
            if rrhh.email and rrhh.email not in destinatarios:
                destinatarios.append(rrhh.email)
        
        if not destinatarios:
            return False
        
        # Contexto
        contexto = {
            'solicitud': solicitud,
            'empleado': empleado,
            'dias_pendientes': (solicitud.fecha_inicio - solicitud.fecha_solicitud).days,
            'url_procesar': f"http://127.0.0.1:8000/empleados/manager/solicitud/{solicitud.id}/procesar/"
        }
        
        # Renderizar email
        html_message = render_to_string('empleados/emails/recordatorio_aprobacion.html', contexto)
        plain_message = strip_tags(html_message)
        
        asunto = f"⏰ Recordatorio: Solicitud de vacaciones pendiente - {empleado.nombre} {empleado.apellido}"
        
        # Enviar email
        send_mail(
            subject=asunto,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=destinatarios,
            html_message=html_message,
            fail_silently=False
        )
        
        logger.info(f"Recordatorio enviado para solicitud {solicitud.id}")
        return True
        
    except Exception as e:
        logger.error(f"Error enviando recordatorio para solicitud {solicitud.id}: {str(e)}")
        return False
