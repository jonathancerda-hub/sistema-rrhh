# 🚨 SOLUCIÓN ERROR DE PRODUCCIÓN: django_session

## 🔍 Problema Identificado

```
django.db.utils.OperationalError: no such table: django_session
```

Este error ocurre cuando las migraciones de Django no se han aplicado correctamente en la base de datos de producción (PostgreSQL en Render).

## ✅ SOLUCIÓN INMEDIATA

### 1. 🌐 Acceder al Diagnóstico Web

Ve a tu URL de producción y agrega `/diagnostico/`:

```
https://tu-app.onrender.com/diagnostico/
```

Esto te mostrará:
- ✅ Estado de la conexión a la base de datos
- ✅ Estado de la tabla django_session
- ✅ Cantidad de usuarios y empleados
- ✅ Configuración actual

### 2. 🔧 Aplicar Migraciones Forzadas

Si el diagnóstico muestra errores, ve a:

```
https://tu-app.onrender.com/fix-migrations/
```

Y presiona el botón "Aplicar Migraciones". Esto:
- ✅ Aplicará todas las migraciones pendientes
- ✅ Creará la tabla django_session
- ✅ Creará el usuario admin si no existe

### 3. 📋 Verificación

Después de aplicar las migraciones:
1. Vuelve a `/diagnostico/` para verificar que todo esté ✅
2. Intenta acceder a `/admin/` con `admin` / `admin123`
3. Verifica que `/empleados/` funcione correctamente

## 🔧 EXPLICACIÓN TÉCNICA

### Causa del Problema
- Render reinicia los contenedores frecuentemente
- Si usas SQLite temporal, se pierden los datos
- Las migraciones deben aplicarse en PostgreSQL de producción

### Archivos Involucrados
- `build.sh`: Script que ejecuta migraciones durante el build
- `settings_production_final.py`: Configuración que usa PostgreSQL
- `fix_production_db.py`: Script específico para resolver este problema
- `diagnostico_views.py`: Endpoints de diagnóstico web

### Scripts Disponibles

1. **build.sh**: Se ejecuta automáticamente en cada deploy
2. **fix_production_db.py**: Puede ejecutarse manualmente
3. **Endpoints web**: `/diagnostico/` y `/fix-migrations/`

## 🚀 PREVENCIÓN FUTURA

### 1. Verificar render.yaml
Asegúrate de que el build command esté correcto:
```yaml
buildCommand: "./build.sh"
```

### 2. Variables de Entorno
Verifica que estén configuradas:
- `DJANGO_SETTINGS_MODULE=nucleo_rrhh.settings_production_final`
- `DATABASE_URL` (automático con PostgreSQL de Render)
- `SECRET_KEY` (automático)

### 3. Monitoreo
- Usa `/diagnostico/` regularmente para verificar el estado
- Revisa los logs de Render si hay problemas

## 📞 SOPORTE DE EMERGENCIA

Si nada funciona:

1. **Redeploy Manual**:
   - Ve al dashboard de Render
   - Busca tu servicio
   - Presiona "Manual Deploy"

2. **Acceso a Logs**:
   - En Render dashboard → Tu servicio → Logs
   - Busca errores durante el build

3. **Reset Completo**:
   - Si es necesario, puedes eliminar y recrear el servicio PostgreSQL
   - Esto borrará todos los datos pero solucionará problemas de estructura

## ✅ CHECKLIST DE VERIFICACIÓN

- [ ] `/diagnostico/` muestra todo ✅
- [ ] `/admin/` es accesible con admin/admin123
- [ ] `/empleados/` carga correctamente
- [ ] Los usuarios pueden hacer login
- [ ] Las solicitudes de vacaciones funcionan

---

**🎯 Con estos pasos, el error de django_session debe quedar completamente resuelto.**
