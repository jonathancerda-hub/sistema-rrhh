"""
Vista para configurar la base de datos Supabase
"""
from django.http import JsonResponse
from django.shortcuts import render
from django.conf import settings
from django.db import connection
from django.views.decorators.csrf import csrf_exempt

def configurar_bd(request):
    """Página para configurar la base de datos"""
    return render(request, 'empleados/configurar_bd.html')

@csrf_exempt
def ejecutar_migraciones(request):
    """Ejecutar migraciones en Supabase"""
    if request.method == 'POST':
        try:
            from django.core.management import call_command
            
            # Ejecutar migraciones
            call_command('migrate', verbosity=1)
            
            return JsonResponse({
                'success': True,
                'message': 'Migraciones ejecutadas exitosamente en Supabase'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e),
                'message': 'Error ejecutando migraciones'
            })
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)

def estado_base_datos(request):
    """Mostrar el estado actual de la base de datos"""
    try:
        # Información de la configuración actual
        db_config = settings.DATABASES['default']
        engine = db_config.get('ENGINE', 'Unknown')
        
        # Determinar tipo de base de datos
        if 'sqlite3' in engine:
            db_type = 'SQLite'
            db_name = db_config.get('NAME', 'Unknown')
            db_info = f"Archivo: {db_name}"
        elif 'postgresql' in engine:
            db_type = 'PostgreSQL (Supabase)'
            host = db_config.get('HOST', 'localhost')
            port = db_config.get('PORT', '5432')
            db_info = f"Host: {host}:{port}"
        else:
            db_type = 'Unknown'
            db_info = str(db_config)
        
        # Probar conexión
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT version(), current_database();")
                result = cursor.fetchone()
                version = result[0] if result else 'Unknown'
                database = result[1] if result and len(result) > 1 else 'Unknown'
                connection_status = f'Conectado a {database}'
        except Exception as e:
            connection_status = f'Error: {str(e)}'
            version = 'N/A'
        
        return JsonResponse({
            'database_type': db_type,
            'database_info': db_info,
            'connection_status': connection_status,
            'engine': engine,
            'version': version,
            'supabase_configured': 'postgresql' in engine and 'supabase' in db_info.lower()
        })
        
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'database_type': 'Error',
            'connection_status': 'Error de configuración'
        })
