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
                                # WebSocket broadcast
                                try:
                                    from api.schema import OnLeadUpdated
                                    OnLeadUpdated.broadcast(group="leads_group", payload={"lead_id": lead.id, "event_type": "updated"})
                                except Exception as ws_err:
                                    print(f"Error broadcasting lead update: {ws_err}")
                            else:
                                # 3. Create a new Lead
                                print(f"Webhook: Creando nuevo lead para {phone_number}")
                                lead = Lead.objects.create(
                                    nombre=f"Contacto WA {phone_number}",
                                    telefono=phone_number,
                                    fuente='WHATSAPP',
                                    estado='NUEVO'
                                )
                                # WebSocket broadcast
                                try:
                                    from api.schema import OnLeadUpdated
                                    OnLeadUpdated.broadcast(group="leads_group", payload={"lead_id": lead.id, "event_type": "created"})
                                except Exception as ws_err:
                                    print(f"Error broadcasting new lead: {ws_err}")



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

@method_decorator(csrf_exempt, name='dispatch')
class TeacherPhotoUploadView(View):
    def post(self, request, *args, **kwargs):
        try:
            teacher_id = request.POST.get('teacher_id')
            photo_file = request.FILES.get('photo')
            if not teacher_id or not photo_file:
                return JsonResponse({"status": "ERROR", "message": "Missing teacher_id or photo file"}, status=400)
            
            from .models import Teacher
            try:
                teacher = Teacher.objects.get(pk=teacher_id)
            except Teacher.DoesNotExist:
                return JsonResponse({"status": "ERROR", "message": f"Teacher with id {teacher_id} does not exist"}, status=404)
            
            # Save the photo
            teacher.photo = photo_file
            teacher.save()
            
            photo_url = teacher.photo.url if teacher.photo else None
            return JsonResponse({
                "status": "SUCCESS", 
                "photoUrl": photo_url
            })
        except Exception as e:
            return JsonResponse({"status": "ERROR", "message": str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class MediaUploadView(View):
    def post(self, request, *args, **kwargs):
        try:
            upload_file = request.FILES.get('file')
            if not upload_file:
                return JsonResponse({"status": "ERROR", "message": "Missing file"}, status=400)
            
            from django.core.files.storage import default_storage
            from django.core.files.base import ContentFile
            import uuid
            import os

            ext = os.path.splitext(upload_file.name)[1]
            filename = f"web_{uuid.uuid4().hex}{ext}"
            
            # Save under media/web/
            saved_path = default_storage.save(f"web/{filename}", ContentFile(upload_file.read()))
            url = default_storage.url(saved_path)

            return JsonResponse({
                "status": "SUCCESS", 
                "url": url
            })
        except Exception as e:
            return JsonResponse({"status": "ERROR", "message": str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class MercadoPagoWebhookView(View):
    def post(self, request, *args, **kwargs):
        import os
        import json
        import requests
        from django.utils import timezone
        from .models import Lead, Student, StudentPack, Plan, Payment, Lesson
        
        print("--- MERCADOPAGO WEBHOOK RECEIVED ---")
        try:
            data = {}
            if request.body:
                try:
                    data = json.loads(request.body.decode('utf-8'))
                except Exception as parse_err:
                    print(f"Could not parse body JSON: {parse_err}")
            
            action = data.get("action")
            event_type = data.get("type")
            data_info = data.get("data", {})
            payment_id = data_info.get("id")
            
            # Fallback to query params
            if not payment_id:
                payment_id = request.GET.get("data.id")
            if not event_type:
                event_type = request.GET.get("type")
            
            print(f"Webhook event_type: {event_type}, payment_id: {payment_id}")
            
            if event_type == "payment" and payment_id:
                # Retrieve the full payment info
                token = os.getenv("MERCADOPAGO_ACCESS_TOKEN", "TEST-4651592514397603-071517-68bc59d1e7da5ac1c14335ee790d8a44-2375919242")
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
                
                pay_resp = requests.get(
                    f"https://api.mercadopago.com/v1/payments/{payment_id}",
                    headers=headers,
                    timeout=10
                )
                
                if pay_resp.status_code == 200:
                    pay_data = pay_resp.json()
                    status = pay_data.get("status")
                    transaction_amount = pay_data.get("transaction_amount")
                    external_reference = pay_data.get("external_reference")
                    
                    print(f"Payment {payment_id} Status: {status}, ExtRef: {external_reference}, Amount: {transaction_amount}")
                    
                    if status == "approved" and external_reference:
                        # Parse external_reference: format "lead_id:X|plan_id:Y"
                        try:
                            ref_parts = dict(part.split(":") for part in external_reference.split("|"))
                            lead_id = ref_parts.get("lead_id")
                            plan_id = ref_parts.get("plan_id")
                        except Exception as parse_ref_err:
                            print(f"Error parsing external reference: {parse_ref_err}")
                            return JsonResponse({"status": "ERROR", "message": "Invalid external reference format"}, status=400)
                        
                        if lead_id and plan_id:
                            lead = Lead.objects.get(pk=int(lead_id))
                            plan = Plan.objects.get(pk=int(plan_id))
                            
                            # Check if Student already exists or create one
                            student = None
                            if lead.telefono:
                                # Match by last 8 digits of phone
                                clean_phone = lead.telefono[-8:]
                                student = Student.objects.filter(phone_number__icontains=clean_phone).first()
                            
                            if not student:
                                student = Student.objects.filter(name__iexact=lead.nombre).first()
                            
                            if not student:
                                student = Student.objects.create(
                                    name=lead.nombre,
                                    phone_number=lead.telefono,
                                    status='ACTIVE'
                                )
                                print(f"Webhook created new student {student.name} for lead {lead.id}")
                            
                            # Convert any lessons
                            lessons_updated = Lesson.objects.filter(lead=lead).update(student=student, is_pre_reservation=False)
                            print(f"Webhook converted {lessons_updated} lessons to student {student.id}")
                            
                            # Mark Lead as concreted
                            lead.estado = 'CONCRETADO'
                            lead.save()
                            
                            # Check if payment already recorded to prevent duplicates
                            existing_payment = Payment.objects.filter(description__icontains=payment_id).first()
                            if not existing_payment:
                                pack = StudentPack.objects.create(
                                    student=student,
                                    plan=plan,
                                    purchase_date=timezone.now()
                                )
                                print(f"Webhook created student pack {pack.id} for plan {plan.name}")
                                
                                # Register approved payment
                                Payment.objects.create(
                                    student=student,
                                    amount=float(transaction_amount),
                                    method='CARD',
                                    description=f"Pago aprobado por Mercado Pago (ID: {payment_id}) para {plan.name}",
                                    pack=pack
                                )
                                print(f"Webhook registered payment for student {student.name}")
                                
                                # Broadcast updates to leads view
                                try:
                                    from api.schema import OnLeadUpdated
                                    OnLeadUpdated.broadcast(group="leads_group", payload={"lead_id": lead.id, "event_type": "updated"})
                                except Exception as ws_err:
                                    print(f"Error broadcasting lead update: {ws_err}")
                            else:
                                print(f"Payment {payment_id} was already processed.")
                else:
                    print(f"Error calling MP Payment API: {pay_resp.status_code} - {pay_resp.text}")
                    
            return JsonResponse({"status": "SUCCESS"})
        except Exception as e:
            print(f"MercadoPago Webhook Error: {e}")
            import traceback
            traceback.print_exc()
            return JsonResponse({"status": "ERROR", "message": str(e)}, status=400)

