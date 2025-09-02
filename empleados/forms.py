from django import forms
from django.core.exceptions import ValidationError
from datetime import date
from .models import SolicitudVacaciones, SolicitudNuevoColaborador, Empleado

class SolicitudVacacionesForm(forms.ModelForm):
    class Meta:
        model = SolicitudVacaciones
        fields = ['fecha_inicio', 'fecha_fin', 'motivo', 'periodo_vacacional', 'tipo_vacaciones']
        widgets = {
            'fecha_inicio': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                    'min': date.today().strftime('%Y-%m-%d')
                }
            ),
            'fecha_fin': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                    'min': date.today().strftime('%Y-%m-%d')
                }
            ),
            'motivo': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Describe el motivo de tu solicitud de vacaciones...'
                }
            ),
            'periodo_vacacional': forms.Select(
                attrs={
                    'class': 'form-control',
                    'id': 'periodo_vacacional'
                }
            ),
            'tipo_vacaciones': forms.Select(
                attrs={
                    'class': 'form-control',
                    'id': 'tipo_vacaciones'
                }
            )
        }
        labels = {
            'fecha_inicio': 'Fecha de Inicio',
            'fecha_fin': 'Fecha de Fin',
            'motivo': 'Motivo (Opcional)',
            'periodo_vacacional': 'Período Vacacional',
            'tipo_vacaciones': 'Tipo de Vacaciones'
        }
        help_texts = {
            'periodo_vacacional': 'Selecciona el período vacacional al que corresponde tu solicitud',
            'tipo_vacaciones': 'El tipo se determina automáticamente según tu antigüedad, pero puedes modificarlo si es necesario'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Hacer el campo tipo_vacaciones de solo lectura inicialmente
        self.fields['tipo_vacaciones'].widget.attrs['readonly'] = True
        self.fields['tipo_vacaciones'].widget.attrs['class'] = 'form-control bg-light'
        
        # Agregar información sobre el cálculo automático
        self.fields['tipo_vacaciones'].help_text = (
            'Este campo se calcula automáticamente según tu antigüedad. '
            'Puedes desbloquearlo para hacer cambios si es necesario.'
        )

    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')
        
        if fecha_inicio and fecha_fin:
            # Validar que la fecha de inicio no sea anterior a hoy
            if fecha_inicio < date.today():
                raise forms.ValidationError(
                    'La fecha de inicio no puede ser anterior a hoy.'
                )
            
            # Validar que la fecha de fin no sea anterior a la de inicio
            if fecha_fin < fecha_inicio:
                raise forms.ValidationError(
                    'La fecha de fin no puede ser anterior a la fecha de inicio.'
                )
            
            # Validar que no se soliciten más de 30 días consecutivos
            delta = fecha_fin - fecha_inicio
            if delta.days > 30:
                raise forms.ValidationError(
                    'No se pueden solicitar más de 30 días consecutivos de vacaciones.'
                )
        
        return cleaned_data


class SolicitudNuevoColaboradorForm(forms.ModelForm):
    # Convertimos a selector de empleados (se limpiará a string para el modelo)
    persona_responsable = forms.ModelChoiceField(
        queryset=Empleado.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Persona Responsable'
    )

    class Meta:
        model = SolicitudNuevoColaborador
        fields = [
            'area_solicitante', 'persona_responsable', 'dni_colaborador', 'nombre_colaborador',
            'apellido_colaborador', 'email_colaborador', 'fecha_inicio_labores',
            'grupo_ocupacional', 'puesto_a_solicitud', 'denominacion_puesto',
            'motivo_contratacion', 'modalidad_contratacion', 'tiempo_meses'
        ]
        widgets = {
            'area_solicitante': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'dni_colaborador': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '12345678',
                'maxlength': '8',
                'pattern': '[0-9]{8}',
                'title': 'Ingrese exactamente 8 dígitos'
            }),
            'nombre_colaborador': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el nombre completo'
            }),
            'apellido_colaborador': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese los apellidos'
            }),
            'email_colaborador': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'usuario@empresa.com'
            }),
            'fecha_inicio_labores': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'grupo_ocupacional': forms.Select(attrs={'class': 'form-select'}),
            'puesto_a_solicitud': forms.TextInput(attrs={'class': 'form-control'}),
            'denominacion_puesto': forms.Select(attrs={'class': 'form-select'}),
            'motivo_contratacion': forms.Select(attrs={'class': 'form-select'}),
            'modalidad_contratacion': forms.TextInput(attrs={'class': 'form-control'}),
            'tiempo_meses': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }
        labels = {
            'area_solicitante': 'Área Solicitante',
            'dni_colaborador': 'DNI del Colaborador',
            'nombre_colaborador': 'Nombre del Colaborador',
            'apellido_colaborador': 'Apellido del Colaborador',
            'email_colaborador': 'Email del Colaborador',
            'fecha_inicio_labores': 'Fecha de inicio de labores',
            'grupo_ocupacional': 'Grupo Ocupacional',
            'puesto_a_solicitud': 'Puesto a Solicitud',
            'denominacion_puesto': 'Denominación del Puesto',
            'motivo_contratacion': 'Motivo de la contratación',
            'modalidad_contratacion': 'Modalidad de Contratación',
            'tiempo_meses': 'Especificar Tiempo (Meses)'
        }

    def __init__(self, *args, **kwargs):
        responsable_queryset = kwargs.pop('responsable_queryset', None)
        responsable_initial = kwargs.pop('responsable_initial', None)
        super().__init__(*args, **kwargs)
        # Cargar queryset del selector
        if responsable_queryset is not None:
            self.fields['persona_responsable'].queryset = responsable_queryset
        else:
            self.fields['persona_responsable'].queryset = Empleado.objects.none()
        # Inicial seleccionado (id del empleado)
        if responsable_initial is not None:
            self.fields['persona_responsable'].initial = responsable_initial

    def clean_persona_responsable(self):
        empleado = self.cleaned_data.get('persona_responsable')
        if isinstance(empleado, Empleado):
            return f"{empleado.nombre} {empleado.apellido}".strip()
        return empleado

    def clean(self):
        cleaned = super().clean()
        fecha_inicio = cleaned.get('fecha_inicio_labores')
        if fecha_inicio and fecha_inicio < date.today():
            raise ValidationError('La fecha de inicio de labores no puede ser anterior a hoy.')
        tiempo = cleaned.get('tiempo_meses')
        if tiempo is not None and tiempo <= 0:
            raise ValidationError('El tiempo en meses debe ser mayor a 0.')
        return cleaned


