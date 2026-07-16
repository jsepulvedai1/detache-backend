import graphene
from django.utils import timezone
from graphene_django import DjangoObjectType
from .models import Teacher, Specialty, Availability, Plan, Student, Instrument, Room, Lesson, Lead, LeadNote, StudentPack, Payment, AcademyTask, Material, StudentPrivateNote, StudentWallMessage, LandingPage, HomepageContent, ClassType, AboutContent, ContactContent, GlobalSettings

# --- Object Types ---

class TeacherType(DjangoObjectType):
    class Meta:
        model = Teacher
        fields = ("id", "name", "description", "photo", "status", "specialties", "availabilities", "phone_number", "rut", "address", "email")

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
    class Meta:
        model = Student
        fields = ("id", "name", "photo", "status", "phone_number", "rut", "birth_date", "guardian_name", "guardian_phone", "level", "start_date", "primary_instrument", "private_notes", "wall_messages", "packs")

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
    class Meta:
        model = Lead
        fields = ("id", "nombre", "telefono", "email", "edad", "servicio", "fuente", "estado", "asignado_a", "fecha_ingreso", "fecha_ultimo_contacto", "notas")

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
        fields = ("id", "title", "description", "assigned_to", "priority", "log", "is_completed", "created_at", "updated_at")

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
            "facebook_url", "instagram_url", "trial_class_email_template"
        )

# --- Queries ---

class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Hello, this is the Detache backend with GraphQL!")
    
    global_settings = graphene.Field(GlobalSettingsType)
    
    # Teachers
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

    def resolve_hello(self, info):
        return "Hello, this is the Detache backend with GraphQL!"

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
        return Lead.objects.all()
        
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

    def resolve_all_class_types(self, info):
        return ClassType.objects.all()

    def resolve_class_type_by_id(self, info, id):
        return ClassType.objects.filter(pk=id).first()

# --- Mutations ---

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

    teacher = graphene.Field(TeacherType)
    def mutate(self, info, name, description="", status="ACTIVE", phone_number=None, rut=None, address=None, email=None, specialty_ids=None):
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
        return CreateTeacher(teacher=teacher)

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
        rut = graphene.String()
        birth_date = graphene.Date()
        guardian_name = graphene.String()
        guardian_phone = graphene.String()
        status = graphene.String()
        phone_number = graphene.String()
        level = graphene.String()
        primary_instrument_id = graphene.Int()

    student = graphene.Field(StudentType)

    def mutate(self, info, name, rut=None, birth_date=None, guardian_name=None, guardian_phone=None, status="ACTIVE", phone_number=None, level="BEGINNER", primary_instrument_id=None):
        primary_instrument = Instrument.objects.filter(pk=primary_instrument_id).first() if primary_instrument_id else None
        student = Student.objects.create(
            name=name,
            rut=rut,
            birth_date=birth_date,
            guardian_name=guardian_name,
            guardian_phone=guardian_phone,
            status=status,
            phone_number=phone_number,
            level=level,
            primary_instrument=primary_instrument
        )
        return CreateStudent(student=student)

