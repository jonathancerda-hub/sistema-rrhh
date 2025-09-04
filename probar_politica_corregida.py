#!/usr/bin/env python
"""
Script para probar la política corregida de vacaciones
30 días totales + debe incluir fines de semana (educativo)
"""

import os
import sys
import django
from datetime import date, timedelta

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nucleo_rrhh.settings')
django.setup()

from empleados.models import Empleado, SolicitudVacaciones

def probar_politica_corregida():
    """
    Prueba la política corregida: 30 días totales + incluir fines de semana (educativo)
    """
    print("🧪 PRUEBAS DE POLÍTICA CORREGIDA DE VACACIONES")
    print("=" * 60)
    
    # Obtener empleado de prueba
    try:
        empleado = Empleado.objects.first()
        if not empleado:
            print("❌ No hay empleados en la base de datos para probar")
            return
    except Exception as e:
        print(f"❌ Error al obtener empleado: {e}")
        return
    
    print(f"👤 Empleado de prueba: {empleado.nombres} {empleado.apellidos}")
    
    # Crear solicitud temporal para pruebas
    solicitud_temp = SolicitudVacaciones(empleado=empleado)
    
    # Mostrar días disponibles
    dias_disponibles = solicitud_temp.calcular_dias_disponibles()
    print(f"📊 Días disponibles: {dias_disponibles}")
    print()
    
    # CASO 1: 5 días laborables (Lunes a Viernes) - PERMITIDO
    print("📅 CASO 1: 5 días laborables (Lunes a Viernes)")
    fecha_inicio = date(2025, 9, 8)  # Lunes
    fecha_fin = date(2025, 9, 12)    # Viernes (5 días)
    
    validacion = solicitud_temp.validar_periodo_vacaciones(fecha_inicio, fecha_fin)
    print(f"  Fechas: {fecha_inicio} a {fecha_fin}")
    print(f"  Días del período: {validacion['dias_periodo']}")
    print(f"  Sábados: {validacion['fines_semana']['sabados']}")
    print(f"  Domingos: {validacion['fines_semana']['domingos']}")
    print(f"  Días disponibles: {validacion['dias_disponibles']}")
    print(f"  Días restantes: {validacion['dias_restantes']}")
    print(f"  ✅ Válido: {validacion['valido']}")
    
    if validacion.get('mensajes_informativos'):
        for mensaje in validacion['mensajes_informativos']:
            print(f"  💡 Info: {mensaje}")
    print()
    
    # CASO 2: 9 días incluyendo fin de semana (Sáb a Dom siguiente) - PERMITIDO y RECOMENDADO
    print("📅 CASO 2: 9 días incluyendo fines de semana")
    fecha_inicio = date(2025, 9, 13)  # Sábado
    fecha_fin = date(2025, 9, 21)     # Domingo (9 días)
    
    validacion = solicitud_temp.validar_periodo_vacaciones(fecha_inicio, fecha_fin)
    print(f"  Fechas: {fecha_inicio} a {fecha_fin}")
    print(f"  Días del período: {validacion['dias_periodo']}")
    print(f"  Sábados: {validacion['fines_semana']['sabados']}")
    print(f"  Domingos: {validacion['fines_semana']['domingos']}")
    print(f"  Días disponibles: {validacion['dias_disponibles']}")
    print(f"  Días restantes: {validacion['dias_restantes']}")
    print(f"  ✅ Válido: {validacion['valido']}")
    
    if validacion.get('mensajes_informativos'):
        for mensaje in validacion['mensajes_informativos']:
            print(f"  💡 Info: {mensaje}")
    print()
    
    # CASO 3: 50 días (excede cuota) - ERROR
    print("📅 CASO 3: 50 días (excede cuota disponible)")
    fecha_inicio = date(2025, 10, 1)
    fecha_fin = date(2025, 11, 19)    # 50 días
    
    validacion = solicitud_temp.validar_periodo_vacaciones(fecha_inicio, fecha_fin)
    print(f"  Fechas: {fecha_inicio} a {fecha_fin}")
    print(f"  Días del período: {validacion['dias_periodo']}")
    print(f"  Días disponibles: {validacion['dias_disponibles']}")
    print(f"  ❌ Válido: {validacion['valido']}")
    
    if validacion['errores']:
        for error in validacion['errores']:
            print(f"  ❌ Error: {error}")
    print()
    
    # CASO 4: Exactamente los días disponibles
    print(f"📅 CASO 4: Exactamente {dias_disponibles} días (cuota completa)")
    fecha_inicio = date(2025, 12, 1)
    fecha_fin = fecha_inicio + timedelta(days=dias_disponibles-1)
    
    validacion = solicitud_temp.validar_periodo_vacaciones(fecha_inicio, fecha_fin)
    print(f"  Fechas: {fecha_inicio} a {fecha_fin}")
    print(f"  Días del período: {validacion['dias_periodo']}")
    print(f"  Sábados: {validacion['fines_semana']['sabados']}")
    print(f"  Domingos: {validacion['fines_semana']['domingos']}")
    print(f"  Días disponibles: {validacion['dias_disponibles']}")
    print(f"  Días restantes: {validacion['dias_restantes']}")
    print(f"  ✅ Válido: {validacion['valido']}")
    
    if validacion.get('mensajes_informativos'):
        for mensaje in validacion['mensajes_informativos']:
            print(f"  💡 Info: {mensaje}")
    print()
    
    print("🏁 RESUMEN DE POLÍTICA CORREGIDA")
    print("✅ El empleado tiene una cuota fija de días anuales")
    print("✅ Puede usar cualquier período que no exceda su cuota")
    print("✅ Se le recomienda incluir fines de semana (educativo, no obligatorio)")
    print("✅ RRHH puede hacer seguimiento del cumplimiento de inclusión de fines de semana")
    print("✅ Control simple: días solicitados vs días disponibles")

if __name__ == "__main__":
    probar_politica_corregida()
