# Guía de Pruebas - Funcionalidad de Envío de Emails

## Implementación Completada

### Cambios Realizados:

1. **Configuración de Email (`project/settings.py`)**
   - ✅ Backend de consola para desarrollo
   - ✅ Configuración de remitente por defecto
   - ✅ Configuración lista para producción (comentada)

2. **Lógica de Envío (`relecloud/views.py`)**
   - ✅ Import de `send_mail` y `logging`
   - ✅ Implementación en `InfoRequestCreateView.form_valid()`
   - ✅ Manejo de errores robusto
   - ✅ Logging de eventos
   - ✅ Mensaje de confirmación al usuario

3. **Tests Unitarios (`relecloud/test_email.py`)**
   - ✅ 6 tests completos
   - ✅ Cobertura de todos los aspectos del email

---

## Pruebas Unitarias

### Ejecutar Tests

```powershell
# (activar venv primero)
.\venv\Scripts\Activate.ps1
python manage.py test relecloud.test_email.EmailTestCase --verbosity=2
```

### Tests Incluidos:

1. ✅ `test_email_sent_on_info_request_creation` - Verifica que se envía un email
2. ✅ `test_email_contains_correct_subject` - Verifica el asunto correcto
3. ✅ `test_email_sent_to_correct_recipient` - Verifica el destinatario
4. ✅ `test_email_contains_cruise_information` - Verifica contenido del crucero
5. ✅ `test_email_contains_user_name` - Verifica nombre del usuario
6. ✅ `test_email_from_address` - Verifica remitente válido

---

## Pruebas Manuales en Desarrollo

### Paso 1: Iniciar el Servidor

```powershell
.\venv\Scripts\Activate.ps1
python manage.py runserver
```

### Paso 2: Acceder al Formulario

1. Abrir navegador en: `http://localhost:8000/info-request/`
2. Completar el formulario:
   - **Nombre Completo:** Tu nombre
   - **Email:** tu_email@example.com
   - **Crucero de Interés:** Selecciona uno
   - **Notas:** Escribe tu consulta

### Paso 3: Enviar y Verificar

1. Click en **"Enviar Solicitud"**
2. Deberías ver:
   - ✅ Redirección a la página de inicio
   - ✅ Mensaje de confirmación verde
   - ✅ **EMAIL EN LA CONSOLA DEL SERVIDOR**

### Ejemplo de Email en Consola:

```
Content-Type: text/plain; charset="utf-8"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
Subject: ReleCloud - Información sobre Viaje a Marte
From: noreply@relecloud.space
To: tu_email@example.com
Date: Mon, 02 Dec 2025 12:00:00 -0000
Message-ID: <...>

Hola Juan Pérez,

¡Gracias por tu interés en ReleCloud! 🚀

Has solicitado información sobre: Viaje a Marte

📝 Descripción del crucero:
Un viaje increíble al planeta rojo

💬 Tus notas:
Me gustaría más información sobre el viaje

Nos pondremos en contacto contigo pronto para ayudarte a planificar tu aventura espacial.

¡Prepárate para explorar el universo!

Saludos,
Equipo ReleCloud 🌌
```

---

## 📧 Configuración para Producción (SMTP Real)

### Opción 1: Gmail (Desarrollo/Testing)

1. **Crear contraseña de aplicación en Google:**
   - Ir a: https://myaccount.google.com/apppasswords
   - Generar contraseña para "Correo"

2. **Configurar variables de entorno:**

```powershell
# Windows PowerShell
$env:EMAIL_HOST_USER="tu_email@gmail.com"
$env:EMAIL_HOST_PASSWORD="tu_contraseña_de_aplicación"
```

3. **Descomentar en `settings.py`:**

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
```

### Opción 2: SendGrid (Recomendado para Producción)

1. **Crear cuenta gratuita:** https://sendgrid.com/
2. **Obtener API Key**
3. **Configurar:**

```python
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = os.getenv('SENDGRID_API_KEY')
```

### Opción 3: Azure Communication Services

Para integración con Azure (proyecto ya está en Azure):

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.azurecomm.net'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('AZURE_COMM_EMAIL')
EMAIL_HOST_PASSWORD = os.getenv('AZURE_COMM_PASSWORD')
```

## Quality Attribute Scenario (QAS) - Verificación

### Criterios Cumplidos:

| Criterio | Estado | Evidencia |
|----------|--------|-----------|
| Email se recibe correctamente | ✅ | Tests + consola en desarrollo |
| Contenido completo y legible | ✅ | Test `test_email_contains_cruise_information` |
| Manejo de errores con mensaje claro | ✅ | Try/catch en `form_valid()` |
| Datos no se pierden en caso de error | ✅ | Email se envía DESPUÉS de guardar |
| Tests unitarios | ✅ | 6 tests en `test_email.py` |
| No exponer datos sensibles | ✅ | Variables de entorno |

---


## Troubleshooting

### Problema: Tests fallan con error de base de datos

**Solución:**
```powershell
# Eliminar base de datos de test y recrear
python manage.py test relecloud.test_email.EmailTestCase
# Cuando pregunte, escribir 'yes' para recrear
```

### Problema: Email no aparece en consola

**Verificar:**
1. `EMAIL_BACKEND = 'console'` en `settings.py`
2. Mirar la consola donde corre `runserver`, NO el navegador
3. Verificar que no haya excepciones en el log


