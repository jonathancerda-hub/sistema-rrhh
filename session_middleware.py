from django.http import HttpResponse
from django.db import OperationalError
from django.contrib.sessions.models import Session

class SessionErrorMiddleware:
    """
    Middleware para manejar errores de django_session cuando la tabla no existe
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except OperationalError as e:
            if 'django_session' in str(e) or 'no such table' in str(e):
                # Error de tabla django_session
                return self.handle_session_error(request, e)
            else:
                raise
    
    def handle_session_error(self, request, error):
        """Manejar error de tabla django_session"""
        
        # Si es una petición a los endpoints de emergencia, dejar pasar
        if request.path.startswith('/health/') or request.path.startswith('/emergency-migrate/'):
            # Intentar continuar sin sesiones para estos endpoints
            return None
        
        # Para otras rutas, mostrar página de error con instrucciones
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Error de Base de Datos - Sistema RRHH</title>
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    margin: 0; 
                    padding: 20px; 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    min-height: 100vh;
                }}
                .container {{
                    max-width: 800px;
                    margin: 0 auto;
                    background: rgba(255,255,255,0.95);
                    padding: 40px;
                    border-radius: 15px;
                    color: #333;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                }}
                .error-icon {{ font-size: 64px; text-align: center; margin-bottom: 20px; }}
                .btn {{ 
                    background: #dc3545; 
                    color: white; 
                    padding: 15px 30px; 
                    text-decoration: none; 
                    border-radius: 5px; 
                    display: inline-block; 
                    margin: 10px 5px;
                    font-weight: bold;
                }}
                .btn.primary {{ background: #007cba; }}
                .error-details {{ 
                    background: #f8f9fa; 
                    padding: 15px; 
                    border-radius: 5px; 
                    margin: 20px 0;
                    border-left: 4px solid #dc3545;
                    font-family: monospace;
                    font-size: 14px;
                }}
                .steps {{ 
                    background: #e7f3ff; 
                    padding: 20px; 
                    border-radius: 5px; 
                    margin: 20px 0;
                    border-left: 4px solid #007cba;
                }}
                .step {{ margin: 10px 0; padding: 10px; background: white; border-radius: 3px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="error-icon">🚨</div>
                <h1>Error de Base de Datos</h1>
                <p>El sistema no puede acceder a la tabla de sesiones de Django.</p>
                
                <div class="error-details">
                    <strong>Error técnico:</strong><br>
                    {str(error)[:200]}...
                </div>
                
                <div class="steps">
                    <h3>🔧 Soluciones Disponibles:</h3>
                    
                    <div class="step">
                        <strong>1. Solución Automática (Recomendada)</strong><br>
                        <a href="/health/" class="btn primary">🏥 Diagnóstico del Sistema</a>
                        <a href="/emergency-migrate/" class="btn">🚨 Migración de Emergencia</a>
                    </div>
                    
                    <div class="step">
                        <strong>2. Para Desarrolladores</strong><br>
                        <p>Ejecutar en el servidor:</p>
                        <code>python manage.py migrate</code>
                    </div>
                    
                    <div class="step">
                        <strong>3. Información del Problema</strong><br>
                        <p>Este error ocurre cuando las migraciones de Django no se han aplicado correctamente a la base de datos.</p>
                        <p>Las migraciones crean las tablas necesarias como <code>django_session</code> para el funcionamiento del sistema.</p>
                    </div>
                </div>
                
                <p><small>Sistema RRHH - Error capturado por SessionErrorMiddleware</small></p>
            </div>
        </body>
        </html>
        """
        
        return HttpResponse(html, status=500)
