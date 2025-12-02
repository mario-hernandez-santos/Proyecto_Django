## Fase 1: TDD - RED PHASE (COMPLETADA)

### Lo que hemos hecho:

#### 1. Tests Creados

Se han creado **6 tests** en `relecloud/tests_email.py` siguiendo la metodología TDD:

- `test_email_sent_on_info_request_creation`: Verifica que se envía un email
- `test_email_contains_correct_subject`: Verifica el asunto correcto
- `test_email_sent_to_correct_recipient`: Verifica el destinatario
- `test_email_contains_cruise_information`: Verifica que incluye info del crucero
- `test_email_contains_user_name`: Verifica que incluye el nombre del usuario
- `test_email_from_address`: Verifica el remitente

**Estado actual:** Estos tests FALLARÁN porque aún no hemos implementado la funcionalidad 

#### 2. Documentación Completa

Se ha creado `DOCUMENTACION_EMAIL.md` con:

- Explicación de `django.core.mail`
- Funciones principales: `send_mail()`, `EmailMessage`, etc.
- Configuración en `settings.py` para diferentes entornos
- Cómo hacer testing de emails


---
