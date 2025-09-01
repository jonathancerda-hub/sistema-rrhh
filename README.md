# 🏢 Sistema de Recursos Humanos (RRHH)

Un sistema web completo de gestión de recursos humanos desarrollado en Django, que permite la gestión de empleados, solicitudes de vacaciones, perfiles de usuario y notificaciones automáticas.

## 🚀 Características Principales

### 👥 Gestión de Empleados
- **Perfiles completos** con información personal y profesional
- **Jerarquías organizacionales** (Gerentes, Managers, Empleados)
- **Áreas de trabajo** y **gerencias** configurables
- **Sistema de autenticación** y autorización
- **Fotos de perfil** con validación automática

### 🏖️ Gestión de Vacaciones
- **Solicitudes de vacaciones** con validación de políticas
- **Aprobación en dos niveles** (Manager → RRHH)
- **Cálculo automático** de días disponibles por antigüedad
- **Tipos de vacaciones** (regulares, compensatorias, etc.)
- **Calendario de vacaciones** y control de disponibilidad

### 📧 Sistema de Notificaciones
- **Notificaciones automáticas** por email
- **Templates HTML profesionales** y responsive
- **Recordatorios** para solicitudes pendientes
- **Configuración Gmail** para producción
- **Panel de administración** de notificaciones

### 🛡️ Control de Acceso
- **Roles diferenciados**: Empleado, Manager, RRHH
- **Permisos granulares** por funcionalidad
- **Dashboard personalizado** según el rol
- **Seguridad de datos** y validaciones

## 🛠️ Tecnologías Utilizadas

- **Backend**: Django 5.2.5
- **Frontend**: HTML5, CSS3, JavaScript
- **Base de Datos**: SQLite (desarrollo), compatible con PostgreSQL/MySQL
- **Email**: Django Email + Gmail SMTP
- **Autenticación**: Django Auth System
- **Archivos**: Pillow para manejo de imágenes

## 📋 Requisitos

- Python 3.11+
- Django 5.2.5
- Pillow 10.4.0
- Navegador web moderno

## 🚀 Instalación y Configuración

### 1. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/proyecto-rrhh.git
cd proyecto-rrhh
```

### 2. Crear entorno virtual
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar dependencias
```bash
pip install django==5.2.5
pip install pillow==10.4.0
```

### 4. Configurar base de datos
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Crear superusuario
```bash
python manage.py createsuperuser
```

### 6. Cargar datos de prueba (opcional)
```bash
python manage.py crear_usuarios_prueba
python manage.py crear_usuario_rrhh
```

### 7. Ejecutar servidor de desarrollo
```bash
python manage.py runserver
```

## 📧 Configuración de Email

### Desarrollo (Consola)
Los emails se mostrarán en la terminal (configuración por defecto).

### Producción (Gmail)
Editar `nucleo_rrhh/settings.py`:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'tu-email@gmail.com'
EMAIL_HOST_PASSWORD = 'tu-app-password'  # Contraseña de aplicación
```

## 👥 Usuarios por Defecto

### Empleados de Prueba
- **Usuario**: `ena.fernandez@agrovetmarket.com` / **Password**: `password123`
- **Usuario**: `teodoro.balarezo@agrovetmarket.com` / **Password**: `password123`

### Personal RRHH
- **Usuario**: `lucia.rrhh@agrovetmarket.com` / **Password**: `password123`
- **Usuario**: `rrhh.admin@empresa.com` / **Password**: `password123`

## 🔧 Comandos Útiles

### Enviar recordatorios de vacaciones
```bash
python manage.py enviar_recordatorios --dias 2 --dry-run
```

### Crear usuario RRHH
```bash
python manage.py crear_usuario_rrhh
```

### Crear usuarios de prueba
```bash
python manage.py crear_usuarios_prueba
```

## 📱 Funcionalidades por Rol

### 👤 Empleado
- Ver y editar su perfil (solo RRHH puede editar datos)
- Crear solicitudes de vacaciones
- Consultar historial de solicitudes
- Recibir notificaciones por email

### 👨‍💼 Manager
- Dashboard con métricas del equipo
- Aprobar/rechazar solicitudes de su equipo
- Ver calendario de vacaciones del equipo
- Gestionar perfiles de empleados

### 👥 RRHH
- Control total del sistema
- Procesar todas las solicitudes
- Configurar notificaciones
- Gestionar empleados y estructura organizacional
- Panel de administración avanzado

## 🗂️ Estructura del Proyecto

```
proyecto_rrhh/
├── empleados/              # App principal
│   ├── management/
│   │   └── commands/      # Comandos Django personalizados
│   ├── migrations/        # Migraciones de base de datos
│   ├── templates/         # Templates HTML
│   │   └── empleados/
│   │       └── emails/    # Templates de email
│   ├── models.py          # Modelos de datos
│   ├── views.py           # Vistas principales
│   ├── views_notificaciones.py  # Vistas de notificaciones
│   ├── forms.py           # Formularios
│   ├── utils.py           # Utilidades (emails)
│   └── urls.py            # URLs de la app
├── nucleo_rrhh/           # Configuración del proyecto
│   ├── settings.py        # Configuraciones
│   ├── urls.py            # URLs principales
│   └── wsgi.py            # WSGI config
├── media/                 # Archivos subidos (fotos, etc.)
├── manage.py              # Comando principal Django
└── requirements.txt       # Dependencias (por crear)
```

## 🎯 Próximas Funcionalidades

- [ ] **Reportes avanzados** con gráficos
- [ ] **API REST** para integración móvil
- [ ] **Chat interno** entre empleados
- [ ] **Gestión de nómina** básica
- [ ] **Calendario compartido** del equipo
- [ ] **Evaluaciones de desempeño**
- [ ] **Onboarding** para nuevos empleados

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 📞 Contacto

**Proyecto**: Sistema RRHH  
**Desarrollador**: [Tu Nombre]  
**Email**: [tu-email@ejemplo.com]  
**Link del Proyecto**: [https://github.com/tu-usuario/proyecto-rrhh](https://github.com/tu-usuario/proyecto-rrhh)

## 🙏 Agradecimientos

- Django Community por el excelente framework
- Bootstrap Icons por los iconos utilizados
- Pillow por el manejo de imágenes
- Gmail por el servicio SMTP confiable

---

⭐ **¡No olvides dar una estrella al proyecto si te fue útil!** ⭐
