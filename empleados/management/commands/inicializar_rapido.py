from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from empleados.models import Empleado
from datetime import date

class Command(BaseCommand):
    help = 'Inicialización mínima y rápida para producción'

    def handle(self, *args, **options):
        self.stdout.write('🚀 Inicialización rápida...')
        
        try:
            # Solo crear superusuario si no existe
            if not User.objects.filter(is_superuser=True).exists():
                User.objects.create_superuser(
                    username='admin',
                    email='admin@empresa.com',
                    password='admin123456'
                )
                self.stdout.write('✅ Admin creado: admin / admin123456')
            
            # Solo crear usuario RRHH básico si no hay empleados
            if not Empleado.objects.exists():
                user_rrhh = User.objects.create_user('rrhh', 'rrhh@empresa.com', 'rrhh123456')
                Empleado.objects.create(
                    user=user_rrhh,
                    nombre='RRHH',
                    apellido='Sistema',
                    dni='12345678',
                    email='rrhh@empresa.com',
                    puesto='Recursos Humanos',
                    fecha_contratacion=date.today(),
                    area='RRHH',
                    gerencia='gerencia_desarrollo_organizacional',
                    jerarquia='director',
                    es_rrhh=True,
                    dias_vacaciones_disponibles=30
                )
                self.stdout.write('✅ Usuario RRHH creado: rrhh / rrhh123456')
            
            self.stdout.write('🎉 Listo! Visita /admin/ o /empleados/')
            
        except Exception as e:
            self.stdout.write(f'❌ Error: {e}')
            return
