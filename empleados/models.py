from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

class Empleado(models.Model):
    JERARQUIA_CHOICES = [
        ('director', 'Director'),
        ('gerente', 'Gerente'),
        ('sub_gerente', 'Sub Gerente'),
        ('jefe', 'Jefe'),
        ('supervisor', 'Supervisor'),
        ('coordinador', 'Coordinador'),
        ('asistente', 'Asistente'),
        ('auxiliar', 'Auxiliar'),
    ]
    
    GERENCIA_CHOICES = [
        ('gerencia_comercial_local', 'Gerencia Comercial Local'),
        ('gerencia_comercial_internacional', 'Gerencia Comercial Internacional'),
        ('gerencia_desarrollo_organizacional', 'Gerencia de Desarrollo Organizacional'),
        ('gerencia_administracion_finanzas', 'Gerencia Administración y Finanzas'),
    ]
    
    # Campo para vincular cada Empleado a un Usuario de Django.
    # null=True es para facilitar la migración si ya tienes datos.
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='empleado', null=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    puesto = models.CharField(max_length=100)
    fecha_contratacion = models.DateField()
    dias_vacaciones_disponibles = models.IntegerField(default=20)
    # Campo para asignar un mánager a cada empleado.
    manager = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True, related_name='equipo'
    )
    # Nuevo campo para identificar usuarios de RRHH
    es_rrhh = models.BooleanField(
        default=False,
        help_text='Indica si este empleado es parte del departamento de RRHH'
    )
    # Campo para el área del empleado
    area = models.CharField(
        max_length=100, 
        null=True, 
        blank=True,
        help_text='Área o departamento del empleado'
    )
    # Campo para la gerencia del empleado
    gerencia = models.CharField(
        max_length=50,
        choices=GERENCIA_CHOICES,
        null=True,
        blank=True,
        help_text='Gerencia a la que pertenece el empleado'
    )
    # Campo para la jerarquía del empleado
    jerarquia = models.CharField(
        max_length=20,
        choices=JERARQUIA_CHOICES,
        default='auxiliar',
        help_text='Nivel jerárquico del empleado en la organización'
    )
    # Campo para la foto de perfil del empleado
    foto_perfil = models.FileField(
        upload_to='fotos_perfil/',
        null=True,
        blank=True,
        help_text='Foto de perfil del empleado'
    )

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    @property
    def es_manager(self):
        """
        Retorna True si este empleado es mánager de al menos una persona.
        """
        return self.equipo.exists()
    
    @property
    def es_empleado_rrhh(self):
        return self.es_rrhh
    
    @property
    def puede_solicitar_nuevo_empleado(self):
        """
        Determina si este empleado puede solicitar la contratación de nuevos empleados.
        Basado en su nivel jerárquico y si es manager.
        """
        # Solo directores, gerentes, sub gerentes y jefes pueden solicitar nuevos empleados
        jerarquias_autorizadas = ['director', 'gerente', 'sub_gerente', 'jefe']
        return self.jerarquia in jerarquias_autorizadas or self.es_manager or self.es_rrhh

