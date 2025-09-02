from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from empleados.models import Empleado, SolicitudVacaciones
from datetime import date
from django.utils import timezone

class Command(BaseCommand):
    help = 'Crea usuarios de prueba para el sistema de RRHH'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 CREANDO USUARIOS DE PRUEBA PARA EL SISTEMA DE RRHH')
        )
        self.stdout.write('=' * 60)
        
        # Crear superusuario
        self.crear_superusuario()
        
        # Crear empleados de prueba
        self.crear_empleados_prueba()
        
        # Crear solicitudes de vacaciones de prueba
        self.crear_solicitudes_vacaciones_prueba()
        
        # Mostrar credenciales
        self.mostrar_credenciales()
        
        self.stdout.write(
            self.style.SUCCESS('\n✅ ¡Usuarios de prueba creados exitosamente!')
        )
        self.stdout.write('🎯 Ahora puedes probar el módulo de vacaciones')

    def crear_superusuario(self):
        """Crear superusuario si no existe"""
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@empresa.com',
                password='admin123'
            )
            self.stdout.write(
                self.style.SUCCESS('✅ Superusuario creado: admin/admin123')
            )
        else:
            self.stdout.write(
                self.style.WARNING('ℹ️  El superusuario admin ya existe')
            )

    def crear_empleados_prueba(self):
        """Crear empleados de prueba con usuarios Django asociados"""
        empleados_data = [
            {
                'username': 'carlos.lopez',
                'nombre': 'Carlos Alberto',
                'apellido': 'López Martínez',
                'email': 'carlos.lopez@empresa.com',
                'puesto': 'Project Manager',
                'gerencia': 'gerencia_desarrollo_organizacional',
                'jerarquia': 'jefe',
                'fecha_contratacion': date(2021, 11, 10),
                'password': 'empleado123',
                'es_rrhh': False
            },
            {
                'username': 'juan.perez',
                'nombre': 'Juan Carlos',
                'apellido': 'Pérez González',
                'email': 'juan.perez@empresa.com',
                'puesto': 'Desarrollador Senior',
                'gerencia': 'gerencia_desarrollo_organizacional',
                'jerarquia': 'coordinador',
                'fecha_contratacion': date(2022, 1, 15),
                'password': 'empleado123',
                'es_rrhh': False
            },
            {
                'username': 'maria.garcia',
                'nombre': 'María Elena',
                'apellido': 'García Rodríguez',
                'email': 'maria.garcia@empresa.com',
                'puesto': 'Diseñadora UX/UI',
                'gerencia': 'gerencia_comercial_local',
                'jerarquia': 'asistente',
                'fecha_contratacion': date(2022, 3, 20),
                'password': 'empleado123',
                'es_rrhh': False
            },
            {
                'username': 'ana.martinez',
                'nombre': 'Ana Sofía',
                'apellido': 'Martínez Silva',
                'email': 'ana.martinez@empresa.com',
                'puesto': 'Analista de QA',
                'gerencia': 'gerencia_desarrollo_organizacional',
                'jerarquia': 'auxiliar',
                'fecha_contratacion': date(2023, 2, 8),
                'password': 'empleado123',
                'es_rrhh': False
            },
            {
                'username': 'roberto.torres',
                'nombre': 'Roberto Daniel',
                'apellido': 'Torres Vargas',
                'email': 'roberto.torres@empresa.com',
                'puesto': 'DevOps Engineer',
                'gerencia': 'gerencia_desarrollo_organizacional',
                'jerarquia': 'supervisor',
                'fecha_contratacion': date(2022, 6, 12),
                'password': 'empleado123',
                'es_rrhh': False
            },
            {
                'username': 'rrhh.admin',
                'nombre': 'Sofía Alejandra',
                'apellido': 'Hernández Morales',
                'email': 'rrhh.admin@empresa.com',
                'puesto': 'Directora de RRHH',
                'gerencia': 'gerencia_desarrollo_organizacional',
                'jerarquia': 'director',
                'fecha_contratacion': date(2020, 5, 15),
                'password': 'rrhh123',
                'es_rrhh': True  # Usuario RRHH independiente
            }
        ]
        
        empleados_creados = 0
        usuarios_creados = 0
        manager = None
        
        for data in empleados_data:
            # Verificar si el empleado ya existe
            if not Empleado.objects.filter(email=data['email']).exists():
                # Crear usuario Django
                if not User.objects.filter(username=data['username']).exists():
                    user = User.objects.create_user(
                        username=data['username'],
                        email=data['email'],
                        password=data['password'],
                        first_name=data['nombre'],
                        last_name=data['apellido']
                    )
                    usuarios_creados += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ Usuario Django creado: {data["username"]}/{data["password"]}')
                    )
                else:
                    user = User.objects.get(username=data['username'])
                    self.stdout.write(
                        self.style.WARNING(f'ℹ️  El usuario {data["username"]} ya existe')
                    )
                
                # Crear perfil de empleado
                empleado = Empleado.objects.create(
                    nombre=data['nombre'],
                    apellido=data['apellido'],
                    email=data['email'],
                    puesto=data['puesto'],
                    gerencia=data.get('gerencia'),
                    jerarquia=data.get('jerarquia', 'auxiliar'),
                    fecha_contratacion=data['fecha_contratacion'],
                    es_rrhh=data.get('es_rrhh', False)
                )
                
                # Si es manager, guardarlo para asignar empleados después
                # Identificar si este empleado puede ser manager por su jerarquía
                if empleado.jerarquia in ['director', 'gerente', 'sub_gerente', 'jefe']:
                    manager = empleado
                
                empleados_creados += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Empleado creado: {data["nombre"]} {data["apellido"]}')
                )
            else:
                print(f"ℹ️  El empleado {data['email']} ya existe")
                # Si ya existe, verificar si puede ser manager
                empleado_existente = Empleado.objects.get(email=data['email'])
                if empleado_existente.jerarquia in ['director', 'gerente', 'sub_gerente', 'jefe']:
                    manager = empleado_existente
        
        # Asignar empleados al manager (EXCLUYENDO al usuario RRHH)
        if manager:
            empleados_sin_manager = Empleado.objects.filter(
                manager__isnull=True, 
                es_rrhh=False  # No asignar usuarios RRHH a managers
            ).exclude(id=manager.id)
            
            for empleado in empleados_sin_manager:
                empleado.manager = manager
                empleado.save()
                self.stdout.write(
                    self.style.SUCCESS(f'✅ {empleado.nombre} asignado al equipo de {manager.nombre}')
                )
        
        self.stdout.write(f'\n📊 Resumen:')
        self.stdout.write(f'   • {usuarios_creados} usuarios Django nuevos creados')
        self.stdout.write(f'   • {empleados_creados} empleados nuevos creados')
        if manager:
            self.stdout.write(f'   • {manager.nombre} es manager de {manager.equipo.count()} empleados')

    def crear_solicitudes_vacaciones_prueba(self):
        """Crear algunas solicitudes de vacaciones de prueba"""
        # Obtener algunos empleados para crear solicitudes
        empleados = Empleado.objects.all()[:3]  # Solo los primeros 3
        
        if not empleados:
            self.stdout.write(
                self.style.WARNING('⚠️  No hay empleados para crear solicitudes de vacaciones')
            )
            return
        
        solicitudes_creadas = 0
        
        for empleado in empleados:
            # Crear solicitud aprobada
            if not SolicitudVacaciones.objects.filter(empleado=empleado, estado='aprobado').exists():
                SolicitudVacaciones.objects.create(
                    empleado=empleado,
                    fecha_inicio=date(2025, 9, 15),
                    fecha_fin=date(2025, 9, 19),
                    dias_solicitados=5,
                    motivo='Vacaciones de verano',
                    estado='aprobado',
                    fecha_resolucion=timezone.now()
                )
                solicitudes_creadas += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Solicitud aprobada creada para {empleado.nombre}')
                )
            
            # Crear solicitud pendiente
            if not SolicitudVacaciones.objects.filter(empleado=empleado, estado='pendiente').exists():
                SolicitudVacaciones.objects.create(
                    empleado=empleado,
                    fecha_inicio=date(2025, 12, 20),
                    fecha_fin=date(2025, 12, 31),
                    dias_solicitados=12,
                    motivo='Vacaciones de fin de año',
                    estado='pendiente'
                )
                solicitudes_creadas += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Solicitud pendiente creada para {empleado.nombre}')
                )
        
        self.stdout.write(f'\n📋 {solicitudes_creadas} solicitudes de vacaciones creadas')

    def mostrar_credenciales(self):
        """Mostrar todas las credenciales creadas"""
        self.stdout.write('\n🔑 CREDENCIALES DE ACCESO:')
        self.stdout.write('=' * 50)
        
        # Superusuario
        self.stdout.write('👑 ADMINISTRADOR:')
        self.stdout.write('   • Usuario: admin')
        self.stdout.write('   • Contraseña: admin123')
        self.stdout.write('   • URL: http://127.0.0.1:8000/admin/')
        
        self.stdout.write('\n👥 EMPLEADOS:')
        empleados = Empleado.objects.all()
        for empleado in empleados:
            try:
                user = User.objects.get(email=empleado.email)
                self.stdout.write(f'   • {empleado.nombre} {empleado.apellido}')
                self.stdout.write(f'     Usuario: {user.username}')
                
                # Mostrar contraseña correcta según el tipo de usuario
                if empleado.es_empleado_rrhh:
                    self.stdout.write(f'     Contraseña: rrhh123')
                    self.stdout.write(f'     Puesto: {empleado.puesto}')
                    self.stdout.write(f'     🔴 USUARIO DE RRHH - ACCESO TOTAL')
                    self.stdout.write(f'     🌐 Dashboard RRHH: http://127.0.0.1:8000/rrhh/')
                elif empleado.puede_gestionar_equipo:
                    self.stdout.write(f'     Contraseña: empleado123')
                    self.stdout.write(f'     Puesto: {empleado.puesto}')
                    self.stdout.write(f'     🔵 GESTIÓN DE EQUIPO ({empleado.get_jerarquia_display()})')
                else:
                    self.stdout.write(f'     Contraseña: empleado123')
                    self.stdout.write(f'     Puesto: {empleado.puesto}')
                
                self.stdout.write('')
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'   ⚠️  {empleado.nombre} {empleado.apellido} - Sin usuario Django')
                )
        
        self.stdout.write('\n🔴 FUNCIONALIDADES ESPECIALES RRHH:')
        self.stdout.write('=' * 50)
        self.stdout.write('   • 📊 Dashboard completo con estadísticas de todas las áreas')
        self.stdout.write('   • 👀 Ver TODAS las solicitudes de vacaciones (sin restricciones)')
        self.stdout.write('   • ✅ Aprobar/Rechazar solicitudes según políticas de la empresa')
        self.stdout.write('   • 📋 Validación automática de políticas de vacaciones')
        self.stdout.write('   • 🎯 Acceso independiente (no depende de managers)')
        self.stdout.write('   • 📈 Reportes por área y estado de solicitudes')
        
        self.stdout.write('\n🌐 URLs DE LA APLICACIÓN:')
        self.stdout.write('=' * 50)
        self.stdout.write('   • Página principal: http://127.0.0.1:8000/')
        self.stdout.write('   • Login: http://127.0.0.1:8000/login/')
        self.stdout.write('   • Perfil: http://127.0.0.1:8000/perfil/')
        self.stdout.write('   • Vacaciones: http://127.0.0.1:8000/vacaciones/')
        self.stdout.write('   • Nueva solicitud: http://127.0.0.1:8000/vacaciones/nueva/')
        self.stdout.write('   • Dashboard Manager: http://127.0.0.1:8000/manager/')
        self.stdout.write('   • 🔴 Dashboard RRHH: http://127.0.0.1:8000/rrhh/')
