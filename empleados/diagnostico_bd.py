from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
import os

@csrf_exempt
def diagnostico_bd(request):
    """Vista para diagnosticar la conexión a la base de datos"""
    
    info = {}
    
    try:
        # Información de la conexión
        db_settings = connection.settings_dict
        info['engine'] = db_settings.get('ENGINE', 'No definido')
        info['name'] = db_settings.get('NAME', 'No definido')
        info['host'] = db_settings.get('HOST', 'No definido')
        info['port'] = db_settings.get('PORT', 'No definido')
        info['user'] = db_settings.get('USER', 'No definido')
        
        # Variables de entorno
        info['database_url_env'] = os.environ.get('DATABASE_URL', 'NO CONFIGURADA')
        info['django_settings_env'] = os.environ.get('DJANGO_SETTINGS_MODULE', 'NO CONFIGURADA')
        
        # Detectar tipo de base de datos
        if 'sqlite' in info['engine'].lower():
            info['tipo_bd'] = 'SQLite'
            info['es_correcto'] = False
        elif 'postgresql' in info['engine'].lower():
            if 'supabase.co' in str(info['host']):
                info['tipo_bd'] = 'Supabase PostgreSQL'
                info['es_correcto'] = True
            else:
                info['tipo_bd'] = 'PostgreSQL (otro)'
                info['es_correcto'] = True
        else:
            info['tipo_bd'] = 'Desconocido'
            info['es_correcto'] = False
            
        # Probar conexión
        try:
            with connection.cursor() as cursor:
                if 'postgresql' in info['engine'].lower():
                    cursor.execute("SELECT version()")
                    info['version_bd'] = cursor.fetchone()[0]
                    cursor.execute("SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public'")
                    info['tablas_count'] = cursor.fetchone()[0]
                else:
                    cursor.execute("SELECT sqlite_version()")
                    info['version_bd'] = cursor.fetchone()[0]
                    cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table'")
                    info['tablas_count'] = cursor.fetchone()[0]
            info['conexion_ok'] = True
        except Exception as e:
            info['conexion_ok'] = False
            info['error_conexion'] = str(e)
            
    except Exception as e:
        info['error_general'] = str(e)
    
    if request.method == 'POST':
        return JsonResponse(info)
    
    return render(request, 'empleados/diagnostico_bd.html', {'info': info})
