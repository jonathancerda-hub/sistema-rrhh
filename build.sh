#!/usr/bin/env bash
set -o errexit

echo "=== Sistema RRHH - Build Script para Render ==="

# --- Validación de Variables de Entorno ---
# Validar que las variables de entorno críticas existan
if [ -z "$DATABASE_URL" ] || [ -z "$SECRET_KEY" ]; then
    echo "❌ ERROR: Las variables de entorno DATABASE_URL o SECRET_KEY no están configuradas en el panel de Render."
    exit 1
fi

# Upgrade pip
echo "📦 Actualizando pip..."
python -m pip install --upgrade pip

# Install dependencies
echo "📦 Instalando dependencias..."
pip install -r requirements.txt

# --- Comandos de Django ---
# Aplicar migraciones a la base de datos...
echo "🗄️ Aplicando migraciones..."
python manage.py migrate --no-input

# --- Carga de Datos Iniciales ---
echo "👤 Creando superusuario 'admin' si no existe..."
python manage.py crear_admin

echo "🚚 Cargando datos de empleados desde CSV..."
python manage.py cargar_organigrama "organigrama - Hoja 1.csv"

# Recolectar archivos estáticos...
echo "📁 Recolectando archivos estáticos..."
python manage.py collectstatic --no-input --clear

echo "✅ Build completado exitosamente."
