# nucleo_rrhh/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', views.health_check, name='health_check'),
    path('simple/', views.vista_simple_root, name='vista_simple_root'),
    path('empleados/', include('empleados.urls')),
    path('', views.root_redirect, name='root_redirect'),
]

# Servir archivos de media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)