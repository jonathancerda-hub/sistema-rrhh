"""
Vista para cambiar dinámicamente la configuración de base de datos
"""
from django.http import JsonResponse
from django.shortcuts import render
from django.conf import settings
import dj_database_url
from django.db import connection
from django.views.decorators.csrf import csrf_exempt
import json

def configurar_bd(request):
    """Página para configurar la base de datos"""
    return render(request, 'empleados/configurar_bd.html')

@csrf_exempt
def cambiar_a_supabase(request):
    """Cambiar la configuración de base de datos a Supabase dinámicamente"""
    if request.method == 'POST':
        try:
            # URL de Supabase
            supabase_url = "postgresql://postgres:3jbxqfv$2gyW$yG@db.mwjdmmowllmxygscgcex.supabase.co:5432/postgres"
            
            # Configurar nueva base de datos
            new_db_config = dj_database_url.parse(supabase_url)
            
            # Cerrar conexión actual
            connection.close()
            
            # Actualizar configuración
            settings.DATABASES['default'] = new_db_config
            
            # Probar nueva conexión
            with connection.cursor() as cursor:
                cursor.execute("SELECT version();")
                version = cursor.fetchone()
            
            return JsonResponse({
                'success': True,
                'message': 'Conectado exitosamente a Supabase',
                'database': 'PostgreSQL (Supabase)',
                'version': version[0] if version else 'Unknown'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e),
                'message': 'Error conectando a Supabase'
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
            db_type = 'PostgreSQL'
            db_info = f"Host: {db_config.get('HOST', 'localhost')}:{db_config.get('PORT', '5432')}"
        else:
            db_type = 'Unknown'
            db_info = str(db_config)
        
        # Probar conexión
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1;")
                connection_status = 'Conectado'
        except Exception as e:
            connection_status = f'Error: {str(e)}'
        
        return JsonResponse({
            'database_type': db_type,
            'database_info': db_info,
            'connection_status': connection_status,
            'engine': engine,
            'supabase_available': True,
            'supabase_url': 'postgresql://postgres:***@db.mwjdmmowllmxygscgcex.supabase.co:5432/postgres'
        })
        
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'database_type': 'Error',
            'connection_status': 'Error de configuración'
        })
