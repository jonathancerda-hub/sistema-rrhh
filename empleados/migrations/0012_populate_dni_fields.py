# Generated migration to populate DNI fields

from django.db import migrations

def populate_dni_fields(apps, schema_editor):
    """
    Poblar los campos DNI con valores únicos para empleados existentes
    """
    Empleado = apps.get_model('empleados', 'Empleado')
    SolicitudNuevoColaborador = apps.get_model('empleados', 'SolicitudNuevoColaborador')
    
    # Poblar DNI de empleados existentes
    empleados = Empleado.objects.all()
    for i, empleado in enumerate(empleados, start=1):
        if not empleado.dni:  # Solo si no tiene DNI
            # Generar un DNI temporal único basado en el ID
            dni_temporal = str(empleado.id).zfill(8)  # Rellenar con ceros a la izquierda
            empleado.dni = dni_temporal
            empleado.save()
    
    # Poblar DNI de solicitudes de nuevo colaborador existentes
    solicitudes = SolicitudNuevoColaborador.objects.all()
    for solicitud in solicitudes:
        if not solicitud.dni_colaborador:  # Solo si no tiene DNI
            # Generar un DNI temporal único basado en el ID de la solicitud
            dni_temporal = str(90000000 + solicitud.id)[:8]  # Comenzar desde 90000000
            solicitud.dni_colaborador = dni_temporal
            solicitud.save()

def reverse_populate_dni_fields(apps, schema_editor):
    """
    Función reversa - limpiar los DNIs si se revierte la migración
    """
    Empleado = apps.get_model('empleados', 'Empleado')
    SolicitudNuevoColaborador = apps.get_model('empleados', 'SolicitudNuevoColaborador')
    
    # Limpiar DNIs temporales
    Empleado.objects.filter(dni__startswith='0').update(dni=None)
    SolicitudNuevoColaborador.objects.filter(dni_colaborador__startswith='9').update(dni_colaborador=None)

class Migration(migrations.Migration):

    dependencies = [
        ('empleados', '0011_add_dni_fields_nullable'),
    ]

    operations = [
        migrations.RunPython(
            populate_dni_fields,
            reverse_populate_dni_fields
        ),
    ]
