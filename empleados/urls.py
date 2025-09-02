# empleados/urls.py
from django.urls import path
from . import views
from . import views_notificaciones
from . import setup_views
from . import setup_simple
from . import setup_admin
from . import crear_superusuario
from . import ver_datos
from . import fix_admin
from . import views_setup

urlpatterns = [
    # URL TEMPORAL para inicializar datos en producción (ELIMINAR DESPUÉS DE USAR)
    path('setup/inicializar/', setup_views.inicializar_datos_produccion, name='inicializar_produccion'),
    path('setup/simple/', setup_simple.setup_simple, name='setup_simple'),
    path('setup/admin/', setup_admin.hacer_admin, name='hacer_admin'),
    path('setup/superuser/', crear_superusuario.crear_superusuario, name='crear_superusuario'),
    path('setup/organigrama/', views_setup.cargar_usuarios_organigrama, name='cargar_organigrama'),
    path('datos/', ver_datos.ver_datos_existentes, name='ver_datos_existentes'),
    path('fix-admin/', fix_admin.fix_admin_access, name='fix_admin_access'),
    
    # URL para la página raíz
    path('', views.inicio_empleado, name='inicio_empleado'),

    # URLs de autenticación
    path('login/', views.login_empleado, name='login_empleado'),
    path('logout/', views.logout_empleado, name='logout_empleado'),

    # URLs de la aplicación principal
    path('perfil/', views.perfil_empleado, name='perfil_empleado'),

    # URLs para Solicitudes de Vacaciones
    path('vacaciones/', views.lista_solicitudes_vacaciones, name='solicitudes_vacaciones'),
    path('vacaciones/nueva/', views.nueva_solicitud_vacaciones, name='nueva_solicitud_vacaciones'),
    path('vacaciones/<int:solicitud_id>/', views.detalle_solicitud_vacaciones, name='detalle_solicitud_vacaciones'),
    path('vacaciones/<int:solicitud_id>/cancelar/', views.cancelar_solicitud_vacaciones, name='cancelar_solicitud_vacaciones'),

    # URL para AJAX
    path('vacaciones/calcular-dias/', views.calcular_dias_vacaciones, name='calcular_dias_vacaciones'),

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
]