@echo off
echo 🚀 Configurando proyecto RRHH...
cd /d "c:\Users\jcerda\Desktop\proyecto_rrhh"

echo.
echo 📊 Verificando estado actual...
python manage.py verificar_estado

echo.
echo 🔄 Aplicando migraciones...
python manage.py migrate

echo.
echo 👥 Creando usuarios de prueba locales...
python manage.py crear_usuarios_prueba

echo.
echo 🌐 Estado del sistema:
python manage.py verificar_estado

echo.
echo ✅ Configuración completada!
echo.
echo 🔗 Para iniciar el servidor ejecuta:
echo    python manage.py runserver
echo.
echo 🌍 Para usar Supabase ejecuta:
echo    python manage.py sync_supabase --create-tables
echo    python manage.py crear_usuarios_supabase
echo.
pause
