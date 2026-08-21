import graphene
from django.utils import timezone
from graphene_django import DjangoObjectType
from .models import Announcement, Teacher, Specialty, Availability, Plan, Student, Instrument, Room, Lesson, Lead, LeadNote, StudentPack, Payment, AcademyTask, Material, StudentPrivateNote, StudentWallMessage, LandingPage, HomepageContent, ClassType, AboutContent, ContactContent, GlobalSettings, UserProfile, AuditLog, ChatMessage, Holiday
from django.contrib.auth.models import User

def log_user_action(info, action, details):
    """
    Utility function to record worker actions in the AuditLog database table.
    """
    user = getattr(info.context, 'user', None)
    ip_addr = None
    if info.context and hasattr(info.context, 'META'):
        x_forwarded = info.context.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded:
            ip_addr = x_forwarded.split(',')[0].strip()
        else:
            ip_addr = info.context.META.get('REMOTE_ADDR')
            
    username = "Anonymous"
    user_obj = None
    if user and user.is_authenticated:
        username = user.username
        user_obj = user

    AuditLog.objects.create(
        user=user_obj,
        username=username,
        action=action,
        details=str(details),
        ip_address=ip_addr
    )

# --- Object Types ---

class UserProfileType(DjangoObjectType):
    class Meta:
        model = UserProfile
        fields = ("id", "user", "role", "allowed_sections")

class UserType(DjangoObjectType):
    profile = graphene.Field(UserProfileType)

    class Meta:
        model = User
        fields = ("id", "username", "email", "is_superuser", "is_staff")

    def resolve_profile(self, info):
        profile, created = UserProfile.objects.get_or_create(user=self)
        if self.is_superuser and profile.role != 'ADMIN':
            profile.role = 'ADMIN'
            profile.save()
        return profile

class AuditLogType(DjangoObjectType):
    class Meta:
        model = AuditLog
        fields = ("id", "user", "username", "action", "details", "ip_address", "timestamp")

class ChatMessageType(DjangoObjectType):
    class Meta:
        model = ChatMessage
        fields = ("id", "lead", "student", "phone_number", "sender", "message_text", "message_id", "timestamp")


class AnnouncementType(DjangoObjectType):
    class Meta:
        model = Announcement
        fields = '__all__'

class TeacherType(DjangoObjectType):
    class Meta:
        model = Teacher
        fields = ("id", "name", "description", "photo", "status", "specialties", "availabilities", "phone_number", "rut", "address", "email", "user")

    def resolve_photo(self, info):
        if self.photo:
            return info.context.build_absolute_uri(self.photo.url)
        return None

class SpecialtyType(DjangoObjectType):
    class Meta:
        model = Specialty
        fields = ("id", "name")

class AvailabilityType(DjangoObjectType):
    class Meta:
        model = Availability
        fields = ("id", "day", "start_time", "end_time", "teacher")

class StudentType(DjangoObjectType):
    status = graphene.String()

    class Meta:
        model = Student
        fields = ("id", "name", "email", "photo", "status", "phone_number", "rut", "birth_date", "guardian_name", "guardian_phone", "level", "start_date", "primary_instrument", "assigned_teachers", "private_notes", "wall_messages", "packs", "user")

    def resolve_status(self, info):
        return str(self.status) if self.status else "ACTIVE"

    def resolve_photo(self, info):
        if self.photo:
            return info.context.build_absolute_uri(self.photo.url)
        return None

class MaterialType(DjangoObjectType):
    class Meta:
        model = Material
        fields = ("id", "title", "type", "url", "teacher", "created_at")

class StudentPrivateNoteType(DjangoObjectType):
    class Meta:
        model = StudentPrivateNote
        fields = ("id", "student", "text", "author", "created_at")

class StudentWallMessageType(DjangoObjectType):
    class Meta:
        model = StudentWallMessage
        fields = ("id", "student", "text", "author", "attached_material", "created_at")

class InstrumentType(DjangoObjectType):
    class Meta:
        model = Instrument
        fields = ("id", "name")

class RoomType(DjangoObjectType):
    class Meta:
        model = Room
        fields = ("id", "name", "capacity", "status", "instruments")

class LessonType(DjangoObjectType):
    status = graphene.String()
    lesson_type = graphene.String()

    class Meta:
        model = Lesson
        fields = ("id", "teacher", "student", "lead", "room", "date", "start_time", "end_time", "status", "lesson_type", "is_pre_reservation")

class PlanType(DjangoObjectType):
    class Meta:
        model = Plan
        fields = ("id", "name", "price", "duration", "classes_count", "is_featured", "benefits")
    
    price = graphene.String()

    def resolve_price(self, info):
        return str(self.price)

class LeadType(DjangoObjectType):
    fuente = graphene.String()
    servicio = graphene.String()
    estado = graphene.String()

    class Meta:
        model = Lead
        fields = ("id", "nombre", "telefono", "email", "edad", "servicio", "fuente", "estado", "asignado_a", "fecha_ingreso", "fecha_ultimo_contacto", "notas", "lessons")

    def resolve_fuente(self, info):
        return str(self.fuente) if self.fuente else "WEB"

    def resolve_servicio(self, info):
        return str(self.servicio) if self.servicio else "CLASE_PRUEBA"

    def resolve_estado(self, info):
        return str(self.estado) if self.estado else "NUEVO"

class LeadNoteType(DjangoObjectType):
    class Meta:
        model = LeadNote
        fields = ("id", "lead", "texto", "autor", "fecha")

class StudentPackType(DjangoObjectType):
    class Meta:
        model = StudentPack
        fields = ("id", "student", "plan", "total_classes", "remaining_classes", "purchase_date", "expiration_date", "is_active", "payments")

class PaymentType(DjangoObjectType):
    class Meta:
        model = Payment
        fields = ("id", "student", "amount", "payment_date", "method", "description", "pack")

class AcademyTaskType(DjangoObjectType):
    class Meta:
        model = AcademyTask
        fields = ("id", "title", "description", "assigned_to", "assigned_user", "priority", "status", "log", "is_completed", "due_date", "duration", "completed_at", "created_at", "updated_at")

class HolidayType(DjangoObjectType):
    class Meta:
        model = Holiday
        fields = ("id", "date", "name", "is_active", "is_custom", "created_at")

class LandingPageType(DjangoObjectType):
    class Meta:
        model = LandingPage
        fields = ("id", "slug", "title", "subtitle", "problem", "solution", "benefits", "image_url", "cta")

class HomepageContentType(DjangoObjectType):
    class Meta:
        model = HomepageContent
        fields = (
            "id",
            "hero_image", "hero_title_1", "hero_title_highlight", "hero_title_2",
            "hero_subtitle", "hero_cta1_text", "hero_cta1_link", "hero_cta2_text", "hero_cta2_link",
            "features",
            "method_badge", "method_title", "method_description", "method_items", "method_image",
            "testimonials",
            "location_title", "location_description", "location_address", "location_address_detail", "location_map_url",
            "final_cta_title", "final_cta_description", "final_cta_button_text",
            "planes_title", "planes_description", "instruments_title", "instruments_description", "gallery_title", "gallery_images",
        )

class AboutContentType(DjangoObjectType):
    class Meta:
        model = AboutContent
        fields = (
            "id",
            "hero_image", "hero_title_highlight_1", "hero_title_text_1", "hero_title_highlight_2",
            "history_image", "history_title", "history_subtitle", "history_description",
            "moving_title", "moving_description", "moving_cards",
            "team_title", "team_description", "team_images",
            "final_title_1", "final_title_2", "final_title_3", "final_image"
        )

class ContactContentType(DjangoObjectType):
    class Meta:
        model = ContactContent
        fields = (
            "id",
            "banner_title_1", "banner_title_2", "banner_title_3", "banner_title_4",
            "location_title", "location_description", "location_address_title", "location_address", "location_map_iframe_url"
        )

class ClassTypeType(DjangoObjectType):
    class Meta:
        model = ClassType
        fields = (
            "id", "name", "description", "duration_minutes", "price", "currency",
            "allowed_levels", "allowed_modalities", "what_you_will_learn", "teachers"
        )

class GlobalSettingsType(DjangoObjectType):
    class Meta:
        model = GlobalSettings
        fields = (
            "id", "phone_number", "email_contact", "address",
            "opening_hours_weekdays", "opening_hours_saturdays",
            "facebook_url", "instagram_url", "trial_class_email_template",
            "whatsapp_number", "whatsapp_assigned_to", "evolution_api_url",
            "evolution_api_key", "evolution_instance_name", "whatsapp_auto_reply",
            "whatsapp_welcome_template"
        )

# --- Queries ---

