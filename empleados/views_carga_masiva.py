from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.contrib.auth.models import User
from empleados.models import Empleado
import csv
import os
import tempfile
import unicodedata
from datetime import datetime

def carga_masiva_view(request):
    """Vista para la carga masiva de empleados desde CSV"""
    context = {
        'total_usuarios': User.objects.count(),
        'usuarios_agrovet': User.objects.filter(email__contains='@agrovetmarket.com').count(),
    }
    return render(request, 'empleados/carga_masiva.html', context)

@csrf_exempt
def procesar_csv_upload(request):
    """Procesar archivo CSV subido"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    if 'archivo_csv' not in request.FILES:
        return JsonResponse({'error': 'No se ha subido ningún archivo'}, status=400)
    
    archivo = request.FILES['archivo_csv']
    
    # Validar que sea un archivo CSV
    if not archivo.name.endswith('.csv'):
        return JsonResponse({'error': 'El archivo debe ser un CSV'}, status=400)
    
    try:
        # Guardar temporalmente el archivo
        with tempfile.NamedTemporaryFile(mode='w+b', delete=False, suffix='.csv') as tmp_file:
            for chunk in archivo.chunks():
                tmp_file.write(chunk)
            tmp_path = tmp_file.name
        
        # Procesar el CSV
        resultado = procesar_csv_empleados(tmp_path)
        
        # Limpiar archivo temporal
        os.unlink(tmp_path)
        
        return JsonResponse(resultado)
        
    except Exception as e:
        return JsonResponse({'error': f'Error al procesar archivo: {str(e)}'}, status=500)

def procesar_csv_empleados(archivo_path):
    """Procesar CSV y crear empleados"""
    resultado = {
        'exito': True,
        'usuarios_creados': 0,
        'usuarios_actualizados': 0,
        'errores': 0,
        'mensajes': [],
        'usuarios': []
    }
    
    try:
        with open(archivo_path, 'r', encoding='utf-8-sig') as file:
            # Detectar delimitador
            sample = file.read(1024)
            file.seek(0)
            
            delimiter = ','
            if ';' in sample:
                delimiter = ';'
            
            reader = csv.DictReader(file, delimiter=delimiter)
            
            for row_num, row in enumerate(reader, 1):
                try:
                    # Campos esperados
                    nombre = row.get('nombre', '').strip()
                    apellido = row.get('apellido', '').strip()
                    dni = row.get('dni', '').strip()
                    email = row.get('email', '').strip()
                    puesto = row.get('puesto', '').strip()
                    
                    if not all([nombre, apellido, email]):
                        resultado['errores'] += 1
                        resultado['mensajes'].append(f'Fila {row_num}: Faltan campos obligatorios (nombre, apellido, email)')
                        continue
                    
                    # Generar username
                    username = generar_username(nombre, apellido)
                    
                    # Crear o actualizar usuario
                    user, created = User.objects.get_or_create(
                        username=username,
                        defaults={
                            'email': email,
                            'first_name': nombre,
                            'last_name': apellido,
                            'is_active': True,
                        }
                    )
                    
                    # Establecer contraseña por defecto
                    user.set_password('agrovet2025')
                    user.save()
                    
                    # Crear o actualizar empleado
                    empleado, emp_created = Empleado.objects.get_or_create(
                        user=user,
                        defaults={
                            'nombre': nombre,
                            'apellido': apellido,
                            'dni': dni,
                            'email': email,
                            'puesto': puesto,
                            'fecha_contratacion': datetime.now().date(),
                            'dias_vacaciones_disponibles': 20,
                            'es_rrhh': False,
                            'area': row.get('area', 'Sin asignar'),
                            'gerencia': mapear_gerencia(row.get('gerencia', '')),
                            'jerarquia': mapear_jerarquia(puesto),
                        }
                    )
                    
                    if created or emp_created:
                        resultado['usuarios_creados'] += 1
                        status = 'CREADO'
                    else:
                        resultado['usuarios_actualizados'] += 1
                        status = 'ACTUALIZADO'
                    
                    resultado['usuarios'].append({
                        'username': username,
                        'nombre': f"{nombre} {apellido}",
                        'email': email,
                        'puesto': puesto,
                        'status': status
                    })
                    
                    resultado['mensajes'].append(f'✅ {username} - {nombre} {apellido} ({status})')
                    
                except Exception as e:
                    resultado['errores'] += 1
                    resultado['mensajes'].append(f'❌ Fila {row_num}: Error - {str(e)}')
    
    except Exception as e:
        resultado['exito'] = False
        resultado['mensajes'].append(f'❌ Error al leer archivo: {str(e)}')
    
    return resultado

def generar_username(nombre, apellido):
    """Generar username normalizado"""
    def normalizar_texto(texto):
        texto_normalizado = unicodedata.normalize('NFD', texto)
        return ''.join(c for c in texto_normalizado if unicodedata.category(c) != 'Mn')
    
    nombre_clean = normalizar_texto(nombre).lower()
    apellido_clean = normalizar_texto(apellido).lower()
    
    # Limpiar caracteres especiales
    nombre_clean = ''.join(c for c in nombre_clean if c.isalnum())
    apellido_clean = ''.join(c for c in apellido_clean if c.isalnum())
    
    return f"{nombre_clean}.{apellido_clean}"

def mapear_jerarquia(puesto):
    """Mapear puesto a jerarquía"""
    puesto_lower = puesto.lower()
    
    if 'director' in puesto_lower:
        return 'director'
    elif 'gerente' in puesto_lower:
        return 'gerente'
    elif 'jefe' in puesto_lower:
        return 'jefe'
    elif 'supervisor' in puesto_lower:
        return 'supervisor'
    elif 'coordinador' in puesto_lower:
        return 'coordinador'
    elif 'asistente' in puesto_lower:
        return 'asistente'
    elif 'practicante' in puesto_lower:
        return 'auxiliar'
    else:
        return 'asistente'

def mapear_gerencia(gerencia):
    """Mapear gerencia a opciones válidas"""
    gerencia_lower = gerencia.lower()
    
    if 'finanzas' in gerencia_lower or 'ti' in gerencia_lower or 'tecnologia' in gerencia_lower:
        return 'gerencia_administracion_finanzas'
    elif 'rrhh' in gerencia_lower or 'recursos humanos' in gerencia_lower:
        return 'gerencia_desarrollo_organizacional'
    elif 'comercial' in gerencia_lower or 'ventas' in gerencia_lower:
        return 'gerencia_comercial'
    elif 'operaciones' in gerencia_lower:
        return 'gerencia_operaciones'
    else:
        return 'gerencia_administracion_finanzas'