class SolicitudVacaciones(models.Model):
    ESTADOS_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
        ('cancelado', 'Cancelado'),
    ]
    
    TIPO_VACACIONES_CHOICES = [
        ('regulares', 'Regulares'),
        ('adelantadas', 'Adelantadas'),
        ('fraccionadas', 'Fraccionadas'),
    ]
    
    PERIODO_VACACIONAL_CHOICES = [
        ('2024-2025', '2024-2025'),
        ('2025-2026', '2025-2026'),
        ('2026-2027', '2026-2027'),
        ('2027-2028', '2027-2028'),
        ('2028-2029', '2028-2029'),
    ]
    
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name='solicitudes_vacaciones')
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    dias_solicitados = models.PositiveIntegerField()
    motivo = models.TextField(max_length=500, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS_CHOICES, default='pendiente')
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_resolucion = models.DateTimeField(null=True, blank=True)
    comentario_admin = models.TextField(max_length=500, blank=True)
    procesado_por = models.ForeignKey(
        Empleado, on_delete=models.SET_NULL, null=True, blank=True, related_name='solicitudes_procesadas'
    )
    
    # Nuevos campos
    periodo_vacacional = models.CharField(
        max_length=20, 
        choices=PERIODO_VACACIONAL_CHOICES,
        default='2025-2026',
        help_text='Período vacacional al que corresponde la solicitud'
    )
    tipo_vacaciones = models.CharField(
        max_length=20,
        choices=TIPO_VACACIONES_CHOICES,
        default='regulares',
        help_text='Tipo de vacaciones según la antigüedad del empleado'
    )
    
    class Meta:
        ordering = ['-fecha_solicitud']
        verbose_name = 'Solicitud de Vacaciones'
        verbose_name_plural = 'Solicitudes de Vacaciones'
    
    def __str__(self):
        return f"Vacaciones de {self.empleado} - {self.fecha_inicio} a {self.fecha_fin} ({self.estado})"
    
    @property
    def dias_calendario(self):
        from datetime import date
        delta = self.fecha_fin - self.fecha_inicio
        return delta.days + 1
    
    def puede_cancelar(self):
        return self.estado == 'pendiente'
    
    def determinar_tipo_vacaciones(self):
        """
        Determina automáticamente el tipo de vacaciones basado en la antigüedad del empleado
        """
        from datetime import date
        hoy = date.today()
        antiguedad = hoy - self.empleado.fecha_contratacion
        
        # Si tiene menos de 1 año, son adelantadas
        if antiguedad.days < 365:
            return 'adelantadas'
        # Si tiene entre 1 y 2 años, pueden ser fraccionadas
        elif antiguedad.days < 730:
            return 'fraccionadas'
        # Si tiene más de 2 años, son regulares
        else:
            return 'regulares'
    
    def calcular_dias_disponibles(self):
        """
        Calcula los días disponibles según el tipo de vacaciones y antigüedad
        """
        tipo = self.determinar_tipo_vacaciones()
        
        if tipo == 'adelantadas':
            # Para empleados nuevos, máximo 15 días
            return min(15, self.empleado.dias_vacaciones_disponibles)
        elif tipo == 'fraccionadas':
            # Para empleados con 1-2 años, máximo 20 días
            return min(20, self.empleado.dias_vacaciones_disponibles)
        else:
            # Para empleados con más de 2 años, días completos
            return self.empleado.dias_vacaciones_disponibles
    
    def validar_incluye_fines_semana(self):
        """
        Valida que la solicitud incluya al menos un sábado o domingo
        """
        from datetime import timedelta
        
        fecha_actual = self.fecha_inicio
        incluye_fin_semana = False
        
        while fecha_actual <= self.fecha_fin:
            # 5 = Sábado, 6 = Domingo
            if fecha_actual.weekday() in [5, 6]:
                incluye_fin_semana = True
                break
            fecha_actual += timedelta(days=1)
        
        return incluye_fin_semana
    
    def contar_fines_semana(self):
        """
        Cuenta cuántos sábados y domingos incluye la solicitud
        """
        from datetime import timedelta
        
        fecha_actual = self.fecha_inicio
        fines_semana = 0
        
        while fecha_actual <= self.fecha_fin:
            # 5 = Sábado, 6 = Domingo
            if fecha_actual.weekday() in [5, 6]:
                fines_semana += 1
            fecha_actual += timedelta(days=1)
        
        return fines_semana
    
    def validar_politica_vacaciones(self):
        """
        Valida que la solicitud cumpla con las políticas de la empresa
        """
        errores = []
        
        # Validar que incluya al menos un fin de semana
        if not self.validar_incluye_fines_semana():
            errores.append("La solicitud debe incluir al menos un sábado o domingo")
        
        # Validar que no exceda el límite de días según el tipo
        dias_disponibles = self.calcular_dias_disponibles()
        if self.dias_solicitados > dias_disponibles:
            errores.append(f"Excede el límite de {dias_disponibles} días para el tipo '{self.get_tipo_vacaciones_display()}'")
        
        # Validar que no sea más de 30 días consecutivos
        if self.dias_solicitados > 30:
            errores.append("No se pueden solicitar más de 30 días consecutivos")
        
        return errores


class SolicitudNuevoColaborador(models.Model):
    ESTADOS_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
        ('observado', 'Observado'),
    ]

    GRUPO_OCUPACIONAL_CHOICES = [
        ('empleado', 'Empleado'),
        ('practicante', 'Practicante'),
        ('locador', 'Locador de Servicios'),
    ]

    DENOMINACION_PUESTO_CHOICES = [
        ('gerente', 'Gerente'),
        ('sub_gerente', 'Sub gerente'),
        ('jefe', 'Jefe'),
        ('supervisor', 'Supervisor'),
        ('analista', 'Analista'),
        ('coordinador', 'Coordinador'),
    ]

    # Quién solicita
    solicitante = models.ForeignKey(
        Empleado, on_delete=models.CASCADE, related_name='solicitudes_nuevo_colaborador'
    )

    # Campos solicitados
    area_solicitante = models.CharField(max_length=120)
    fecha_solicitud = models.DateField(auto_now_add=True)
    persona_responsable = models.CharField(max_length=120)
    fecha_inicio_labores = models.DateField()
    grupo_ocupacional = models.CharField(max_length=20, choices=GRUPO_OCUPACIONAL_CHOICES)
    puesto_a_solicitud = models.CharField(max_length=120)
    denominacion_puesto = models.CharField(max_length=20, choices=DENOMINACION_PUESTO_CHOICES)
    motivo_contratacion = models.TextField(max_length=800)
    modalidad_contratacion = models.CharField(max_length=120)
    tiempo_meses = models.PositiveIntegerField(validators=[MinValueValidator(1)], help_text='Especificar tiempo (meses)')

    # Flujo y auditoría
    estado = models.CharField(max_length=20, choices=ESTADOS_CHOICES, default='pendiente')
    procesado_por = models.ForeignKey(
        Empleado, on_delete=models.SET_NULL, null=True, blank=True, related_name='solicitudes_nuevo_colaborador_procesadas'
    )
    fecha_resolucion = models.DateTimeField(null=True, blank=True)
    comentario_rrhh = models.TextField(max_length=800, blank=True)

    class Meta:
        ordering = ['-fecha_solicitud']
        verbose_name = 'Solicitud de Nuevo Colaborador'
        verbose_name_plural = 'Solicitudes de Nuevo Colaborador'

    def __str__(self) -> str:
        return f"Nuevo colaborador para {self.area_solicitante} - {self.puesto_a_solicitud} ({self.estado})"

    def validar_campos_rrhh(self):
        errores: list[str] = []
        # Reglas simples de consistencia para RRHH
        if self.fecha_inicio_labores < self.fecha_solicitud:
            errores.append('La fecha de inicio de labores no puede ser anterior a la fecha de solicitud.')
        if self.tiempo_meses <= 0:
            errores.append('El tiempo en meses debe ser mayor a 0.')
        if not self.motivo_contratacion or len(self.motivo_contratacion.strip()) < 10:
            errores.append('El motivo de la contratación debe ser más descriptivo.')
        return errores