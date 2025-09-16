# nucleo_rrhh/urls.py - SISTEMA RRHH SIMPLIFICADO

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Redirige la URL raíz (/) a la página de inicio de la app de empleados.
    path('', RedirectView.as_view(url='/empleados/', permanent=True)),
    
    # Incluye todas las URLs de la aplicación de empleados bajo el prefijo /empleados/
    path('empleados/', include('empleados.urls')),

    # --- URLs de Autenticación ---
    # Django busca por defecto el template en 'registration/login.html'
    # Usar la plantilla de login dentro de la app empleados para mantener el diseño
    path('login/', auth_views.LoginView.as_view(template_name='empleados/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
]

# Servir archivos de media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)