class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Hello, this is the Detache backend with GraphQL!")
    
    global_settings = graphene.Field(GlobalSettingsType)
    whatsapp_qr_code = graphene.String()
    whatsapp_connection_status = graphene.String()
    all_admin_accounts = graphene.List(UserType)
    all_audit_logs = graphene.List(AuditLogType)
    me = graphene.Field(UserType)
    chat_messages = graphene.List(ChatMessageType, phone=graphene.String(required=True))
    my_student_profile = graphene.Field(StudentType)
    my_teacher_profile = graphene.Field(TeacherType)
    my_lessons = graphene.List(LessonType, start_date=graphene.String(), end_date=graphene.String())
    my_students = graphene.List(StudentType)
    my_wall_messages = graphene.List(StudentWallMessageType)
    my_packs = graphene.List(StudentPackType)

    # Teachers

    all_announcements = graphene.List(AnnouncementType)
    active_announcements = graphene.List(AnnouncementType, target_audience=graphene.String())

    all_teachers = graphene.List(TeacherType)
    teacher_by_id = graphene.Field(TeacherType, id=graphene.Int(required=True))
    
    # Students
    all_students = graphene.List(StudentType)
    student_by_id = graphene.Field(StudentType, id=graphene.Int(required=True))
    
    # Rooms
    all_rooms = graphene.List(RoomType)
    room_by_id = graphene.Field(RoomType, id=graphene.Int(required=True))
    
    # Lessons
    all_lessons = graphene.List(LessonType)
    lesson_by_id = graphene.Field(LessonType, id=graphene.Int(required=True))
    
    # Plans
    all_plans = graphene.List(PlanType)
    plan_by_id = graphene.Field(PlanType, id=graphene.Int(required=True))

    # Leads
    all_leads = graphene.List(LeadType)
    lead_by_id = graphene.Field(LeadType, id=graphene.Int(required=True))

    # Student Packs & Payments
    all_student_packs = graphene.List(StudentPackType)
    all_payments = graphene.List(PaymentType)
    all_academy_tasks = graphene.List(AcademyTaskType)
    all_instruments = graphene.List(InstrumentType)
    all_materials = graphene.List(MaterialType)
    
    # Landing Pages
    all_landing_pages = graphene.List(LandingPageType)
    landing_page_by_slug = graphene.Field(LandingPageType, slug=graphene.String(required=True))

    # Homepage
    homepage_content = graphene.Field(HomepageContentType)
    about_content = graphene.Field(AboutContentType)
    contact_content = graphene.Field(ContactContentType)

    # Class Types / Catalog
    all_class_types = graphene.List(ClassTypeType)
    class_type_by_id = graphene.Field(ClassTypeType, id=graphene.Int(required=True))

    # Holidays / Non-working days
    all_holidays = graphene.List(HolidayType, year=graphene.Int())
    active_holidays = graphene.List(HolidayType, year=graphene.Int())

    def resolve_hello(self, info):
        return "Hello, this is the Detache backend with GraphQL!"


    def resolve_all_announcements(self, info):
        return Announcement.objects.all()

    def resolve_active_announcements(self, info, target_audience=None):
        qs = Announcement.objects.filter(is_active=True)
        if target_audience:
            qs = qs.filter(target_audience__in=['ALL', target_audience])
        return qs

    def resolve_all_teachers(self, info):
        return Teacher.objects.all()

    def resolve_teacher_by_id(self, info, id):
        return Teacher.objects.filter(pk=id).first()

    def resolve_all_students(self, info):
        return Student.objects.all()

    def resolve_student_by_id(self, info, id):
        return Student.objects.filter(pk=id).first()

    def resolve_all_rooms(self, info):
        return Room.objects.all()

    def resolve_room_by_id(self, info, id):
        return Room.objects.filter(pk=id).first()

    def resolve_all_lessons(self, info):
        return Lesson.objects.all()

    def resolve_lesson_by_id(self, info, id):
        return Lesson.objects.filter(pk=id).first()

    def resolve_all_plans(self, info):
        return Plan.objects.all()

    def resolve_plan_by_id(self, info, id):
        return Plan.objects.filter(pk=id).first()

    def resolve_all_leads(self, info):
        return Lead.objects.all().order_by('-fecha_ingreso', '-id')
        
    def resolve_lead_by_id(self, info, id):
        return Lead.objects.filter(pk=id).first()

    def resolve_all_student_packs(self, info):
        return StudentPack.objects.all()

    def resolve_all_instruments(self, info):
        return Instrument.objects.all()

    def resolve_all_payments(self, info):
        return Payment.objects.all()

    def resolve_all_academy_tasks(self, info):
        return AcademyTask.objects.all()

    def resolve_all_materials(self, info):
        return Material.objects.all()

    def resolve_all_landing_pages(self, info):
        return LandingPage.objects.all()

    def resolve_landing_page_by_slug(self, info, slug):
        return LandingPage.objects.filter(slug=slug).first()

    def resolve_homepage_content(self, info):
        return HomepageContent.get_singleton()

    def resolve_about_content(self, info):
        return AboutContent.get_singleton()

    def resolve_contact_content(self, info):
        return ContactContent.get_singleton()

    def resolve_global_settings(self, info):
        return GlobalSettings.get_singleton()

    def resolve_all_holidays(self, info, year=None):
        qs = Holiday.objects.all().order_by('date')
        if year:
            qs = qs.filter(date__year=year)
        if not qs.exists() and Holiday.objects.count() == 0:
            Holiday.seed_default_chilean_holidays()
            qs = Holiday.objects.all().order_by('date')
            if year:
                qs = qs.filter(date__year=year)
        return qs

    def resolve_active_holidays(self, info, year=None):
        qs = Holiday.objects.filter(is_active=True).order_by('date')
        if year:
            qs = qs.filter(date__year=year)
        if not qs.exists() and Holiday.objects.count() == 0:
            Holiday.seed_default_chilean_holidays()
            qs = Holiday.objects.filter(is_active=True).order_by('date')
            if year:
                qs = qs.filter(date__year=year)
        return qs

    def resolve_whatsapp_qr_code(self, info):
        import requests
        from .whatsapp import get_evolution_config
        api_url, api_key, instance_name = get_evolution_config()
        try:
            res = requests.get(f"{api_url}/instance/connect/{instance_name}", headers={'apikey': api_key}, timeout=8)
            if res.status_code == 200:
                data = res.json()
                return data.get('base64') or data.get('code')
        except Exception as e:
            print("Error resolving whatsapp_qr_code:", e)
        return None

    def resolve_whatsapp_connection_status(self, info):
        import requests
        from .whatsapp import get_evolution_config
        api_url, api_key, instance_name = get_evolution_config()
        try:
            res = requests.get(f"{api_url}/instance/fetchInstances", headers={'apikey': api_key}, timeout=8)
            if res.status_code == 200:
                instances = res.json()
                for inst in instances:
                    if inst.get('name') == instance_name:
                        return inst.get('connectionStatus')
        except Exception as e:
            print("Error checking connection status:", e)
        return 'offline'

    def resolve_all_class_types(self, info):
        return ClassType.objects.all()

    def resolve_class_type_by_id(self, info, id):
        return ClassType.objects.filter(pk=id).first()

    def resolve_all_admin_accounts(self, info):
        return User.objects.filter(student_profile__isnull=True).order_by('username')

    def resolve_all_audit_logs(self, info):
        return AuditLog.objects.all().order_by('-timestamp')

    def resolve_me(self, info):
        user = getattr(info.context, 'user', None)
        if user and user.is_authenticated:
            return user
        return None

    def resolve_chat_messages(self, info, phone):
        clean_num = phone[-8:] if len(phone) >= 8 else phone
        return ChatMessage.objects.filter(phone_number__icontains=clean_num).order_by('timestamp')

    def resolve_my_student_profile(self, info):
        user = getattr(info.context, 'user', None)
        if not user or not user.is_authenticated:
            raise Exception("No autenticado.")
        try:
            return user.student_profile
        except:
            raise Exception("No tienes un perfil de alumno vinculado.")

    def resolve_my_teacher_profile(self, info):
        user = getattr(info.context, 'user', None)
        if not user or not user.is_authenticated:
            raise Exception("No autenticado.")
        try:
            return user.teacher_profile
        except:
            raise Exception("No tienes un perfil de profesor vinculado.")

    def resolve_my_lessons(self, info, start_date=None, end_date=None):
        user = getattr(info.context, 'user', None)
        if not user or not user.is_authenticated:
            raise Exception("No autenticado.")
        qs = Lesson.objects.all()
        if hasattr(user, 'student_profile'):
            try:
                qs = qs.filter(student=user.student_profile)
            except:
                return []
        elif hasattr(user, 'teacher_profile'):
            try:
                qs = qs.filter(teacher=user.teacher_profile)
            except:
                return []
        else:
            return []
        if start_date:
            qs = qs.filter(date__gte=start_date)
        if end_date:
            qs = qs.filter(date__lte=end_date)
        return qs.order_by('date', 'start_time')

    def resolve_my_students(self, info):
        user = getattr(info.context, 'user', None)
        if not user or not user.is_authenticated:
            raise Exception("No autenticado.")
        try:
            teacher = user.teacher_profile
            from django.db.models import Q
            return Student.objects.filter(
                Q(assigned_teachers=teacher) | Q(lessons__teacher=teacher)
            ).distinct().order_by('name')
        except:
            return []

    def resolve_my_wall_messages(self, info):
        user = getattr(info.context, 'user', None)
        if not user or not user.is_authenticated:
            raise Exception("No autenticado.")
        try:
            student = user.student_profile
            return StudentWallMessage.objects.filter(student=student).order_by('-created_at')
        except:
            raise Exception("No tienes un perfil de alumno vinculado.")

    def resolve_my_packs(self, info):
        user = getattr(info.context, 'user', None)
        if not user or not user.is_authenticated:
            raise Exception("No autenticado.")
        try:
            student = user.student_profile
            return StudentPack.objects.filter(student=student).order_by('-purchase_date')
        except:
            raise Exception("No tienes un perfil de alumno vinculado.")

# --- Mutations ---

class CreatePreReservation(graphene.Mutation):
    class Arguments:
        nombre = graphene.String(required=True)
        telefono = graphene.String(required=True)
        email = graphene.String()
        servicio = graphene.String()
        profesor_nombre = graphene.String(required=True)
        fecha = graphene.Date(required=True)
        hora = graphene.Time(required=True)
        sala = graphene.String()
        modalidad = graphene.String()
        notas = graphene.String()

    success = graphene.Boolean()
    lesson = graphene.Field(LessonType)

    def mutate(self, info, nombre, telefono, profesor_nombre, fecha, hora, email=None, servicio='CLASE_PRUEBA', sala=None, modalidad='PRESENCIAL', notas=None):
        clean_service = servicio or 'CLASE_PRUEBA'
        if 'prueba' in str(clean_service).lower():
            clean_service = 'CLASE_PRUEBA'

        lead = Lead.objects.create(
            nombre=nombre,
            telefono=telefono,
            email=email,
            servicio=clean_service,
            fuente='WEB',
            estado='PRE_RESERVA'
        )
        if notas:
            LeadNote.objects.create(lead=lead, texto=notas, autor='Reserva Web')

        teacher = Teacher.objects.filter(name__icontains=profesor_nombre).first()
        if not teacher:
            teacher = Teacher.objects.first()
        from datetime import datetime, timedelta, date, time
        if isinstance(hora, str):
            parts = [int(p) for p in hora.split(':')]
            hora = time(parts[0], parts[1])
        if isinstance(fecha, str):
            fecha = datetime.strptime(fecha, "%Y-%m-%d").date()

        end_time = (datetime.combine(datetime.today(), hora) + timedelta(minutes=45)).time()
        lesson = Lesson.objects.create(
            teacher=teacher,
            lead=lead,
            date=fecha,
            start_time=hora,
            end_time=end_time,
            status='PENDING',
            is_pre_reservation=True,
            lesson_type='INDIVIDUAL'
        )

        # Register initial appointment summary as ChatMessage for the Lead
        try:
            from .models import ChatMessage, GlobalSettings
            from .whatsapp import WhatsAppService
            
            chat_summary = (
                f"📋 Solicitud de Cita / Pre-Reserva Clínica:\n"
                f"• Especialidad: {servicio or 'Clase de Prueba'}\n"
                f"• Profesional: {teacher.name if teacher else profesor_nombre}\n"
                f"• Fecha: {fecha.strftime('%d/%m/%Y') if hasattr(fecha, 'strftime') else str(fecha)}\n"
                f"• Horario: {hora.strftime('%H:%M') if hasattr(hora, 'strftime') else str(hora)}\n"
                f"• Notas / Motivo: {notas or 'Sin notas adicionales'}"
            )
            ChatMessage.objects.create(
                lead=lead,
                phone_number=telefono,
                sender='LEAD',
                message_text=chat_summary
            )

            # Auto-reply via WhatsApp if enabled
            gs = GlobalSettings.get_singleton()
            if gs.whatsapp_auto_reply and gs.whatsapp_welcome_template:
                template = gs.whatsapp_welcome_template.replace('{nombre}', nombre)
                WhatsAppService.send_text_message(telefono, template)
        except Exception as chat_err:
            print(f"Error registering chat message / WhatsApp notification: {chat_err}")

        # Send confirmation email if email provided
        if email:
            try:
                from django.core.mail import send_mail
                from .models import GlobalSettings
                settings = GlobalSettings.get_singleton()
                template = settings.trial_class_email_template
                if template:
                    body = template.format(
                        nombre=nombre,
                        profesor=teacher.name if teacher else profesor_nombre,
                        fecha=fecha.strftime("%d/%m/%Y") if hasattr(fecha, 'strftime') else str(fecha),
                        hora=hora.strftime("%H:%M") if hasattr(hora, 'strftime') else str(hora)
                    )
                    send_mail(
                        subject="Pre-reserva Clase de Prueba - Academia Détaché",
                        message=body,
                        from_email=settings.email_contact or "academia@detache.cl",
                        recipient_list=[email],
                        fail_silently=True
                    )
            except Exception as mail_err:
                print(f"Error sending trial class email: {mail_err}")

        return CreatePreReservation(success=True, lesson=lesson)

