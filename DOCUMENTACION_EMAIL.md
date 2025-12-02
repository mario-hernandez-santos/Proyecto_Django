# Documentación: Sistema de Envío de Emails en Django

## Introducción

Django incluye de forma nativa el módulo `django.core.mail` que facilita el envío de emails sin necesidad de instalar librerías adicionales. Este módulo es un wrapper sobre la librería estándar de Python `smtplib`.

---

## 🔧 Librería Utilizada: `django.core.mail`

### ¿Qué es?

`django.core.mail` es el módulo integrado en Django que proporciona funciones para enviar correos electrónicos de manera sencilla. 

### Características principales:

- ✅ **Integrada en Django**: No requiere instalación adicional
- ✅ **Múltiples backends**: Consola, SMTP, archivos, backends personalizados
- ✅ **Soporte para HTML**: Envío de emails con formato HTML
- ✅ **Adjuntos**: Permite añadir archivos adjuntos
- ✅ **Emails en lote**: Envío eficiente de múltiples emails
- ✅ **Plantillas**: Integración con el sistema de templates de Django

---

## 📖 Funciones Principales

### 1. `send_mail()`

La función más sencilla para enviar un email:

```python
from django.core.mail import send_mail

send_mail(
    subject='Asunto del email',           # Asunto
    message='Contenido del mensaje',      # Cuerpo en texto plano
    from_email='remitente@example.com',   # Remitente
    recipient_list=['destinatario@example.com'],  # Lista de destinatarios
    fail_silently=False,                  # Si True, no lanza excepción en caso de error
)
```

**Parámetros:**
- `subject` (str): Asunto del email
- `message` (str): Cuerpo del mensaje en texto plano
- `from_email` (str): Dirección del remitente
- `recipient_list` (list): Lista de direcciones de destinatarios
- `fail_silently` (bool): Si es False, lanza excepciones en caso de error
- `auth_user` (str, opcional): Usuario para autenticación SMTP
- `auth_password` (str, opcional): Contraseña para autenticación SMTP
- `connection` (opcional): Conexión SMTP personalizada
- `html_message` (str, opcional): Versión HTML del mensaje

**Retorno:** Número de emails enviados exitosamente

---

### 2. `EmailMessage`

Clase para crear emails más complejos:

```python
from django.core.mail import EmailMessage

email = EmailMessage(
    subject='Asunto',
    body='Cuerpo del mensaje',
    from_email='remitente@example.com',
    to=['destinatario1@example.com', 'destinatario2@example.com'],
    bcc=['copia_oculta@example.com'],
    reply_to=['responder_a@example.com'],
)

# Adjuntar archivos
email.attach_file('/ruta/al/archivo.pdf')

# Enviar
email.send()
```

**Ventajas:**
- Mayor control sobre el email
- Permite CC y BCC
- Facilita adjuntar archivos
- Permite configurar cabeceras personalizadas

---

### 3. `send_mass_mail()`

Para enviar múltiples emails eficientemente:

```python
from django.core.mail import send_mass_mail

message1 = ('Asunto 1', 'Mensaje 1', 'from@example.com', ['dest1@example.com'])
message2 = ('Asunto 2', 'Mensaje 2', 'from@example.com', ['dest2@example.com'])

send_mass_mail((message1, message2), fail_silently=False)
```

**Ventaja:** Reutiliza la conexión SMTP, mejorando el rendimiento

---

### 4. `mail_admins()` y `mail_managers()`

Funciones especiales para notificar a administradores:

```python
from django.core.mail import mail_admins

mail_admins(
    subject='Error en producción',
    message='Se ha producido un error crítico',
    fail_silently=False
)
```

---

## Configuración en `settings.py`

### Backend de Consola (Desarrollo)

Para desarrollo, podemos ver los emails en la consola:

```python
# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

### Backend SMTP (Producción)

Configuración típica para usar un servidor SMTP real:

```python
# settings.py

# Backend SMTP
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Servidor SMTP
EMAIL_HOST = 'smtp.gmail.com'  # Ejemplo con Gmail
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# Credenciales
EMAIL_HOST_USER = 'tu_email@gmail.com'
EMAIL_HOST_PASSWORD = 'tu_contraseña_de_aplicación'

# Remitente por defecto
DEFAULT_FROM_EMAIL = 'noreply@relecloud.com'
SERVER_EMAIL = 'server@relecloud.com'
```

### Backend de Archivos (Testing)

Para testing, podemos guardar los emails en archivos:

```python
# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = '/tmp/app-messages'  # Ruta donde se guardarán
```

### Backend en Memoria (Tests Unitarios)

Para tests unitarios, Django usa automáticamente:

```python
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
```

Los emails se almacenan en `django.core.mail.outbox`

---

## Testing

En los tests, Django automáticamente usa el backend en memoria:

```python
from django.test import TestCase
from django.core import mail

class EmailTest(TestCase):
    def test_send_email(self):
        # Limpiar el buzón
        mail.outbox = []
        
        # Enviar email
        send_mail(
            'Test Subject',
            'Test Message',
            'from@example.com',
            ['to@example.com'],
        )
        
        # Verificar
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Test Subject')
        self.assertEqual(mail.outbox[0].to, ['to@example.com'])
```

## Emails HTML

### Usando `html_message`

```python
from django.core.mail import send_mail

send_mail(
    subject='Bienvenido',
    message='Versión texto plano',  # Fallback
    from_email='from@example.com',
    recipient_list=['to@example.com'],
    html_message='<h1>Bienvenido</h1><p>Versión HTML</p>',
)
```

### Usando Templates de Django

```python
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

# Renderizar template
html_content = render_to_string('emails/info_request.html', {
    'name': info_request.name,
    'cruise': info_request.cruise,
})

text_content = render_to_string('emails/info_request.txt', {
    'name': info_request.name,
    'cruise': info_request.cruise,
})

# Crear email
email = EmailMultiAlternatives(
    subject='ReleCloud',
    body=text_content,
    from_email='from@example.com',
    to=['to@example.com'],
)
email.attach_alternative(html_content, "text/html")
email.send()
```