class UpdateStudent(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        name = graphene.String()
        rut = graphene.String()
        birth_date = graphene.Date()
        guardian_name = graphene.String()
        guardian_phone = graphene.String()
        status = graphene.String()
        phone_number = graphene.String()
        level = graphene.String()
        primary_instrument_id = graphene.Int()

    student = graphene.Field(StudentType)

    def mutate(self, info, id, name=None, rut=None, birth_date=None, guardian_name=None, guardian_phone=None, status=None, phone_number=None, level=None, primary_instrument_id=None):
        try:
            student = Student.objects.get(pk=id)
            if name is not None: student.name = name
            if rut is not None: student.rut = rut
            if birth_date is not None: student.birth_date = birth_date
            if guardian_name is not None: student.guardian_name = guardian_name
            if guardian_phone is not None: student.guardian_phone = guardian_phone
            if status is not None: student.status = status
            if phone_number is not None: student.phone_number = phone_number
            if level is not None: student.level = level
            if primary_instrument_id is not None:
                student.primary_instrument = Instrument.objects.filter(pk=primary_instrument_id).first()
            student.save()
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

    global_settings = graphene.Field(GlobalSettingsType)

    def mutate(self, info, phone_number=None, email_contact=None, address=None, opening_hours_weekdays=None, opening_hours_saturdays=None, facebook_url=None, instagram_url=None, trial_class_email_template=None):
        settings = GlobalSettings.get_singleton()
        if phone_number is not None: settings.phone_number = phone_number
        if email_contact is not None: settings.email_contact = email_contact
        if address is not None: settings.address = address
        if opening_hours_weekdays is not None: settings.opening_hours_weekdays = opening_hours_weekdays
        if opening_hours_saturdays is not None: settings.opening_hours_saturdays = opening_hours_saturdays
        if facebook_url is not None: settings.facebook_url = facebook_url
        if instagram_url is not None: settings.instagram_url = instagram_url
        if trial_class_email_template is not None: settings.trial_class_email_template = trial_class_email_template
        settings.save()
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

        try:
            OnLeadUpdated.broadcast(group="leads_group", payload={"lead_id": lead.id, "event_type": "created"})
        except Exception as ws_err:
            print(f"Error broadcasting new lead: {ws_err}")
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
                phone_number=lead.telefono,
                status='ACTIVE'
            )
            
            Lesson.objects.filter(lead=lead).update(student=student, is_pre_reservation=False)
            
            lead.estado = 'CONCRETADO'
            lead.save()
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

        payment = Payment.objects.create(
            student=student,
            amount=amount,
            method=method,
            description=description,
            pack=pack
        )
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

            # Auto-deduct class if status changed to COMPLETED
            if old_status != 'COMPLETED' and status == 'COMPLETED':
                active_pack = StudentPack.objects.filter(
                    student=lesson.student,
                    is_active=True,
                    remaining_classes__gt=0
                ).order_by('expiration_date').first()
                if active_pack:
                    active_pack.remaining_classes -= 1
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
            try:
                OnLeadUpdated.broadcast(group="leads_group", payload={"lead_id": lead.id, "event_type": "updated"})
            except Exception as ws_err:
                print(f"Error broadcasting lead status update: {ws_err}")
            return UpdateLeadStatus(success=True, lead=lead)
        except Lead.DoesNotExist:
            return UpdateLeadStatus(success=False, lead=None)


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
        priority = graphene.String()
        log = graphene.String()

    task = graphene.Field(AcademyTaskType)

    def mutate(self, info, title, description="", assigned_to="RECEPCION", priority="RECORDATORIO", log=""):
        task = AcademyTask.objects.create(
            title=title,
            description=description,
            assigned_to=assigned_to,
            priority=priority,
            log=log
        )
        return CreateAcademyTask(task=task)

class UpdateAcademyTask(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        title = graphene.String()
        description = graphene.String()
        assigned_to = graphene.String()
        priority = graphene.String()
        log = graphene.String()
        is_completed = graphene.Boolean()

    task = graphene.Field(AcademyTaskType)

    def mutate(self, info, id, title=None, description=None, assigned_to=None, priority=None, log=None, is_completed=None):
        try:
            task = AcademyTask.objects.get(pk=id)
            if title is not None: task.title = title
            if description is not None: task.description = description
            if assigned_to is not None: task.assigned_to = assigned_to
            if priority is not None: task.priority = priority
            if log is not None: task.log = log
            if is_completed is not None: task.is_completed = is_completed
            task.save()
            return UpdateAcademyTask(task=task)
        except AcademyTask.DoesNotExist:
            return UpdateAcademyTask(task=None)

class DeleteAcademyTask(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    success = graphene.Boolean()

    def mutate(self, info, id):
        AcademyTask.objects.filter(pk=id).delete()
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
        author = graphene.String(required=True)

    note = graphene.Field(StudentPrivateNoteType)

    def mutate(self, info, student_id, text, author):
        student = Student.objects.get(pk=student_id)
        note = StudentPrivateNote.objects.create(student=student, text=text, author=author)
        return CreateStudentPrivateNote(note=note)

class CreateStudentWallMessage(graphene.Mutation):
    class Arguments:
        student_id = graphene.Int(required=True)
        text = graphene.String(required=True)
        author = graphene.String(required=True)
        attached_material_id = graphene.Int()

    message = graphene.Field(StudentWallMessageType)

    def mutate(self, info, student_id, text, author, attached_material_id=None):
        student = Student.objects.get(pk=student_id)
        material = Material.objects.filter(pk=attached_material_id).first() if attached_material_id else None
        message = StudentWallMessage.objects.create(
            student=student, 
            text=text, 
            author=author, 
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
        try:
            # 1. Fetch the plan
            plan = Plan.objects.get(pk=plan_id)
            
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


class Mutation(graphene.ObjectType):
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
    update_plan = UpdatePlan.Field()
    delete_plan = DeletePlan.Field()
    update_teacher = UpdateTeacher.Field()
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

