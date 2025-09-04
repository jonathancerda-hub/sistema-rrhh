#!/usr/bin/env bash
set -o errexit

echo "=== Sistema RRHH - Build Script para Render ==="

# Upgrade pip
echo "📦 Actualizando pip..."
python -m pip install --upgrade pip

# Install dependencies
echo "📦 Instalando dependencias..."
pip install -r requirements.txt

# Verificar configuración de base de datos
echo "🔧 Configurando base de datos temporal..."
echo "DJANGO_SETTINGS_MODULE: $DJANGO_SETTINGS_MODULE"

# Crear directorio temporal si no existe
mkdir -p /tmp

# Aplicar migraciones
echo "🗄️ Aplicando migraciones de base de datos..."
python manage.py migrate --no-input --verbosity=2

# Crear superusuario si no existe
echo "👤 Configurando usuario administrador..."
python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nucleo_rrhh.settings_production')
django.setup()

from django.contrib.auth.models import User

# Crear superusuario si no existe
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@empresa.com', 'admin123')
    print('✅ Superusuario admin creado')
else:
    print('ℹ️ Superusuario admin ya existe')
"

# Collect static files
echo "📁 Recolectando archivos estáticos..."
python manage.py collectstatic --no-input --clear

# Verificar estado de la aplicación
echo "🔍 Verificando estado de la aplicación..."
python manage.py check --deploy

echo "✅ Build completado exitosamente"
echo "🚀 La aplicación está lista para ejecutarse"
echo "💡 Visita la URL principal para acceder al sistema"
