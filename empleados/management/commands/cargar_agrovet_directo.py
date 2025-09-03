from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from empleados.models import Empleado
from datetime import datetime
import unicodedata

class Command(BaseCommand):
    help = 'Cargar usuarios de AgroVet Market - DIRECTO'

    def handle(self, *args, **options):
        self.stdout.write('🏢 Cargando usuarios AgroVet Market...')
        self.stdout.write(f'👥 Total usuarios antes: {User.objects.count()}')
        
        # Datos directos de AgroVet
        usuarios_agrovet = [
            ('José', 'Garcia', '00000001', 'jose.garcia@agrovetmarket.com', 'Director Finanzas y T.I'),
            ('Ena', 'Fernández', '00000002', 'ena.fernandez@agrovetmarket.com', 'Gerente Transformación Digital'),
            ('Teodoro', 'Balarezo', '00000003', 'teodoro.balarezo@agrovetmarket.com', 'Jefe de Proyectos TI'),
            ('Juana', 'Lovaton', '00000004', 'juana.lovaton@agrovetmarket.com', 'Jefe de Aplicaciones'),
            ('José', 'Pariasca', '00000005', 'jose.pariasca@agrovetmarket.com', 'Jefe Finanzas'),
            ('Pamela', 'Torres', '00000006', 'pamela.torres@agrovetmarket.com', 'Jefe Planeamiento Financiero'),
            ('Ricardo', 'Calderón', '00000007', 'ricardo.calderon@agrovetmarket.com', 'Jefe Admin'),
            ('Kevin', 'Marroquín', '00000008', 'kevin.marroquin@agrovetmarket.com', 'Asesor Legal'),
            ('César', 'García', '00000009', 'cesar.garcia@agrovetmarket.com', 'Supervisor Infraestructura TI'),
            ('Mariano', 'Polo', '00000010', 'mariano.polo@agrovetmarket.com', 'Supervisor Seguridad'),
            ('Juan', 'Portal', '00000011', 'juan.portal@agrovetmarket.com', 'Asistente Aplicaciones'),
            ('Miguel', 'Maguiña', '00000012', 'miguel.maguina@agrovetmarket.com', 'Asistente TI'),
            ('Denis', 'Huamán', '00000013', 'denis.huaman@agrovetmarket.com', 'Asistente TI'),
            ('José', 'Guerrero', '00000014', 'jose.guerrero@agrovetmarket.com', 'Practicante TI'),
            ('Luis', 'Ortega', '00000015', 'luis.ortega@agrovetmarket.com', 'Practicante TI'),
            ('Marilia', 'Tinoco', '00000016', 'marilia.tinoco@agrovetmarket.com', 'Supervisor Finanzas'),
            ('Katia', 'Bárcena', '00000017', 'katia.barcena@agrovetmarket.com', 'Supervisor Créditos'),
            ('Ana', 'Flores', '00000018', 'ana.flores@agrovetmarket.com', 'Supervisor Contable'),
            ('Blanca', 'Loayza', '00000019', 'blanca.loayza@agrovetmarket.com', 'Supervisor Costos'),
        ]
        
        creados = 0
        
        for nombre, apellido, dni, email, puesto in usuarios_agrovet:
            try:
                # Generar username sin tildes
                username = self.generar_username(nombre, apellido)
                
                # Crear usuario Django
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    first_name=nombre,
                    last_name=apellido,
                    password='agrovet2025'
                )
                user.is_active = True
                user.save()
                
                # Crear empleado
                empleado = Empleado.objects.create(
                    user=user,
                    nombre=nombre,
                    apellido=apellido,
                    dni=dni,
                    email=email,
                    puesto=puesto,
                    fecha_contratacion=datetime(2001, 10, 2).date(),
                    dias_vacaciones_disponibles=20,
                    es_rrhh=False,
                    area='Finanzas y T.I',
                    gerencia='gerencia_administracion_finanzas',
                    jerarquia=self.mapear_jerarquia(puesto),
                )
                
                creados += 1
                self.stdout.write(f'✅ {username:<25} | {nombre} {apellido}')
                    
            except Exception as e:
                self.stdout.write(f'❌ Error con {nombre} {apellido}: {e}')
        
        self.stdout.write('='*60)
        self.stdout.write(self.style.SUCCESS(f'🎉 Usuarios creados: {creados}'))
        self.stdout.write(f'👥 Total usuarios ahora: {User.objects.count()}')
        self.stdout.write('🔐 Contraseña para todos: agrovet2025')
    
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
