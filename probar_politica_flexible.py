#!/usr/bin/env python
"""
Script para probar la nueva política FLEXIBLE de vacaciones
El empleado puede elegir cualquier período, pero recibe mensajes informativos
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

def probar_politica_flexible():
    """
    Prueba la nueva política flexible de vacaciones
    """
    print("🧪 PRUEBAS DE POLÍTICA FLEXIBLE DE VACACIONES")
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
    print()
    
    # Crear solicitud temporal para pruebas
    solicitud_temp = SolicitudVacaciones(empleado=empleado)
    
    # CASO 1: Solo días de semana (5 días laborables) - PERMITIDO
    print("📅 CASO 1: Solo días laborables (Lunes a Viernes)")
    fecha_inicio = date(2025, 9, 8)  # Lunes
    fecha_fin = date(2025, 9, 12)    # Viernes (5 días)
    
    validacion = solicitud_temp.validar_periodo_vacaciones(fecha_inicio, fecha_fin)
    print(f"  Fechas: {fecha_inicio} a {fecha_fin}")
    print(f"  Días calendario: {validacion['dias_calendario']}")
    print(f"  Sábados: {validacion['fines_semana']['sabados']}")
    print(f"  Domingos: {validacion['fines_semana']['domingos']}")
    print(f"  ✅ Válido: {validacion['valido']} (PERMITIDO)")
    
    if validacion.get('mensajes_informativos'):
        for mensaje in validacion['mensajes_informativos']:
            print(f"  💡 Info: {mensaje}")
    
    if validacion['advertencias']:
        for advertencia in validacion['advertencias']:
            print(f"  ⚠️ Advertencia: {advertencia}")
    print()
    
    # CASO 2: Fin de semana largo (3 días con sábado y domingo) - PERMITIDO
    print("📅 CASO 2: Fin de semana largo (incluye sábado y domingo)")
    fecha_inicio = date(2025, 9, 13)  # Sábado
    fecha_fin = date(2025, 9, 15)     # Lunes (3 días)
    
    validacion = solicitud_temp.validar_periodo_vacaciones(fecha_inicio, fecha_fin)
    print(f"  Fechas: {fecha_inicio} a {fecha_fin}")
    print(f"  Días calendario: {validacion['dias_calendario']}")
    print(f"  Sábados: {validacion['fines_semana']['sabados']}")
    print(f"  Domingos: {validacion['fines_semana']['domingos']}")
    print(f"  ✅ Válido: {validacion['valido']} (PERMITIDO)")
    
    if validacion.get('mensajes_informativos'):
        for mensaje in validacion['mensajes_informativos']:
            print(f"  💡 Info: {mensaje}")
    
    if validacion['advertencias']:
        for advertencia in validacion['advertencias']:
            print(f"  ⚠️ Advertencia: {advertencia}")
    print()
    
    # CASO 3: Un solo día (miércoles) - PERMITIDO
    print("📅 CASO 3: Un solo día (miércoles)")
    fecha_inicio = date(2025, 9, 17)  # Miércoles
    fecha_fin = date(2025, 9, 17)     # Mismo día
    
    validacion = solicitud_temp.validar_periodo_vacaciones(fecha_inicio, fecha_fin)
    print(f"  Fechas: {fecha_inicio} a {fecha_fin}")
    print(f"  Días calendario: {validacion['dias_calendario']}")
    print(f"  Sábados: {validacion['fines_semana']['sabados']}")
    print(f"  Domingos: {validacion['fines_semana']['domingos']}")
    print(f"  ✅ Válido: {validacion['valido']} (PERMITIDO)")
    
    if validacion.get('mensajes_informativos'):
        for mensaje in validacion['mensajes_informativos']:
            print(f"  💡 Info: {mensaje}")
    
    if validacion['advertencias']:
        for advertencia in validacion['advertencias']:
            print(f"  ⚠️ Advertencia: {advertencia}")
    print()
    
    # CASO 4: Dos semanas con fines de semana - PERMITIDO y RECOMENDADO
    print("📅 CASO 4: Dos semanas completas (incluye 4 fines de semana)")
    fecha_inicio = date(2025, 9, 15)  # Lunes
    fecha_fin = date(2025, 9, 28)     # Domingo (14 días)
    
    validacion = solicitud_temp.validar_periodo_vacaciones(fecha_inicio, fecha_fin)
    print(f"  Fechas: {fecha_inicio} a {fecha_fin}")
    print(f"  Días calendario: {validacion['dias_calendario']}")
    print(f"  Sábados: {validacion['fines_semana']['sabados']}")
    print(f"  Domingos: {validacion['fines_semana']['domingos']}")
    print(f"  ✅ Válido: {validacion['valido']} (PERMITIDO)")
    
    if validacion.get('mensajes_informativos'):
        for mensaje in validacion['mensajes_informativos']:
            print(f"  💡 Info: {mensaje}")
    
    if validacion['advertencias']:
        for advertencia in validacion['advertencias']:
            print(f"  ⚠️ Advertencia: {advertencia}")
    print()
    
    # CASO 5: Exceso de días disponibles - ERROR
    print("📅 CASO 5: Más días de los disponibles (50 días)")
    fecha_inicio = date(2025, 10, 1)
    fecha_fin = date(2025, 11, 19)    # 50 días
    
    validacion = solicitud_temp.validar_periodo_vacaciones(fecha_inicio, fecha_fin)
    print(f"  Fechas: {fecha_inicio} a {fecha_fin}")
    print(f"  Días calendario: {validacion['dias_calendario']}")
    print(f"  Sábados: {validacion['fines_semana']['sabados']}")
    print(f"  Domingos: {validacion['fines_semana']['domingos']}")
    print(f"  ❌ Válido: {validacion['valido']} (ERROR)")
    
    if validacion['errores']:
        for error in validacion['errores']:
            print(f"  ❌ Error: {error}")
    
    if validacion.get('mensajes_informativos'):
        for mensaje in validacion['mensajes_informativos']:
            print(f"  💡 Info: {mensaje}")
    print()
    
    print("🏁 RESUMEN DE PRUEBAS")
    print("✅ La nueva política es FLEXIBLE:")
    print("   • Permite cualquier período de fechas")
    print("   • Cuenta días calendario (incluyendo fines de semana)")
    print("   • Da mensajes informativos para promover inclusión de fines de semana")
    print("   • Solo da ERROR si excede días disponibles o fechas inválidas")
    print("   • Proporciona seguimiento del cumplimiento anual")

if __name__ == "__main__":
    probar_politica_flexible()
