"""
Configuración local para desarrollo - SQLite simple
"""
from .settings import *

# Debug mode para desarrollo
DEBUG = True

# Hosts permitidos para desarrollo local
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '[::1]',
]

# SQLite para desarrollo local
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db_local.sqlite3',
    }
}

# Zona horaria Perú
LANGUAGE_CODE = 'es-pe'
TIME_ZONE = 'America/Lima'
USE_I18N = True
USE_TZ = True

# Email para desarrollo
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'Sistema RRHH <noreply@empresa.com>'

print("🔧 Configuración LOCAL con SQLite")
