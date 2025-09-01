# empleados/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, date, timedelta
from .models import Empleado, SolicitudVacaciones, SolicitudNuevoColaborador
from .forms import SolicitudVacacionesForm, SolicitudNuevoColaboradorForm

def login_empleado(request):
    """
    Vista personalizada para el login de empleados
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'¡Bienvenido, {user.username}!')
            return redirect('inicio_empleado')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos. Inténtalo de nuevo.')
    
    return render(request, 'empleados/login.html')

def logout_empleado(request):
    """
    Vista para cerrar sesión
    """
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente.')
    return redirect('login_empleado')

@login_required
def inicio_empleado(request):
    """
    Vista de inicio para empleados autenticados
    """
    try:
        empleado = Empleado.objects.get(email=request.user.email)
        
        # Verificar si es manager
        es_manager = empleado.es_manager
        equipo_count = empleado.equipo.count() if es_manager else 0
        
        # Obtener solicitudes pendientes si es manager
        solicitudes_pendientes = None
        if es_manager:
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
        
        # Calcular días tomados en el período actual
        hoy = date.today()
        inicio_periodo = date(hoy.year, 1, 1)  # 1 de enero del año actual
        fin_periodo = date(hoy.year, 12, 31)   # 31 de diciembre del año actual
        
        # Días tomados en el período actual
        dias_tomados_periodo = sum(
            s.dias_solicitados for s in solicitudes_aprobadas 
            if s.fecha_inicio >= inicio_periodo and s.fecha_fin <= fin_periodo
        )
        
        # Días tomados totales (para cálculo de antigüedad)
        dias_tomados_total = sum(s.dias_solicitados for s in solicitudes_aprobadas)
        
        # Calcular días disponibles según antigüedad
        antiguedad = hoy - empleado.fecha_contratacion
        dias_por_antiguedad = 20  # Base
        
        if antiguedad.days >= 1825:  # Más de 5 años
            dias_por_antiguedad = 35
        elif antiguedad.days >= 730:  # Más de 2 años
            dias_por_antiguedad = 30
        elif antiguedad.days >= 365:  # Más de 1 año
            dias_por_antiguedad = 25
        
        # Días restantes del período actual
        dias_restantes_periodo = max(0, dias_por_antiguedad - dias_tomados_periodo)
        
        # Días restantes totales
        dias_restantes_total = max(0, dias_por_antiguedad - dias_tomados_total)
        
        # Calcular fecha límite para tomar vacaciones (generalmente 6 meses después del período)
        fecha_limite = fin_periodo + timedelta(days=180)  # 6 meses después
        
        # Verificar políticas de vacaciones
        politicas_info = []
        
        # Política: No más de 15 días consecutivos
        if dias_restantes_periodo > 15:
            politicas_info.append("⚠️ Máximo 15 días consecutivos por solicitud")
        
        # Política: Fines de semana no cuentan
        politicas_info.append("ℹ️ Los fines de semana no cuentan como días de vacaciones")
        
        # Política: Días festivos no cuentan
        politicas_info.append("ℹ️ Los días festivos no cuentan como días de vacaciones")
        
        # Política: Aviso previo
        politicas_info.append("ℹ️ Mínimo 15 días de aviso previo para solicitudes")
        
        # Alerta si quedan pocos días
        if dias_restantes_periodo <= 5:
            politicas_info.append("🚨 Solo quedan {} días disponibles en este período".format(dias_restantes_periodo))
        
        # Alerta si se acerca la fecha límite
        dias_hasta_limite = (fecha_limite - hoy).days
        if dias_hasta_limite <= 60:
            politicas_info.append("⏰ Fecha límite para tomar vacaciones: {} (en {} días)".format(
                fecha_limite.strftime("%d/%m/%Y"), dias_hasta_limite
            ))
        
        contexto = {
            'empleado': empleado,
            'es_manager': es_manager,
            'equipo_count': equipo_count,
            'solicitudes_pendientes': solicitudes_pendientes,
            # Información de vacaciones
            'dias_restantes_periodo': dias_restantes_periodo,
            'dias_restantes_total': dias_restantes_total,
            'dias_por_antiguedad': dias_por_antiguedad,
            'fecha_limite': fecha_limite,
            'politicas_info': politicas_info,
            'dias_tomados_periodo': dias_tomados_periodo,
            'antiguedad_dias': antiguedad.days,
            'solicitudes_pendientes_empleado': solicitudes_pendientes_empleado.count(),
            'user': request.user
        }
        
        return render(request, 'empleados/inicio.html', contexto)
        
    except Empleado.DoesNotExist:
        # Si el usuario no tiene perfil de empleado, lo redirigimos al login
        logout(request)
        messages.warning(request, 'Tu usuario no tiene un perfil de empleado asociado.')
        return redirect('login_empleado')

@login_required
def perfil_empleado(request):
    """
    Esta vista muestra y permite editar la información del perfil del empleado que ha iniciado sesión.
    Solo los empleados de RRHH pueden editar su perfil.
    """
    try:
        # Obtenemos el objeto 'Empleado' que corresponde al usuario actual.
        empleado = Empleado.objects.get(email=request.user.email)
        
        # Verificar si el empleado es de RRHH para permitir edición
        puede_editar = empleado.es_rrhh
        
        if request.method == 'POST':
            if not puede_editar:
                messages.error(request, 'Solo los empleados de RRHH pueden editar su perfil.')
                return redirect('perfil_empleado')
                
            from .forms import EmpleadoPerfilForm
            form = EmpleadoPerfilForm(request.POST, request.FILES, instance=empleado)
            if form.is_valid():
                form.save()
                messages.success(request, 'Tu perfil ha sido actualizado exitosamente.')
                return redirect('perfil_empleado')
        else:
            from .forms import EmpleadoPerfilForm
            form = EmpleadoPerfilForm(instance=empleado)
        
        contexto = {
            'empleado': empleado,
            'user': request.user,
            'form': form,
            'puede_editar': puede_editar
        }
        
    except Empleado.DoesNotExist:
        # Si no hay empleado asociado, mostramos un mensaje
        contexto = {
            'empleado': None,
            'user': request.user,
            'mensaje': 'No tienes un perfil de empleado asociado a tu cuenta.'
        }
    
    # Renderizamos la plantilla HTML y le pasamos el contexto.
    return render(request, 'empleados/perfil.html', contexto)

@login_required
def lista_solicitudes_vacaciones(request):
    """
    Vista para listar las solicitudes de vacaciones del empleado
    """
    try:
        empleado = Empleado.objects.get(email=request.user.email)
        solicitudes = SolicitudVacaciones.objects.filter(empleado=empleado).order_by('-fecha_solicitud')
        
        contexto = {
            'empleado': empleado,
            'solicitudes': solicitudes,
            'user': request.user
        }
        
    except Empleado.DoesNotExist:
        messages.error(request, 'No tienes un perfil de empleado asociado.')
        return redirect('login_empleado')
    
    return render(request, 'empleados/solicitudes_vacaciones.html', contexto)

@login_required
def nueva_solicitud_vacaciones(request):
    """
    Vista para crear una nueva solicitud de vacaciones
    """
    try:
        empleado = Empleado.objects.get(email=request.user.email)
    except Empleado.DoesNotExist:
        messages.error(request, 'No tienes un perfil de empleado asociado.')
        return redirect('login_empleado')
    
    # Calcular información de vacaciones del empleado
    from datetime import date, timedelta
    
    # Obtener solicitudes del empleado
    solicitudes = SolicitudVacaciones.objects.filter(empleado=empleado)
    solicitudes_aprobadas = solicitudes.filter(estado='aprobado')
    solicitudes_pendientes = solicitudes.filter(estado='pendiente')
    
    # Calcular días tomados en el período actual
    hoy = date.today()
    inicio_periodo = date(hoy.year, 1, 1)  # 1 de enero del año actual
    fin_periodo = date(hoy.year, 12, 31)   # 31 de diciembre del año actual
    
    # Días tomados en el período actual
    dias_tomados_periodo = sum(
        s.dias_solicitados for s in solicitudes_aprobadas 
        if s.fecha_inicio >= inicio_periodo and s.fecha_fin <= fin_periodo
    )
    
    # Días tomados totales (para cálculo de antigüedad)
    dias_tomados_total = sum(s.dias_solicitados for s in solicitudes_aprobadas)
    
    # Calcular días disponibles según antigüedad
    antiguedad = hoy - empleado.fecha_contratacion
    dias_por_antiguedad = 20  # Base
    
    if antiguedad.days >= 1825:  # Más de 5 años
        dias_por_antiguedad = 35
    elif antiguedad.days >= 730:  # Más de 2 años
        dias_por_antiguedad = 30
    elif antiguedad.days >= 365:  # Más de 1 año
        dias_por_antiguedad = 25
    
    # Días restantes del período actual
    dias_restantes_periodo = max(0, dias_por_antiguedad - dias_tomados_periodo)
    
    # Días restantes totales
    dias_restantes_total = max(0, dias_por_antiguedad - dias_tomados_total)
    
    # Calcular fecha límite para tomar vacaciones (generalmente 6 meses después del período)
    fecha_limite = fin_periodo + timedelta(days=180)  # 6 meses después
    
    # Verificar políticas de vacaciones
    politicas_info = []
    
    # Política: No más de 15 días consecutivos
    if dias_restantes_periodo > 15:
        politicas_info.append("⚠️ Máximo 15 días consecutivos por solicitud")
    
    # Política: Fines de semana no cuentan
    politicas_info.append("ℹ️ Los fines de semana no cuentan como días de vacaciones")
    
    # Política: Días festivos no cuentan
    politicas_info.append("ℹ️ Los días festivos no cuentan como días de vacaciones")
    
    # Política: Aviso previo
    politicas_info.append("ℹ️ Mínimo 15 días de aviso previo para solicitudes")
    
    # Alerta si quedan pocos días
    if dias_restantes_periodo <= 5:
        politicas_info.append("🚨 Solo quedan {} días disponibles en este período".format(dias_restantes_periodo))
    
    # Alerta si se acerca la fecha límite
    dias_hasta_limite = (fecha_limite - hoy).days
    if dias_hasta_limite <= 60:
        politicas_info.append("⏰ Fecha límite para tomar vacaciones: {} (en {} días)".format(
            fecha_limite.strftime("%d/%m/%Y"), dias_hasta_limite
        ))
    
    if request.method == 'POST':
        form = SolicitudVacacionesForm(request.POST)
        if form.is_valid():
            solicitud = form.save(commit=False)
            solicitud.empleado = empleado
            
            # Validar que la fecha de inicio no sea anterior a hoy
            if solicitud.fecha_inicio < date.today():
                messages.error(request, 'La fecha de inicio no puede ser anterior a hoy.')
                return render(request, 'empleados/nueva_solicitud_vacaciones.html', {
                    'form': form, 
                    'empleado': empleado,
                    'dias_restantes_periodo': dias_restantes_periodo,
                    'dias_restantes_total': dias_restantes_total,
                    'dias_por_antiguedad': dias_por_antiguedad,
                    'fecha_limite': fecha_limite,
                    'politicas_info': politicas_info,
                    'dias_tomados_periodo': dias_tomados_periodo,
                    'antiguedad_dias': antiguedad.days
                })
            
            # Validar que la fecha de fin no sea anterior a la de inicio
            if solicitud.fecha_fin < solicitud.fecha_inicio:
                messages.error(request, 'La fecha de fin no puede ser anterior a la fecha de inicio.')
                return render(request, 'empleados/nueva_solicitud_vacaciones.html', {
                    'form': form, 
                    'empleado': empleado,
                    'dias_restantes_periodo': dias_restantes_periodo,
                    'dias_restantes_total': dias_restantes_total,
                    'dias_por_antiguedad': dias_por_antiguedad,
                    'fecha_limite': fecha_limite,
                    'politicas_info': politicas_info,
                    'dias_tomados_periodo': dias_tomados_periodo,
                    'antiguedad_dias': antiguedad.days
                })
            
            # Calcular días solicitados
            delta = solicitud.fecha_fin - solicitud.fecha_inicio
            solicitud.dias_solicitados = delta.days + 1
            
            # Validar que no exceda días restantes del período
            if solicitud.dias_solicitados > dias_restantes_periodo:
                messages.error(
                    request, 
                    f'No puedes solicitar {solicitud.dias_solicitados} días. '
                    f'Solo tienes {dias_restantes_periodo} días disponibles en este período.'
                )
                return render(request, 'empleados/nueva_solicitud_vacaciones.html', {
                    'form': form, 
                    'empleado': empleado,
                    'dias_restantes_periodo': dias_restantes_periodo,
                    'dias_restantes_total': dias_restantes_total,
                    'dias_por_antiguedad': dias_por_antiguedad,
                    'fecha_limite': fecha_limite,
                    'politicas_info': politicas_info,
                    'dias_tomados_periodo': dias_tomados_periodo,
                    'antiguedad_dias': antiguedad.days
                })
            
            # Calcular automáticamente el tipo de vacaciones si no se especificó
            if not solicitud.tipo_vacaciones or solicitud.tipo_vacaciones == 'regulares':
                solicitud.tipo_vacaciones = solicitud.determinar_tipo_vacaciones()
            
            # Validar días disponibles según el tipo
            dias_disponibles = solicitud.calcular_dias_disponibles()
            if solicitud.dias_solicitados > dias_disponibles:
                messages.error(
                    request, 
                    f'No puedes solicitar {solicitud.dias_solicitados} días. '
                    f'Según tu tipo de vacaciones ({solicitud.get_tipo_vacaciones_display()}), '
                    f'tienes disponibles máximo {dias_disponibles} días.'
                )
                return render(request, 'empleados/nueva_solicitud_vacaciones.html', {
                    'form': form, 
                    'empleado': empleado,
                    'dias_restantes_periodo': dias_restantes_periodo,
                    'dias_restantes_total': dias_restantes_total,
                    'dias_por_antiguedad': dias_por_antiguedad,
                    'fecha_limite': fecha_limite,
                    'politicas_info': politicas_info,
                    'dias_tomados_periodo': dias_tomados_periodo,
                    'antiguedad_dias': antiguedad.days
                })
            
            solicitud.save()
            
            # Enviar notificación por email a los responsables de aprobar
            from .utils import enviar_notificacion_nueva_solicitud_vacaciones
            try:
                if enviar_notificacion_nueva_solicitud_vacaciones(solicitud):
                    messages.success(request, 'Solicitud de vacaciones enviada exitosamente. Se ha notificado a los responsables de la aprobación.')
                else:
                    messages.success(request, 'Solicitud de vacaciones enviada exitosamente.')
                    messages.warning(request, 'No se pudo enviar la notificación por email. Tu solicitud fue registrada correctamente.')
            except Exception as e:
                messages.success(request, 'Solicitud de vacaciones enviada exitosamente.')
                messages.warning(request, 'Hubo un problema enviando la notificación por email, pero tu solicitud fue registrada correctamente.')
            
            return redirect('solicitudes_vacaciones')
    else:
        form = SolicitudVacacionesForm()
        
        # Pre-calcular el tipo de vacaciones para mostrar en el formulario
        solicitud_temp = SolicitudVacaciones()
        solicitud_temp.empleado = empleado
        tipo_calculado = solicitud_temp.determinar_tipo_vacaciones()
        form.fields['tipo_vacaciones'].initial = tipo_calculado
    
    contexto = {
        'form': form,
        'empleado': empleado,
        'dias_restantes_periodo': dias_restantes_periodo,
        'dias_restantes_total': dias_restantes_total,
        'dias_por_antiguedad': dias_por_antiguedad,
        'fecha_limite': fecha_limite,
        'politicas_info': politicas_info,
        'dias_tomados_periodo': dias_tomados_periodo,
        'antiguedad_dias': antiguedad.days,
        'user': request.user
    }
    
    return render(request, 'empleados/nueva_solicitud_vacaciones.html', contexto)

@login_required
def detalle_solicitud_vacaciones(request, solicitud_id):
    """
    Vista para mostrar el detalle de una solicitud de vacaciones
    """
    try:
        empleado = Empleado.objects.get(email=request.user.email)
        solicitud = get_object_or_404(SolicitudVacaciones, id=solicitud_id, empleado=empleado)
        
        contexto = {
            'empleado': empleado,
            'solicitud': solicitud,
            'user': request.user
        }
        
    except Empleado.DoesNotExist:
        messages.error(request, 'No tienes un perfil de empleado asociado.')
        return redirect('login_empleado')
    
    return render(request, 'empleados/detalle_solicitud_vacaciones.html', contexto)

@login_required
def cancelar_solicitud_vacaciones(request, solicitud_id):
    """
    Vista para cancelar una solicitud de vacaciones
    """
    try:
        empleado = Empleado.objects.get(email=request.user.email)
        solicitud = get_object_or_404(SolicitudVacaciones, id=solicitud_id, empleado=empleado)
        
        if solicitud.puede_cancelar():
            solicitud.estado = 'cancelado'
            solicitud.save()
            messages.success(request, 'Solicitud de vacaciones cancelada exitosamente.')
        else:
            messages.error(request, 'No se puede cancelar esta solicitud.')
            
    except Empleado.DoesNotExist:
        messages.error(request, 'No tienes un perfil de empleado asociado.')
        return redirect('login_empleado')

    return redirect('solicitudes_vacaciones')

@login_required
def calcular_dias_vacaciones(request):
    """
    Vista AJAX para calcular días de vacaciones
    """
    if request.method == 'POST' and request.is_ajax():
        fecha_inicio = request.POST.get('fecha_inicio')
        fecha_fin = request.POST.get('fecha_fin')
        
        try:
            fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
            
            delta = fecha_fin - fecha_inicio
            dias = delta.days + 1
            
            return JsonResponse({'dias': dias, 'success': True})
        except ValueError:
            return JsonResponse({'error': 'Fechas inválidas', 'success': False})
    
    return JsonResponse({'error': 'Método no permitido', 'success': False})

@login_required
def manager_dashboard(request):
    """
    Dashboard para managers - muestra solicitudes de vacaciones de su equipo
    """
    try:
        empleado = Empleado.objects.get(email=request.user.email)
        
        # Verificar si es manager
        if not empleado.es_manager:
            messages.error(request, 'No tienes permisos de manager para acceder a esta página.')
            return redirect('inicio_empleado')
        
        # Obtener solicitudes pendientes del equipo
        solicitudes_pendientes = SolicitudVacaciones.objects.filter(
            empleado__manager=empleado,
            estado='pendiente'
        ).order_by('fecha_solicitud')
        
        # Obtener solicitudes recientes del equipo
        solicitudes_recientes = SolicitudVacaciones.objects.filter(
            empleado__manager=empleado
        ).exclude(estado='pendiente').order_by('-fecha_resolucion')[:10]
        
        # Estadísticas del equipo
        total_empleados = empleado.equipo.count()
        solicitudes_pendientes_count = solicitudes_pendientes.count()
        solicitudes_aprobadas_count = SolicitudVacaciones.objects.filter(
            empleado__manager=empleado,
            estado='aprobado'
        ).count()
        
        contexto = {
            'empleado': empleado,
            'solicitudes_pendientes': solicitudes_pendientes,
            'solicitudes_recientes': solicitudes_recientes,
            'total_empleados': total_empleados,
            'solicitudes_pendientes_count': solicitudes_pendientes_count,
            'solicitudes_aprobadas_count': solicitudes_aprobadas_count,
            'user': request.user
        }
        
    except Empleado.DoesNotExist:
        messages.error(request, 'No tienes un perfil de empleado asociado.')
        return redirect('login_empleado')
    
    return render(request, 'empleados/manager_dashboard.html', contexto)

@login_required
def procesar_solicitud_manager(request, solicitud_id):
    """
    Vista para que los managers aprueben o rechacen solicitudes
    """
    try:
        empleado = Empleado.objects.get(email=request.user.email)
        
        # Verificar si es manager
        if not empleado.es_manager:
            messages.error(request, 'No tienes permisos de manager.')
            return redirect('inicio_empleado')
        
        solicitud = get_object_or_404(SolicitudVacaciones, id=solicitud_id)
        
        # Verificar que la solicitud sea de su equipo
        if solicitud.empleado.manager != empleado:
            messages.error(request, 'No puedes procesar solicitudes de empleados que no están en tu equipo.')
            return redirect('manager_dashboard')
        
        if request.method == 'POST':
            accion = request.POST.get('accion')
            comentario = request.POST.get('comentario', '')
            
            if accion in ['aprobado', 'rechazado']:
                estado_anterior = solicitud.estado
                solicitud.estado = accion
                solicitud.fecha_resolucion = timezone.now()
                solicitud.procesado_por = empleado
                solicitud.comentario_admin = comentario
                solicitud.save()
                
                # Enviar notificación por email al empleado
                from .utils import enviar_notificacion_cambio_estado_solicitud
                try:
                    enviar_notificacion_cambio_estado_solicitud(solicitud, estado_anterior)
                except Exception as e:
                    # Log del error pero no interrumpir el proceso
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Error enviando notificación de cambio de estado: {str(e)}")
                
                # Mensaje de éxito
                if accion == 'aprobado':
                    messages.success(request, f'Solicitud de {solicitud.empleado.nombre} aprobada exitosamente. Se ha notificado al empleado.')
                else:
                    messages.success(request, f'Solicitud de {solicitud.empleado.nombre} rechazada. Se ha notificado al empleado.')
                
                return redirect('manager_dashboard')
        
        contexto = {
            'empleado': empleado,
            'solicitud': solicitud,
            'user': request.user
        }
        
    except Empleado.DoesNotExist:
        messages.error(request, 'No tienes un perfil de empleado asociado.')
        return redirect('login_empleado')
    
    return render(request, 'empleados/procesar_solicitud_manager.html', contexto)

@login_required
def equipo_manager(request):
    """
    Vista para que los managers vean su equipo
    """
    try:
        empleado = Empleado.objects.get(email=request.user.email)

        if not empleado.es_manager:
            messages.error(request, 'No tienes permisos de manager para acceder a esta página.')
            return redirect('inicio_empleado')

        # Obtener miembros del equipo
        equipo = empleado.equipo.all().order_by('nombre')
        
        # Estadísticas del equipo
        total_empleados = equipo.count()
        
        # Contar solicitudes por estado
        solicitudes_pendientes = 0
        solicitudes_aprobadas = 0
        solicitudes_rechazadas = 0
        
        for miembro in equipo:
            solicitudes = SolicitudVacaciones.objects.filter(empleado=miembro)
            solicitudes_pendientes += solicitudes.filter(estado='pendiente').count()
            solicitudes_aprobadas += solicitudes.filter(estado='aprobado').count()
            solicitudes_rechazadas += solicitudes.filter(estado='rechazado').count()
        
        contexto = {
            'empleado': empleado,
            'equipo': equipo,
            'total_empleados': total_empleados,
            'solicitudes_pendientes': solicitudes_pendientes,
            'solicitudes_aprobadas': solicitudes_aprobadas,
            'solicitudes_rechazadas': solicitudes_rechazadas,
            'user': request.user
        }

    except Empleado.DoesNotExist:
        messages.error(request, 'No tienes un perfil de empleado asociado.')
        return redirect('login_empleado')

    return render(request, 'empleados/equipo_manager.html', contexto)

@login_required
def rrhh_dashboard(request):
    """
    Dashboard para usuarios de RRHH - muestra todas las solicitudes de todas las áreas
    """
    try:
        empleado = Empleado.objects.get(email=request.user.email)
        
        # Verificar si es RRHH
        if not empleado.es_empleado_rrhh:
            messages.error(request, 'No tienes permisos de RRHH para acceder a esta página.')
            return redirect('inicio_empleado')
        
        # Obtener todas las solicitudes pendientes de todas las áreas
        solicitudes_pendientes = SolicitudVacaciones.objects.filter(
            estado='pendiente'
        ).order_by('fecha_solicitud')
        
        # Obtener solicitudes recientes de todas las áreas
        solicitudes_recientes = SolicitudVacaciones.objects.filter(
            estado__in=['aprobado', 'rechazado']
        ).order_by('-fecha_resolucion')[:20]
        
        # Estadísticas generales
        total_solicitudes = SolicitudVacaciones.objects.count()
        solicitudes_pendientes_count = solicitudes_pendientes.count()
        solicitudes_aprobadas_count = SolicitudVacaciones.objects.filter(estado='aprobado').count()
        solicitudes_rechazadas_count = SolicitudVacaciones.objects.filter(estado='rechazado').count()
        
        # Contar solicitudes por área (puesto)
        solicitudes_por_area = {}
        for solicitud in SolicitudVacaciones.objects.all():
            area = solicitud.empleado.puesto
            if area not in solicitudes_por_area:
                solicitudes_por_area[area] = {
                    'total': 0,
                    'pendientes': 0,
                    'aprobadas': 0,
                    'rechazadas': 0
                }
            solicitudes_por_area[area]['total'] += 1
            
            # Mapear el estado a la clave correcta del diccionario
            estado_clave = solicitud.estado
            if estado_clave == 'pendiente':
                solicitudes_por_area[area]['pendientes'] += 1
            elif estado_clave == 'aprobado':
                solicitudes_por_area[area]['aprobadas'] += 1
            elif estado_clave == 'rechazado':
                solicitudes_por_area[area]['rechazadas'] += 1
        
        # Nuevo Colaborador: pendientes y conteo total
        solicitudes_nc_pendientes = SolicitudNuevoColaborador.objects.filter(estado='pendiente').order_by('-fecha_solicitud')[:10]
        total_solicitudes_nuevo_colaborador = SolicitudNuevoColaborador.objects.count()

        contexto = {
            'empleado': empleado,
            'solicitudes_pendientes': solicitudes_pendientes,
            'solicitudes_recientes': solicitudes_recientes,
            'total_solicitudes': total_solicitudes,
            'solicitudes_pendientes_count': solicitudes_pendientes_count,
            'solicitudes_aprobadas_count': solicitudes_aprobadas_count,
            'solicitudes_rechazadas_count': solicitudes_rechazadas_count,
            'solicitudes_por_area': solicitudes_por_area,
            'solicitudes_nc_pendientes': solicitudes_nc_pendientes,
            'total_solicitudes_nuevo_colaborador': total_solicitudes_nuevo_colaborador,
            'user': request.user
        }
        
    except Empleado.DoesNotExist:
        messages.error(request, 'No tienes un perfil de empleado asociado.')
        return redirect('login_empleado')
    
    return render(request, 'empleados/rrhh_dashboard.html', contexto)


@login_required
def nueva_solicitud_nuevo_colaborador(request):
    try:
        empleado = Empleado.objects.get(email=request.user.email)
    except Empleado.DoesNotExist:
        messages.error(request, 'No tienes un perfil de empleado asociado.')
        return redirect('login_empleado')

    # Solo Jefes/Managers pueden crear
    if not (empleado.es_manager or 'Jefe' in empleado.puesto or 'Gerente' in empleado.puesto):
        messages.error(request, 'Solo Jefes o Gerentes pueden crear esta solicitud.')
        return redirect('inicio_empleado')

    # Queryset de posibles responsables: el manager + su equipo directo
    equipo_ids = list(empleado.equipo.values_list('id', flat=True))
    equipo_ids.append(empleado.id)
    responsables_qs = Empleado.objects.filter(id__in=equipo_ids).order_by('nombre', 'apellido')

    if request.method == 'POST':
        form = SolicitudNuevoColaboradorForm(request.POST, responsable_queryset=responsables_qs)
        if form.is_valid():
            solicitud = form.save(commit=False)
            solicitud.solicitante = empleado
            # Completar campos desde datos del empleado si vienen vacíos
            if not solicitud.area_solicitante:
                solicitud.area_solicitante = empleado.puesto
            if not solicitud.persona_responsable:
                solicitud.persona_responsable = f"{empleado.nombre} {empleado.apellido}".strip()
            if not solicitud.modalidad_contratacion:
                solicitud.modalidad_contratacion = 'Indefinido'
            solicitud.save()
            messages.success(request, 'Solicitud de nuevo colaborador enviada para revisión de RRHH.')
            return redirect('inicio_empleado')
    else:
        form = SolicitudNuevoColaboradorForm(
            initial={
                'area_solicitante': empleado.puesto,
                'modalidad_contratacion': 'Indefinido'
            },
            responsable_queryset=responsables_qs,
            responsable_initial=empleado.id
        )

    return render(request, 'empleados/nueva_solicitud_nuevo_colaborador.html', {
        'form': form,
        'empleado': empleado,
        'user': request.user
    })


@login_required
def lista_solicitudes_nuevo_colaborador(request):
    try:
        empleado = Empleado.objects.get(email=request.user.email)
    except Empleado.DoesNotExist:
        messages.error(request, 'No tienes un perfil de empleado asociado.')
        return redirect('login_empleado')

    # Si es RRHH ve todas, si no solo las propias
    if empleado.es_empleado_rrhh:
        solicitudes = SolicitudNuevoColaborador.objects.all().order_by('-fecha_solicitud')
    else:
        solicitudes = SolicitudNuevoColaborador.objects.filter(solicitante=empleado).order_by('-fecha_solicitud')

    return render(request, 'empleados/lista_solicitudes_nuevo_colaborador.html', {
        'solicitudes': solicitudes,
        'empleado': empleado,
        'user': request.user
    })


@login_required
def procesar_solicitud_nuevo_colaborador_rrhh(request, solicitud_id: int):
    try:
        empleado = Empleado.objects.get(email=request.user.email)
    except Empleado.DoesNotExist:
        messages.error(request, 'No tienes un perfil de empleado asociado.')
        return redirect('login_empleado')

    if not empleado.es_empleado_rrhh:
        messages.error(request, 'No tienes permisos de RRHH.')
        return redirect('inicio_empleado')

    solicitud = get_object_or_404(SolicitudNuevoColaborador, id=solicitud_id)

    if request.method == 'POST':
        accion = request.POST.get('accion')  # 'aprobado' | 'rechazado' | 'observado'
        comentario = request.POST.get('comentario', '')

        # Validaciones RRHH solo si se aprueba
        if accion == 'aprobado':
            errores = solicitud.validar_campos_rrhh()
            if errores:
                for e in errores:
                    messages.error(request, e)
                return render(request, 'empleados/procesar_solicitud_nuevo_colaborador.html', {
                    'solicitud': solicitud,
                    'empleado': empleado,
                    'user': request.user
                })

        if accion in ['aprobado', 'rechazado', 'observado']:
            solicitud.estado = accion
            solicitud.fecha_resolucion = timezone.now()
            solicitud.procesado_por = empleado
            solicitud.comentario_rrhh = comentario
            solicitud.save()
            messages.success(request, f'Solicitud procesada: {accion}.')
            return redirect('lista_solicitudes_nuevo_colaborador')

    return render(request, 'empleados/procesar_solicitud_nuevo_colaborador.html', {
        'solicitud': solicitud,
        'empleado': empleado,
        'user': request.user
    })

@login_required
def procesar_solicitud_rrhh(request, solicitud_id):
    """
    Vista para que RRHH procese solicitudes de todas las áreas
    """
    try:
        empleado = Empleado.objects.get(email=request.user.email)
        
        # Verificar si es RRHH
        if not empleado.es_empleado_rrhh:
            messages.error(request, 'No tienes permisos de RRHH.')
            return redirect('inicio_empleado')
        
        solicitud = get_object_or_404(SolicitudVacaciones, id=solicitud_id)
        
        if request.method == 'POST':
            accion = request.POST.get('accion')
            comentario = request.POST.get('comentario', '')
            
            if accion in ['aprobado', 'rechazado']:
                # Validar políticas antes de aprobar
                if accion == 'aprobado':
                    errores_validacion = solicitud.validar_politica_vacaciones()
                    if errores_validacion:
                        for error in errores_validacion:
                            messages.error(request, error)
                        return render(request, 'empleados/procesar_solicitud_rrhh.html', {
                            'empleado': empleado,
                            'solicitud': solicitud,
                            'user': request.user
                        })
                
                estado_anterior = solicitud.estado
                solicitud.estado = accion
                solicitud.fecha_resolucion = timezone.now()
                solicitud.procesado_por = empleado
                solicitud.comentario_admin = comentario
                solicitud.save()
                
                # Enviar notificación por email al empleado
                from .utils import enviar_notificacion_cambio_estado_solicitud
                try:
                    enviar_notificacion_cambio_estado_solicitud(solicitud, estado_anterior)
                except Exception as e:
                    # Log del error pero no interrumpir el proceso
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Error enviando notificación de cambio de estado: {str(e)}")
                
                # Mensaje de éxito
                if accion == 'aprobado':
                    messages.success(request, f'Solicitud de {solicitud.empleado.nombre} aprobada por RRHH. Se ha notificado al empleado.')
                else:
                    messages.success(request, f'Solicitud de {solicitud.empleado.nombre} rechazada por RRHH. Se ha notificado al empleado.')
                
                return redirect('rrhh_dashboard')
        
        contexto = {
            'empleado': empleado,
            'solicitud': solicitud,
            'user': request.user
        }
        
    except Empleado.DoesNotExist:
        messages.error(request, 'No tienes un perfil de empleado asociado.')
        return redirect('login_empleado')
    
    return render(request, 'empleados/procesar_solicitud_rrhh.html', contexto)

@login_required
def rrhh_historial_vacaciones(request):
    try:
        empleado = Empleado.objects.get(email=request.user.email)
    except Empleado.DoesNotExist:
        messages.error(request, 'No tienes un perfil de empleado asociado.')
        return redirect('login_empleado')

    if not empleado.es_empleado_rrhh:
        messages.error(request, 'No tienes permisos de RRHH para acceder a esta página.')
        return redirect('inicio_empleado')

    qs = SolicitudVacaciones.objects.all().order_by('-fecha_solicitud')

    # Filtros
    estado = request.GET.get('estado')  # pendiente | aprobado | rechazado | cancelado
    desde = request.GET.get('desde')
    hasta = request.GET.get('hasta')

    if estado:
        qs = qs.filter(estado=estado)
    if desde:
        try:
            d = datetime.strptime(desde, '%Y-%m-%d').date()
            qs = qs.filter(fecha_solicitud__date__gte=d)
        except ValueError:
            pass
    if hasta:
        try:
            h = datetime.strptime(hasta, '%Y-%m-%d').date()
            qs = qs.filter(fecha_solicitud__date__lte=h)
        except ValueError:
            pass

    return render(request, 'empleados/rrhh_historial_vacaciones.html', {
        'empleado': empleado,
        'solicitudes': qs,
        'f_estado': estado or '',
        'f_desde': desde or '',
        'f_hasta': hasta or '',
        'user': request.user
    })


@login_required
def rrhh_historial_nuevo_colaborador(request):
    try:
        empleado = Empleado.objects.get(email=request.user.email)
    except Empleado.DoesNotExist:
        messages.error(request, 'No tienes un perfil de empleado asociado.')
        return redirect('login_empleado')

    if not empleado.es_empleado_rrhh:
        messages.error(request, 'No tienes permisos de RRHH para acceder a esta página.')
        return redirect('inicio_empleado')

    qs = SolicitudNuevoColaborador.objects.all().order_by('-fecha_solicitud')

    # Filtros
    estado = request.GET.get('estado')  # pendiente | aprobado | rechazado | observado
    desde = request.GET.get('desde')
    hasta = request.GET.get('hasta')

    if estado:
        qs = qs.filter(estado=estado)
    if desde:
        try:
            d = datetime.strptime(desde, '%Y-%m-%d').date()
            qs = qs.filter(fecha_solicitud__gte=d)
        except ValueError:
            pass
    if hasta:
        try:
            h = datetime.strptime(hasta, '%Y-%m-%d').date()
            qs = qs.filter(fecha_solicitud__lte=h)
        except ValueError:
            pass

    return render(request, 'empleados/rrhh_historial_nuevo_colaborador.html', {
        'empleado': empleado,
        'solicitudes': qs,
        'f_estado': estado or '',
        'f_desde': desde or '',
        'f_hasta': hasta or '',
        'user': request.user
    })

@login_required
def rrhh_control_vacaciones(request):
    """
    Vista para que RRHH controle días de vacaciones de cada empleado
    """
    try:
        empleado = Empleado.objects.get(email=request.user.email)
    except Empleado.DoesNotExist:
        messages.error(request, 'No tienes un perfil de empleado asociado.')
        return redirect('login_empleado')

    if not empleado.es_empleado_rrhh:
        messages.error(request, 'No tienes permisos de RRHH para acceder a esta página.')
        return redirect('inicio_empleado')

    # Obtener todos los empleados con información de vacaciones
    empleados = Empleado.objects.all().order_by('nombre', 'apellido')
    
    # Calcular estadísticas de vacaciones para cada empleado
    empleados_vacaciones = []
    for emp in empleados:
        # Solicitudes del empleado
        solicitudes = SolicitudVacaciones.objects.filter(empleado=emp)
        solicitudes_aprobadas = solicitudes.filter(estado='aprobado')
        solicitudes_pendientes = solicitudes.filter(estado='pendiente')
        
        # Calcular días tomados
        dias_tomados = sum(s.dias_solicitados for s in solicitudes_aprobadas)
        
        # Calcular días disponibles según antigüedad
        from datetime import date
        hoy = date.today()
        antiguedad = hoy - emp.fecha_contratacion
        dias_por_antiguedad = 20  # Base
        
        if antiguedad.days >= 365:  # Más de 1 año
            dias_por_antiguedad = 25
        if antiguedad.days >= 730:  # Más de 2 años
            dias_por_antiguedad = 30
        if antiguedad.days >= 1825:  # Más de 5 años
            dias_por_antiguedad = 35
        
        # Días restantes
        dias_restantes = max(0, dias_por_antiguedad - dias_tomados)
        
        # Alertas
        alertas = []
        
        # Alerta por días próximos a vencer
        if dias_restantes <= 5 and dias_restantes > 0:
            alertas.append(f"⚠️ Solo {dias_restantes} días restantes")
        
        # Alerta por próximo período vacacional
        if antiguedad.days >= 365 and antiguedad.days < 395:  # Próximo a cumplir 1 año
            alertas.append("🔄 Próximo a cumplir 1 año (nuevo período)")
        elif antiguedad.days >= 730 and antiguedad.days < 760:  # Próximo a cumplir 2 años
            alertas.append("🔄 Próximo a cumplir 2 años (nuevo período)")
        
        # Alerta por solicitudes pendientes
        if solicitudes_pendientes.exists():
            dias_pendientes = sum(s.dias_solicitados for s in solicitudes_pendientes)
            if dias_pendientes > dias_restantes:
                alertas.append(f"🚨 Solicitud pendiente excede días disponibles ({dias_pendientes} > {dias_restantes})")
        
        # Verificar políticas en solicitudes recientes
        solicitudes_recientes = solicitudes_aprobadas.filter(fecha_resolucion__gte=timezone.now() - timezone.timedelta(days=90))
        for solicitud in solicitudes_recientes:
            errores_politica = solicitud.validar_politica_vacaciones()
            if errores_politica:
                alertas.append(f"📋 Política: {', '.join(errores_politica[:2])}")
        
        empleados_vacaciones.append({
            'empleado': emp,
            'dias_tomados': dias_tomados,
            'dias_restantes': dias_restantes,
            'dias_por_antiguedad': dias_por_antiguedad,
            'solicitudes_pendientes': solicitudes_pendientes.count(),
            'dias_pendientes': sum(s.dias_solicitados for s in solicitudes_pendientes),
            'antiguedad_dias': antiguedad.days,
            'alertas': alertas,
            'ultima_solicitud': solicitudes.order_by('-fecha_solicitud').first()
        })

    return render(request, 'empleados/rrhh_control_vacaciones.html', {
        'empleado': empleado,
        'empleados_vacaciones': empleados_vacaciones,
        'user': request.user
    })


@login_required
def rrhh_notificar_manager_vacaciones(request, empleado_id):
    """
    Vista para que RRHH notifique a un manager sobre situación de vacaciones de su empleado
    """
    try:
        empleado_rrhh = Empleado.objects.get(email=request.user.email)
    except Empleado.DoesNotExist:
        messages.error(request, 'No tienes un perfil de empleado asociado.')
        return redirect('login_empleado')

    if not empleado_rrhh.es_empleado_rrhh:
        messages.error(request, 'No tienes permisos de RRHH.')
        return redirect('inicio_empleado')

    empleado = get_object_or_404(Empleado, id=empleado_id)
    
    if request.method == 'POST':
        mensaje = request.POST.get('mensaje', '')
        tipo_alerta = request.POST.get('tipo_alerta', 'general')
        
        # Aquí podrías implementar el envío de notificación
        # Por ahora solo mostramos un mensaje de éxito
        messages.success(request, f'Notificación enviada al manager de {empleado.nombre} {empleado.apellido}')
        return redirect('rrhh_control_vacaciones')

    return render(request, 'empleados/rrhh_notificar_manager.html', {
        'empleado_rrhh': empleado_rrhh,
        'empleado': empleado,
        'user': request.user
    })