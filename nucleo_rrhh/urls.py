# nucleo_rrhh/urls.py - SISTEMA RRHH SIMPLIFICADO

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Importar vistas de diagnóstico
from diagnostico_views import diagnostico_produccion, forzar_migraciones

# Importar vistas de emergencia (sin autenticación)
from emergency_views import health_check_simple, emergency_migrate

urlpatterns = [
    # URLs de emergencia - DEBEN ir primero (sin middleware de sesiones)
    path('health/', health_check_simple, name='health_check'),
    path('emergency-migrate/', emergency_migrate, name='emergency_migrate'),
    
    path('admin/', admin.site.urls),
    path('', include('empleados.urls')),
    # Endpoints de diagnóstico para producción
    path('diagnostico/', diagnostico_produccion, name='diagnostico'),
    path('fix-migrations/', forzar_migraciones, name='fix_migrations'),
]

# Servir archivos de media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)