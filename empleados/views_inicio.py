from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.db import connection
from django.core.exceptions import OperationalError
from .views_estado import sistema_no_inicializado, verificar_estado_sistema

def inicio_sistema(request):
    """
    Vista de inicio que maneja el caso cuando las tablas no existen
    """
    try:
        # Intentar verificar si existen las tablas básicas
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='django_session';")
            tabla_sesion = cursor.fetchone()
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='auth_user';")
            tabla_user = cursor.fetchone()
        
        # Si las tablas no existen, mostrar página de inicialización
        if not tabla_sesion or not tabla_user:
            return sistema_no_inicializado(request)
        
        # Si las tablas existen, verificar si hay usuarios
        try:
            user_count = User.objects.count()
            if user_count == 0:
                return redirect('/empleados/setup/emergencia/')
        except OperationalError:
            return sistema_no_inicializado(request)
        
        # Si el usuario está autenticado, ir al dashboard normal
        if request.user.is_authenticated:
            return redirect('/empleados/dashboard/')
        
        # Si no está autenticado pero el sistema está inicializado, ir al login
        return redirect('/empleados/login/')
        
    except Exception as e:
        # En caso de cualquier error, mostrar página de inicialización
        return sistema_no_inicializado(request)

def dashboard_empleado(request):
    """
    Vista del dashboard que reemplaza inicio_empleado pero sin @login_required
    """
    # Si no está autenticado, redirigir al login
    if not request.user.is_authenticated:
        return redirect('/empleados/login/')
    
    try:
        from .models import Empleado, SolicitudVacaciones
        empleado = Empleado.objects.get(email=request.user.email)
        
        # Verificar si es manager o puede gestionar equipos
        puede_gestionar_equipo = empleado.puede_gestionar_equipo
        equipo_count = empleado.equipo.count() if puede_gestionar_equipo else 0
        
        # Obtener solicitudes pendientes si puede gestionar equipos
        solicitudes_pendientes = None
        if puede_gestionar_equipo:
            solicitudes_pendientes = SolicitudVacaciones.objects.filter(
                empleado__manager=empleado,
                estado='pendiente'
            ).count()
        
        # Calcular información de vacaciones del empleado
        from datetime import date, timedelta
        
        # Obtener solicitudes del empleado
        solicitudes = SolicitudVacaciones.objects.filter(empleado=empleado)
        solicitudes_aprobadas = solicitudes.filter(estado='aprobado')
        solicitudes_pendientes_empleado = solicitudes.filter(estado='pendiente')
        
        # Calcular días usados en el año actual
        año_actual = date.today().year
        solicitudes_año_actual = solicitudes_aprobadas.filter(fecha_inicio__year=año_actual)
        
        dias_usados = 0
        for solicitud in solicitudes_año_actual:
            dias_usados += solicitud.dias_solicitados
        
        # Contexto para el template
        context = {
            'empleado': empleado,
            'puede_gestionar_equipo': puede_gestionar_equipo,
            'equipo_count': equipo_count,
            'solicitudes_pendientes': solicitudes_pendientes,
            'solicitudes_pendientes_empleado': solicitudes_pendientes_empleado.count(),
            'dias_disponibles': empleado.dias_vacaciones_disponibles,
            'dias_usados': dias_usados,
            'dias_restantes': empleado.dias_vacaciones_disponibles - dias_usados,
        }
        
        return render(request, 'empleados/inicio.html', context)
        
    except Exception as e:
        # Si hay error, mostrar página de error amigable
        return HttpResponse(f"""
            <html>
            <head><title>Error del Sistema</title></head>
            <body style="font-family: Arial; padding: 40px;">
                <h1>⚠️ Error del Sistema</h1>
                <p>Hay un problema con tu cuenta de empleado.</p>
                <p><strong>Error:</strong> {str(e)}</p>
                <p><a href="/empleados/setup/emergencia/">🔧 Ir a Configuración de Emergencia</a></p>
                <p><a href="/empleados/login/">🔐 Intentar Login</a></p>
                <p><a href="/admin/">⚙️ Panel de Admin</a></p>
            </body>
            </html>
        """)
