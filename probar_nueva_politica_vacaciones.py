#!/usr/bin/env python
"""
Script para probar la nueva política de vacaciones
Verifica que los períodos incluyan exactamente 4 sábados y 4 domingos
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

def probar_politica_vacaciones():
    """
    Prueba varios escenarios de la nueva política de vacaciones
    """
    print("🧪 PRUEBAS DE NUEVA POLÍTICA DE VACACIONES")
    print("=" * 50)
    
    # Obtener o crear empleado de prueba
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
    
    # Caso 1: Período de 29 días (4 sábados y 4 domingos) - VÁLIDO
    print("📅 CASO 1: Período de 29 días calendario (4 sábados y 4 domingos)")
    fecha_inicio = date(2025, 9, 1)  # Lunes 1 septiembre
    fecha_fin = fecha_inicio + timedelta(days=28)  # 29 días total
    
    validacion = solicitud_temp.validar_periodo_vacaciones(fecha_inicio, fecha_fin)
    print(f"  Fechas: {fecha_inicio} a {fecha_fin}")
    print(f"  Días calendario: {validacion['dias_calendario']}")
    print(f"  Sábados: {validacion['fines_semana']['sabados']}")
    print(f"  Domingos: {validacion['fines_semana']['domingos']}")
    print(f"  ✅ Válido: {validacion['valido']}")
    
    if validacion['errores']:
        for error in validacion['errores']:
            print(f"  ❌ Error: {error}")
    
    if validacion['advertencias']:
        for advertencia in validacion['advertencias']:
            print(f"  ⚠️ Advertencia: {advertencia}")
    print()
    
    # Caso 2: Período de 15 días (solo 2 sábados y 2 domingos) - INVÁLIDO
    print("📅 CASO 2: Período de 15 días calendario (solo 2 sábados y 2 domingos)")
    fecha_inicio = date(2025, 9, 1)  # Lunes 1 septiembre
    fecha_fin = fecha_inicio + timedelta(days=14)  # 15 días total
    
    validacion = solicitud_temp.validar_periodo_vacaciones(fecha_inicio, fecha_fin)
    print(f"  Fechas: {fecha_inicio} a {fecha_fin}")
    print(f"  Días calendario: {validacion['dias_calendario']}")
    print(f"  Sábados: {validacion['fines_semana']['sabados']}")
    print(f"  Domingos: {validacion['fines_semana']['domingos']}")
    print(f"  ❌ Válido: {validacion['valido']}")
    
    if validacion['errores']:
        for error in validacion['errores']:
            print(f"  ❌ Error: {error}")
    
    if validacion['advertencias']:
        for advertencia in validacion['advertencias']:
            print(f"  ⚠️ Advertencia: {advertencia}")
    print()
    
    # Caso 3: Período de 22 días (3 sábados y 3 domingos) - INVÁLIDO
    print("📅 CASO 3: Período de 22 días calendario (3 sábados y 3 domingos)")
    fecha_inicio = date(2025, 9, 1)  # Lunes 1 septiembre
    fecha_fin = fecha_inicio + timedelta(days=21)  # 22 días total
    
    validacion = solicitud_temp.validar_periodo_vacaciones(fecha_inicio, fecha_fin)
    print(f"  Fechas: {fecha_inicio} a {fecha_fin}")
    print(f"  Días calendario: {validacion['dias_calendario']}")
    print(f"  Sábados: {validacion['fines_semana']['sabados']}")
    print(f"  Domingos: {validacion['fines_semana']['domingos']}")
    print(f"  ❌ Válido: {validacion['valido']}")
    
    if validacion['errores']:
        for error in validacion['errores']:
            print(f"  ❌ Error: {error}")
    
    if validacion['advertencias']:
        for advertencia in validacion['advertencias']:
            print(f"  ⚠️ Advertencia: {advertencia}")
    print()
    
    # Caso 4: Período exacto de 4 semanas (28 días) - VÁLIDO
    print("📅 CASO 4: Período exacto de 4 semanas (28 días calendario)")
    fecha_inicio = date(2025, 9, 1)  # Lunes 1 septiembre
    fecha_fin = fecha_inicio + timedelta(days=27)  # 28 días total
    
    validacion = solicitud_temp.validar_periodo_vacaciones(fecha_inicio, fecha_fin)
    print(f"  Fechas: {fecha_inicio} a {fecha_fin}")
    print(f"  Días calendario: {validacion['dias_calendario']}")
    print(f"  Sábados: {validacion['fines_semana']['sabados']}")
    print(f"  Domingos: {validacion['fines_semana']['domingos']}")
    print(f"  ✅ Válido: {validacion['valido']}")
    
    if validacion['errores']:
        for error in validacion['errores']:
            print(f"  ❌ Error: {error}")
    
    if validacion['advertencias']:
        for advertencia in validacion['advertencias']:
            print(f"  ⚠️ Advertencia: {advertencia}")
    print()
    
    print("🏁 PRUEBAS COMPLETADAS")
    print("La nueva política requiere exactamente 4 sábados y 4 domingos en el período de vacaciones.")

if __name__ == "__main__":
    probar_politica_vacaciones()
