# empleados/tests.py
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Empleado, SolicitudVacaciones # Asegúrate de que estos modelos existan y se importen correctamente
import datetime

class SolicitudVacacionesTests(TestCase):

    def setUp(self):
        """
        Configuración inicial para las pruebas.
        Crea un usuario, un empleado y un cliente de prueba que se loguea.
        """
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.empleado = Empleado.objects.create(user=self.user) # Asume que el modelo Empleado se relaciona con User
        self.client = Client()
        self.client.login(username='testuser', password='password123')

    def test_crear_nueva_solicitud_vacaciones(self):
        """
        Prueba la creación de una nueva solicitud de vacaciones a través de una petición POST.
        """
        url = reverse('nueva_solicitud_vacaciones')
        
        # Datos para la solicitud POST
        fecha_inicio = datetime.date.today() + datetime.timedelta(days=10)
        fecha_fin = datetime.date.today() + datetime.timedelta(days=15)
        
        datos_solicitud = {
            'fecha_inicio': fecha_inicio.strftime('%Y-%m-%d'),
            'fecha_fin': fecha_fin.strftime('%Y-%m-%d'),
            'comentarios': 'Prueba de solicitud de vacaciones.'
        }

        response = self.client.post(url, datos_solicitud)

        # 1. Verificar que se redirige a la lista de solicitudes tras crearla exitosamente.
        self.assertRedirects(response, reverse('solicitudes_vacaciones'))

        # 2. Verificar que la solicitud se creó en la base de datos con los datos correctos.
        self.assertTrue(SolicitudVacaciones.objects.filter(empleado=self.empleado, fecha_inicio=fecha_inicio).exists())
        solicitud = SolicitudVacaciones.objects.get(empleado=self.empleado, fecha_inicio=fecha_inicio)
        self.assertEqual(solicitud.fecha_fin, fecha_fin)
        self.assertEqual(solicitud.estado, 'Pendiente') # Asumiendo que 'Pendiente' es el estado inicial por defecto.