"""
Comando para enviar recordatorios de solicitudes pendientes de aprobación
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from empleados.models import SolicitudVacaciones
from empleados.utils import enviar_notificacion_recordatorio_aprobacion


class Command(BaseCommand):
    help = 'Envía recordatorios para solicitudes de vacaciones pendientes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dias',
            type=int,
            default=2,
            help='Días de antigüedad mínima para enviar recordatorio (default: 2)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Solo mostrar qué recordatorios se enviarían sin enviarlos realmente'
        )

    def handle(self, *args, **options):
        dias_antiguedad = options['dias']
        dry_run = options['dry_run']
        
        # Fecha límite para considerar una solicitud como "antigua"
        fecha_limite = timezone.now() - timedelta(days=dias_antiguedad)
        
        # Obtener solicitudes pendientes antiguas
        solicitudes_pendientes = SolicitudVacaciones.objects.filter(
            estado='pendiente',
            fecha_solicitud__lte=fecha_limite
        ).select_related('empleado', 'empleado__manager')
        
        if not solicitudes_pendientes.exists():
            self.stdout.write(
                self.style.SUCCESS(
                    f'No hay solicitudes pendientes con más de {dias_antiguedad} días de antigüedad.'
                )
            )
            return
        
        self.stdout.write(
            self.style.WARNING(
                f'Encontradas {solicitudes_pendientes.count()} solicitudes pendientes '
                f'con más de {dias_antiguedad} días de antigüedad:'
            )
        )
        
        recordatorios_enviados = 0
        errores = 0
        
        for solicitud in solicitudes_pendientes:
            dias_pendiente = (timezone.now() - solicitud.fecha_solicitud).days
            
            self.stdout.write(
                f'  - Solicitud #{solicitud.id}: {solicitud.empleado.nombre} '
                f'({dias_pendiente} días pendiente)'
            )
            
            if not dry_run:
                try:
                    if enviar_notificacion_recordatorio_aprobacion(solicitud):
                        recordatorios_enviados += 1
                        self.stdout.write(
                            self.style.SUCCESS(f'    ✓ Recordatorio enviado')
                        )
                    else:
                        errores += 1
                        self.stdout.write(
                            self.style.ERROR(f'    ✗ No se pudo enviar (sin destinatarios)')
                        )
                except Exception as e:
                    errores += 1
                    self.stdout.write(
                        self.style.ERROR(f'    ✗ Error: {str(e)}')
                    )
            else:
                self.stdout.write(
                    self.style.WARNING(f'    → Se enviaría recordatorio (dry-run)')
                )
        
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\nDry-run completado. Se enviarían {solicitudes_pendientes.count()} recordatorios.'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\nProceso completado:'
                    f'\n  - Recordatorios enviados: {recordatorios_enviados}'
                    f'\n  - Errores: {errores}'
                )
            )
