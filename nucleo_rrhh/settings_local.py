"""
Configuración local para desarrollo - SQLite simple
"""
from .settings import *
import os

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
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'postgres',
            'USER': 'postgres',
            'PASSWORD': '3jbxqfv$2gyW$yG',
            'HOST': 'db.mwjdmmowllmxygscgcex.supabase.co',
            'PORT': '5432',
            'CONN_MAX_AGE': 600,
        }
    }
    print("🌐 Conectado a Supabase PostgreSQL")
    
except Exception as e:
    # Si hay problemas de conexión, usar SQLite local
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db_local.sqlite3',
        }
    }
    print(f"🔄 Usando SQLite local (Supabase no disponible: {e})")

print("� Configuración LOCAL usando SQLite")
print("🔧 Modo desarrollo - fácil migración a PostgreSQL después")

# Email backend para desarrollo
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'Sistema RRHH <noreply@empresa.com>'

# Static files para desarrollo
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Configuración de Supabase para referencia futura
SUPABASE_CONFIG = {
    'ENGINE': 'django.db.backends.postgresql',
    'NAME': 'postgres',
    'USER': 'postgres',
    'PASSWORD': '3jbxqfv$2gyW$yG',
    'HOST': 'db.mwjdmmowllmxygscgcex.supabase.co',
    'PORT': '5432',
}
