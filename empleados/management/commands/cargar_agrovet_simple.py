"""
Comando simple para cargar usuarios de AgroVet
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from empleados.models import Empleado
import csv
import unicodedata
from datetime import datetime

class Command(BaseCommand):
    help = 'Cargar usuarios de AgroVet Market'

    def handle(self, *args, **options):
        self.stdout.write('🏢 Cargando usuarios AgroVet Market...')
        
        # Datos directos de AgroVet
        usuarios_agrovet = [
            ('José', 'Garcia', '00000001', 'jose.garcia@agrovetmarket.com', 'Director Finanzas y T.I', True, False),
            ('Ena', 'Fernández', '00000002', 'ena.fernandez@agrovetmarket.com', 'Gerente Transformación Digital', True, False),
            ('Teodoro', 'Balarezo', '00000003', 'teodoro.balarezo@agrovetmarket.com', 'Jefe de Proyectos TI', True, False),
            ('Juana', 'Lovaton', '00000004', 'juana.lovaton@agrovetmarket.com', 'Jefe de Aplicaciones', True, False),
            ('José', 'Pariasca', '00000005', 'jose.pariasca@agrovetmarket.com', 'Jefe Finanzas', True, False),
            ('Pamela', 'Torres', '00000006', 'pamela.torres@agrovetmarket.com', 'Jefe Planeamiento Financiero', True, False),
            ('Ricardo', 'Calderón', '00000007', 'ricardo.calderon@agrovetmarket.com', 'Jefe Admin', True, False),
            ('Kevin', 'Marroquín', '00000008', 'kevin.marroquin@agrovetmarket.com', 'Asesor Legal', False, False),
            ('César', 'García', '00000009', 'cesar.garcia@agrovetmarket.com', 'Supervisor Infraestructura TI', False, False),
            ('Mariano', 'Polo', '00000010', 'mariano.polo@agrovetmarket.com', 'Supervisor Seguridad', False, False),
            ('Juan', 'Portal', '00000011', 'juan.portal@agrovetmarket.com', 'Asistente Aplicaciones', False, False),
            ('Miguel', 'Maguiña', '00000012', 'miguel.maguina@agrovetmarket.com', 'Asistente TI', False, False),
            ('Denis', 'Huamán', '00000013', 'denis.huaman@agrovetmarket.com', 'Asistente TI', False, False),
            ('José', 'Guerrero', '00000014', 'jose.guerrero@agrovetmarket.com', 'Practicante TI', False, False),
            ('Luis', 'Ortega', '00000015', 'luis.ortega@agrovetmarket.com', 'Practicante TI', False, False),
            ('Marilia', 'Tinoco', '00000016', 'marilia.tinoco@agrovetmarket.com', 'Supervisor Finanzas', False, False),
            ('Katia', 'Bárcena', '00000017', 'katia.barcena@agrovetmarket.com', 'Supervisor Créditos', False, False),
            ('Ana', 'Flores', '00000018', 'ana.flores@agrovetmarket.com', 'Supervisor Contable', False, False),
            ('Blanca', 'Loayza', '00000019', 'blanca.loayza@agrovetmarket.com', 'Supervisor Costos', False, False),
        ]
        
        creados = 0
        
        for nombre, apellido, dni, email, puesto, es_manager, es_rrhh in usuarios_agrovet:
            try:
                # Generar username sin tildes
                username = self.generar_username(nombre, apellido)
                
                # Crear usuario Django
                user, user_created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        'email': email,
                        'first_name': nombre,
                        'last_name': apellido,
                        'is_active': True,
                        'is_staff': es_rrhh,
                    }
                )
                
                # Establecer contraseña
                user.set_password('agrovet2025')
                user.save()
                
                # Crear empleado
                empleado, emp_created = Empleado.objects.get_or_create(
                    user=user,
                    defaults={
                        'nombre': nombre,
                        'apellido': apellido,
                        'dni': dni,
                        'email': email,
                        'puesto': puesto,
                        'fecha_contratacion': datetime(2001, 10, 2).date(),
                        'dias_vacaciones_disponibles': 20,
                        'es_rrhh': es_rrhh,
                        'area': 'Finanzas y T.I',
                        'gerencia': 'gerencia_administracion_finanzas',
                        'jerarquia': self.mapear_jerarquia(puesto),
                    }
                )
                
                if user_created or emp_created:
                    creados += 1
                    manager_text = " (MANAGER)" if es_manager else ""
                    self.stdout.write(f'✅ {username:<25} | {nombre} {apellido}{manager_text}')
                else:
                    self.stdout.write(f'ℹ️ {username:<25} | {nombre} {apellido} (ya existe)')
                    
            except Exception as e:
                self.stdout.write(f'❌ Error con {nombre} {apellido}: {e}')
        
        self.stdout.write('='*60)
        self.stdout.write(self.style.SUCCESS(f'🎉 Usuarios creados: {creados}'))
        self.stdout.write(f'👥 Total usuarios en sistema: {User.objects.count()}')
        self.stdout.write('🔐 Contraseña para todos: agrovet2025')
        self.stdout.write('\n🌐 Páginas útiles:')
        self.stdout.write('   • http://127.0.0.1:8000/agrovet/')
        self.stdout.write('   • http://127.0.0.1:8000/usuarios/')
        self.stdout.write('   • http://127.0.0.1:8000/login-debug/')
    
    def generar_username(self, nombre, apellido):
        """Generar username sin tildes"""
        nombre_clean = self.normalizar_texto(nombre).lower()
        apellido_clean = self.normalizar_texto(apellido).lower()
        
        # Limpiar caracteres especiales
        nombre_clean = ''.join(c for c in nombre_clean if c.isalnum())
        apellido_clean = ''.join(c for c in apellido_clean if c.isalnum())
        
        return f"{nombre_clean}.{apellido_clean}"
    
    def normalizar_texto(self, texto):
        """Remover tildes"""
        texto_normalizado = unicodedata.normalize('NFD', texto)
        return ''.join(c for c in texto_normalizado if unicodedata.category(c) != 'Mn')
    
    def mapear_jerarquia(self, puesto):
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
        elif 'asistente' in puesto_lower:
            return 'asistente'
        elif 'practicante' in puesto_lower:
            return 'auxiliar'
        else:
            return 'asistente'
