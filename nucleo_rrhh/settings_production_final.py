import os
import dj_database_url
from .settings import *

# CONFIGURACIÓN SIMPLE DE PRODUCCIÓN
DEBUG = False
ALLOWED_HOSTS = [
    'sistema-rrhh.onrender.com',
    '.onrender.com',
    'localhost',
    '127.0.0.1'
]

# Configuración de base de datos con fallback
DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    # PostgreSQL para producción
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL)
    }
    print(f"🔗 Usando PostgreSQL: {DATABASE_URL[:50]}...")
else:
    # Fallback a SQLite con migraciones automáticas
    print("⚠️ DATABASE_URL no encontrada, usando SQLite temporal")
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': '/tmp/emergency.db',
            'OPTIONS': {
                'timeout': 20,
            }
        }
    }
    
    # Auto-aplicar migraciones en SQLite
    import subprocess
    import sys
    try:
        print("🔧 Aplicando migraciones automáticamente...")
        subprocess.run([sys.executable, 'manage.py', 'migrate'], check=True)
        print("✅ Migraciones aplicadas")
    except Exception as e:
        print(f"❌ Error aplicando migraciones: {e}")

# Archivos estáticos
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'session_middleware.SessionErrorMiddleware',  # Manejar errores de django_session
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Secret key
SECRET_KEY = os.environ.get('SECRET_KEY', SECRET_KEY)

# Zona horaria Perú
LANGUAGE_CODE = 'es-pe'
TIME_ZONE = 'America/Lima'
USE_I18N = True
USE_TZ = True

# Email simple
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'Sistema RRHH <noreply@empresa.com>'
