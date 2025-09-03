from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.core.management import call_command
from django.db import connection
from empleados.models import Empleado
from datetime import datetime
import json
import io

def es_superuser_o_sin_usuarios(user):
    """Permite acceso si es superuser o si no hay usuarios en el sistema"""
    return user.is_superuser or User.objects.count() == 0

@csrf_exempt
def cargar_usuarios_organigrama(request):
    """Vista para cargar usuarios del organigrama directamente en producción"""
    
    # Datos del organigrama (copiados del CSV)
    usuarios_organigrama = [
        {
            'nombre': 'José',
            'apellido': 'García',
            'dni': '00000001',
            'email': 'jose.garcia@agrovetmarket.com',
            'puesto': 'DIRECTOR FINANZAS Y T.I',
            'gerencia': 'Gerencia Finanzas y T.I',
            'es_rrhh': False,
            'fecha_contratacion': '02-10-2001'
        },
        {
            'nombre': 'Ena',
            'apellido': 'E. Fernández',
            'dni': '00000002',
            'email': 'ena.fernandez@agrovetmarket.com',
            'puesto': 'Gerente Transformación Digital',
            'gerencia': 'Gerencia Finanzas y T.I',
            'es_rrhh': False,
            'fecha_contratacion': '03-10-2001'
        },
        {
            'nombre': 'Teodoro',
            'apellido': 'Balarezo',
            'dni': '00000004',
            'email': 'teodoro.balarezo@agrovetmarket.com',
            'puesto': 'Jefe de Proyectos Ti',
            'gerencia': 'Gerencia Finanzas y T.I',
            'es_rrhh': False,
            'fecha_contratacion': '05-10-2001'
        },
        {
            'nombre': 'Juana',
            'apellido': 'Lovaton',
            'dni': '00000005',
            'email': 'juana.lovaton@agrovetmarket.com',
            'puesto': 'Jefe de Aplicaciones',
            'gerencia': 'Gerencia Finanzas y T.I',
            'es_rrhh': False,
            'fecha_contratacion': '06-10-2001'
        },
        {
            'nombre': 'José',
            'apellido': 'Pariasca',
            'dni': '00000006',
            'email': 'jose.pariasca@agrovetmarket.com',
            'puesto': 'Jefe Finanzas',
            'gerencia': 'Gerencia Finanzas y T.I',
            'es_rrhh': False,
            'fecha_contratacion': '07-10-2001'
        },
        {
            'nombre': 'Pamela',
            'apellido': 'Torres',
            'dni': '00000007',
            'email': 'pamela.torres@agrovetmarket.com',
            'puesto': 'Jefe Planeamiento Financiero',
            'gerencia': 'Gerencia Finanzas y T.I',
            'es_rrhh': False,
            'fecha_contratacion': '08-10-2001'
        },
        {
            'nombre': 'Ricardo',
            'apellido': 'Calderón',
            'dni': '00000008',
            'email': 'ricardo.calderon@agrovetmarket.com',
            'puesto': 'Jefe Admin.',
            'gerencia': 'Gerencia Finanzas y T.I',
            'es_rrhh': False,
            'fecha_contratacion': '09-10-2001'
        },
        {
            'nombre': 'Kevin',
            'apellido': 'Marroquin',
            'dni': '00000009',
            'email': 'kevin.marroquin@agrovetmarket.com',
            'puesto': 'Asesor Legal',
            'gerencia': 'Gerencia Finanzas y T.I',
            'es_rrhh': False,
            'fecha_contratacion': '10-10-2001'
        },
        {
            'nombre': 'Cesar',
            'apellido': 'Garcia',
            'dni': '00000010',
            'email': 'carlos.garcia@agrovetmarket.com',
            'puesto': 'Supervisor de Infraestructura y Operaciones Ti',
            'gerencia': 'Gerencia Finanzas y T.I',
            'es_rrhh': False,
            'fecha_contratacion': '11-10-2001'
        },
        {
            'nombre': 'Mariano',
            'apellido': 'Polo',
            'dni': '00000011',
            'email': 'mariano.polo@agrovetmarket.com',
            'puesto': 'Supervisor de Seguridad de la Información',
            'gerencia': 'Gerencia Finanzas y T.I',
            'es_rrhh': False,
            'fecha_contratacion': '12-10-2001'
        },
        {
            'nombre': 'Juan',
            'apellido': 'Portal',
            'dni': '00000012',
            'email': 'juan.portal@agrovetmarket.com',
            'puesto': 'Asistente de Aplicaciones',
            'gerencia': 'Gerencia Finanzas y T.I',
            'es_rrhh': False,
            'fecha_contratacion': '13-10-2001'
        },
        {
            'nombre': 'Miguel',
            'apellido': 'Maguiña',
            'dni': '00000013',
            'email': 'miguel.maguina@agrovetmarket.com',
            'puesto': 'Asistente Infraestructura y Soporte Ti',
            'gerencia': 'Gerencia Finanzas y T.I',
            'es_rrhh': False,
            'fecha_contratacion': '14-10-2001'
        },
        {
            'nombre': 'Denis',
            'apellido': 'Huamán',
            'dni': '00000014',
            'email': 'denis.huaman@agrovetmarket.com',
            'puesto': 'Asistente Infraestructura y Soporte TI',
            'gerencia': 'Gerencia Finanzas y T.I',
            'es_rrhh': False,
            'fecha_contratacion': '15-10-2001'
        },
        {
            'nombre': 'José',
            'apellido': 'Guerrero',
            'dni': '00000015',
            'email': 'jose.guerrero@agrovetmarket.com',
            'puesto': 'Practicante Ti',
            'gerencia': 'Gerencia Finanzas y T.I',
            'es_rrhh': False,
            'fecha_contratacion': '16-10-2001'
        },
        {
            'nombre': 'Luis',
            'apellido': 'Ortega',
            'dni': '00000016',
            'email': 'luis.ortega@agrovetmarket.com',
            'puesto': 'Practicante Ti',
            'gerencia': 'Gerencia Finanzas y T.I',
            'es_rrhh': False,
            'fecha_contratacion': '17-10-2001'
        },
        {
            'nombre': 'Marilia',
            'apellido': 'Tinoco',
            'dni': '00000017',
            'email': 'marilia.tinoco@agrovetmarket.com',
            'puesto': 'Supervisor Finanzas',
            'gerencia': 'Gerencia Finanzas y T.I',
            'es_rrhh': False,
            'fecha_contratacion': '18-10-2001'
        },
        {
            'nombre': 'Katia',
            'apellido': 'Barcena',
            'dni': '00000018',
            'email': 'katia.barcena@agrovetmarket.com',
            'puesto': 'Supervisor Créditos y Cobranzas',
            'gerencia': 'Gerencia Finanzas y T.I',
            'es_rrhh': False,
            'fecha_contratacion': '19-10-2001'
        },
        {
            'nombre': 'Ana',
            'apellido': 'Flores',
            'dni': '00000019',
            'email': 'ana.flores@agrovetmarket.com',
            'puesto': 'Supervisor Contable',
            'gerencia': 'Gerencia Finanzas y T.I',
            'es_rrhh': False,
            'fecha_contratacion': '20-10-2001'
        },
        {
            'nombre': 'Blanca',
            'apellido': 'Loayza',
            'dni': '00000020',
            'email': 'blanca.loayza@agrovetmarket.com',
            'puesto': 'Supervisor Costos',
            'gerencia': 'Gerencia Finanzas y T.I',
            'es_rrhh': False,
            'fecha_contratacion': '21-10-2001'
        }
    ]

    if request.method == 'GET':
        # Mostrar página de confirmación
        context = {
            'usuarios_count': len(usuarios_organigrama),
            'usuarios_existentes': User.objects.count(),
            'usuarios_muestra': usuarios_organigrama[:5]  # Mostrar 5 como muestra
        }
        return render(request, 'empleados/cargar_organigrama.html', context)
    
    elif request.method == 'POST':
        # Ejecutar la carga
        resultado = {
            'creados': 0,
            'actualizados': 0,
            'errores': 0,
            'detalles': []
        }
        
        try:
            for user_data in usuarios_organigrama:
                try:
                    # Parsear fecha
                    fecha_str = user_data['fecha_contratacion']
                    fecha_contratacion = datetime.strptime(fecha_str, '%d-%m-%Y').date()
                    
                    # Generar username
                    username = f"{user_data['nombre'].lower()}.{user_data['apellido'].split()[0].lower()}"
                    username = ''.join(c for c in username if c.isalnum() or c == '.')[:30]
                    
                    # Buscar usuario existente
                    usuario_existente = None
                    try:
                        usuario_existente = User.objects.get(email=user_data['email'])
                    except User.DoesNotExist:
                        try:
                            empleado_existente = Empleado.objects.get(dni=user_data['dni'])
                            usuario_existente = empleado_existente.user
                        except Empleado.DoesNotExist:
                            pass

                    if usuario_existente:
                        # Actualizar usuario existente
                        usuario_existente.username = username
                        usuario_existente.first_name = user_data['nombre']
                        usuario_existente.last_name = user_data['apellido']
                        usuario_existente.email = user_data['email']
                        usuario_existente.is_staff = user_data['es_rrhh']
                        usuario_existente.is_superuser = user_data['es_rrhh']
                        usuario_existente.save()

                        # Actualizar o crear empleado
                        if hasattr(usuario_existente, 'empleado'):
                            empleado = usuario_existente.empleado
                            empleado.nombre = user_data['nombre']
                            empleado.apellido = user_data['apellido']
                            empleado.dni = user_data['dni']
                            empleado.email = user_data['email']
                            empleado.puesto = user_data['puesto']
                            empleado.gerencia = user_data['gerencia']
                            empleado.es_rrhh = user_data['es_rrhh']
                            empleado.fecha_contratacion = fecha_contratacion
                            empleado.save()
                        else:
                            Empleado.objects.create(
                                user=usuario_existente,
                                nombre=user_data['nombre'],
                                apellido=user_data['apellido'],
                                dni=user_data['dni'],
                                email=user_data['email'],
                                puesto=user_data['puesto'],
                                gerencia=user_data['gerencia'],
                                es_rrhh=user_data['es_rrhh'],
                                fecha_contratacion=fecha_contratacion,
                                dias_vacaciones_disponibles=30
                            )

                        resultado['actualizados'] += 1
                        resultado['detalles'].append(f"Actualizado: {user_data['nombre']} {user_data['apellido']}")

                    else:
                        # Crear nuevo usuario
                        nuevo_user = User.objects.create_user(
                            username=username,
                            email=user_data['email'],
                            password='agrovet2024',
                            first_name=user_data['nombre'],
                            last_name=user_data['apellido'],
                            is_staff=user_data['es_rrhh'],
                            is_superuser=user_data['es_rrhh']
                        )

                        Empleado.objects.create(
                            user=nuevo_user,
                            nombre=user_data['nombre'],
                            apellido=user_data['apellido'],
                            dni=user_data['dni'],
                            email=user_data['email'],
                            puesto=user_data['puesto'],
                            gerencia=user_data['gerencia'],
                            es_rrhh=user_data['es_rrhh'],
                            fecha_contratacion=fecha_contratacion,
                            dias_vacaciones_disponibles=30
                        )

                        resultado['creados'] += 1
                        resultado['detalles'].append(f"Creado: {user_data['nombre']} {user_data['apellido']}")

                except Exception as e:
                    resultado['errores'] += 1
                    resultado['detalles'].append(f"Error con {user_data['nombre']} {user_data['apellido']}: {str(e)}")

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

        return JsonResponse({
            'success': True,
            'resultado': resultado
        })

    return JsonResponse({'error': 'Método no permitido'}, status=405)

