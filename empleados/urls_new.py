# empleados/urls.py
from django.urls import path
from . import views
from . import views_notificaciones
from . import login_debug
from . import listar_usuarios
from . import login_agrovet
from . import views_estado

urlpatterns = [
    # URLs principales del sistema
    path('', views.inicio, name='inicio'),
    path('login/', views.login_empleado, name='login'),
    path('logout/', views.logout_empleado, name='logout'),
    path('perfil/', views.perfil, name='perfil'),
    
    # Solicitudes de vacaciones
    path('solicitud/', views.nueva_solicitud, name='nueva_solicitud'),
    path('solicitud/nueva/', views.nueva_solicitud_vacaciones, name='nueva_solicitud_vacaciones'),
    path('solicitudes/', views.lista_solicitudes, name='lista_solicitudes'),
    path('solicitudes/detalle/<int:solicitud_id>/', views.detalle_solicitud_vacaciones, name='detalle_solicitud_vacaciones'),
    
    # URLs para Managers
    path('manager/', views.manager_dashboard, name='manager_dashboard'),
    path('manager/equipo/', views.equipo_manager, name='equipo_manager'),
    path('manager/solicitud/<int:solicitud_id>/procesar/', views.procesar_solicitud_manager, name='procesar_solicitud_manager'),
    path('manager/empleado/<int:empleado_id>/perfil/', views.ver_perfil_empleado, name='ver_perfil_empleado'),
    path('manager/empleado/<int:empleado_id>/solicitudes/', views.ver_solicitudes_empleado, name='ver_solicitudes_empleado'),
    path('manager/empleado/<int:empleado_id>/solicitud/<int:solicitud_id>/', views.detalle_solicitud_empleado, name='detalle_solicitud_empleado'),
    
    # Solicitud de Nuevo Colaborador (crean Jefes/Managers)
    path('colaboradores/nuevo/', views.nueva_solicitud_nuevo_colaborador, name='nueva_solicitud_nuevo_colaborador'),
    path('colaboradores/solicitudes/', views.lista_solicitudes_nuevo_colaborador, name='lista_solicitudes_nuevo_colaborador'),
    
    # URLs para RRHH
    path('rrhh/', views.rrhh_dashboard, name='rrhh_dashboard'),
    path('rrhh/solicitud/<int:solicitud_id>/procesar/', views.procesar_solicitud_rrhh, name='procesar_solicitud_rrhh'),
    path('rrhh/colaboradores/<int:solicitud_id>/procesar/', views.procesar_solicitud_nuevo_colaborador_rrhh, name='procesar_solicitud_nuevo_colaborador_rrhh'),
    # Historiales RRHH
    path('rrhh/historial/vacaciones/', views.rrhh_historial_vacaciones, name='rrhh_historial_vacaciones'),
    path('rrhh/historial/nuevo-colaborador/', views.rrhh_historial_nuevo_colaborador, name='rrhh_historial_nuevo_colaborador'),
    # Control de vacaciones RRHH
    path('rrhh/control-vacaciones/', views.rrhh_control_vacaciones, name='rrhh_control_vacaciones'),
    path('rrhh/notificar-manager/<int:empleado_id>/', views.rrhh_notificar_manager_vacaciones, name='rrhh_notificar_manager_vacaciones'),
    # Gestión de empleados RRHH
    path('rrhh/empleados/', views.rrhh_lista_empleados, name='rrhh_lista_empleados'),
    path('rrhh/empleados/<int:empleado_id>/editar/', views.rrhh_editar_empleado, name='rrhh_editar_empleado'),
    path('rrhh/empleados/<int:empleado_id>/offboarding/', views.rrhh_offboarding_empleado, name='rrhh_offboarding_empleado'),
    # Configuración de notificaciones
    path('rrhh/configurar-notificaciones/', views_notificaciones.configurar_notificaciones, name='configurar_notificaciones'),
    
    # URLs de diagnóstico y AgroVet - Solo las esenciales
    path('login-debug/', login_debug.login_debug_view, name='login_debug'),
    path('usuarios/', listar_usuarios.listar_usuarios_view, name='listar_usuarios'),
    path('agrovet/', login_agrovet.login_agrovet_view, name='login_agrovet'),
    path('estado/', views_estado.estado_sistema, name='estado_sistema'),
]
