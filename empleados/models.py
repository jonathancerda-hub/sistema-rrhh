from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, RegexValidator
from django.core.exceptions import ValidationError

def validar_dni(value):
    """Validador personalizado para DNI peruano"""
    if not value.isdigit():
        raise ValidationError('El DNI debe contener solo números.')
    if len(value) != 8:
        raise ValidationError('El DNI debe tener exactamente 8 dígitos.')
    return value

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
    dni = models.CharField(
        max_length=8, 
        unique=True,
        validators=[validar_dni],
        help_text='Documento Nacional de Identidad (8 dígitos)',
        verbose_name='DNI'
    )
    email = models.EmailField(unique=True)
    puesto = models.CharField(max_length=100)
    fecha_contratacion = models.DateField()
    # Política actual: todos los empleados tienen 30 días anuales por defecto
    dias_vacaciones_disponibles = models.IntegerField(default=30, help_text='Días laborables de vacaciones por período')
    # Nuevos campos para control de días calendario
    dias_vacaciones_calendario = models.IntegerField(
        default=42, 
        help_text='Días calendario equivalentes (laborables + fines de semana estimados)'
    )
    dias_calendario_tomados_año = models.IntegerField(
        default=0,
        help_text='Días calendario ya tomados en el año actual'
    )
    fines_semana_incluidos_año = models.IntegerField(
        default=0,
        help_text='Cantidad de fines de semana incluidos en vacaciones del año'
    )
    # NOTE: `manager` DB field was removed in favor of explicit hierarchy fields
    # (director, gerente, jefe). For backward compatibility we expose a
    # `manager` property (the nearest superior: jefe > gerente > director)
    # and an `equipo` property that returns direct reports based on the
    # explicit hierarchy fields. This allows existing code that used
    # empleado.manager and empleado.equipo to keep working.
    # Campos explícitos para guardar referencias a niveles de jerarquía
    director = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True, related_name='dir_subordinados'
    )
    gerente = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True, related_name='ger_subordinados'
    )
    jefe = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True, related_name='jefe_subordinados'
    )
    # Compatibilidad: exponer 'manager' y 'equipo' como propiedades que
    # utilizan los nuevos campos jerárquicos. Esto mantiene compatibilidad
    # con código que aún usa empleado.manager o empleado.equipo.
    @property
    def manager(self):
        """Retorna el superior inmediato: preferir jefe, luego gerente, luego director."""
        return self.jefe or self.gerente or self.director

    @manager.setter
    def manager(self, value):
        """Compatibilidad para asignar un manager.

        Si se asigna un Empleado, colocamos su id en el campo jerárquico
        correspondiente (jefe/gerente/director) según su `jerarquia`.
        Si se asigna None, limpiamos los campos jerárquicos directos.
        Se usa update() para evitar recursiones en save().
        """
        if value is None:
            Empleado.objects.filter(pk=self.pk).update(jefe_id=None, gerente_id=None, director_id=None)
            self.jefe = None
            self.gerente = None
            self.director = None
            return

        # value should be an Empleado instance
        jer = getattr(value, 'jerarquia', None)
        if jer == 'jefe':
            Empleado.objects.filter(pk=self.pk).update(jefe_id=value.id)
            self.jefe = value
        elif jer == 'gerente':
            Empleado.objects.filter(pk=self.pk).update(gerente_id=value.id)
            self.gerente = value
        elif jer == 'director':
            Empleado.objects.filter(pk=self.pk).update(director_id=value.id)
            self.director = value
        else:
            # fallback: set jefe_id
            Empleado.objects.filter(pk=self.pk).update(jefe_id=value.id)
            self.jefe = value
        # Recompute propagated values for dependents
        try:
            self._recompute_and_propagate()
        except Exception:
            # Best-effort: ignore propagation errors here
            pass

    @property
    def equipo(self):
        """QuerySet con los empleados que tienen a este empleado como jefe/gerente/director."""
        return Empleado.objects.filter(models.Q(jefe=self) | models.Q(gerente=self) | models.Q(director=self))
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

    def _compute_hierarchy_ids(self):
        """
        Recorre la cadena de managers hacia arriba y devuelve una tupla
        (director_id, gerente_id, jefe_id) con los ids encontrados o None.
        """
        director_id = None
        gerente_id = None
        jefe_id = None

        cur = self.manager
        visited = set()
        while cur is not None and cur.id not in visited:
            visited.add(cur.id)
            if director_id is None and cur.jerarquia == 'director':
                director_id = cur.id
            # gerente puede ser gerente o director (tomamos el más cercano)
            if gerente_id is None and cur.jerarquia in ('gerente', 'director'):
                gerente_id = cur.id
            if jefe_id is None and cur.jerarquia == 'jefe':
                jefe_id = cur.id
            cur = cur.manager

        return director_id, gerente_id, jefe_id

    def _recompute_and_propagate(self):
        """
        Recalcula los campos director/gerente/jefe para este empleado
        y los propaga recursivamente a sus subordinados directos.
        Usa actualizaciones en base de datos para evitar recursión en save().
        """
        director_id, gerente_id, jefe_id = self._compute_hierarchy_ids()

        # Actualizar en BD si hay cambios
        updated = False
        changes = {}
        if self.director_id != director_id:
            changes['director_id'] = director_id
            self.director_id = director_id
            updated = True
        if self.gerente_id != gerente_id:
            changes['gerente_id'] = gerente_id
            self.gerente_id = gerente_id
            updated = True
        if self.jefe_id != jefe_id:
            changes['jefe_id'] = jefe_id
            self.jefe_id = jefe_id
            updated = True

        if updated and changes:
            Empleado.objects.filter(pk=self.pk).update(**changes)

        # Propagar a subordinados directos (usar equipo derivado de jerarquías)
        directos = list(self.equipo)
        for sub in directos:
            sub._recompute_and_propagate()

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

    @property
    def puede_gestionar_equipo(self):
        """
        Determina si este empleado puede gestionar equipos (ver equipos, aprobar solicitudes).
        Incluye managers reales y jefes por jerarquía.
        """
        # Jerarquías que pueden gestionar equipos
        jerarquias_gestoras = ['director', 'gerente', 'sub_gerente', 'jefe']
        return self.es_manager or self.jerarquia in jerarquias_gestoras or self.es_rrhh

    # ---------- Helpers jerárquicos ----------
    def get_equipo_directo(self):
        """
        Retorna QuerySet con los empleados cuyo manager es este empleado (equipo directo).
        """
        # Devuelve empleados que tienen a este empleado como jefe/gerente/director
        return self.equipo

    def get_equipo_extendido(self, max_depth=10):
        """
        Retorna una lista plana con el equipo extendido (recursivo) hasta max_depth niveles.
        Evita ciclos mediante un set de IDs visitados.
        """
        resultados = []
        visitados = set()

        def _recorrer(nodo, profundidad):
            if profundidad > max_depth or nodo.id in visitados:
                return
            visitados.add(nodo.id)
            # Buscar directos según campos jerárquicos
            directos = list(Empleado.objects.filter(models.Q(jefe=nodo) | models.Q(gerente=nodo) | models.Q(director=nodo)))
            for miembro in directos:
                resultados.append(miembro)
                _recorrer(miembro, profundidad + 1)

        _recorrer(self, 1)
        return resultados

    def get_gerente(self):
        """
        Retorna el gerente más cercano en la jerarquía hacia arriba (primer 'gerente' o 'director').
        Si el manager directo no existe, retorna None.
        """
        actual = self
        while actual and actual.manager:
            if actual.manager.jerarquia in ['gerente', 'director']:
                return actual.manager
            actual = actual.manager
        return None

    def get_director(self):
        """
        Retorna el director asociado al empleado recorriendo hacia arriba por `manager`.
        """
        actual = self
        while actual and actual.manager:
            if actual.manager.jerarquia == 'director':
                return actual.manager
            actual = actual.manager
        return None

    def get_team_tree(self, max_depth=5):
        """
        Retorna una estructura tipo árbol (dict) con el equipo del empleado, útil para render en templates.
        { 'empleado': <Empleado>, 'directos': [ {...}, ... ] }
        """
        def _build(node, depth):
            if depth < 0:
                return {'empleado': node, 'directos': []}
            hijos = Empleado.objects.filter(models.Q(jefe=node) | models.Q(gerente=node) | models.Q(director=node))
            return {
                'empleado': node,
                'directos': [_build(h, depth - 1) for h in hijos]
            }

        return _build(self, max_depth)

    def calcular_dias_disponibles(self):
        """
        Calcula días de vacaciones disponibles según la política de la empresa.
        Regla implementada:
        - Cada período anual otorga 30 días.
        - Todos los empleados reciben el primer período desde el inicio.
        - Se suman 30 días adicionales solo cuando se cumple un período adicional (aniversario).
        - Días disponibles = 30 * períodos_totales - días_utilizados (todas las solicitudes aprobadas desde contratación)
        """
        from datetime import date
        hoy = date.today()

        # Calcular años completos desde la fecha de contratación
        if self.fecha_contratacion:
            años_completos = hoy.year - self.fecha_contratacion.year - (
                1 if (hoy.month, hoy.day) < (self.fecha_contratacion.month, self.fecha_contratacion.day) else 0
            )
        else:
            años_completos = 0

        # Periodos totales: al menos 1 (el período inicial)
        periodos = max(1, años_completos)

        # Total de días otorgados hasta la fecha
        total_otorgado = 30 * periodos

        # Sumar todos los días aprobados desde la contratación (histórico)
        solicitudes_aprobadas = SolicitudVacaciones.objects.filter(
            empleado=self,
            estado='aprobado'
        )
        dias_utilizados = sum(s.dias_solicitados for s in solicitudes_aprobadas)

        return max(0, total_otorgado - dias_utilizados)

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
    
    def calcular_dias_calendario(self, fecha_inicio, fecha_fin):
        """
        Calcula días del período (días corridos simples).
        Política simplificada: Solo cuenta días del período, no diferencia calendario vs laborable.
        """
        if not fecha_inicio or not fecha_fin:
            return 0
        
        delta = fecha_fin - fecha_inicio
        return delta.days + 1
    
    def contar_fines_de_semana(self, fecha_inicio, fecha_fin):
        """
        Cuenta sábados y domingos en el rango de fechas
        """
        if not fecha_inicio or not fecha_fin:
            return {'sabados': 0, 'domingos': 0}
        
        from datetime import timedelta
        
        sabados = 0
        domingos = 0
        fecha_actual = fecha_inicio
        
        while fecha_actual <= fecha_fin:
            if fecha_actual.weekday() == 5:  # Sábado
                sabados += 1
            elif fecha_actual.weekday() == 6:  # Domingo
                domingos += 1
            fecha_actual += timedelta(days=1)
        
        return {'sabados': sabados, 'domingos': domingos}
    
    def validar_periodo_vacaciones(self, fecha_inicio, fecha_fin):
        """
        Valida período de vacaciones con política simple:
    - El empleado tiene X días totales (30 por período; la política actual es 30 días por período cumplido)
        - Debe incluir fines de semana en sus períodos (política educativa)
        - Se cuentan los días solicitados contra el total disponible
        """
        # Calcular días del período (simplemente días corridos)
        dias_periodo = (fecha_fin - fecha_inicio).days + 1
        fines_semana = self.contar_fines_de_semana(fecha_inicio, fecha_fin)
        
        errores = []
        advertencias = []
        mensajes_informativos = []
        
        # Validaciones básicas (solo errores críticos)
        if fecha_fin < fecha_inicio:
            errores.append("La fecha de fin no puede ser anterior a la fecha de inicio")
        
        # Verificar días disponibles (ESTO ES LO IMPORTANTE)
        dias_disponibles = self.empleado.calcular_dias_disponibles()
        if dias_periodo > dias_disponibles:
            errores.append(f"Estás solicitando {dias_periodo} días pero solo tienes {dias_disponibles} disponibles en tu cuota anual")
        
        # Mensajes informativos sobre fines de semana (política educativa)
        if fines_semana['sabados'] == 0 and fines_semana['domingos'] == 0:
            mensajes_informativos.append("💡 POLÍTICA: Se recomienda incluir algunos fines de semana en tus períodos de vacaciones")
        elif fines_semana['sabados'] > 0 or fines_semana['domingos'] > 0:
            mensajes_informativos.append(f"✅ Excelente! Cumples la política incluyendo {fines_semana['sabados']} sábados y {fines_semana['domingos']} domingos")
        
        # Verificar cumplimiento anual de política de fines de semana
        cumplimiento_anual = {}
        if self.empleado:
            cumplimiento_anual = self.verificar_cumplimiento_politica_anual()
            if cumplimiento_anual['necesita_mas_fines_semana']:
                mensajes_informativos.append(f"📅 Para cumplir mejor la política anual, considera incluir más fines de semana (llevas {cumplimiento_anual['fines_semana_incluidos']} de {cumplimiento_anual['meta_fines_semana']} recomendados)")
        else:
            # Si no hay empleado asignado, usar valores por defecto
            cumplimiento_anual = {
                'total_sabados': 0,
                'total_domingos': 0,
                'fines_semana_incluidos': 0,
                'meta_fines_semana': 4,
                'necesita_mas_fines_semana': True,
                'fines_semana_faltantes': 4,
                'porcentaje_cumplimiento': 0
            }
        
        # Advertencia sobre días no utilizados (si quedan muchos días)
        if dias_periodo < dias_disponibles:
            dias_restantes = dias_disponibles - dias_periodo
            if dias_restantes > 10:
                advertencias.append(f"Te quedan {dias_restantes} días de vacaciones pendientes. Considera planificar más períodos.")
        
        return {
            'valido': len(errores) == 0,
            'dias_periodo': dias_periodo,  # Cambié de 'dias_calendario' a 'dias_periodo'
            'fines_semana': fines_semana,
            'errores': errores,
            'advertencias': advertencias,
            'mensajes_informativos': mensajes_informativos,
            'cumplimiento_anual': cumplimiento_anual,
            'dias_disponibles': dias_disponibles,
            'dias_restantes': max(0, dias_disponibles - dias_periodo)
        }
    
    def verificar_cumplimiento_politica_anual(self):
        """
        Verifica si el empleado ha cumplido con la política anual de incluir fines de semana
        """
        from datetime import date
        año_actual = date.today().year
        
        # Obtener todas las solicitudes aprobadas del año actual
        solicitudes_año = SolicitudVacaciones.objects.filter(
            empleado=self.empleado,
            estado='aprobado',
            fecha_inicio__year=año_actual
        )
        
        # Contar total de fines de semana incluidos en vacaciones del año
        total_sabados = 0
        total_domingos = 0
        
        for solicitud in solicitudes_año:
            fines_semana = self.contar_fines_de_semana(solicitud.fecha_inicio, solicitud.fecha_fin)
            total_sabados += fines_semana['sabados']
            total_domingos += fines_semana['domingos']
        
        # Política flexible: Se recomienda incluir al menos algunos fines de semana
        # Meta sugerida: al menos 4 fines de semana en el año (más flexible)
        meta_fines_semana = 4
        
        fines_semana_incluidos = total_sabados + total_domingos
        necesita_mas = fines_semana_incluidos < meta_fines_semana
        faltantes = max(0, meta_fines_semana - fines_semana_incluidos)
        
        return {
            'total_sabados': total_sabados,
            'total_domingos': total_domingos,
            'fines_semana_incluidos': fines_semana_incluidos,
            'meta_fines_semana': meta_fines_semana,
            'necesita_mas_fines_semana': necesita_mas,
            'fines_semana_faltantes': faltantes,
            'porcentaje_cumplimiento': min(100, (fines_semana_incluidos / meta_fines_semana) * 100) if meta_fines_semana > 0 else 100
        }
    
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
        dias_disponibles = self.empleado.calcular_dias_disponibles()
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

    MOTIVO_CONTRATACION_CHOICES = [
        ('nuevo_puesto', 'Nuevo puesto de trabajo'),
        ('reemplazo_promocion', 'Reemplazo por promoción'),
        ('reemplazo_renuncia', 'Reemplazo por renuncia'),
        ('reemplazo_vencimiento', 'Reemplazo por vencimiento de contrato'),
        ('fallecimiento', 'Fallecimiento'),
        ('otros', 'Otros'),
    ]

    # Quién solicita
    solicitante = models.ForeignKey(
        Empleado, on_delete=models.CASCADE, related_name='solicitudes_nuevo_colaborador'
    )

    # Campos solicitados
    area_solicitante = models.CharField(max_length=120)
    fecha_solicitud = models.DateField(auto_now_add=True)
    persona_responsable = models.CharField(max_length=120)
    dni_colaborador = models.CharField(
        max_length=8,
        validators=[validar_dni],
        help_text='DNI del nuevo colaborador (8 dígitos)',
        verbose_name='DNI del Colaborador'
    )
    nombre_colaborador = models.CharField(
        max_length=100,
        verbose_name='Nombre del Colaborador',
        help_text='Nombre completo del nuevo colaborador'
    )
    apellido_colaborador = models.CharField(
        max_length=100,
        verbose_name='Apellido del Colaborador',
        help_text='Apellidos del nuevo colaborador'
    )
    email_colaborador = models.EmailField(
        verbose_name='Email del Colaborador',
        help_text='Correo electrónico del nuevo colaborador'
    )
    fecha_inicio_labores = models.DateField()
    grupo_ocupacional = models.CharField(max_length=20, choices=GRUPO_OCUPACIONAL_CHOICES)
    puesto_a_solicitud = models.CharField(max_length=120)
    denominacion_puesto = models.CharField(max_length=20, choices=DENOMINACION_PUESTO_CHOICES)
    motivo_contratacion = models.CharField(
        max_length=30, 
        choices=MOTIVO_CONTRATACION_CHOICES,
        help_text='Seleccione el motivo de la contratación'
    )
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