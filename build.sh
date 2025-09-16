#!/usr/bin/env bash
set -o errexit

echo "=== Sistema RRHH - Build Script para Render ==="

# Upgrade pip
echo "📦 Actualizando pip..."
python -m pip install --upgrade pip

# Install dependencies
echo "📦 Instalando dependencias..."
pip install -r requirements.txt

# --- Debugging: Imprimir variables de entorno ---
echo "🔍 Imprimiendo variables de entorno disponibles..."
printenv | grep "DATABASE_URL" || echo "DATABASE_URL no encontrada"
printenv | grep "SECRET_KEY" || echo "SECRET_KEY no encontrada"

# --- Validación de Variables de Entorno ---
echo "🔧 Configuración actual:"
echo "DJANGO_SETTINGS_MODULE: ${DJANGO_SETTINGS_MODULE:-No configurado}"

# Validar que las variables de entorno críticas existan
if [ -z "$DATABASE_URL" ] || [ -z "$SECRET_KEY" ]; then
    echo "❌ ERROR: Las variables de entorno DATABASE_URL o SECRET_KEY no están configuradas en Render."
    exit 1
fi

# --- Comandos de Django ---
# Aplicar migraciones a la base de datos...
echo "🗄️ Aplicando migraciones..."
python manage.py migrate --no-input

# Recolectar archivos estáticos...
echo "📁 Recolectando archivos estáticos..."
python manage.py collectstatic --no-input --clear

echo "✅ Build completado exitosamente."
