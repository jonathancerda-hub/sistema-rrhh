"""
Comando para resetear y verificar contraseñas de usuarios
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from empleados.models import Empleado

class Command(BaseCommand):
    help = 'Resetear y verificar contraseñas de usuarios'

    def handle(self, *args, **options):
        self.stdout.write('🔑 Verificando y reseteando contraseñas...')
        
        usuarios_configurar = [
            ('admin_rrhh', 'admin123'),
            ('manager_ventas', 'manager123'),
            ('ana_garcia', 'empleado123'),
        ]
        
        for username, password in usuarios_configurar:
            try:
                user = User.objects.get(username=username)
                user.set_password(password)
                user.save()
                
                # Verificar si tiene empleado asociado
                try:
                    empleado = user.empleado
                    self.stdout.write(f'✅ {username} / {password} - {empleado.nombre} {empleado.apellido}')
                    if empleado.es_rrhh:
                        self.stdout.write('   🔴 ACCESO RRHH')
                    elif empleado.es_manager:
                        self.stdout.write('   🔵 MANAGER')
                    else:
                        self.stdout.write('   👤 EMPLEADO')
                except:
                    self.stdout.write(f'✅ {username} / {password} - Sin perfil de empleado')
                    
            except User.DoesNotExist:
                self.stdout.write(f'❌ Usuario {username} no encontrado')
        
        # Crear usuario admin si no existe
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@empresa.com',
                password='admin123'
            )
            self.stdout.write('✅ admin / admin123 - Superusuario creado')
        else:
            admin_user = User.objects.get(username='admin')
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write('✅ admin / admin123 - Superusuario actualizado')
        
        self.stdout.write('\n🌐 URLs para probar:')
        self.stdout.write('   • http://127.0.0.1:8000/ (Login principal)')
        self.stdout.write('   • http://127.0.0.1:8000/admin/ (Panel admin)')
        self.stdout.write('   • http://127.0.0.1:8000/empleados/login/ (Login empleados)')
        
        self.stdout.write('\n🎯 Usuarios configurados correctamente!')
