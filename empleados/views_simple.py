from django.http import HttpResponse

def vista_simple(request):
    """Vista súper simple para testing rápido"""
    return HttpResponse("""
        <html>
        <head><title>Sistema RRHH - Funcionando</title></head>
        <body style="font-family: Arial; padding: 40px; text-align: center;">
            <h1>✅ Sistema RRHH Funcionando</h1>
            <p>El servidor está respondiendo correctamente.</p>
            <div style="margin: 20px;">
                <a href="/empleados/setup/emergencia/" style="padding: 10px 20px; background: #f44336; color: white; text-decoration: none; border-radius: 5px;">
                    🚨 Inicializar Sistema
                </a>
                <a href="/admin/" style="padding: 10px 20px; background: #2196f3; color: white; text-decoration: none; border-radius: 5px; margin-left: 10px;">
                    ⚙️ Admin
                </a>
            </div>
            <p><small>Fecha: {}</small></p>
        </body>
        </html>
    """.format(__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

def test_db(request):
    """Test básico de conectividad a BD"""
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
        
        return HttpResponse(f"""
            <html>
            <head><title>Test BD</title></head>
            <body style="font-family: Arial; padding: 40px;">
                <h1>✅ Base de Datos OK</h1>
                <p>Resultado: {result}</p>
                <p><a href="/">← Volver</a></p>
            </body>
            </html>
        """)
    except Exception as e:
        return HttpResponse(f"""
            <html>
            <head><title>Error BD</title></head>
            <body style="font-family: Arial; padding: 40px;">
                <h1>❌ Error de Base de Datos</h1>
                <p>Error: {str(e)}</p>
                <p><a href="/empleados/setup/emergencia/">🚨 Inicializar</a></p>
            </body>
            </html>
        """, status=500)
