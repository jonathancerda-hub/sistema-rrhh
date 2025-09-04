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
echo "🗄️ Aplicando migraciones..."
python manage.py migrate --no-input --verbosity=2

# Ejecutar script de configuración específico
echo "🔧 Ejecutando configuración específica de producción..."
python fix_production_db.py

# Collect static files
echo "📁 Recolectando archivos estáticos..."
python manage.py collectstatic --no-input --clear

# Verificar que todo esté bien
echo "🔍 Verificando estado final..."
python manage.py check --deploy

echo "✅ Build completado exitosamente"

echo "=== Build completed ==="
