# nucleo_rrhh/urls.py - SISTEMA RRHH SIMPLIFICADO

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # La URL raíz ahora apunta directamente a la app de empleados
    path('', include('empleados.urls')), 
]

# Servir archivos de media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)