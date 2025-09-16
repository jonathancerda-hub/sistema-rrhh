#!/usr/bin/env bash
set -o errexit

echo "=== Sistema RRHH - Build Script ==="

# Upgrade pip
echo "📦 Actualizando pip..."
python -m pip install --upgrade pip

# Install dependencies
echo "📦 Instalando dependencias..."
pip install -r requirements.txt

# Verificar configuración
echo "🔧 Configuración actual:"
echo "DJANGO_SETTINGS_MODULE: ${DJANGO_SETTINGS_MODULE:-No configurado}"

# Aplicar migraciones con más detalle
echo "🗄️ Aplicando migraciones a la base de datos..."
python manage.py migrate --no-input

# Collect static files
echo "📁 Recolectando archivos estáticos..."
python manage.py collectstatic --no-input --clear

echo "✅ Build completado exitosamente"
