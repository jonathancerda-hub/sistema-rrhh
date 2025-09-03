@echo off
echo 👥 HERRAMIENTA DE CARGA DE USUARIOS - SISTEMA RRHH
echo ====================================================
echo.

cd /d "c:\Users\jcerda\Desktop\proyecto_rrhh"

:menu
echo 📋 OPCIONES DISPONIBLES:
echo.
echo 1. 🎭 Crear usuarios de demostración
echo 2. 📄 Crear plantilla CSV
echo 3. 📁 Cargar usuarios desde CSV
echo 4. 👥 Ver todos los usuarios
echo 5. 🔍 Verificar estado del sistema
echo 6. 🌐 Abrir sistema en navegador
echo 7. 🚪 Salir
echo.

set /p opcion="Selecciona una opción (1-7): "

if "%opcion%"=="1" goto demo
if "%opcion%"=="2" goto plantilla
if "%opcion%"=="3" goto csv
if "%opcion%"=="4" goto ver_usuarios
if "%opcion%"=="5" goto verificar
if "%opcion%"=="6" goto abrir_web
if "%opcion%"=="7" goto salir

echo ❌ Opción inválida. Intenta de nuevo.
echo.
goto menu

:demo
echo 🎭 Creando usuarios de demostración...
python manage.py cargar_usuarios --demo
echo.
echo ✅ ¡Usuarios de demostración creados!
pause
goto menu

:plantilla
echo 📄 Creando plantilla CSV...
python manage.py cargar_usuarios --plantilla
echo.
echo ✅ ¡Plantilla creada! Edita 'plantilla_usuarios.csv' y usa la opción 3.
pause
goto menu

:csv
echo 📁 Carga desde CSV
set /p archivo="Nombre del archivo CSV (ejemplo: usuarios.csv): "
if exist "%archivo%" (
    echo Cargando usuarios desde %archivo%...
    python manage.py cargar_usuarios --csv "%archivo%"
    echo.
    echo ✅ ¡Carga completada!
) else (
    echo ❌ Archivo no encontrado: %archivo%
)
pause
goto menu

:ver_usuarios
echo 👥 Verificando usuarios...
python manage.py verificar_estado
echo.
echo 🌐 También puedes ver en: http://127.0.0.1:8000/usuarios/
pause
goto menu

:verificar
echo 🔍 Verificando estado del sistema...
python manage.py verificar_estado
echo.
pause
goto menu

:abrir_web
echo 🌐 Abriendo sistema en navegador...
start http://127.0.0.1:8000/usuarios/
echo.
echo 💡 Si no se abre automáticamente, ve a: http://127.0.0.1:8000/usuarios/
pause
goto menu

:salir
echo 👋 ¡Hasta luego!
pause
exit
