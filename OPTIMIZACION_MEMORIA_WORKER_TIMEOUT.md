# SOLUCIÓN A PROBLEMAS DE MEMORIA Y WORKER TIMEOUT

## 🚨 Problema Identificado

Los logs muestran:
- **WORKER TIMEOUT**: Workers terminados por timeout
- **Out of Memory**: Workers eliminados por consumo excesivo de memoria
- **SIGKILL**: Proceso forzadamente terminado

## ⚡ Optimizaciones Implementadas

### 1. **Configuración de Gunicorn Optimizada**
```yaml
# render.yaml
startCommand: "gunicorn --timeout 120 --workers 2 --max-requests 100 --max-requests-jitter 10 --preload nucleo_rrhh.wsgi:application"
envVars:
  - key: WEB_CONCURRENCY
    value: 2  # Reducido de 4 a 2 workers
```

**Cambios:**
- ✅ `--timeout 120`: Aumentado a 2 minutos
- ✅ `--workers 2`: Reducido workers para usar menos memoria
- ✅ `--max-requests 100`: Reinicia workers después de 100 requests
- ✅ `--preload`: Carga la aplicación una vez para todos los workers

### 2. **Comando de Inicialización Rápida**
```python
# empleados/management/commands/inicializar_rapido.py
- Solo crea superusuario y usuario RRHH básico
- No ejecuta collectstatic durante inicialización
- No hace verificaciones complejas
- Uso mínimo de memoria
```

### 3. **Configuración de Producción Optimizada**
```python
# settings_production.py
DEBUG = False                    # Reduce uso de memoria
CONN_MAX_AGE = 60               # Reutiliza conexiones BD
DATA_UPLOAD_MAX_MEMORY_SIZE = 10MB  # Limita uploads
```

### 4. **Logging Optimizado**
```python
# Solo mensajes WARNING y ERROR
'level': 'WARNING'  # Reduce logs verbosos
'django.db': {'handlers': []}  # Desactiva logs de BD
```

### 5. **Build Simplificado**
```bash
# build.sh
- Solo ejecuta migraciones básicas
- No inicializa usuarios durante build
- Inicialización diferida al primer acceso web
```

### 6. **Vistas de Testing Simple**
```python
# views_simple.py
- Vista sin dependencias complejas
- Testing rápido de conectividad
- Fallback para debugging
```

## 🔗 URLs de Diagnóstico

- `/simple/` - Vista simple sin dependencias
- `/empleados/test/` - Test básico de funcionamiento
- `/empleados/test/db/` - Test de conectividad a BD
- `/health/` - Health check optimizado
- `/empleados/setup/emergencia/` - Inicialización rápida

## 📊 Monitoreo de Memoria

### Comandos para Verificar Estado:
```bash
# Ver procesos y memoria
ps aux | grep gunicorn

# Logs de Render
# Verificar si aparecen menos timeouts
```

### Señales de Mejora:
- ✅ No más mensajes "WORKER TIMEOUT"
- ✅ No más "out of memory"
- ✅ Workers estables sin SIGKILL
- ✅ Respuestas HTTP más rápidas

## 🎯 Estrategia de Recuperación

### Si Persisten Problemas:
1. **Paso 1**: Acceder a `/simple/` para verificar que el servidor responde
2. **Paso 2**: Usar `/empleados/test/db/` para verificar conectividad BD
3. **Paso 3**: Ejecutar inicialización rápida en `/empleados/setup/emergencia/`
4. **Paso 4**: Verificar con `/health/` que todo funciona

### Si Todo Falla:
- Render puede necesitar restart manual
- Considerar upgrade del plan de Render
- Verificar límites de memoria del plan actual

## 📋 Checklist de Verificación

- ✅ Workers se mantienen vivos más de 30 segundos
- ✅ No hay mensajes SIGKILL en logs
- ✅ `/health/` responde OK
- ✅ `/simple/` responde rápidamente
- ✅ Inicialización completa en menos de 30 segundos

---

**Optimizaciones**: Gunicorn, memoria, comandos, logging, build  
**Resultado Esperado**: Workers estables, sin timeouts, inicialización rápida  
**Fecha**: September 4, 2025
