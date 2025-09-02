# empleados/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db import models, transaction
from datetime import datetime, date, timedelta
import secrets
import string
import pytz
from .models import Empleado, SolicitudVacaciones, SolicitudNuevoColaborador
from .forms import SolicitudVacacionesForm, SolicitudNuevoColaboradorForm

def obtener_fecha_lima():
    """
    Obtiene la fecha actual en zona horaria de Lima, Perú
    """
    lima_tz = pytz.timezone('America/Lima')
    return timezone.now().astimezone(lima_tz)

def obtener_solo_fecha_lima():
    """
    Obtiene solo la fecha (sin hora) en zona horaria de Lima, Perú
    """
    return obtener_fecha_lima().date()

def generar_password_temporal():
    """
    Genera una contraseña temporal segura de 12 caracteres
    """
    caracteres = string.ascii_letters + string.digits
    return ''.join(secrets.choice(caracteres) for _ in range(12))

def mapear_denominacion_a_jerarquia(denominacion_puesto):
    """
    Mapea la denominación del puesto a la jerarquía del empleado
    """
    mapeo = {
        'gerente': 'gerente',
        'sub_gerente': 'sub_gerente',
        'jefe': 'jefe',
        'supervisor': 'supervisor',
        'analista': 'asistente',  # Los analistas van como asistentes
        'coordinador': 'coordinador',
    }
    return mapeo.get(denominacion_puesto, 'auxiliar')  # auxiliar por defecto

def mapear_area_a_gerencia(area_solicitante):
    """
    Mapea el área solicitante a una gerencia específica
    """
    mapeo = {
        'comercial': 'gerencia_comercial_local',
        'internacional': 'gerencia_comercial_internacional',
        'recursos humanos': 'gerencia_desarrollo_organizacional',
        'rrhh': 'gerencia_desarrollo_organizacional',
        'finanzas': 'gerencia_administracion_finanzas',
        'administracion': 'gerencia_administracion_finanzas',
        'contabilidad': 'gerencia_administracion_finanzas',
    }
    
    # Buscar coincidencias parciales en el área
    area_lower = area_solicitante.lower()
    for key, value in mapeo.items():
        if key in area_lower:
            return value
    
    # Por defecto, usar gerencia de desarrollo organizacional
    return 'gerencia_desarrollo_organizacional'

def mapear_area_a_gerencia(area):
    """
    Mapea el área a una gerencia válida
    """
    area_lower = area.lower()
    if 'comercial' in area_lower and ('local' in area_lower or 'nacional' in area_lower):
        return 'gerencia_comercial_local'
    elif 'comercial' in area_lower and ('internacional' in area_lower or 'export' in area_lower):
        return 'gerencia_comercial_internacional'
    elif 'desarrollo' in area_lower or 'organizacional' in area_lower or 'rrhh' in area_lower:
        return 'gerencia_desarrollo_organizacional'
    elif 'administracion' in area_lower or 'finanzas' in area_lower or 'contabilidad' in area_lower:
        return 'gerencia_administracion_finanzas'
    else:
        return 'gerencia_administracion_finanzas'  # Por defecto

def normalizar_texto_username(texto):
    """
    Normaliza texto para usar como username removiendo acentos y caracteres especiales
    """
    import unicodedata
    # Remover acentos
    texto_normalizado = unicodedata.normalize('NFD', texto)
    texto_sin_acentos = ''.join(c for c in texto_normalizado if unicodedata.category(c) != 'Mn')
    # Convertir a minúsculas y remover espacios
    texto_limpio = texto_sin_acentos.lower().replace(" ", "")
    return texto_limpio

