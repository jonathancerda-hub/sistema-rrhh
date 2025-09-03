import os
import sys
import dj_database_url
from .settings import *

# Temporary debug for deployment issues
DEBUG = True  # Cambiar a False después de verificar que funciona

# Configuración de zona horaria para Perú
LANGUAGE_CODE = 'es-pe'
TIME_ZONE = 'America/Lima'
USE_I18N = True
USE_TZ = True

# Override settings for production

# Render provides the hostname
ALLOWED_HOSTS = [
    'tea-d2f53dumcj7s738afjo0.onrender.com',
    '.onrender.com',  # Permite cualquier subdominio de onrender.com
    'localhost',
    '127.0.0.1',
    '*'  # Temporal para debugging (quitar en producción final)
]

# Database configuration - Usar SQLite durante build, Supabase en runtime
DATABASE_URL = os.environ.get('DATABASE_URL')

# Usar SQLite por defecto para evitar problemas de conectividad durante el build
# Supabase se configurará después del deploy mediante las herramientas web
print("📦 Usando SQLite para build seguro")
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/tmp/app.db',  # En Render, usar directorio temporal
    }
}

# Información para configuración posterior
SUPABASE_URL = "postgresql://postgres:3jbxqfv$2gyW$yG@db.mwjdmmowllmxygscgcex.supabase.co:5432/postgres"
print(f"💡 Supabase URL disponible para configuración: {SUPABASE_URL[:50]}...")
print("🔧 Usa /setup/diagnostico/ para verificar la conexión después del deploy")

# Static files configuration
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Whitenoise configuration
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Debe estar aquí
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

# Logging configuration for debugging
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

# Email configuration for production
if os.environ.get('EMAIL_HOST'):
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = os.environ.get('EMAIL_HOST')
    EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
    DEFAULT_FROM_EMAIL = f'Sistema RRHH <{EMAIL_HOST_USER}>'
else:
    # Keep console backend for development/staging
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    DEFAULT_FROM_EMAIL = 'Sistema RRHH <noreply@empresa.com>'