@csrf_exempt
def crear_tablas_supabase(request):
    """Vista para crear manualmente las tablas en Supabase si no se crearon automáticamente"""
    
    if request.method == 'GET':
        # Mostrar página de confirmación
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public'")
                tabla_count = cursor.fetchone()[0]
        except:
            tabla_count = 0
            
        context = {
            'tablas_existentes': tabla_count,
            'es_supabase': 'supabase.co' in str(connection.settings_dict.get('HOST', ''))
        }
        return render(request, 'empleados/crear_tablas.html', context)
    
    elif request.method == 'POST':
        resultado = {
            'success': False,
            'mensaje': '',
            'tablas_creadas': 0,
            'errores': []
        }
        
        try:
            # Capturar output de las migraciones
            output = io.StringIO()
            
            # Ejecutar migraciones
            call_command('migrate', verbosity=2, stdout=output)
            
            # Contar tablas después de migrar
            with connection.cursor() as cursor:
                cursor.execute("SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public'")
                tabla_count = cursor.fetchone()[0]
            
            resultado['success'] = True
            resultado['mensaje'] = f'Migraciones ejecutadas correctamente. {tabla_count} tablas en la base de datos.'
            resultado['tablas_creadas'] = tabla_count
            resultado['output'] = output.getvalue()
            
        except Exception as e:
            resultado['errores'].append(str(e))
            resultado['mensaje'] = f'Error ejecutando migraciones: {str(e)}'
        
        return JsonResponse(resultado)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)
