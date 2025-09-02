from django import template
from django.utils import timezone
import locale
from datetime import datetime

register = template.Library()

@register.filter
def fecha_peru(value):
    """Convertir fecha a formato peruano con nombres en español"""
    if not value:
        return ""
    
    # Si es datetime, convertir a zona horaria de Lima
    if hasattr(value, 'astimezone'):
        lima_tz = timezone.get_current_timezone()
        value = value.astimezone(lima_tz)
    
    # Nombres de meses en español
    meses = {
        1: 'enero', 2: 'febrero', 3: 'marzo', 4: 'abril',
        5: 'mayo', 6: 'junio', 7: 'julio', 8: 'agosto',
        9: 'septiembre', 10: 'octubre', 11: 'noviembre', 12: 'diciembre'
    }
    
    # Nombres de días en español
    dias = {
        0: 'lunes', 1: 'martes', 2: 'miércoles', 3: 'jueves',
        4: 'viernes', 5: 'sábado', 6: 'domingo'
    }
    
    try:
        if isinstance(value, datetime):
            dia_semana = dias[value.weekday()]
            dia = value.day
            mes = meses[value.month]
            año = value.year
            return f"{dia_semana}, {dia} de {mes} de {año}"
        else:
            # Si es solo fecha
            dia = value.day
            mes = meses[value.month]
            año = value.year
            return f"{dia} de {mes} de {año}"
    except:
        return str(value)

@register.filter
def fecha_corta_peru(value):
    """Formato de fecha corto DD/MM/YYYY"""
    if not value:
        return ""
    
    try:
        if hasattr(value, 'astimezone'):
            lima_tz = timezone.get_current_timezone()
            value = value.astimezone(lima_tz)
        
        return value.strftime("%d/%m/%Y")
    except:
        return str(value)

@register.filter
def datetime_peru(value):
    """Formato de fecha y hora completo DD/MM/YYYY HH:MM"""
    if not value:
        return ""
    
    try:
        if hasattr(value, 'astimezone'):
            lima_tz = timezone.get_current_timezone()
            value = value.astimezone(lima_tz)
        
        return value.strftime("%d/%m/%Y %H:%M")
    except:
        return str(value)

@register.filter
def hora_peru(value):
    """Formato de hora HH:MM"""
    if not value:
        return ""
    
    try:
        if hasattr(value, 'astimezone'):
            lima_tz = timezone.get_current_timezone()
            value = value.astimezone(lima_tz)
        
        return value.strftime("%H:%M")
    except:
        return str(value)
