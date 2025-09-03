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

# Database configuration con estrategia de fallback
DATABASE_URL = os.environ.get('DATABASE_URL')

# Detectar si estamos en build/migrate vs runtime
IS_BUILDING = any([
    'collectstatic' in sys.argv,
    'migrate' in sys.argv,
    os.environ.get('BUILD_PHASE') == 'true'
])

if IS_BUILDING:
    # Durante el build, usar SQLite para evitar problemas de red
    print("🔨 Fase de build detectada - usando SQLite temporal")
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': '/tmp/build_temp.db',
        }
    }
else:
    # En runtime, intentar usar Supabase
    if not DATABASE_URL:
        print("⚠️ DATABASE_URL no encontrada, usando Supabase directo")
        DATABASE_URL = "postgresql://postgres:3jbxqfv$2gyW$yG@db.mwjdmmowllmxygscgcex.supabase.co:5432/postgres"
    
    try:
        DATABASES = {
            'default': dj_database_url.config(
                default=DATABASE_URL,
                conn_max_age=600,
                conn_health_checks=True,
            )
        }
        print(f"✅ Configurado PostgreSQL: {DATABASE_URL[:50]}...")
    except Exception as e:
        print(f"⚠️ Error configurando PostgreSQL: {e}")
        # Fallback a SQLite si hay problemas
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': '/tmp/fallback.db',
            }
        }

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
