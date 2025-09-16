"""
Configuración local para desarrollo - Conexión a Supabase vía .env
"""
from .settings import *
import os
import dj_database_url
from dotenv import load_dotenv

# --- Cargar variables de entorno desde el archivo .env ---
# Por defecto, python-dotenv busca el archivo .env en la raíz del proyecto.
# Como tu archivo está en la carpeta 'venv', especificamos la ruta completa.
dotenv_path = BASE_DIR / 'venv' / '.env'
if dotenv_path.exists():
    load_dotenv(dotenv_path=dotenv_path)
    print(f"Variables de entorno cargadas desde: {dotenv_path}")

# Debug mode para desarrollo
DEBUG = True

# Hosts permitidos para desarrollo local
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]']

# --- Configuración de Base de Datos para Desarrollo (Supabase) ---
# Lee la URL de la base de datos desde la variable de entorno DATABASE_URL en el archivo .env
DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True
        )
    }
    # Forzar SSL para Supabase
    DATABASES['default']['OPTIONS'] = {'sslmode': 'require'}
    print("Conectado a la base de datos de Supabase (local).")
else:
    # Fallback a SQLite si DATABASE_URL no está definida
    print("ADVERTENCIA: No se encontró DATABASE_URL en .env. Usando SQLite como fallback.")
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

# --- Configuración de Media Files para Desarrollo (Supabase Storage) ---
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
SUPABASE_BUCKET = os.environ.get('SUPABASE_BUCKET')

if SUPABASE_URL and SUPABASE_KEY and SUPABASE_BUCKET:
    DEFAULT_FILE_STORAGE = 'storages.backends.supabase.SupabaseStorage'
    print("Usando Supabase Storage para archivos multimedia (local).")
else:
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'
    print("ADVERTENCIA: No se encontraron credenciales de Supabase Storage. Usando almacenamiento local para media.")