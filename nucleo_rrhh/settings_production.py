import os
import sys
import dj_database_url
from .settings import *

# Debug setting for deployment
DEBUG = True  # Cambiar a False después de verificar que funciona

# Configuración de zona horaria para Perú
LANGUAGE_CODE = 'es-pe'
TIME_ZONE = 'America/Lima'
USE_I18N = True
USE_TZ = True

# Render provides the hostname
ALLOWED_HOSTS = [
    'tea-d2f53dumcj7s738afjo0.onrender.com',
    '.onrender.com',
    'localhost',
    '127.0.0.1',
    '*'  # Temporal para debugging
]

# Database configuration - Usar SQLite para que la aplicación funcione
# Supabase se configurará manualmente después usando las herramientas web

# Usar SQLite temporalmente hasta que se configure Supabase
print("🔧 Usando SQLite temporal - visita / para inicializar o /empleados/setup/emergencia/")
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/tmp/app.db',
        'OPTIONS': {
            'timeout': 20,
        }
    }
}

# Información de Supabase para configuración posterior
SUPABASE_DATABASE_URL = "postgresql://postgres:3jbxqfv$2gyW$yG@db.mwjdmmowllmxygscgcex.supabase.co:5432/postgres"
print(f"💡 URL de Supabase disponible: {SUPABASE_DATABASE_URL[:60]}...")
print("🔧 Visita /setup/diagnostico/ para verificar y configurar Supabase")

# Static files configuration
STATIC_URL = '/static/'
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

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Use environment variable for secret key in production
SECRET_KEY = os.environ.get('SECRET_KEY', SECRET_KEY)

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

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