class CreateLesson(graphene.Mutation):
    class Arguments:
        teacher_id = graphene.Int(required=True)
        student_id = graphene.Int(required=True)
        room_id = graphene.Int(required=True)
        date = graphene.Date(required=True)
        start_time = graphene.Time(required=True)
        end_time = graphene.Time(required=True)
        lesson_type = graphene.String()

    lesson = graphene.Field(LessonType)

    def mutate(self, info, teacher_id, student_id, room_id, date, start_time, end_time, lesson_type="INDIVIDUAL"):
        teacher = Teacher.objects.get(pk=teacher_id)
        student = Student.objects.get(pk=student_id)
        room = Room.objects.get(pk=room_id)
        
        lesson = Lesson.objects.create(
            teacher=teacher,
            student=student,
            room=room,
            date=date,
            start_time=start_time,
            end_time=end_time,
            lesson_type=lesson_type
        )
        return CreateLesson(lesson=lesson)

class CreateAnnouncement(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        content = graphene.String(required=True)
        target_audience = graphene.String()
        is_active = graphene.Boolean()

    announcement = graphene.Field(AnnouncementType)

    def mutate(self, info, title, content, target_audience='ALL', is_active=True):
        announcement = Announcement.objects.create(
            title=title,
            content=content,
            target_audience=target_audience,
            is_active=is_active
        )
        return CreateAnnouncement(announcement=announcement)

class UpdateAnnouncement(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        title = graphene.String()
        content = graphene.String()
        target_audience = graphene.String()
        is_active = graphene.Boolean()

    announcement = graphene.Field(AnnouncementType)

    def mutate(self, info, id, title=None, content=None, target_audience=None, is_active=None):
        try:
            announcement = Announcement.objects.get(pk=id)
            if title is not None: announcement.title = title
            if content is not None: announcement.content = content
            if target_audience is not None: announcement.target_audience = target_audience
            if is_active is not None: announcement.is_active = is_active
            announcement.save()
            return UpdateAnnouncement(announcement=announcement)
        except Announcement.DoesNotExist:
            return UpdateAnnouncement(announcement=None)

class DeleteAnnouncement(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
    success = graphene.Boolean()

    def mutate(self, info, id):
        try:
            Announcement.objects.get(pk=id).delete()
            return DeleteAnnouncement(success=True)
        except Announcement.DoesNotExist:
            return DeleteAnnouncement(success=False)

class CreateTeacher(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        description = graphene.String()
        status = graphene.String()
        phone_number = graphene.String()
        rut = graphene.String()
        address = graphene.String()
        email = graphene.String()
        specialty_ids = graphene.List(graphene.Int)
        provisional_password = graphene.String()

    teacher = graphene.Field(TeacherType)
    provisional_password = graphene.String()
    user_created = graphene.Boolean()
    username = graphene.String()

    def mutate(self, info, name, description="", status="ACTIVE", phone_number=None, rut=None, address=None, email=None, specialty_ids=None, provisional_password=None):
        teacher = Teacher.objects.create(
            name=name, 
            description=description, 
            status=status,
            phone_number=phone_number,
            rut=rut,
            address=address,
            email=email
        )
        if specialty_ids:
            teacher.specialties.set(specialty_ids)

        assigned_user = None
        user_created = False
        password_used = provisional_password or "Detache2026!"
        username_used = None

        if email and email.strip():
            clean_email = email.strip().lower()
            username_used = clean_email
            
            existing_user = User.objects.filter(username=username_used).first()
            if not existing_user:
                existing_user = User.objects.filter(email=clean_email).first()

            if existing_user:
                assigned_user = existing_user
                user_created = False
            else:
                name_parts = name.strip().split(' ', 1)
                first_name = name_parts[0]
                last_name = name_parts[1] if len(name_parts) > 1 else ""

                assigned_user = User.objects.create_user(
                    username=username_used,
                    email=clean_email,
                    password=password_used,
                    first_name=first_name,
                    last_name=last_name
                )
                user_created = True

            profile, _ = UserProfile.objects.get_or_create(user=assigned_user)
            if profile.role not in ['ADMIN', 'SUPERADMIN']:
                profile.role = 'PROFESOR'
                profile.allowed_sections = ["DASHBOARD", "CALENDAR", "STUDENTS", "MATERIALS"]
                profile.save()

            teacher.user = assigned_user
            teacher.save()
            log_user_action(info, "CREATE_TEACHER_ACCOUNT_AUTO", f"Cuenta de portal creada automáticamente para profesor: {teacher.name} (username: {username_used})")
        elif rut and rut.strip():
            clean_rut = rut.strip().lower().replace('.', '').replace('-', '')
            username_used = clean_rut
            existing_user = User.objects.filter(username=username_used).first()
            if not existing_user:
                name_parts = name.strip().split(' ', 1)
                first_name = name_parts[0]
                last_name = name_parts[1] if len(name_parts) > 1 else ""
                assigned_user = User.objects.create_user(
                    username=username_used,
                    password=password_used,
                    first_name=first_name,
                    last_name=last_name
                )
                user_created = True
                profile, _ = UserProfile.objects.get_or_create(user=assigned_user)
                profile.role = 'PROFESOR'
                profile.allowed_sections = ["DASHBOARD", "CALENDAR", "STUDENTS", "MATERIALS"]
                profile.save()
                teacher.user = assigned_user
                teacher.save()
                log_user_action(info, "CREATE_TEACHER_ACCOUNT_AUTO", f"Cuenta de portal creada automáticamente para profesor: {teacher.name} (username: {username_used})")

        log_user_action(info, "CREATE_TEACHER", f"Creado profesor: {teacher.name} (ID: {teacher.id})")
        return CreateTeacher(
            teacher=teacher,
            provisional_password=password_used if user_created else None,
            user_created=user_created,
            username=username_used
        )

class UpdateTeacher(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        name = graphene.String()
        description = graphene.String()
        status = graphene.String()
        phone_number = graphene.String()
        rut = graphene.String()
        address = graphene.String()
        email = graphene.String()
        specialty_ids = graphene.List(graphene.Int)

    teacher = graphene.Field(TeacherType)

    def mutate(self, info, id, name=None, description=None, status=None, phone_number=None, rut=None, address=None, email=None, specialty_ids=None):
        try:
            teacher = Teacher.objects.get(pk=id)
            if name is not None: teacher.name = name
            if description is not None: teacher.description = description
            if status is not None: teacher.status = status
            if phone_number is not None: teacher.phone_number = phone_number
            if rut is not None: teacher.rut = rut
            if address is not None: teacher.address = address
            if email is not None: teacher.email = email
            if specialty_ids is not None:
                teacher.specialties.set(specialty_ids)
            teacher.save()
            return UpdateTeacher(teacher=teacher)
        except Teacher.DoesNotExist:
            return UpdateTeacher(teacher=None)

class DeleteTeacher(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    success = graphene.Boolean()
    error = graphene.String()

    def mutate(self, info, id):
        try:
            teacher = Teacher.objects.get(pk=id)
            if teacher.user:
                u = teacher.user
                teacher.user = None
                teacher.save()
                u.delete()
            teacher.delete()
            return DeleteTeacher(success=True)
        except Teacher.DoesNotExist:
            return DeleteTeacher(success=False, error="Profesor no encontrado.")
        except Exception as e:
            return DeleteTeacher(success=False, error=str(e))

class CreateAvailability(graphene.Mutation):
    class Arguments:
        teacher_id = graphene.Int(required=True)
        day = graphene.String(required=True)
        start_time = graphene.Time(required=True)
        end_time = graphene.Time(required=True)

    availability = graphene.Field(AvailabilityType)

    def mutate(self, info, teacher_id, day, start_time, end_time):
        teacher = Teacher.objects.get(pk=teacher_id)
        availability = Availability.objects.create(
            teacher=teacher,
            day=day,
            start_time=start_time,
            end_time=end_time
        )
        return CreateAvailability(availability=availability)

class UpdateAvailability(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        day = graphene.String()
        start_time = graphene.Time()
        end_time = graphene.Time()

    availability = graphene.Field(AvailabilityType)

    def mutate(self, info, id, day=None, start_time=None, end_time=None):
        availability = Availability.objects.get(pk=id)
        if day:
            availability.day = day
        if start_time:
            availability.start_time = start_time
        if end_time:
            availability.end_time = end_time
        availability.save()
        return UpdateAvailability(availability=availability)

class DeleteAvailability(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    success = graphene.Boolean()

    def mutate(self, info, id):
        Availability.objects.filter(pk=id).delete()
        return DeleteAvailability(success=True)

class CreateStudent(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String()
        rut = graphene.String()
        birth_date = graphene.Date()
        guardian_name = graphene.String()
        guardian_phone = graphene.String()
        status = graphene.String()
        phone_number = graphene.String()
        level = graphene.String()
        primary_instrument_id = graphene.Int()
        assigned_teacher_ids = graphene.List(graphene.Int)

    student = graphene.Field(StudentType)

    def mutate(self, info, name, email=None, rut=None, birth_date=None, guardian_name=None, guardian_phone=None, status="ACTIVE", phone_number=None, level="BEGINNER", primary_instrument_id=None, assigned_teacher_ids=None):
        primary_instrument = Instrument.objects.filter(pk=primary_instrument_id).first() if primary_instrument_id else None
        student = Student.objects.create(
            name=name,
            email=email,
            rut=rut,
            birth_date=birth_date,
            guardian_name=guardian_name,
            guardian_phone=guardian_phone,
            status=status,
            phone_number=phone_number,
            level=level,
            primary_instrument=primary_instrument
        )
        if assigned_teacher_ids:
            student.assigned_teachers.set(Teacher.objects.filter(pk__in=assigned_teacher_ids))
        log_user_action(info, "CREATE_STUDENT", f"Registrado nuevo estudiante: {student.name} (ID: {student.id})")
        return CreateStudent(student=student)

class UpdateStudent(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        name = graphene.String()
        email = graphene.String()
        rut = graphene.String()
        birth_date = graphene.Date()
        guardian_name = graphene.String()
        guardian_phone = graphene.String()
        status = graphene.String()
        phone_number = graphene.String()
        level = graphene.String()
        primary_instrument_id = graphene.Int()
        assigned_teacher_ids = graphene.List(graphene.Int)

    student = graphene.Field(StudentType)

    def mutate(self, info, id, name=None, email=None, rut=None, birth_date=None, guardian_name=None, guardian_phone=None, status=None, phone_number=None, level=None, primary_instrument_id=None, assigned_teacher_ids=None):
        try:
            student = Student.objects.get(pk=id)
            if name is not None: student.name = name
            if email is not None: student.email = email
            if rut is not None: student.rut = rut
            if birth_date is not None: student.birth_date = birth_date
            if guardian_name is not None: student.guardian_name = guardian_name
            if guardian_phone is not None: student.guardian_phone = guardian_phone
            if status is not None: student.status = status
            if phone_number is not None: student.phone_number = phone_number
            if level is not None: student.level = level
            if primary_instrument_id is not None:
                student.primary_instrument = Instrument.objects.filter(pk=primary_instrument_id).first()
            if assigned_teacher_ids is not None:
                student.assigned_teachers.set(Teacher.objects.filter(pk__in=assigned_teacher_ids))
            student.save()
            log_user_action(info, "UPDATE_STUDENT", f"Actualizada ficha del estudiante: {student.name} (ID: {student.id})")
            return UpdateStudent(student=student)
        except Student.DoesNotExist:
            return UpdateStudent(student=None)

class UpdateGlobalSettings(graphene.Mutation):
    class Arguments:
        phone_number = graphene.String()
        email_contact = graphene.String()
        address = graphene.String()
        opening_hours_weekdays = graphene.String()
        opening_hours_saturdays = graphene.String()
        facebook_url = graphene.String()
        instagram_url = graphene.String()
        trial_class_email_template = graphene.String()
        whatsapp_number = graphene.String()
        whatsapp_assigned_to = graphene.String()
        evolution_api_url = graphene.String()
        evolution_api_key = graphene.String()
        evolution_instance_name = graphene.String()
        whatsapp_auto_reply = graphene.Boolean()
        whatsapp_welcome_template = graphene.String()

    global_settings = graphene.Field(GlobalSettingsType)

    def mutate(self, info, phone_number=None, email_contact=None, address=None, opening_hours_weekdays=None, opening_hours_saturdays=None, facebook_url=None, instagram_url=None, trial_class_email_template=None, whatsapp_number=None, whatsapp_assigned_to=None, evolution_api_url=None, evolution_api_key=None, evolution_instance_name=None, whatsapp_auto_reply=None, whatsapp_welcome_template=None):
        settings = GlobalSettings.get_singleton()
        if phone_number is not None: settings.phone_number = phone_number
        if email_contact is not None: settings.email_contact = email_contact
        if address is not None: settings.address = address
        if opening_hours_weekdays is not None: settings.opening_hours_weekdays = opening_hours_weekdays
        if opening_hours_saturdays is not None: settings.opening_hours_saturdays = opening_hours_saturdays
        if facebook_url is not None: settings.facebook_url = facebook_url
        if instagram_url is not None: settings.instagram_url = instagram_url
        if trial_class_email_template is not None: settings.trial_class_email_template = trial_class_email_template
        if whatsapp_number is not None: settings.whatsapp_number = whatsapp_number
        if whatsapp_assigned_to is not None: settings.whatsapp_assigned_to = whatsapp_assigned_to
        if evolution_api_url is not None: settings.evolution_api_url = evolution_api_url
        if evolution_api_key is not None: settings.evolution_api_key = evolution_api_key
        if evolution_instance_name is not None: settings.evolution_instance_name = evolution_instance_name
        if whatsapp_auto_reply is not None: settings.whatsapp_auto_reply = whatsapp_auto_reply
        if whatsapp_welcome_template is not None: settings.whatsapp_welcome_template = whatsapp_welcome_template
        settings.save()
        log_user_action(info, "UPDATE_SETTINGS", "Actualizada configuración global y parámetros de WhatsApp")
        return UpdateGlobalSettings(global_settings=settings)

class SendWhatsApp(graphene.Mutation):
    class Arguments:
        phone_number = graphene.String(required=True)
        message = graphene.String(required=True)

    success = graphene.Boolean()
    response = graphene.String()

    def mutate(self, info, phone_number, message):
        from .whatsapp import WhatsAppService
        result = WhatsAppService.send_text_message(phone_number, message)
        if result:
            from .models import ChatMessage, Student, Lead
            
            clean_num = phone_number[-8:] if len(phone_number) >= 8 else phone_number
            student = Student.objects.filter(phone_number__icontains=clean_num).first()
            lead = Lead.objects.filter(telefono__icontains=clean_num).first()
            
            # Save outgoing message to history
            msg_id = None
            if isinstance(result, dict):
                # Try to resolve msg_id from Evolution API response format
                msg_id = result.get('key', {}).get('id') or result.get('messageId')
                
            ChatMessage.objects.create(
                lead=lead,
                student=student,
                phone_number=phone_number,
                sender='ACADEMY',
                message_text=message,
                message_id=msg_id
            )
            
            log_user_action(info, "SEND_WHATSAPP", f"Enviado mensaje WA a {phone_number}: {message[:50]}...")
            
            import json
            return SendWhatsApp(success=True, response=json.dumps(result))
        return SendWhatsApp(success=False, response="Failed to send message")

class SendWhatsAppButtons(graphene.Mutation):
    class Arguments:
        phone_number = graphene.String(required=True)
        text = graphene.String(required=True)
        buttons_json = graphene.String(required=True) # JSON string of buttons

    success = graphene.Boolean()
    response = graphene.String()

    def mutate(self, info, phone_number, text, buttons_json):
        from .whatsapp import WhatsAppService
        import json
        buttons = json.loads(buttons_json)
        result = WhatsAppService.send_button_message(phone_number, text, buttons)
        if result:
            return SendWhatsAppButtons(success=True, response=json.dumps(result))
        return SendWhatsAppButtons(success=False, response="Failed to send buttons")

class CreateLead(graphene.Mutation):
    class Arguments:
        nombre = graphene.String(required=True)
        telefono = graphene.String(required=True)
        email = graphene.String()
        edad = graphene.Int()
        servicio = graphene.String()
        fuente = graphene.String()

    lead = graphene.Field(LeadType)

    def mutate(self, info, nombre, telefono, email=None, edad=None, servicio='CLASE_PRUEBA', fuente='WEB'):
        parsed_res = None
        if email and "|" in email:
            try:
                parts = [p.strip() for p in email.split("|")]
                real_email = parts[0]
                
                info_dict = {}
                for part in parts[1:]:
                    if ":" in part:
                        k, v = part.split(":", 1)
                        info_dict[k.strip().lower()] = v.strip()
                        
                profesor_name = info_dict.get('profesor')
                fecha_str = info_dict.get('fecha')
                horario_str = info_dict.get('horario')
                
                if profesor_name and fecha_str and horario_str:
                    times = horario_str.split("-")
                    start_time_str = times[0].strip()
                    end_time_str = times[1].strip()
                    parsed_res = {
                        'email': real_email,
                        'profesor': profesor_name,
                        'fecha': fecha_str,
                        'start_time': start_time_str,
                        'end_time': end_time_str
                    }
            except Exception as e:
                print(f"Error parsing email details in CreateLead: {e}")

        lead_email = parsed_res['email'] if parsed_res else email

        lead = Lead.objects.create(
            nombre=nombre,
            telefono=telefono,
            email=lead_email,
            edad=edad,
            servicio=servicio,
            fuente=fuente
        )

        if parsed_res:
            try:
                from datetime import datetime
                teacher = Teacher.objects.filter(name__icontains=parsed_res['profesor']).first()
                if not teacher:
                    teacher = Teacher.objects.first()
                
                if teacher:
                    parsed_date = datetime.strptime(parsed_res['fecha'], "%Y-%m-%d").date()
                    start_t = datetime.strptime(parsed_res['start_time'], "%H:%M").time()
                    end_t = datetime.strptime(parsed_res['end_time'], "%H:%M").time()
                    
                    Lesson.objects.create(
                        teacher=teacher,
                        lead=lead,
                        student=None,
                        date=parsed_date,
                        start_time=start_t,
                        end_time=end_t,
                        status='PENDING',
                        is_pre_reservation=True,
                        lesson_type='INDIVIDUAL'
                    )
            except Exception as lesson_err:
                print(f"Error creating pre-reservation lesson: {lesson_err}")

        # Register initial contact / inquiry as ChatMessage for the Lead
        try:
            from .models import ChatMessage, GlobalSettings
            from .whatsapp import WhatsAppService
            
            chat_parts = [f"📋 Solicitud Web de Contacto / Reserva:"]
            chat_parts.append(f"• Servicio / Especialidad: {servicio or 'General'}")
            if parsed_res:
                chat_parts.append(f"• Profesional: {parsed_res.get('profesor')}")
                chat_parts.append(f"• Fecha: {parsed_res.get('fecha')}")
                chat_parts.append(f"• Horario: {parsed_res.get('start_time')} - {parsed_res.get('end_time')}")
            elif email and "|" in email:
                chat_parts.append(f"• Mensaje / Motivo: {email.split('|', 1)[-1].strip()}")

            ChatMessage.objects.create(
                lead=lead,
                phone_number=telefono,
                sender='LEAD',
                message_text="\n".join(chat_parts)
            )

            # Auto-reply via WhatsApp if enabled
            gs = GlobalSettings.get_singleton()
            if gs.whatsapp_auto_reply and gs.whatsapp_welcome_template:
                template = gs.whatsapp_welcome_template.replace('{nombre}', nombre)
                WhatsAppService.send_text_message(telefono, template)
        except Exception as chat_err:
            print(f"Error registering chat message in CreateLead: {chat_err}")

        try:
            OnLeadUpdated.broadcast(group="leads_group", payload={"lead_id": lead.id, "event_type": "created"})
        except Exception as ws_err:
            print(f"Error broadcasting new lead: {ws_err}")
        log_user_action(info, "CREATE_LEAD", f"Creado prospecto: {lead.nombre} (ID: {lead.id})")
        return CreateLead(lead=lead)


class ConvertLeadToStudent(graphene.Mutation):
    class Arguments:
        lead_id = graphene.Int(required=True)

    success = graphene.Boolean()
    student = graphene.Field(StudentType)

    def mutate(self, info, lead_id):
        try:
            lead = Lead.objects.get(pk=lead_id)
            if lead.estado == 'CONCRETADO':
                return ConvertLeadToStudent(success=False, student=None)

            student = Student.objects.create(
                name=lead.nombre,
                email=lead.email,
                phone_number=lead.telefono,
                status='ACTIVE'
            )
            
            Lesson.objects.filter(lead=lead).update(student=student, is_pre_reservation=False)
            
            lead.estado = 'CONCRETADO'
            lead.save()
            log_user_action(info, "CONVERT_LEAD_TO_STUDENT", f"Convertido prospecto {lead.nombre} (ID: {lead.id}) a estudiante {student.name} (ID: {student.id})")
            return ConvertLeadToStudent(success=True, student=student)
        except Lead.DoesNotExist:
            return ConvertLeadToStudent(success=False, student=None)

class RegisterPayment(graphene.Mutation):
    class Arguments:
        student_id = graphene.Int(required=True)
        amount = graphene.Float(required=True)
        method = graphene.String(required=True) # TRANSFER, CASH, CARD
        description = graphene.String()
        plan_id = graphene.Int() # If they also bought a pack

    success = graphene.Boolean()
    payment = graphene.Field(PaymentType)
    pack = graphene.Field(StudentPackType)

    def mutate(self, info, student_id, amount, method, description=None, plan_id=None):
        student = Student.objects.get(pk=student_id)
        
        pack = None
        if plan_id:
            plan = Plan.objects.get(pk=plan_id)
            pack = StudentPack.objects.create(student=student, plan=plan)
            # Call purchase notifications
            try:
                from .whatsapp import WhatsAppService
                WhatsAppService.send_purchase_notifications(student, plan, amount)
            except Exception as notif_err:
                print(f"Error triggering manual purchase notifications: {notif_err}")

        payment = Payment.objects.create(
            student=student,
            amount=amount,
            method=method,
            description=description,
            pack=pack
        )
        log_user_action(info, "REGISTER_PAYMENT", f"Registrado pago de ${int(amount)} CLP para estudiante {student.name} (ID: {student.id})")
        return RegisterPayment(success=True, payment=payment, pack=pack)


class CreateStudentPack(graphene.Mutation):
    class Arguments:
        student_id = graphene.Int(required=True)
        plan_id = graphene.Int(required=True)
        purchase_date = graphene.Date()

    pack = graphene.Field(StudentPackType)

    def mutate(self, info, student_id, plan_id, purchase_date=None):
        student = Student.objects.get(pk=student_id)
        plan = Plan.objects.get(pk=plan_id)
        
        pack = StudentPack.objects.create(
            student=student,
            plan=plan,
            purchase_date=purchase_date if purchase_date else timezone.now()
        )
        # Call purchase notifications
        try:
            from .whatsapp import WhatsAppService
            WhatsAppService.send_purchase_notifications(student, plan, plan.price)
        except Exception as notif_err:
            print(f"Error triggering pack creation notifications: {notif_err}")
        log_user_action(info, "CREATE_STUDENT_PACK", f"Asociado pack de clases: {plan.name} para estudiante {student.name} (ID: {student.id})")
        return CreateStudentPack(pack=pack)

class ManualDeductClass(graphene.Mutation):
    class Arguments:
        pack_id = graphene.Int(required=True)

    success = graphene.Boolean()
    pack = graphene.Field(StudentPackType)

    def mutate(self, info, pack_id):
        try:
            pack = StudentPack.objects.get(pk=pack_id)
            if pack.remaining_classes > 0:
                pack.remaining_classes -= 1
                pack.save()
                return ManualDeductClass(success=True, pack=pack)
            return ManualDeductClass(success=False, pack=pack)
        except StudentPack.DoesNotExist:
            return ManualDeductClass(success=False, pack=None)

class UpdateLessonStatus(graphene.Mutation):
    class Arguments:
        lesson_id = graphene.Int(required=True)
        status = graphene.String(required=True) # PENDING, COMPLETED, CANCELLED

    success = graphene.Boolean()
    lesson = graphene.Field(LessonType)

    def mutate(self, info, lesson_id, status):
        try:
            lesson = Lesson.objects.get(pk=lesson_id)
            old_status = lesson.status
            lesson.status = status
            lesson.save()

            # Auto-deduct class if status changed to COMPLETED or ABSENT
            deducting_statuses = ['COMPLETED', 'ABSENT']
            if old_status not in deducting_statuses and status in deducting_statuses:
                active_pack = StudentPack.objects.filter(
                    student=lesson.student,
                    is_active=True,
                    remaining_classes__gt=0
                ).order_by('expiration_date').first()
                if active_pack:
                    active_pack.remaining_classes -= 1
                    active_pack.save()
            
            # Auto-refund class if changed from COMPLETED/ABSENT to something else
            elif old_status in deducting_statuses and status not in deducting_statuses:
                active_pack = StudentPack.objects.filter(
                    student=lesson.student,
                    is_active=True
                ).order_by('-expiration_date').first()
                if active_pack:
                    active_pack.remaining_classes += 1
                    active_pack.save()
                    
            return UpdateLessonStatus(success=True, lesson=lesson)
        except Lesson.DoesNotExist:
            return UpdateLessonStatus(success=False, lesson=None)

class UpdateLeadStatus(graphene.Mutation):
    class Arguments:
        lead_id = graphene.ID(required=True)
        status = graphene.String(required=True)

    success = graphene.Boolean()
    lead = graphene.Field(LeadType)

    def mutate(self, info, lead_id, status):
        try:
            lead = Lead.objects.get(pk=lead_id)
            lead.estado = status
            lead.save()

            if status == 'RESERVA_CONFIRMADA':
                Lesson.objects.filter(lead=lead, is_pre_reservation=True).update(status='CONFIRMED', is_pre_reservation=False)

            try:
                OnLeadUpdated.broadcast(group="leads_group", payload={"lead_id": lead.id, "event_type": "updated"})
            except Exception as ws_err:
                print(f"Error broadcasting lead status update: {ws_err}")
            return UpdateLeadStatus(success=True, lead=lead)
        except Lead.DoesNotExist:
            return UpdateLeadStatus(success=False, lead=None)

class ConfirmLeadReservationWithLesson(graphene.Mutation):
    class Arguments:
        lead_id = graphene.Int(required=True)
        teacher_id = graphene.Int(required=True)
        date = graphene.Date(required=True)
        start_time = graphene.Time(required=True)
        end_time = graphene.Time(required=True)
        room_id = graphene.Int()
        lesson_type = graphene.String()

    success = graphene.Boolean()
    lead = graphene.Field(LeadType)
    lesson = graphene.Field(LessonType)
    error = graphene.String()

    def mutate(self, info, lead_id, teacher_id, date, start_time, end_time, room_id=None, lesson_type="INDIVIDUAL"):
        try:
            lead = Lead.objects.get(pk=lead_id)
            teacher = Teacher.objects.get(pk=teacher_id)
            room = Room.objects.filter(pk=room_id).first() if room_id else None

            # Check if there's an existing pre-reservation lesson for this lead
            existing_lesson = Lesson.objects.filter(lead=lead, is_pre_reservation=True).first()
            if existing_lesson:
                existing_lesson.teacher = teacher
                existing_lesson.date = date
                existing_lesson.start_time = start_time
                existing_lesson.end_time = end_time
                existing_lesson.room = room
                existing_lesson.status = 'CONFIRMED'
                existing_lesson.is_pre_reservation = False
                existing_lesson.lesson_type = lesson_type or 'INDIVIDUAL'
                existing_lesson.save()
                lesson = existing_lesson
            else:
                lesson = Lesson.objects.create(
                    lead=lead,
                    teacher=teacher,
                    date=date,
                    start_time=start_time,
                    end_time=end_time,
                    room=room,
                    status='CONFIRMED',
                    is_pre_reservation=False,
                    lesson_type=lesson_type or 'INDIVIDUAL'
                )

            lead.estado = 'RESERVA_CONFIRMADA'
            lead.save()

            try:
                OnLeadUpdated.broadcast(group="leads_group", payload={"lead_id": lead.id, "event_type": "updated"})
            except Exception as ws_err:
                print(f"Error broadcasting lead confirmation: {ws_err}")

            log_user_action(info, "CONFIRM_RESERVATION", f"Confirmada reserva y agendada clase para lead {lead.nombre} con profesor {teacher.name}")
            return ConfirmLeadReservationWithLesson(success=True, lead=lead, lesson=lesson)
        except Lead.DoesNotExist:
            return ConfirmLeadReservationWithLesson(success=False, error="Lead no encontrado.")
        except Teacher.DoesNotExist:
            return ConfirmLeadReservationWithLesson(success=False, error="Profesor no encontrado.")
        except Exception as e:
            return ConfirmLeadReservationWithLesson(success=False, error=str(e))

class CreateLeadNote(graphene.Mutation):
    class Arguments:
        lead_id = graphene.Int(required=True)
        texto = graphene.String(required=True)
        autor = graphene.String()

    success = graphene.Boolean()
    lead_note = graphene.Field(LeadNoteType)
    lead = graphene.Field(LeadType)

    def mutate(self, info, lead_id, texto, autor="Admin"):
        try:
            lead = Lead.objects.get(pk=lead_id)
            user = getattr(info.context, 'user', None)
            resolved_author = autor
            if user and user.is_authenticated:
                if user.first_name:
                    resolved_author = f"{user.first_name} {user.last_name}".strip()
                elif user.username:
                    resolved_author = user.username

            note = LeadNote.objects.create(
                lead=lead,
                texto=texto,
                autor=resolved_author or "Admin"
            )
            lead.fecha_ultimo_contacto = timezone.now()
            lead.save()
            try:
                OnLeadUpdated.broadcast(group="leads_group", payload={"lead_id": lead.id, "event_type": "updated"})
            except Exception as ws_err:
                print(f"Error broadcasting lead note update: {ws_err}")
            log_user_action(info, "CREATE_LEAD_NOTE", f"Agregada nota a lead {lead.nombre}: {texto[:30]}...")
            return CreateLeadNote(success=True, lead_note=note, lead=lead)
        except Lead.DoesNotExist:
            return CreateLeadNote(success=False, lead_note=None, lead=None)

class DeleteLead(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    success = graphene.Boolean()

    def mutate(self, info, id):
        try:
            lead = Lead.objects.get(pk=id)
            lead_name = lead.nombre
            # Clean up associated pre-reservation lessons if any
            Lesson.objects.filter(lead=lead, is_pre_reservation=True, student__isnull=True).delete()
            lead.delete()
            try:
                OnLeadUpdated.broadcast(group="leads_group", payload={"lead_id": int(id), "event_type": "deleted"})
            except Exception as ws_err:
                print(f"Error broadcasting lead deletion: {ws_err}")
            log_user_action(info, "DELETE_LEAD", f"Eliminado prospecto: {lead_name} (ID: {id})")
            return DeleteLead(success=True)
        except Lead.DoesNotExist:
            return DeleteLead(success=False)

class CreatePlan(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        price = graphene.Float(required=True)
        duration = graphene.Int(required=True)
        classes_count = graphene.Int(required=True)
        is_featured = graphene.Boolean()
        benefits = graphene.List(graphene.String)

    plan = graphene.Field(PlanType)

    def mutate(self, info, name, price, duration, classes_count, is_featured=False, benefits=None):
        if benefits is None:
            benefits = []
        plan = Plan.objects.create(
            name=name,
            price=price,
            duration=duration,
            classes_count=classes_count,
            is_featured=is_featured,
            benefits=benefits
        )
        return CreatePlan(plan=plan)

class DeletePlan(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    success = graphene.Boolean()

    def mutate(self, info, id):
        try:
            plan = Plan.objects.get(pk=id)
            plan.delete()
            return DeletePlan(success=True)
        except Plan.DoesNotExist:
            return DeletePlan(success=False)

class UpdatePlan(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        name = graphene.String()
        price = graphene.Float()
        duration = graphene.Int()
        classes_count = graphene.Int()
        is_featured = graphene.Boolean()
        benefits = graphene.List(graphene.String)

    plan = graphene.Field(PlanType)

    def mutate(self, info, id, name=None, price=None, duration=None, classes_count=None, is_featured=None, benefits=None):
        try:
            plan = Plan.objects.get(pk=id)
            if name is not None: plan.name = name
            if price is not None: plan.price = price
            if duration is not None: plan.duration = duration
            if classes_count is not None: plan.classes_count = classes_count
            if is_featured is not None: plan.is_featured = is_featured
            if benefits is not None: plan.benefits = benefits
            plan.save()
            return UpdatePlan(plan=plan)
        except Plan.DoesNotExist:
            return UpdatePlan(plan=None)

class CreateAcademyTask(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        description = graphene.String()
        assigned_to = graphene.String()
        assigned_user_id = graphene.Int()
        priority = graphene.String()
        status = graphene.String()
        due_date = graphene.Date()
        duration = graphene.Int()
        log = graphene.String()

    task = graphene.Field(AcademyTaskType)

    def mutate(self, info, title, description="", assigned_to="RECEPCION", priority="RECORDATORIO", status="PENDING", log="", assigned_user_id=None, due_date=None, duration=30):
        assigned_user = User.objects.filter(pk=assigned_user_id).first() if assigned_user_id else None
        task = AcademyTask.objects.create(
            title=title,
            description=description,
            assigned_to=assigned_to,
            assigned_user=assigned_user,
            priority=priority,
            status=status or "PENDING",
            due_date=due_date,
            duration=duration,
            log=log
        )
        log_user_action(info, "CREATE_TASK", f"Creada tarea: {task.title} (ID: {task.id})")
        return CreateAcademyTask(task=task)

class UpdateAcademyTask(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        title = graphene.String()
        description = graphene.String()
        assigned_to = graphene.String()
        assigned_user_id = graphene.Int()
        priority = graphene.String()
        status = graphene.String()
        log = graphene.String()
        is_completed = graphene.Boolean()
        due_date = graphene.Date()
        duration = graphene.Int()

    task = graphene.Field(AcademyTaskType)

    def mutate(self, info, id, title=None, description=None, assigned_to=None, priority=None, status=None, log=None, is_completed=None, assigned_user_id=None, due_date=None, duration=None):
        try:
            task = AcademyTask.objects.get(pk=id)
            if title is not None: task.title = title
            if description is not None: task.description = description
            if assigned_to is not None: task.assigned_to = assigned_to
            if priority is not None: task.priority = priority
            if log is not None: task.log = log
            if due_date is not None: task.due_date = due_date
            if duration is not None: task.duration = duration
            
            if assigned_user_id is not None:
                task.assigned_user = User.objects.filter(pk=assigned_user_id).first() if assigned_user_id > 0 else None
                
            if status is not None:
                task.status = status
                if status == 'COMPLETED':
                    task.is_completed = True
                    task.completed_at = timezone.now()
                else:
                    task.is_completed = False
                    task.completed_at = None
            elif is_completed is not None:
                task.is_completed = is_completed
                if is_completed:
                    task.status = 'COMPLETED'
                    task.completed_at = timezone.now()
                else:
                    if task.status == 'COMPLETED':
                        task.status = 'PENDING'
                    task.completed_at = None
                
            task.save()
            log_user_action(info, "UPDATE_TASK", f"Actualizada tarea: {task.title} (ID: {task.id})")
            return UpdateAcademyTask(task=task)
        except AcademyTask.DoesNotExist:
            return UpdateAcademyTask(task=None)

class DeleteAcademyTask(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    success = graphene.Boolean()

    def mutate(self, info, id):
        task = AcademyTask.objects.filter(pk=id).first()
        if task:
            title = task.title
            task.delete()
            log_user_action(info, "DELETE_TASK", f"Eliminada tarea: {title} (ID: {id})")
        return DeleteAcademyTask(success=True)

class CreateInstrument(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)

    instrument = graphene.Field(InstrumentType)

    def mutate(self, info, name):
        instrument = Instrument.objects.create(name=name)
        return CreateInstrument(instrument=instrument)

class UpdateInstrument(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        name = graphene.String(required=True)

    instrument = graphene.Field(InstrumentType)

    def mutate(self, info, id, name):
        try:
            instrument = Instrument.objects.get(pk=id)
            instrument.name = name
            instrument.save()
            return UpdateInstrument(instrument=instrument)
        except Instrument.DoesNotExist:
            return UpdateInstrument(instrument=None)

class DeleteInstrument(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    success = graphene.Boolean()

    def mutate(self, info, id):
        Instrument.objects.filter(pk=id).delete()
        return DeleteInstrument(success=True)

class CreateMaterial(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        type = graphene.String(required=True)
        url = graphene.String(required=True)
        teacher_id = graphene.Int()

    material = graphene.Field(MaterialType)

    def mutate(self, info, title, type, url, teacher_id=None):
        teacher = Teacher.objects.filter(pk=teacher_id).first() if teacher_id else None
        material = Material.objects.create(title=title, type=type, url=url, teacher=teacher)
        return CreateMaterial(material=material)

class CreateStudentPrivateNote(graphene.Mutation):
    class Arguments:
        student_id = graphene.Int(required=True)
        text = graphene.String(required=True)
        author = graphene.String()

    note = graphene.Field(StudentPrivateNoteType)

    def mutate(self, info, student_id, text, author=None):
        student = Student.objects.get(pk=student_id)
        user = getattr(info.context, 'user', None)
        resolved_author = author
        if user and user.is_authenticated:
            try:
                if hasattr(user, 'teacher_profile') and user.teacher_profile:
                    resolved_author = user.teacher_profile.name
            except Exception:
                pass
            if not resolved_author or resolved_author in ["Profesor", "Staff"]:
                if user.first_name:
                    resolved_author = f"{user.first_name} {user.last_name}".strip()
                elif user.username:
                    resolved_author = user.username
        if not resolved_author or resolved_author in ["Profesor", "Staff"]:
            resolved_author = author or "Staff"

        note = StudentPrivateNote.objects.create(student=student, text=text, author=resolved_author)
        return CreateStudentPrivateNote(note=note)

class CreateStudentWallMessage(graphene.Mutation):
    class Arguments:
        student_id = graphene.Int(required=True)
        text = graphene.String(required=True)
        author = graphene.String()
        attached_material_id = graphene.Int()

    message = graphene.Field(StudentWallMessageType)

    def mutate(self, info, student_id, text, author=None, attached_material_id=None):
        student = Student.objects.get(pk=student_id)
        material = Material.objects.filter(pk=attached_material_id).first() if attached_material_id else None
        
        user = getattr(info.context, 'user', None)
        resolved_author = author
        if user and user.is_authenticated:
            try:
                if hasattr(user, 'teacher_profile') and user.teacher_profile:
                    resolved_author = user.teacher_profile.name
            except Exception:
                pass
            if not resolved_author or resolved_author in ["Profesor", "Staff"]:
                if user.first_name:
                    resolved_author = f"{user.first_name} {user.last_name}".strip()
                elif user.username:
                    resolved_author = user.username
        if not resolved_author:
            resolved_author = author or "Profesor"

        message = StudentWallMessage.objects.create(
            student=student, 
            text=text, 
            author=resolved_author, 
            attached_material=material
        )
        return CreateStudentWallMessage(message=message)

class UpdateLandingPage(graphene.Mutation):
    class Arguments:
        slug = graphene.String(required=True)
        title = graphene.String()
        subtitle = graphene.String()
        problem = graphene.String()
        solution = graphene.String()
        benefits = graphene.List(graphene.String)
        image_url = graphene.String()
        cta = graphene.String()

    success = graphene.Boolean()
    landing_page = graphene.Field(LandingPageType)

    def mutate(self, info, slug, title=None, subtitle=None, problem=None, solution=None, benefits=None, image_url=None, cta=None):
        try:
            landing = LandingPage.objects.get(slug=slug)
            if title is not None: landing.title = title
            if subtitle is not None: landing.subtitle = subtitle
            if problem is not None: landing.problem = problem
            if solution is not None: landing.solution = solution
            if benefits is not None: landing.benefits = benefits
            if image_url is not None: landing.image_url = image_url
            if cta is not None: landing.cta = cta
            landing.save()
            return UpdateLandingPage(success=True, landing_page=landing)
        except LandingPage.DoesNotExist:
            return UpdateLandingPage(success=False, landing_page=None)


class CloneLandingPage(graphene.Mutation):
    class Arguments:
        source_slug = graphene.String(required=True)
        new_slug = graphene.String(required=True)
        new_title = graphene.String(required=True)

    success = graphene.Boolean()
    landing_page = graphene.Field(LandingPageType)
    error = graphene.String()

    def mutate(self, info, source_slug, new_slug, new_title):
        try:
            if LandingPage.objects.filter(slug=new_slug).exists():
                return CloneLandingPage(success=False, landing_page=None, error="El slug ya existe.")
            source = LandingPage.objects.get(slug=source_slug)
            clone = LandingPage.objects.create(
                slug=new_slug,
                title=new_title,
                subtitle=source.subtitle,
                problem=source.problem,
                solution=source.solution,
                benefits=source.benefits,
                image_url=source.image_url,
                cta=source.cta
            )
            return CloneLandingPage(success=True, landing_page=clone, error=None)
        except LandingPage.DoesNotExist:
            return CloneLandingPage(success=False, landing_page=None, error="Página origen no encontrada.")
        except Exception as e:
            return CloneLandingPage(success=False, landing_page=None, error=str(e))


class UpdateHomepageContent(graphene.Mutation):
    class Arguments:
        hero_image = graphene.String()
        hero_title_1 = graphene.String()
        hero_title_highlight = graphene.String()
        hero_title_2 = graphene.String()
        hero_subtitle = graphene.String()
        hero_cta1_text = graphene.String()
        hero_cta1_link = graphene.String()
        hero_cta2_text = graphene.String()
        hero_cta2_link = graphene.String()
        features = graphene.String()        # JSON string
        method_badge = graphene.String()
        method_title = graphene.String()
        method_description = graphene.String()
        method_items = graphene.String()    # JSON string
        method_image = graphene.String()
        testimonials = graphene.String()    # JSON string
        location_title = graphene.String()
        location_description = graphene.String()
        location_address = graphene.String()
        location_address_detail = graphene.String()
        location_map_url = graphene.String()
        final_cta_title = graphene.String()
        final_cta_description = graphene.String()
        final_cta_button_text = graphene.String()
        planes_title = graphene.String()
        planes_description = graphene.String()
        instruments_title = graphene.String()
        instruments_description = graphene.String()
        gallery_title = graphene.String()
        gallery_images = graphene.String()  # JSON string

    success = graphene.Boolean()
    homepage = graphene.Field(HomepageContentType)

    def mutate(self, info, **kwargs):
        import json
        homepage = HomepageContent.get_singleton()
        json_fields = {'features', 'method_items', 'testimonials', 'gallery_images'}
        for field, value in kwargs.items():
            if field in json_fields:
                setattr(homepage, field, json.loads(value))
            else:
                setattr(homepage, field, value)
        homepage.save()
        return UpdateHomepageContent(success=True, homepage=homepage)


class UpdateAboutContent(graphene.Mutation):
    class Arguments:
        hero_image = graphene.String()
        hero_title_highlight_1 = graphene.String()
        hero_title_text_1 = graphene.String()
        hero_title_highlight_2 = graphene.String()
        history_image = graphene.String()
        history_title = graphene.String()
        history_subtitle = graphene.String()
        history_description = graphene.String()
        moving_title = graphene.String()
        moving_description = graphene.String()
        moving_cards = graphene.String()
        team_title = graphene.String()
        team_description = graphene.String()
        team_images = graphene.String()
        final_title_1 = graphene.String()
        final_title_2 = graphene.String()
        final_title_3 = graphene.String()
        final_image = graphene.String()

    success = graphene.Boolean()
    about = graphene.Field(AboutContentType)

    def mutate(self, info, **kwargs):
        import json
        about = AboutContent.get_singleton()
        json_fields = {'moving_cards', 'team_images'}
        for field, value in kwargs.items():
            if field in json_fields:
                try:
                    setattr(about, field, json.loads(value))
                except Exception as e:
                    print(f"Error parsing JSON for {field}: {e}")
            else:
                setattr(about, field, value)
        about.save()
        return UpdateAboutContent(success=True, about=about)


class UpdateContactContent(graphene.Mutation):
    class Arguments:
        banner_title_1 = graphene.String()
        banner_title_2 = graphene.String()
        banner_title_3 = graphene.String()
        banner_title_4 = graphene.String()
        location_title = graphene.String()
        location_description = graphene.String()
        location_address_title = graphene.String()
        location_address = graphene.String()
        location_map_iframe_url = graphene.String()

    success = graphene.Boolean()
    contact = graphene.Field(ContactContentType)

    def mutate(self, info, **kwargs):
        contact = ContactContent.get_singleton()
        for field, value in kwargs.items():
            setattr(contact, field, value)
        contact.save()
        return UpdateContactContent(success=True, contact=contact)


class CreateClassType(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        description = graphene.String()
        duration_minutes = graphene.Int()
        price = graphene.Int()
        currency = graphene.String()
        allowed_levels = graphene.List(graphene.String)
        allowed_modalities = graphene.List(graphene.String)
        what_you_will_learn = graphene.List(graphene.String)
        teacher_ids = graphene.List(graphene.Int)

    class_type = graphene.Field(ClassTypeType)

    def mutate(self, info, name, description=None, duration_minutes=45, price=0, currency='CLP', allowed_levels=None, allowed_modalities=None, what_you_will_learn=None, teacher_ids=None):
        class_type = ClassType.objects.create(
            name=name,
            description=description,
            duration_minutes=duration_minutes,
            price=price,
            currency=currency,
            allowed_levels=allowed_levels or [],
            allowed_modalities=allowed_modalities or [],
            what_you_will_learn=what_you_will_learn or []
        )
        if teacher_ids:
            class_type.teachers.set(Teacher.objects.filter(pk__in=teacher_ids))
        return CreateClassType(class_type=class_type)


class UpdateClassType(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        name = graphene.String()
        description = graphene.String()
        duration_minutes = graphene.Int()
        price = graphene.Int()
        currency = graphene.String()
        allowed_levels = graphene.List(graphene.String)
        allowed_modalities = graphene.List(graphene.String)
        what_you_will_learn = graphene.List(graphene.String)
        teacher_ids = graphene.List(graphene.Int)

    success = graphene.Boolean()
    class_type = graphene.Field(ClassTypeType)

    def mutate(self, info, id, name=None, description=None, duration_minutes=None, price=None, currency=None, allowed_levels=None, allowed_modalities=None, what_you_will_learn=None, teacher_ids=None):
        try:
            ct = ClassType.objects.get(pk=id)
            if name is not None: ct.name = name
            if description is not None: ct.description = description
            if duration_minutes is not None: ct.duration_minutes = duration_minutes
            if price is not None: ct.price = price
            if currency is not None: ct.currency = currency
            if allowed_levels is not None: ct.allowed_levels = allowed_levels
            if allowed_modalities is not None: ct.allowed_modalities = allowed_modalities
            if what_you_will_learn is not None: ct.what_you_will_learn = what_you_will_learn
            if teacher_ids is not None:
                ct.teachers.set(Teacher.objects.filter(pk__in=teacher_ids))
            ct.save()
            return UpdateClassType(success=True, class_type=ct)
        except ClassType.DoesNotExist:
            return UpdateClassType(success=False, class_type=None)


class DeleteClassType(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    success = graphene.Boolean()

    def mutate(self, info, id):
        try:
            ct = ClassType.objects.get(pk=id)
            ct.delete()
            return DeleteClassType(success=True)
        except ClassType.DoesNotExist:
            return DeleteClassType(success=False)


class CreateRoom(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        capacity = graphene.Int()
        status = graphene.String()
        instrument_ids = graphene.List(graphene.Int)

    room = graphene.Field(RoomType)

    def mutate(self, info, name, capacity=1, status='AVAILABLE', instrument_ids=None):
        room = Room.objects.create(
            name=name,
            capacity=capacity,
            status=status
        )
        if instrument_ids:
            room.instruments.set(Instrument.objects.filter(pk__in=instrument_ids))
        return CreateRoom(room=room)


class UpdateRoom(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        name = graphene.String()
        capacity = graphene.Int()
        status = graphene.String()
        instrument_ids = graphene.List(graphene.Int)

    success = graphene.Boolean()
    room = graphene.Field(RoomType)

    def mutate(self, info, id, name=None, capacity=None, status=None, instrument_ids=None):
        try:
            room = Room.objects.get(pk=id)
            if name is not None: room.name = name
            if capacity is not None: room.capacity = capacity
            if status is not None: room.status = status
            if instrument_ids is not None:
                room.instruments.set(Instrument.objects.filter(pk__in=instrument_ids))
            room.save()
            return UpdateRoom(success=True, room=room)
        except Room.DoesNotExist:
            return UpdateRoom(success=False, room=None)


class DeleteRoom(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    success = graphene.Boolean()

    def mutate(self, info, id):
        try:
            room = Room.objects.get(pk=id)
            room.delete()
            return DeleteRoom(success=True)
        except Room.DoesNotExist:
            return DeleteRoom(success=False)


class CreatePaymentPreference(graphene.Mutation):
    class Arguments:
        plan_id = graphene.Int(required=True)
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String(required=True)
        back_url = graphene.String(required=True)

    success = graphene.Boolean()
    preference_id = graphene.String()
    init_point = graphene.String()

    def mutate(self, info, plan_id, name, email, phone, back_url):
        import os
        import requests
        from urllib.parse import urlparse
        try:
            # 1. Fetch the plan
            plan = Plan.objects.get(pk=plan_id)
            
            # Clean and sanitize back_url to base origin
            back_url = back_url.strip().rstrip('/')
            if not back_url or not (back_url.startswith("http://") or back_url.startswith("https://")):
                # Fallback to referer or default host
                referer = info.context.META.get('HTTP_REFERER')
                if referer:
                    parsed = urlparse(referer)
                    back_url = f"{parsed.scheme}://{parsed.netloc}".rstrip('/')
                else:
                    back_url = "https://www.detache.cl"
            else:
                parsed = urlparse(back_url)
                back_url = f"{parsed.scheme}://{parsed.netloc}".rstrip('/')
            
            print(f"DEBUG: CreatePaymentPreference clean back_url is '{back_url}'")
            
            # Mercado Pago API rejects localhost/127.0.0.1 domains when auto_return is enabled.
            # We map local environments to the public Vercel test domain for validation.
            if "localhost" in back_url or "127.0.0.1" in back_url:
                back_url = "https://pianoacademy-git-main-jsepulvedai1s-projects.vercel.app"
                print(f"DEBUG: Replaced local back_url with Vercel test domain: '{back_url}'")
            
            # 2. Create or update the Lead to track payment initiation
            lead = Lead.objects.filter(email=email).first()
            if not lead:
                lead = Lead.objects.create(
                    nombre=name,
                    email=email,
                    telefono=phone,
                    fuente='WEB',
                    estado='NUEVO'
                )
            else:
                lead.nombre = name
                lead.telefono = phone
                lead.save()

            log_user_action(info, "CREATE_PAYMENT_PREFERENCE", f"Iniciado intento de pago de plan {plan.name} para lead: {name} (Email: {email})")

            # 3. Request preference from Mercado Pago
            token = os.getenv("MERCADOPAGO_ACCESS_TOKEN", "TEST-4651592514397603-071517-68bc59d1e7da5ac1c14335ee790d8a44-2375919242")
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            preference_data = {
                "items": [
                    {
                        "title": f"Plan {plan.name} - Détaché",
                        "quantity": 1,
                        "unit_price": float(plan.price),
                        "currency_id": "CLP"
                    }
                ],
                "payer": {
                    "name": name,
                    "email": email,
                    "phone": {
                        "number": phone.replace("+56", "")
                    }
                },
                "back_urls": {
                    "success": f"{back_url}/checkout/success",
                    "pending": f"{back_url}/checkout/pending",
                    "failure": f"{back_url}/checkout/failure"
                },
                "auto_return": "approved",
                "external_reference": f"lead_id:{lead.id}|plan_id:{plan.id}"
            }
            
            notification_url = info.context.build_absolute_uri('/api/mercadopago/webhook/')
            if "localhost" not in notification_url and "127.0.0.1" not in notification_url:
                preference_data["notification_url"] = notification_url
            
            response = requests.post(
                "https://api.mercadopago.com/checkout/preferences",
                headers=headers,
                json=preference_data,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                res_data = response.json()
                pref_id = res_data.get("id")
                # Use sandbox init point if sandbox token, otherwise live init point
                init_pt = res_data.get("sandbox_init_point") if "TEST" in token else res_data.get("init_point")
                if not init_pt:
                    init_pt = res_data.get("sandbox_init_point") or res_data.get("init_point")
                
                return CreatePaymentPreference(
                    success=True,
                    preference_id=pref_id,
                    init_point=init_pt
                )
            else:
                print(f"Mercado Pago API error: {response.status_code} - {response.text}")
                return CreatePaymentPreference(success=False, preference_id=None, init_point=None)
                
        except Exception as e:
            print(f"Error creating payment preference: {e}")
            return CreatePaymentPreference(success=False, preference_id=None, init_point=None)


class LoginUser(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)

    success = graphene.Boolean()
    token = graphene.String()
    user = graphene.Field(UserType)
    portal_type = graphene.String()
    error = graphene.String()

    def mutate(self, info, username, password):
        from django.contrib.auth import authenticate
        import django.core.signing as signing
        
        user = authenticate(username=username, password=password)
        if user is not None:
            if not user.is_active:
                return LoginUser(success=False, error="Cuenta inactiva.")
            
            # Generate the signed token
            token = signing.dumps({'user_id': user.id, 'username': user.username})
            
            # Detect portal type
            portal_type = 'ADMIN'
            if hasattr(user, 'student_profile'):
                try:
                    user.student_profile
                    portal_type = 'STUDENT'
                except:
                    pass
            if hasattr(user, 'teacher_profile'):
                try:
                    user.teacher_profile
                    portal_type = 'TEACHER'
                except:
                    pass
            if user.is_staff or user.is_superuser:
                portal_type = 'ADMIN'
            
            # Temporary context mock to log action under this user
            info.context.user = user
            log_user_action(info, "LOGIN", f"Inicio de sesión exitoso para usuario: {username} ({portal_type})")
            
            return LoginUser(success=True, token=token, user=user, portal_type=portal_type)
        else:
            # Audit failed login attempt
            log_user_action(info, "LOGIN_FAILED", f"Intento fallido de inicio de sesión para usuario: {username}")
            return LoginUser(success=False, error="Usuario o contraseña incorrectos.")


class CreateAdminAccount(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        email = graphene.String()
        role = graphene.String(required=True) # ADMIN, VENTAS, RECEPCION
        allowed_sections = graphene.List(graphene.String, required=True)

    success = graphene.Boolean()
    user = graphene.Field(UserType)
    error = graphene.String()

    def mutate(self, info, username, password, role, allowed_sections, email=None):
        if User.objects.filter(username=username).exists():
            return CreateAdminAccount(success=False, error="El nombre de usuario ya está registrado.")

        # Create user and profile
        user = User.objects.create_user(username=username, email=email or "", password=password, is_staff=True)
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.role = role
        profile.allowed_sections = allowed_sections
        profile.save()

        log_user_action(info, "CREATE_ADMIN", f"Creada cuenta administrativa: {username} con rol {role}")
        return CreateAdminAccount(success=True, user=user)


class UpdateAdminAccount(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        password = graphene.String()
        role = graphene.String()
        allowed_sections = graphene.List(graphene.String)

    success = graphene.Boolean()
    user = graphene.Field(UserType)
    error = graphene.String()

    def mutate(self, info, id, password=None, role=None, allowed_sections=None):
        try:
            user = User.objects.get(pk=id)
            profile, created = UserProfile.objects.get_or_create(user=user)
            
            if password:
                user.set_password(password)
                user.save()
            
            if role:
                profile.role = role
            
            if allowed_sections is not None:
                profile.allowed_sections = allowed_sections
                
            profile.save()

            log_user_action(info, "UPDATE_ADMIN", f"Actualizada cuenta administrativa: {user.username}")
            return UpdateAdminAccount(success=True, user=user)
        except User.DoesNotExist:
            return UpdateAdminAccount(success=False, error="Usuario no encontrado.")


class DeleteAdminAccount(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    success = graphene.Boolean()
    error = graphene.String()

    def mutate(self, info, id):
        try:
            user = User.objects.get(pk=id)
            if user.is_superuser and User.objects.filter(is_superuser=True).count() <= 1:
                return DeleteAdminAccount(success=False, error="No se puede eliminar el único Administrador Supremo del sistema.")

            username = user.username
            user.delete()
            log_user_action(info, "DELETE_ADMIN", f"Eliminada cuenta administrativa: {username}")
            return DeleteAdminAccount(success=True)
        except User.DoesNotExist:
            return DeleteAdminAccount(success=False, error="Usuario no encontrado.")
        except Exception as e:
            return DeleteAdminAccount(success=False, error=f"Error al eliminar usuario: {str(e)}")


class CreateStudentAccount(graphene.Mutation):
    class Arguments:
        student_id = graphene.Int(required=True)
        password = graphene.String(required=True)

    success = graphene.Boolean()
    error = graphene.String()

    def mutate(self, info, student_id, password):
        try:
            student = Student.objects.get(pk=student_id)
        except Student.DoesNotExist:
            return CreateStudentAccount(success=False, error="Alumno no encontrado.")
        if student.user:
            return CreateStudentAccount(success=False, error="Este alumno ya tiene una cuenta de portal.")
        username = student.rut or student.email or f"alumno_{student.id}"
        username = username.strip().lower().replace(' ', '_')
        if User.objects.filter(username=username).exists():
            return CreateStudentAccount(success=False, error=f"El username '{username}' ya existe. Verifica el RUT o correo del alumno.")
        user = User.objects.create_user(username=username, password=password, email=student.email or '')
        student.user = user
        student.save()
        log_user_action(info, "CREATE_STUDENT_ACCOUNT", f"Cuenta de portal creada para alumno: {student.name} (username: {username})")
        return CreateStudentAccount(success=True)


class CreateTeacherAccount(graphene.Mutation):
    class Arguments:
        teacher_id = graphene.Int(required=True)
        password = graphene.String(required=True)

    success = graphene.Boolean()
    error = graphene.String()

    def mutate(self, info, teacher_id, password):
        try:
            teacher = Teacher.objects.get(pk=teacher_id)
        except Teacher.DoesNotExist:
            return CreateTeacherAccount(success=False, error="Profesor no encontrado.")
        if teacher.user:
            return CreateTeacherAccount(success=False, error="Este profesor ya tiene una cuenta de portal.")
        username = teacher.rut or teacher.email or f"profesor_{teacher.id}"
        username = username.strip().lower().replace(' ', '_')
        if User.objects.filter(username=username).exists():
            return CreateTeacherAccount(success=False, error=f"El username '{username}' ya existe. Verifica el RUT o correo del profesor.")
        user = User.objects.create_user(username=username, password=password, email=teacher.email or '')
        teacher.user = user
        teacher.save()
        log_user_action(info, "CREATE_TEACHER_ACCOUNT", f"Cuenta de portal creada para profesor: {teacher.name} (username: {username})")
        return CreateTeacherAccount(success=True)


class ResetPortalPassword(graphene.Mutation):
    class Arguments:
        user_id = graphene.Int(required=True)
        new_password = graphene.String(required=True)

    success = graphene.Boolean()
    error = graphene.String()

    def mutate(self, info, user_id, new_password):
        try:
            target_user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return ResetPortalPassword(success=False, error="Usuario no encontrado.")
        target_user.set_password(new_password)
        target_user.save()
        log_user_action(info, "RESET_PORTAL_PASSWORD", f"Contraseña reseteada para usuario: {target_user.username}")
        return ResetPortalPassword(success=True)


class ChangeMyPassword(graphene.Mutation):
    class Arguments:
        current_password = graphene.String(required=True)
        new_password = graphene.String(required=True)

    success = graphene.Boolean()
    error = graphene.String()

    def mutate(self, info, current_password, new_password):
        user = getattr(info.context, 'user', None)
        if not user or not user.is_authenticated:
            return ChangeMyPassword(success=False, error="No autenticado.")
        if not user.check_password(current_password):
            return ChangeMyPassword(success=False, error="La contraseña actual es incorrecta.")
        user.set_password(new_password)
        user.save()
        log_user_action(info, "CHANGE_PASSWORD", f"El usuario {user.username} cambió su contraseña.")
        return ChangeMyPassword(success=True)


class CreateHoliday(graphene.Mutation):
    class Arguments:
        date = graphene.Date(required=True)
        name = graphene.String(required=True)
        is_active = graphene.Boolean(default_value=True)

    holiday = graphene.Field(HolidayType)
    success = graphene.Boolean()
    error = graphene.String()

    def mutate(self, info, date, name, is_active=True):
        existing = Holiday.objects.filter(date=date).first()
        if existing:
            existing.name = name
            existing.is_active = is_active
            existing.save()
            log_user_action(info, "UPDATE_HOLIDAY", f"Feriado actualizado para fecha {date}: {name}")
            return CreateHoliday(holiday=existing, success=True)
        holiday = Holiday.objects.create(
            date=date,
            name=name,
            is_active=is_active,
            is_custom=True
        )
        log_user_action(info, "CREATE_HOLIDAY", f"Feriado creado para fecha {date}: {name}")
        return CreateHoliday(holiday=holiday, success=True)


class UpdateHoliday(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        name = graphene.String()
        date = graphene.Date()
        is_active = graphene.Boolean()

    holiday = graphene.Field(HolidayType)
    success = graphene.Boolean()
    error = graphene.String()

    def mutate(self, info, id, name=None, date=None, is_active=None):
        holiday = Holiday.objects.filter(pk=id).first()
        if not holiday:
            return UpdateHoliday(holiday=None, success=False, error="Feriado no encontrado.")
        if name is not None:
            holiday.name = name
        if date is not None:
            holiday.date = date
        if is_active is not None:
            holiday.is_active = is_active
        holiday.save()
        log_user_action(info, "UPDATE_HOLIDAY", f"Feriado {holiday.id} actualizado.")
        return UpdateHoliday(holiday=holiday, success=True)


class ToggleHoliday(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        is_active = graphene.Boolean()

    holiday = graphene.Field(HolidayType)
    success = graphene.Boolean()

    def mutate(self, info, id, is_active=None):
        holiday = Holiday.objects.filter(pk=id).first()
        if not holiday:
            return ToggleHoliday(holiday=None, success=False)
        if is_active is not None:
            holiday.is_active = is_active
        else:
            holiday.is_active = not holiday.is_active
        holiday.save()
        log_user_action(info, "TOGGLE_HOLIDAY", f"Feriado {holiday.name} ({holiday.date}) {'activado' if holiday.is_active else 'desactivado'}")
        return ToggleHoliday(holiday=holiday, success=True)


class DeleteHoliday(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    success = graphene.Boolean()

    def mutate(self, info, id):
        Holiday.objects.filter(pk=id).delete()
        log_user_action(info, "DELETE_HOLIDAY", f"Feriado ID {id} eliminado.")
        return DeleteHoliday(success=True)


class SeedDefaultHolidays(graphene.Mutation):
    class Arguments:
        years = graphene.List(graphene.Int)

    count = graphene.Int()
    success = graphene.Boolean()

    def mutate(self, info, years=None):
        count = Holiday.seed_default_chilean_holidays(target_years=years)
        log_user_action(info, "SEED_HOLIDAYS", f"Se cargaron {count} feriados chilenos por defecto.")
        return SeedDefaultHolidays(count=count, success=True)


class Mutation(graphene.ObjectType):
    create_announcement = CreateAnnouncement.Field()
    update_announcement = UpdateAnnouncement.Field()
    delete_announcement = DeleteAnnouncement.Field()
    create_pre_reservation = CreatePreReservation.Field()
    create_lesson = CreateLesson.Field()
    create_student = CreateStudent.Field()
    create_teacher = CreateTeacher.Field()
    create_availability = CreateAvailability.Field()
    update_availability = UpdateAvailability.Field()
    delete_availability = DeleteAvailability.Field()
    send_whatsapp = SendWhatsApp.Field()
    send_whatsapp_buttons = SendWhatsAppButtons.Field()
    create_lead = CreateLead.Field()
    convert_lead_to_student = ConvertLeadToStudent.Field()
    register_payment = RegisterPayment.Field()
    update_lesson_status = UpdateLessonStatus.Field()
    update_lead_status = UpdateLeadStatus.Field()
    confirm_lead_reservation_with_lesson = ConfirmLeadReservationWithLesson.Field()
    create_lead_note = CreateLeadNote.Field()
    delete_lead = DeleteLead.Field()
    update_plan = UpdatePlan.Field()
    delete_plan = DeletePlan.Field()
    update_teacher = UpdateTeacher.Field()
    delete_teacher = DeleteTeacher.Field()
    create_class_type = CreateClassType.Field()
    update_class_type = UpdateClassType.Field()
    delete_class_type = DeleteClassType.Field()
    create_academy_task = CreateAcademyTask.Field()
    update_academy_task = UpdateAcademyTask.Field()
    delete_academy_task = DeleteAcademyTask.Field()
    create_instrument = CreateInstrument.Field()
    update_instrument = UpdateInstrument.Field()
    delete_instrument = DeleteInstrument.Field()
    create_student_pack = CreateStudentPack.Field()
    manual_deduct_class = ManualDeductClass.Field()
    create_material = CreateMaterial.Field()
    create_student_private_note = CreateStudentPrivateNote.Field()
    create_student_wall_message = CreateStudentWallMessage.Field()
    create_plan = CreatePlan.Field()
    update_landing_page = UpdateLandingPage.Field()
    clone_landing_page = CloneLandingPage.Field()
    update_homepage_content = UpdateHomepageContent.Field()
    update_about_content = UpdateAboutContent.Field()
    update_contact_content = UpdateContactContent.Field()
    create_room = CreateRoom.Field()
    update_room = UpdateRoom.Field()
    delete_room = DeleteRoom.Field()
    update_student = UpdateStudent.Field()
    update_global_settings = UpdateGlobalSettings.Field()
    create_payment_preference = CreatePaymentPreference.Field()
    login_user = LoginUser.Field()
    create_admin_account = CreateAdminAccount.Field()
    update_admin_account = UpdateAdminAccount.Field()
    delete_admin_account = DeleteAdminAccount.Field()
    create_student_account = CreateStudentAccount.Field()
    create_teacher_account = CreateTeacherAccount.Field()
    reset_portal_password = ResetPortalPassword.Field()
    change_my_password = ChangeMyPassword.Field()
    create_holiday = CreateHoliday.Field()
    update_holiday = UpdateHoliday.Field()
    toggle_holiday = ToggleHoliday.Field()
    delete_holiday = DeleteHoliday.Field()
    seed_default_holidays = SeedDefaultHolidays.Field()


import channels_graphql_ws

class OnLeadUpdated(channels_graphql_ws.Subscription):
    lead = graphene.Field(LeadType)
    event_type = graphene.String()

    class Arguments:
        pass

    def subscribe(self, info):
        # All clients subscribe to 'leads_group'
        return ["leads_group"]

    def publish(self, info):
        lead_id = self.get("lead_id")
        event_type = self.get("event_type")
        from api.models import Lead
        try:
            lead = Lead.objects.get(pk=lead_id)
        except Lead.DoesNotExist:
            lead = None
        return OnLeadUpdated(lead=lead, event_type=event_type)

class Subscription(graphene.ObjectType):
    on_lead_updated = OnLeadUpdated.Field()

