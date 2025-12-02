from django.test import TestCase
from django.core import mail
from django.urls import reverse
from .models import Cruise, InfoRequest

class EmailTestCase(TestCase):
    """
    Tests para verificar el envío de emails cuando un usuario solicita información.
    Siguiendo metodología TDD (Test-Driven Development).
    """
    
    def setUp(self):
        """Configuración inicial para los tests"""
        # Crear un crucero de prueba
        self.cruise = Cruise.objects.create(
            name="Viaje a Marte",
            description="Un viaje increíble al planeta rojo"
        )
        
        # Datos del formulario
        self.form_data = {
            'name': 'Juan Pérez',
            'email': 'juan.perez@example.com',
            'notes': 'Me gustaría más información sobre el viaje',
            'cruise': self.cruise.id
        }
    
    def test_email_sent_on_info_request_creation(self):
        """
        Test 1: Verificar que se envía un email cuando se crea una solicitud de información.
        """
        # Limpiar el buzón de salida
        mail.outbox = []
        
        # Enviar el formulario
        response = self.client.post(reverse('info_request'), self.form_data)
        
        # Verificar que se redirige correctamente
        self.assertEqual(response.status_code, 302)
        
        # Verificar que se creó la solicitud en la base de datos
        self.assertEqual(InfoRequest.objects.count(), 1)
        
        # TEST QUE FALLARÁ: Verificar que se envió exactamente un email
        self.assertEqual(len(mail.outbox), 1)
    
    def test_email_contains_correct_subject(self):
        """
        Test 2: Verificar que el email tiene el asunto correcto.
        """
        mail.outbox = []
        
        self.client.post(reverse('info_request'), self.form_data)
        
        # TEST QUE FALLARÁ: Verificar el asunto del email
        email = mail.outbox[0]
        self.assertIn('ReleCloud', email.subject)
        self.assertIn(self.cruise.name, email.subject)
    
    def test_email_sent_to_correct_recipient(self):
        """
        Test 3: Verificar que el email se envía al destinatario correcto.
        """
        mail.outbox = []
        
        self.client.post(reverse('info_request'), self.form_data)
        
        # TEST QUE FALLARÁ: Verificar el destinatario
        email = mail.outbox[0]
        self.assertIn(self.form_data['email'], email.to)
    
    def test_email_contains_cruise_information(self):
        """
        Test 4: Verificar que el email contiene información sobre el crucero solicitado.
        """
        mail.outbox = []
        
        self.client.post(reverse('info_request'), self.form_data)
        
        # TEST QUE FALLARÁ: Verificar el contenido del email
        email = mail.outbox[0]
        self.assertIn(self.cruise.name, email.body)
        self.assertIn(self.cruise.description, email.body)
    
    def test_email_contains_user_name(self):
        """
        Test 5: Verificar que el email incluye el nombre del usuario.
        """
        mail.outbox = []
        
        self.client.post(reverse('info_request'), self.form_data)
        
        # TEST QUE FALLARÁ: Verificar que incluye el nombre del usuario
        email = mail.outbox[0]
        self.assertIn(self.form_data['name'], email.body)
    
    def test_email_from_address(self):
        """
        Test 6: Verificar que el email tiene un remitente configurado correctamente.
        """
        mail.outbox = []
        
        self.client.post(reverse('info_request'), self.form_data)
        
        # TEST QUE FALLARÁ: Verificar el remitente
        email = mail.outbox[0]
        self.assertTrue(len(email.from_email) > 0)
        self.assertIn('@', email.from_email)
