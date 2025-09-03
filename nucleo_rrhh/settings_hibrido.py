"""
Configuración híbrida: Intenta Supabase, si falla usa SQLite
"""
from .settings import *

# Debug activado para desarrollo local
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Configuración de Supabase
SUPABASE_CONFIG = {
    'ENGINE': 'django.db.backends.postgresql',
    'NAME': 'postgres',
    'USER': 'postgres',
    'PASSWORD': '3jbxqfv$2gyW$yG',
    'HOST': 'db.mwjdmmowllmxygscgcex.supabase.co',
    'PORT': '5432',
    'CONN_MAX_AGE': 600,
}

# Intentar conectar a Supabase, si falla usar SQLite
try:
    import socket
    # Test básico de conectividad
    socket.create_connection((SUPABASE_CONFIG['HOST'], int(SUPABASE_CONFIG['PORT'])), timeout=5)
    
    # Si llegamos aquí, hay conectividad
    DATABASES = {
        'default': SUPABASE_CONFIG
    }
    print("🌐 ✅ Conectado a Supabase PostgreSQL")
    DATABASE_TYPE = "SUPABASE"
    
except Exception as e:
    # Si hay problemas, usar SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
    print(f"🗄️ ⚠️ Usando SQLite local (Supabase no disponible: {type(e).__name__})")
    DATABASE_TYPE = "SQLITE"

# Archivos estáticos para desarrollo
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Email backend para desarrollo
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'Sistema RRHH <noreply@empresa.com>'

# Variable global para saber qué BD estamos usando
CURRENT_DATABASE = DATABASE_TYPE
