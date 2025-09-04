from django.shortcuts import render
from django.http import HttpResponse
from django.core.management import call_command
from django.contrib.auth.models import User
from empleados.models import Empleado
from io import StringIO
import sys

def inicializar_emergencia(request):
    """Vista de emergencia para inicializar el sistema si el build falló"""
    
    if request.method == 'GET':
        # Mostrar estado actual del sistema
        context = {
            'users_count': User.objects.count(),
            'empleados_count': Empleado.objects.count(),
            'superusers_count': User.objects.filter(is_superuser=True).count(),
        }
        return render(request, 'empleados/inicializar_emergencia.html', context)
    
    elif request.method == 'POST':
        # Ejecutar inicialización
        output = StringIO()
        
        try:
            # Capturar la salida del comando
            old_stdout = sys.stdout
            sys.stdout = output
            
            # Ejecutar el comando de inicialización rápida en lugar del completo
            call_command('inicializar_rapido')
            
            # Restaurar stdout
            sys.stdout = old_stdout
            
            result = output.getvalue()
            
            return HttpResponse(f"""
                <html>
                <head>
                    <title>Inicialización Completada</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 40px; }}
                        .success {{ color: green; }}
                        .error {{ color: red; }}
                        pre {{ background: #f5f5f5; padding: 20px; border-radius: 5px; }}
                    </style>
                </head>
                <body>
                    <h1 class="success">✅ Inicialización Completada</h1>
                    <h2>Resultado del proceso:</h2>
                    <pre>{result}</pre>
                    <p><a href="/empleados/">🏠 Ir al Sistema RRHH</a></p>
                    <p><a href="/admin/">⚙️ Ir al Panel de Admin</a></p>
                </body>
                </html>
            """)
            
        except Exception as e:
            sys.stdout = old_stdout
            return HttpResponse(f"""
                <html>
                <head>
                    <title>Error en Inicialización</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 40px; }}
                        .error {{ color: red; }}
                        pre {{ background: #f5f5f5; padding: 20px; border-radius: 5px; }}
                    </style>
                </head>
                <body>
                    <h1 class="error">❌ Error en Inicialización</h1>
                    <p class="error">Error: {str(e)}</p>
                    <pre>{output.getvalue()}</pre>
                    <p><a href="/empleados/setup/emergencia/">🔄 Intentar de nuevo</a></p>
                </body>
                </html>
            """)
