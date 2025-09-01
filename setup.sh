#!/bin/bash
echo "==============================================="
echo "   🏢 Sistema RRHH - Configuración Inicial"
echo "==============================================="
echo

echo "📦 Instalando dependencias..."
pip install -r requirements.txt

echo
echo "🗃️ Configurando base de datos..."
python manage.py makemigrations
python manage.py migrate

echo
echo "👥 Creando usuarios de prueba..."
python manage.py crear_usuarios_prueba
python manage.py crear_usuario_rrhh

echo
echo "✅ Configuración completada!"
echo
echo "🚀 Para iniciar el servidor ejecuta:"
echo "   python manage.py runserver"
echo
echo "🌐 Luego visita: http://127.0.0.1:8000/empleados/"
echo
echo "👤 Usuarios de prueba:"
echo "   📧 ena.fernandez@agrovetmarket.com (password: password123)"
echo "   📧 lucia.rrhh@agrovetmarket.com (password: password123) [RRHH]"
echo
