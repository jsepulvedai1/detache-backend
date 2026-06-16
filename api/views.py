import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.utils.decorators import method_decorator
from .models import Lesson

@method_decorator(csrf_exempt, name='dispatch')
class WhatsAppWebhookView(View):
    def post(self, request, *args, **kwargs):
        """
        Receives webhooks from Evolution API.
        """
        print(f"--- WEBHOOK RECEIVED ---")
        print(f"Body: {request.body.decode('utf-8')}")
        try:
            data = json.loads(request.body)
            event_type = data.get('event', '').lower().replace('.', '_')
            
            # Evolution API v2 uses 'messages.upsert' or 'MESSAGES_UPSERT'
            if event_type == 'messages_upsert':
                print(f"Evento Detectado: messages.upsert")
                message_data = data.get('data', {})
                msg = message_data.get('message', {})
                buttons_response = msg.get('buttonsResponseMessage')
                list_response = msg.get('listResponseMessage')
                # Also handle text messages
                text_content = msg.get('conversation', '')
                
                remote_jid = message_data.get('key', {}).get('remoteJid', '')
                phone_number = remote_jid.split('@')[0]

                if buttons_response:
                    button_id = buttons_response.get('selectedButtonId')
                    self.process_button_id(button_id)
                elif list_response:
                    # Handle list response
                    pass
                elif text_content:
                    print(f"Webhook: Mensaje de texto recibido: '{text_content}' de {phone_number}")
                    # Handle "1" or "2" text response
                    text_strip = text_content.strip()
                    if text_strip == "1":
                        self.confirm_last_lesson(phone_number)
                    elif text_strip == "2":
                        self.cancel_last_lesson(phone_number)
                    else:
                        from .models import Student, Lead
                        from django.utils import timezone
                        
                        # 1. Check if it's an active Student
                        student = Student.objects.filter(phone_number__icontains=phone_number).first()
                        if student:
                            print(f"Webhook: Mensaje de alumno registrado ({student.name})")
                        else:
                            # 2. Check if it's an existing Lead
                            lead = Lead.objects.filter(telefono__icontains=phone_number).first()
                            if lead:
                                print(f"Webhook: Mensaje de lead existente ({lead.nombre})")
                                if lead.estado == 'NUEVO':
                                    lead.estado = 'CONTACTADO'
                                lead.fecha_ultimo_contacto = timezone.now()
                                lead.save()
                            else:
                                # 3. Create a new Lead
                                print(f"Webhook: Creando nuevo lead para {phone_number}")
                                Lead.objects.create(
                                    nombre=f"Contacto WA {phone_number}",
                                    telefono=phone_number,
                                    fuente='WHATSAPP',
                                    estado='NUEVO'
                                )

            return JsonResponse({"status": "SUCCESS"})
        except Exception as e:
            print(f"Webhook Error: {e}")
            import traceback
            traceback.print_exc()
            return JsonResponse({"status": "ERROR", "message": str(e)}, status=400)

    def process_button_id(self, button_id):
        if button_id.startswith('confirm_lesson_'):
            lesson_id = button_id.replace('confirm_lesson_', '')
            self.confirm_lesson(lesson_id)
        elif button_id.startswith('cancel_lesson_'):
            lesson_id = button_id.replace('cancel_lesson_', '')
            self.cancel_lesson(lesson_id)

    def confirm_last_lesson(self, phone_number):
        # Find the most recent pending lesson for this student
        print(f"Buscando lección para confirmar para el número: {phone_number}")
        try:
            # We use icontains to handle different formats (with/without country code)
            lesson = Lesson.objects.filter(student__phone_number__icontains=phone_number).latest('id')
            print(f"Lección encontrada: ID {lesson.id} para {lesson.student.name}")
            self.confirm_lesson(lesson.id)
            # Re-enviar mensaje de confirmación
            from .whatsapp import WhatsAppService
            res = WhatsAppService.send_text_message(phone_number, "Muchas gracias, su hora ha sido confirmada ✅")
            print(f"Respuesta de envío de confirmación: {res}")
        except Lesson.DoesNotExist:
            print(f"No se encontró ninguna lección para el número {phone_number}")

    def cancel_last_lesson(self, phone_number):
        print(f"Buscando lección para cancelar para el número: {phone_number}")
        try:
            lesson = Lesson.objects.filter(student__phone_number__icontains=phone_number).latest('id')
            print(f"Lección encontrada para cancelar: ID {lesson.id} para {lesson.student.name}")
            self.cancel_lesson(lesson.id)
            from .whatsapp import WhatsAppService
            res = WhatsAppService.send_text_message(phone_number, "Entendido, su hora ha sido cancelada ❌")
            print(f"Respuesta de envío de cancelación: {res}")
        except Lesson.DoesNotExist:
            print(f"No se encontró ninguna lección para el número {phone_number}")

    def confirm_lesson(self, lesson_id):
        try:
            lesson = Lesson.objects.get(pk=lesson_id)
            lesson.status = 'COMPLETED' # Or a new 'CONFIRMED' status
            lesson.save()
            print(f"Lesson {lesson_id} confirmed via WhatsApp.")
        except Lesson.DoesNotExist:
            print(f"Lesson {lesson_id} not found.")

    def cancel_lesson(self, lesson_id):
        try:
            lesson = Lesson.objects.get(pk=lesson_id)
            lesson.status = 'CANCELLED'
            lesson.save()
            print(f"Lesson {lesson_id} cancelled via WhatsApp.")
        except Lesson.DoesNotExist:
            print(f"Lesson {lesson_id} not found.")
