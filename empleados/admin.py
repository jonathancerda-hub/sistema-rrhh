from django.contrib import admin
from .models import Empleado, SolicitudVacaciones, SolicitudNuevoColaborador

@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'apellido', 'email', 'puesto', 'jerarquia', 'gerencia', 'fecha_contratacion', 'dias_vacaciones_disponibles', 'manager', 'puede_gestionar_equipo', 'puede_solicitar_nuevo_empleado']
    # 'manager' was removed as a DB field; show it via get_manager and remove from filters
    list_display = ['nombre', 'apellido', 'email', 'puesto', 'jerarquia', 'gerencia', 'fecha_contratacion', 'dias_vacaciones_disponibles', 'get_manager', 'puede_gestionar_equipo', 'puede_solicitar_nuevo_empleado']
    list_filter = ['puesto', 'jerarquia', 'gerencia', 'fecha_contratacion', 'es_rrhh']
    search_fields = ['nombre', 'apellido', 'email', 'puesto', 'gerencia', 'jerarquia']
    ordering = ['nombre', 'apellido']
    readonly_fields = ['puede_gestionar_equipo', 'puede_solicitar_nuevo_empleado']
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('nombre', 'apellido', 'email', 'puesto')
        }),
        ('Información Laboral', {
            # Mostrar los campos jerárquicos explícitos en lugar del antiguo campo manager
            'fields': ('jerarquia', 'gerencia', 'area', 'fecha_contratacion', 'dias_vacaciones_disponibles', 'jefe', 'gerente', 'director')
        }),
        ('Información del Sistema', {
            'fields': ('puede_gestionar_equipo', 'es_rrhh', 'puede_solicitar_nuevo_empleado'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """
        Validar antes de guardar
        """
        obj.clean()  # Ejecutar validaciones personalizadas
        super().save_model(request, obj, form, change)

    def get_manager(self, obj):
        """Muestra el manager calculado (compatibilidad)."""
        mgr = obj.manager
        return f"{mgr.nombre} {mgr.apellido}" if mgr else ''
    get_manager.short_description = 'Manager'

@admin.register(SolicitudVacaciones)
class SolicitudVacacionesAdmin(admin.ModelAdmin):
    list_display = ['empleado', 'fecha_inicio', 'fecha_fin', 'dias_solicitados', 'tipo_vacaciones', 'periodo_vacacional', 'estado', 'fecha_solicitud']
    list_filter = ['estado', 'tipo_vacaciones', 'periodo_vacacional', 'fecha_solicitud', 'empleado__puesto']
    search_fields = ['empleado__nombre', 'empleado__apellido', 'empleado__email', 'motivo']
    ordering = ['-fecha_solicitud']
    readonly_fields = ['fecha_solicitud', 'dias_calendario']
    
    fieldsets = (
        ('Información del Empleado', {
            'fields': ('empleado', 'tipo_vacaciones', 'periodo_vacacional')
        }),
        ('Detalles de la Solicitud', {
            'fields': ('fecha_inicio', 'fecha_fin', 'dias_solicitados', 'motivo')
        }),
        ('Estado y Procesamiento', {
            'fields': ('estado', 'fecha_resolucion', 'comentario_admin', 'procesado_por')
        }),
        ('Información del Sistema', {
            'fields': ('fecha_solicitud', 'dias_calendario'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        # Si el estado cambió, establecer fecha_resolucion
        if change:
            old_obj = self.model.objects.get(pk=obj.pk)
            if old_obj.estado != obj.estado and obj.estado in ['aprobado', 'rechazado']:
                from django.utils import timezone
                obj.fecha_resolucion = timezone.now()
                obj.procesado_por = request.user.empleado if hasattr(request.user, 'empleado') else None
        
        super().save_model(request, obj, form, change)


@admin.register(SolicitudNuevoColaborador)
class SolicitudNuevoColaboradorAdmin(admin.ModelAdmin):
    list_display = [
        'area_solicitante', 'puesto_a_solicitud', 'grupo_ocupacional',
        'denominacion_puesto', 'fecha_inicio_labores', 'estado', 'fecha_solicitud'
    ]
    list_filter = ['estado', 'grupo_ocupacional', 'denominacion_puesto', 'fecha_solicitud']
    search_fields = [
        'area_solicitante', 'puesto_a_solicitud', 'persona_responsable',
        'motivo_contratacion'
    ]
    readonly_fields = ['fecha_solicitud']
