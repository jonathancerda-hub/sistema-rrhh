#!/usr/bin/env bash
# Exit on error
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

# Apply database migrations
echo "Applying migrations..."
python manage.py migrate --no-input

echo "=== Build completed successfully ==="
