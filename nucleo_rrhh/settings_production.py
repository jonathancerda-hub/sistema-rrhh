import os
import sys
import dj_database_url
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# --- Core Settings ---
ROOT_URLCONF = 'nucleo_rrhh.urls'
WSGI_APPLICATION = 'nucleo_rrhh.wsgi.application'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Debug setting for deployment
DEBUG = os.environ.get('DEBUG', '0') == '1'

# Configuración de zona horaria para Perú
LANGUAGE_CODE = 'es-pe'
TIME_ZONE = 'America/Lima'
USE_I18N = True
USE_TZ = True

# --- Installed Apps ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'empleados',  # Tu app principal
]

# Optimizaciones para memoria
CONN_MAX_AGE = 60  # Reutilizar conexiones de BD
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB máximo

# Render provides the hostname
ALLOWED_HOSTS = [
    os.environ.get('RENDER_EXTERNAL_HOSTNAME'),
]
# Add render.com hostnames to allowed hosts
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# --- Configuración de Base de Datos para Producción ---
# Lee la URL de la base de datos desde las variables de entorno de Render.
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("CRITICAL: No se ha configurado la variable de entorno DATABASE_URL en Render.")

# Verificación para asegurar que se está usando la URL del Pooler de Supabase
if '.pooler.supabase.com' not in DATABASE_URL:
    raise ValueError(f"CRITICAL: La DATABASE_URL no parece ser la URL del Connection Pooler de Supabase. "
                     f"Asegúrate de usar la URL que contiene '.pooler.supabase.com'. URL detectada: {DATABASE_URL[:70]}...")
 
DATABASES = {
    'default': dj_database_url.config(
        default=DATABASE_URL,
        conn_max_age=600,      # Reutilizar conexiones por 10 minutos
        conn_health_checks=True # Habilitar chequeos de salud de la conexión
    )
}

# Forzar el uso de SSL para la conexión a la base de datos, como se requiere en Supabase.
DATABASES['default']['OPTIONS'] = {
    'sslmode': 'require',
}

# Static files configuration
STATIC_URL = '/static/'
STATICFILES_DIRS = [] # Anular STATICFILES_DIRS del settings base para producción
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Whitenoise configuration
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# --- Templates ---
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Use environment variable for secret key in production
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("CRITICAL: No se ha configurado la variable de entorno SECRET_KEY en Render.")

# Logging configuration optimizado
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'WARNING',  # Solo mensajes importantes
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'ERROR',  # Solo errores de Django
            'propagate': False,
        },
        'django.db': {
            'handlers': [],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

# --- Media Files ---
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Email configuration
if os.environ.get('EMAIL_HOST'):
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = os.environ.get('EMAIL_HOST')
    EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
    DEFAULT_FROM_EMAIL = f'Sistema RRHH <{EMAIL_HOST_USER}>'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    DEFAULT_FROM_EMAIL = 'Sistema RRHH <noreply@empresa.com>'

# --- Supabase Storage for Media Files ---
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
SUPABASE_BUCKET = os.environ.get('SUPABASE_BUCKET')

if SUPABASE_URL and SUPABASE_KEY and SUPABASE_BUCKET:
    # Configuración para archivos de medios (subidos por usuarios)
    DEFAULT_FILE_STORAGE = 'storages.backends.supabase.SupabaseStorage'
    # Configuración para archivos estáticos (opcional, pero recomendado)
    # STATICFILES_STORAGE = 'storages.backends.supabase.SupabaseStorage'
    # Las variables de Supabase se leen automáticamente por django-storages
