#!/usr/bin/env bash
# Exit on error, but handle database connection issues gracefully
set -o errexit

echo "=== Starting build process ==="

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --no-input --clear

# Apply database migrations and initialize system
echo "Applying migrations and initializing system..."
MAX_RETRIES=3
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if python manage.py migrate --no-input; then
        echo "✅ Migrations applied successfully"
        
        # Initialize production system
        echo "🚀 Initializing production system..."
        if python manage.py inicializar_completo; then
            echo "✅ System initialization completed"
        else
            echo "⚠️ System initialization failed, but continuing..."
            echo "💡 You can initialize manually at /empleados/setup/diagnostico/"
        fi
        break
    else
        RETRY_COUNT=$((RETRY_COUNT + 1))
        echo "⚠️ Migration attempt $RETRY_COUNT failed"
        if [ $RETRY_COUNT -lt $MAX_RETRIES ]; then
            echo "🔄 Retrying in 5 seconds..."
            sleep 5
        else
            echo "❌ All migration attempts failed. Continuing with build..."
            echo "💡 You can run migrations manually after deploy using /setup/tablas/"
        fi
    fi
done

# Skip user creation during build - will be done via web interface
echo "⏭️ Skipping user creation during build (will be done via web setup)"

echo "=== Build completed ==="