def crear_empleado_desde_solicitud(solicitud, procesado_por):
    """
    Crea un usuario y empleado a partir de una solicitud aprobada
    """
    try:
        with transaction.atomic():
            # Generar username único basado en nombre.apellido
            nombre_normalizado = normalizar_texto_username(solicitud.nombre_colaborador)
            apellido_normalizado = normalizar_texto_username(solicitud.apellido_colaborador)
            username_base = f"{nombre_normalizado}.{apellido_normalizado}"
            username = username_base
            
            # Si ya existe, agregar un número al final
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{username_base}{counter}"
                counter += 1
            
            # Crear usuario
            password_temporal = generar_password_temporal()
            user = User.objects.create_user(
                username=username,
                email=solicitud.email_colaborador,
                password=password_temporal,
                first_name=solicitud.nombre_colaborador,
                last_name=solicitud.apellido_colaborador
            )
            
            # Mapear denominación a jerarquía y área a gerencia
            jerarquia = mapear_denominacion_a_jerarquia(solicitud.denominacion_puesto)
            gerencia = mapear_area_a_gerencia(solicitud.area_solicitante)
            
            # Crear empleado
            empleado = Empleado.objects.create(
                user=user,
                nombre=solicitud.nombre_colaborador,
                apellido=solicitud.apellido_colaborador,
                dni=solicitud.dni_colaborador,
                email=solicitud.email_colaborador,
                puesto=solicitud.puesto_a_solicitud,
                area=solicitud.area_solicitante,
                gerencia=gerencia,
                jerarquia=jerarquia,
                manager=solicitud.solicitante,  # El que solicitó será el manager
                fecha_contratacion=solicitud.fecha_inicio_labores if solicitud.fecha_inicio_labores else timezone.now().date(),
                es_rrhh=False,
                dias_vacaciones_disponibles=30  # 30 días por defecto
            )
            
            return user, empleado, password_temporal
            
    except Exception as e:
        raise Exception(f"Error al crear empleado: {str(e)}")

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
        if empleado.fecha_contratacion:
            antiguedad = hoy - empleado.fecha_contratacion
            dias_por_antiguedad = 20  # Base
            
            if antiguedad.days >= 1825:  # Más de 5 años
                dias_por_antiguedad = 35
            elif antiguedad.days >= 730:  # Más de 2 años
                dias_por_antiguedad = 30
            elif antiguedad.days >= 365:  # Más de 1 año
                dias_por_antiguedad = 25
        else:
            # Si no tiene fecha de contratación, asumir días base
            antiguedad = None
            dias_por_antiguedad = 20
        
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
            'puede_gestionar_equipo': puede_gestionar_equipo,
            'equipo_count': equipo_count,
            'solicitudes_pendientes': solicitudes_pendientes,
            # Información de vacaciones
            'dias_restantes_periodo': dias_restantes_periodo,
            'dias_restantes_total': dias_restantes_total,
            'dias_por_antiguedad': dias_por_antiguedad,
            'fecha_limite': fecha_limite,
            'politicas_info': politicas_info,
            'dias_tomados_periodo': dias_tomados_periodo,
            'antiguedad_dias': antiguedad.days if antiguedad else 0,
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
    if empleado.fecha_contratacion:
        antiguedad = hoy - empleado.fecha_contratacion
        dias_por_antiguedad = 20  # Base
        
        if antiguedad.days >= 1825:  # Más de 5 años
            dias_por_antiguedad = 35
        elif antiguedad.days >= 730:  # Más de 2 años
            dias_por_antiguedad = 30
        elif antiguedad.days >= 365:  # Más de 1 año
            dias_por_antiguedad = 25
    else:
        # Si no tiene fecha de contratación, asumir días base
        antiguedad = None
        dias_por_antiguedad = 20
    
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
                    'antiguedad_dias': antiguedad.days if antiguedad else 0
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
                    'antiguedad_dias': antiguedad.days if antiguedad else 0
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
                    'antiguedad_dias': antiguedad.days if antiguedad else 0
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
                    'antiguedad_dias': antiguedad.days if antiguedad else 0
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
        'antiguedad_dias': antiguedad.days if antiguedad else 0,
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
    Dashboard para managers y jefes - muestra solicitudes de vacaciones de su equipo
    """
    try:
        empleado = Empleado.objects.get(email=request.user.email)
        
        # Verificar si puede gestionar equipos (managers o jefes)
        if not empleado.puede_gestionar_equipo:
            messages.error(request, 'No tienes permisos para gestionar equipos.')
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
        
        # Verificar si puede gestionar equipos (managers o jefes)
        if not empleado.puede_gestionar_equipo:
            messages.error(request, 'No tienes permisos para procesar solicitudes de equipo.')
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
    Vista para que los managers y jefes vean su equipo
    """
    try:
        empleado = Empleado.objects.get(email=request.user.email)

        if not empleado.puede_gestionar_equipo:
            messages.error(request, 'No tienes permisos para gestionar equipos.')
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
    if not empleado.puede_gestionar_equipo:
        messages.error(request, 'Solo usuarios con permisos de gestión pueden crear esta solicitud.')
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

    # Obtener mensajes de sesión si existen
    mensaje_procesamiento = request.session.pop('mensaje_procesamiento', None)
    tipo_mensaje = request.session.pop('tipo_mensaje', None)

    return render(request, 'empleados/lista_solicitudes_nuevo_colaborador.html', {
        'solicitudes': solicitudes,
        'empleado': empleado,
        'user': request.user,
        'mensaje_procesamiento': mensaje_procesamiento,
        'tipo_mensaje': tipo_mensaje
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
            # Si se aprueba la solicitud, crear automáticamente el empleado
            if accion == 'aprobado':
                try:
                    user, nuevo_empleado, password_temporal = crear_empleado_desde_solicitud(solicitud, empleado)
                    
                    # Actualizar la solicitud
                    solicitud.estado = accion
                    solicitud.fecha_resolucion = timezone.now()
                    solicitud.procesado_por = empleado
                    solicitud.comentario_rrhh = comentario
                    solicitud.save()
                    
                    # Redirigir a una página especial con las credenciales
                    return render(request, 'empleados/empleado_creado_exitoso.html', {
                        'solicitud': solicitud,
                        'nuevo_empleado': nuevo_empleado,
                        'username': user.username,
                        'password_temporal': password_temporal,
                        'empleado': empleado,
                        'user': request.user,
                        'mensaje_exito': 'Empleado creado exitosamente',
                        'mensaje_info': f'Usuario creado: {user.username}',
                        'mensaje_warning': 'IMPORTANTE: Guarda estas credenciales y entrégalas al nuevo empleado'
                    })
                    
                except Exception as e:
                    return render(request, 'empleados/procesar_solicitud_nuevo_colaborador.html', {
                        'solicitud': solicitud,
                        'empleado': empleado,
                        'user': request.user,
                        'error_mensaje': f'Error al crear el empleado: {str(e)}',
                        'error_tipo': 'error'
                    })
            else:
                # Solo actualizar la solicitud si se rechaza u observa
                solicitud.estado = accion
                solicitud.fecha_resolucion = timezone.now()
                solicitud.procesado_por = empleado
                solicitud.comentario_rrhh = comentario
                solicitud.save()
                
                # Usar sesión para mostrar mensaje en la siguiente página
                if accion == 'rechazado':
                    request.session['mensaje_procesamiento'] = f'Solicitud rechazada exitosamente'
                    request.session['tipo_mensaje'] = 'warning'
                elif accion == 'observado':
                    request.session['mensaje_procesamiento'] = f'Solicitud marcada como observada'
                    request.session['tipo_mensaje'] = 'info'
            
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
        if emp.fecha_contratacion:
            antiguedad = hoy - emp.fecha_contratacion
            dias_por_antiguedad = 20  # Base
            
            if antiguedad.days >= 365:  # Más de 1 año
                dias_por_antiguedad = 25
            if antiguedad.days >= 730:  # Más de 2 años
                dias_por_antiguedad = 30
            if antiguedad.days >= 1825:  # Más de 5 años
                dias_por_antiguedad = 35
        else:
            # Si no tiene fecha de contratación, asumir días base
            antiguedad = None
            dias_por_antiguedad = 20
        
        # Días restantes
        dias_restantes = max(0, dias_por_antiguedad - dias_tomados)
        
        # Alertas
        alertas = []
        
        # Alerta por días próximos a vencer
        if dias_restantes <= 5 and dias_restantes > 0:
            alertas.append(f"⚠️ Solo {dias_restantes} días restantes")
        
        # Alerta por próximo período vacacional
        if antiguedad and antiguedad.days >= 365 and antiguedad.days < 395:  # Próximo a cumplir 1 año
            alertas.append("🔄 Próximo a cumplir 1 año (nuevo período)")
        elif antiguedad and antiguedad.days >= 730 and antiguedad.days < 760:  # Próximo a cumplir 2 años
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
            'antiguedad_dias': antiguedad.days if antiguedad else 0,
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


@login_required
def rrhh_lista_empleados(request):
    """
    Vista para que RRHH vea la lista completa de empleados con todas sus funcionalidades
    """
    try:
        empleado_rrhh = Empleado.objects.get(email=request.user.email)
        if not empleado_rrhh.es_rrhh:
            messages.error(request, 'No tienes permisos para acceder a esta sección.')
            return redirect('inicio_empleado')
    except Empleado.DoesNotExist:
        messages.error(request, 'Empleado no encontrado.')
        return redirect('login_empleado')

    # Filtros de búsqueda
    search_query = request.GET.get('search', '')
    area_filter = request.GET.get('area', '')
    gerencia_filter = request.GET.get('gerencia', '')
    jerarquia_filter = request.GET.get('jerarquia', '')
    estado_filter = request.GET.get('estado', '')

    # Obtener empleados con filtros
    empleados = Empleado.objects.all()

    if search_query:
        empleados = empleados.filter(
            models.Q(nombre__icontains=search_query) |
            models.Q(apellido__icontains=search_query) |
            models.Q(dni__icontains=search_query) |
            models.Q(email__icontains=search_query) |
            models.Q(puesto__icontains=search_query)
        )

    if area_filter:
        empleados = empleados.filter(area__icontains=area_filter)

    if gerencia_filter:
        empleados = empleados.filter(gerencia=gerencia_filter)

    if jerarquia_filter:
        empleados = empleados.filter(jerarquia=jerarquia_filter)

    if estado_filter == 'activo':
        empleados = empleados.filter(user__is_active=True)
    elif estado_filter == 'inactivo':
        empleados = empleados.filter(user__is_active=False)

    # Ordenar por apellido y nombre
    empleados = empleados.order_by('apellido', 'nombre')

    # Obtener opciones para filtros
    areas_disponibles = Empleado.objects.exclude(area__isnull=True).exclude(area='').values_list('area', flat=True).distinct()
    gerencias_disponibles = [choice[0] for choice in Empleado.GERENCIA_CHOICES]
    jerarquias_disponibles = [choice[0] for choice in Empleado.JERARQUIA_CHOICES]

    context = {
        'empleado_rrhh': empleado_rrhh,
        'empleados': empleados,
        'user': request.user,
        'search_query': search_query,
        'area_filter': area_filter,
        'gerencia_filter': gerencia_filter,
        'jerarquia_filter': jerarquia_filter,
        'estado_filter': estado_filter,
        'areas_disponibles': areas_disponibles,
        'gerencias_disponibles': gerencias_disponibles,
        'jerarquias_disponibles': jerarquias_disponibles,
        'total_empleados': empleados.count(),
    }

    return render(request, 'empleados/rrhh_lista_empleados.html', context)


@login_required
def rrhh_editar_empleado(request, empleado_id):
    """
    Vista para que RRHH edite un empleado específico
    """
    try:
        empleado_rrhh = Empleado.objects.get(email=request.user.email)
        if not empleado_rrhh.es_rrhh:
            messages.error(request, 'No tienes permisos para acceder a esta sección.')
            return redirect('inicio_empleado')
    except Empleado.DoesNotExist:
        messages.error(request, 'Empleado no encontrado.')
        return redirect('login_empleado')

    empleado = get_object_or_404(Empleado, id=empleado_id)

    if request.method == 'POST':
        # Actualizar información del empleado
        empleado.nombre = request.POST.get('nombre', empleado.nombre)
        empleado.apellido = request.POST.get('apellido', empleado.apellido)
        empleado.dni = request.POST.get('dni', empleado.dni)
        empleado.email = request.POST.get('email', empleado.email)
        empleado.puesto = request.POST.get('puesto', empleado.puesto)
        empleado.area = request.POST.get('area', empleado.area)
        empleado.gerencia = request.POST.get('gerencia', empleado.gerencia)
        empleado.jerarquia = request.POST.get('jerarquia', empleado.jerarquia)
        empleado.dias_vacaciones_disponibles = int(request.POST.get('dias_vacaciones', empleado.dias_vacaciones_disponibles))
        empleado.es_rrhh = request.POST.get('es_rrhh') == 'on'

        # Actualizar manager si se especifica
        manager_id = request.POST.get('manager')
        if manager_id:
            try:
                empleado.manager = Empleado.objects.get(id=manager_id)
            except Empleado.DoesNotExist:
                empleado.manager = None
        else:
            empleado.manager = None

        # Actualizar estado del usuario
        usuario_activo = request.POST.get('usuario_activo') == 'on'
        if empleado.user:
            empleado.user.is_active = usuario_activo
            empleado.user.save()

        try:
            empleado.save()
            messages.success(request, f'Empleado {empleado.nombre} {empleado.apellido} actualizado exitosamente.')
            return redirect('rrhh_lista_empleados')
        except Exception as e:
            messages.error(request, f'Error al actualizar empleado: {str(e)}')

    # Obtener lista de posibles managers (empleados que pueden gestionar equipos)
    posibles_managers = Empleado.objects.filter(
        jerarquia__in=['director', 'gerente', 'sub_gerente', 'jefe']
    ).exclude(id=empleado.id)

    context = {
        'empleado_rrhh': empleado_rrhh,
        'empleado': empleado,
        'posibles_managers': posibles_managers,
        'gerencias_disponibles': Empleado.GERENCIA_CHOICES,
        'jerarquias_disponibles': Empleado.JERARQUIA_CHOICES,
        'user': request.user
    }

    return render(request, 'empleados/rrhh_editar_empleado.html', context)


@login_required
def rrhh_offboarding_empleado(request, empleado_id):
    """
    Vista para el proceso de offboarding (baja) de un empleado
    """
    try:
        empleado_rrhh = Empleado.objects.get(email=request.user.email)
        if not empleado_rrhh.es_rrhh:
            messages.error(request, 'No tienes permisos para acceder a esta sección.')
            return redirect('inicio_empleado')
    except Empleado.DoesNotExist:
        messages.error(request, 'Empleado no encontrado.')
        return redirect('login_empleado')

    empleado = get_object_or_404(Empleado, id=empleado_id)

    if request.method == 'POST':
        tipo_baja = request.POST.get('tipo_baja')
        fecha_baja = request.POST.get('fecha_baja')
        motivo = request.POST.get('motivo', '')
        observaciones = request.POST.get('observaciones', '')

        # Desactivar cuenta de usuario
        if empleado.user:
            empleado.user.is_active = False
            empleado.user.save()

        # Aquí podrías agregar más lógica de offboarding como:
        # - Crear registro en tabla de bajas
        # - Enviar notificaciones
        # - Transferir responsabilidades
        # - etc.

        messages.success(request, f'Proceso de offboarding completado para {empleado.nombre} {empleado.apellido}')
        return redirect('rrhh_lista_empleados')

    context = {
        'empleado_rrhh': empleado_rrhh,
        'empleado': empleado,
        'user': request.user
    }

    return render(request, 'empleados/rrhh_offboarding_empleado.html', context)


@login_required
def ver_perfil_empleado(request, empleado_id):
    """
    Vista para que managers/jefes vean el perfil de un miembro de su equipo
    """
    try:
        empleado_actual = Empleado.objects.get(email=request.user.email)
        
        # Verificar permisos: solo managers/jefes pueden ver perfiles de su equipo
        if not empleado_actual.puede_gestionar_equipo:
            messages.error(request, 'No tienes permisos para ver este perfil.')
            return redirect('inicio_empleado')
        
        # Obtener el empleado cuyo perfil se quiere ver
        empleado = get_object_or_404(Empleado, id=empleado_id)
        
        # Verificar que el empleado pertenece al equipo del manager
        if empleado.manager != empleado_actual:
            messages.error(request, 'Solo puedes ver perfiles de tu equipo.')
            return redirect('equipo_manager')
        
        context = {
            'empleado': empleado,
            'empleado_manager': empleado_actual,
            'user': request.user
        }
        
        return render(request, 'empleados/ver_perfil_empleado.html', context)
        
    except Empleado.DoesNotExist:
        messages.error(request, 'No tienes un perfil de empleado asociado.')
        return redirect('login_empleado')


@login_required 
def ver_solicitudes_empleado(request, empleado_id):
    """
    Vista para que managers/jefes vean las solicitudes de un miembro de su equipo
    """
    try:
        empleado_actual = Empleado.objects.get(email=request.user.email)
        
        # Verificar permisos: solo managers/jefes pueden ver solicitudes de su equipo
        if not empleado_actual.puede_gestionar_equipo:
            messages.error(request, 'No tienes permisos para ver estas solicitudes.')
            return redirect('inicio_empleado')
        
        # Obtener el empleado cuyas solicitudes se quieren ver
        empleado = get_object_or_404(Empleado, id=empleado_id)
        
        # Verificar que el empleado pertenece al equipo del manager
        if empleado.manager != empleado_actual:
            messages.error(request, 'Solo puedes ver solicitudes de tu equipo.')
            return redirect('equipo_manager')
        
        # Obtener solicitudes de vacaciones del empleado
        solicitudes_vacaciones = SolicitudVacaciones.objects.filter(
            empleado=empleado
        ).order_by('-fecha_solicitud')
        
        # Obtener solicitudes de nuevo colaborador creadas por el empleado
        solicitudes_colaborador = SolicitudNuevoColaborador.objects.filter(
            solicitante=empleado
        ).order_by('-fecha_solicitud')
        
        context = {
            'empleado': empleado,
            'empleado_manager': empleado_actual,
            'solicitudes_vacaciones': solicitudes_vacaciones,
            'solicitudes_colaborador': solicitudes_colaborador,
            'user': request.user
        }
        
        return render(request, 'empleados/ver_solicitudes_empleado.html', context)
        
    except Empleado.DoesNotExist:
        messages.error(request, 'No tienes un perfil de empleado asociado.')
        return redirect('login_empleado')


@login_required
def detalle_solicitud_empleado(request, empleado_id, solicitud_id):
    """
    Vista para que managers/jefes vean el detalle de una solicitud de un miembro de su equipo
    """
    try:
        empleado_actual = Empleado.objects.get(email=request.user.email)
        
        # Verificar permisos: solo managers/jefes pueden ver solicitudes de su equipo
        if not empleado_actual.puede_gestionar_equipo:
            messages.error(request, 'No tienes permisos para ver esta solicitud.')
            return redirect('inicio_empleado')
        
        # Obtener el empleado cuya solicitud se quiere ver
        empleado = get_object_or_404(Empleado, id=empleado_id)
        
        # Verificar que el empleado pertenece al equipo del manager
        if empleado.manager != empleado_actual:
            messages.error(request, 'Solo puedes ver solicitudes de tu equipo.')
            return redirect('equipo_manager')
        
        # Obtener la solicitud específica
        solicitud = get_object_or_404(SolicitudVacaciones, id=solicitud_id, empleado=empleado)
        
        context = {
            'empleado': empleado,
            'empleado_manager': empleado_actual,
            'solicitud': solicitud,
            'user': request.user
        }
        
        return render(request, 'empleados/detalle_solicitud_empleado.html', context)
        
    except Empleado.DoesNotExist:
        messages.error(request, 'No tienes un perfil de empleado asociado.')
        return redirect('login_empleado')