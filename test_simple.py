#!/usr/bin/env python
"""
Script simple para probar los métodos de validación de vacaciones
"""

import os
import sys
import django
from datetime import date, timedelta

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nucleo_rrhh.settings')
django.setup()

# Test simple
print("=== PRUEBA SIMPLE DE MÉTODOS ===")

# Importar después de configurar Django
from empleados.models import SolicitudVacaciones

# Crear instancia temporal
solicitud_temp = SolicitudVacaciones()

# Probar método de cálculo de días calendario
fecha_inicio = date(2025, 9, 1)  # Lunes
fecha_fin = date(2025, 9, 28)    # 28 días después

dias_calendario = solicitud_temp.calcular_dias_calendario(fecha_inicio, fecha_fin)
print(f"Días calendario desde {fecha_inicio} hasta {fecha_fin}: {dias_calendario}")

# Probar conteo de fines de semana
fines_semana = solicitud_temp.contar_fines_de_semana(fecha_inicio, fecha_fin)
print(f"Sábados: {fines_semana['sabados']}, Domingos: {fines_semana['domingos']}")

print("✅ Métodos funcionan correctamente")
