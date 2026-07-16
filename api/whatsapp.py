import requests
from django.conf import settings

class WhatsAppService:
    @staticmethod
    def send_text_message(phone_number, message):
        """
        Sends a text message using the Evolution API.
        """
        url = f"{settings.EVOLUTION_API_URL}/message/sendText/{settings.EVOLUTION_INSTANCE_NAME}"
        
        headers = {
            'apikey': settings.EVOLUTION_API_KEY,
            'Content-Type': 'application/json'
        }
        
        payload = {
            "number": phone_number,
            "text": message
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code not in [200, 201]:
                print(f"Error Evolution API ({response.status_code}): {response.text}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return None

    @staticmethod
    def send_button_message(phone_number, text, buttons, title="Détaché CRM"):
        """
        Sends a message with interactive buttons using Evolution API.
        'buttons' should be a list of dicts: [{'displayText': 'Sí', 'buttonId': 'id1'}, ...]
        """
        url = f"{settings.EVOLUTION_API_URL}/message/sendButtons/{settings.EVOLUTION_INSTANCE_NAME}"
        
        headers = {
            'apikey': settings.EVOLUTION_API_KEY,
            'Content-Type': 'application/json'
        }
        
        # Evolution API v2 requires 'type': 'reply' for each button
        formatted_buttons = []
        for btn in buttons:
            formatted_buttons.append({
                "buttonId": btn.get("buttonId"),
                "buttonText": {"displayText": btn.get("displayText")},
                "type": "reply"
            })

        payload = {
            "number": phone_number,
            "title": title,
            "description": text,
            "buttons": formatted_buttons
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code not in [200, 201]:
                print(f"Error Evolution API Buttons ({response.status_code}): {response.text}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return None

    @staticmethod
    def send_purchase_notifications(student, plan, amount):
        """
        Sends email and WhatsApp notifications confirming a pack purchase.
        """
        import os
        from django.core.mail import send_mail
        from django.utils import timezone
        from django.conf import settings
        from .models import Lead
        
        # 1. Clean student phone number
        phone = student.phone_number
        if phone:
            # WhatsApp text message
            wa_message = (
                f"🎻 *Academia Détaché*\n\n"
                f"¡Hola *{student.name}*!\n"
                f"Confirmamos la compra de tu pack de clases:\n\n"
                f"📦 *Programa:* {plan.name} ({plan.classes_count} clases)\n"
                f"💰 *Monto:* ${int(amount):,} CLP\n\n"
                f"En breve un coordinador de la academia te contactará para agendar tus horarios de clase. ¡Gracias por tu confianza!"
            )
            # Send WA
            print(f"DEBUG: Sending purchase WhatsApp to {phone}")
            WhatsAppService.send_text_message(phone, wa_message)
            
        # 2. Email Notification (if student/lead email is available)
        email = student.email
        if not email:
            lead = None
            if phone:
                clean_phone = phone[-8:]
                lead = Lead.objects.filter(telefono__icontains=clean_phone).first()
            if not lead:
                lead = Lead.objects.filter(nombre__iexact=student.name).first()
            if lead and lead.email:
                email = lead.email
            
        if email:
            subject = "🎻 Confirmación de Compra - Academia Détaché"
            email_message = (
                f"¡Hola {student.name}!\n\n"
                f"Queremos confirmar la compra de tu pack de clases en la Academia de Música Détaché.\n\n"
                f"Detalles de tu compra:\n"
                f"-----------------------------------------\n"
                f"Programa: {plan.name}\n"
                f"Clases del Pack: {plan.classes_count} clases\n"
                f"Monto Pagado: ${int(amount):,} CLP\n"
                f"Fecha de Compra: {timezone.now().strftime('%d/%m/%Y')}\n"
                f"-----------------------------------------\n\n"
                f"Próximos pasos:\n"
                f"Un coordinador de nuestro equipo académico se comunicará contigo vía WhatsApp en breve para definir tu horario fijo de clases y asignarte un profesor.\n\n"
                f"Si tienes alguna pregunta, no dudes en responder a este correo o contactarnos directamente por WhatsApp.\n\n"
                f"¡Te deseamos el mayor de los éxitos en tus clases!\n\n"
                f"Atentamente,\n"
                f"Equipo Academia de Música Détaché"
            )
            print(f"DEBUG: Sending purchase email to {email}")
            try:
                send_mail(
                    subject,
                    email_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False
                )
            except Exception as mail_err:
                print(f"Error sending purchase email: {mail_err}")