class EmpleadoPerfilForm(forms.ModelForm):
    """
    Formulario para que los empleados editen su perfil básico
    """
    class Meta:
        model = Empleado
        fields = ['nombre', 'apellido', 'dni', 'email', 'foto_perfil']
        widgets = {
            'nombre': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingresa tu nombre'
                }
            ),
            'apellido': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingresa tu apellido'
                }
            ),
            'dni': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': '12345678',
                    'maxlength': '8',
                    'pattern': '[0-9]{8}',
                    'title': 'Ingrese exactamente 8 dígitos'
                }
            ),
            'email': forms.EmailInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'tu.email@empresa.com'
                }
            ),
            'foto_perfil': forms.FileInput(
                attrs={
                    'class': 'form-control',
                    'accept': 'image/*',
                    'id': 'foto_perfil'
                }
            )
        }
        labels = {
            'nombre': 'Nombre',
            'apellido': 'Apellido',
            'dni': 'DNI',
            'email': 'Correo Electrónico',
            'foto_perfil': 'Foto de Perfil'
        }
        help_texts = {
            'dni': 'Documento Nacional de Identidad (8 dígitos)',
            'foto_perfil': 'Sube una imagen para tu perfil (JPG, PNG, máximo 5MB)',
            'email': 'Este email se usará para notificaciones importantes'
        }

    def clean_foto_perfil(self):
        foto = self.cleaned_data.get('foto_perfil')
        if foto:
            # Verificar el tamaño del archivo (máximo 5MB)
            if foto.size > 5 * 1024 * 1024:
                raise forms.ValidationError('El archivo es demasiado grande. Máximo 5MB.')
            
            # Verificar el tipo de archivo
            valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
            file_extension = foto.name.lower().split('.')[-1]
            if f'.{file_extension}' not in valid_extensions:
                raise forms.ValidationError('Solo se permiten archivos JPG, PNG o GIF.')
        
        return foto

