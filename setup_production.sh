#!/usr/bin/env bash
# Script para configurar datos iniciales en Render
echo "Creando usuario RRHH y datos de prueba..."
python manage.py crear_usuario_rrhh
python manage.py crear_usuarios_prueba
