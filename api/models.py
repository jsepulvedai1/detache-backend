from django.db import models
from django.utils import timezone

# ─── CMS (WEB CONTENT) ───
class LandingPage(models.Model):
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=255)
    subtitle = models.TextField()
    problem = models.TextField()
    solution = models.TextField()
    benefits = models.JSONField(default=list)
    image_url = models.CharField(max_length=500, blank=True, null=True)
    cta = models.CharField(max_length=100)

    def __str__(self):
        return f"Landing: {self.title} ({self.slug})"


class HomepageContent(models.Model):
    """Singleton model – only one row ever exists (id=1)."""
    # Hero
    hero_image = models.CharField(max_length=500, default='/images/piano-hero.png')
    hero_title_1 = models.CharField(max_length=255, default='')
    hero_title_highlight = models.CharField(max_length=255, default='')
    hero_title_2 = models.CharField(max_length=255, default='')
    hero_subtitle = models.TextField(default='')
    hero_cta1_text = models.CharField(max_length=100, default='Solicitar Clase de Prueba')
    hero_cta1_link = models.CharField(max_length=200, default='/book')
    hero_cta2_text = models.CharField(max_length=100, default='Nuestros Maestros')
    hero_cta2_link = models.CharField(max_length=200, default='/teachers')

    # Features (3 cards)
    features = models.JSONField(default=list)

    # Methodology
    method_badge = models.CharField(max_length=100, default='Nuestro Método Técnico')
    method_title = models.TextField(default='No son clases sueltas, es un proceso de maestría')
    method_description = models.TextField(default='En Détaché, no creemos en el aprendizaje fragmentado.')
    method_items = models.JSONField(default=list)
    method_image = models.CharField(max_length=500, default='/images/method.png')

    # Testimonials
    testimonials = models.JSONField(default=list)

    # Location
    location_title = models.CharField(max_length=255, default='Estamos cerca de ti')
    location_description = models.TextField(default='Nuestra academia se encuentra en un punto estratégico.')
    location_address = models.CharField(max_length=255, default='Gran Avenida José Miguel Carrera 8520, Of. C, La Cisterna')
    location_address_detail = models.CharField(max_length=255, default='A pasos de Metro La Cisterna')
    location_map_url = models.CharField(max_length=500, default='https://maps.google.com')

    # Final CTA
    final_cta_title = models.CharField(max_length=255, default='¿Listo para empezar?')
    final_cta_description = models.TextField(default='Déjanos tus datos y te contactaremos para agendar tu primera experiencia.')
    final_cta_button_text = models.CharField(max_length=100, default='Solicitar Clase de Prueba')

    # Planes Section
    planes_title = models.CharField(max_length=255, default='Nuestros Planes')
    planes_description = models.TextField(default='Haz espacio para la música en tu vida y encuentra el programa perfecto para ti.')

    # Instruments Section
    instruments_title = models.CharField(max_length=255, default='Aprende con Nosotros')
    instruments_description = models.TextField(default='La música comienza con una primera nota. Nosotros te acompañamos en el resto del camino.')

    # Gallery Section
    gallery_title = models.CharField(max_length=255, default='LA MÚSICA COMO NUNCA TE LA HABÍAN EXPLICADO')
    gallery_images = models.JSONField(default=list)

    class Meta:
        verbose_name = "Contenido del Homepage"

    def __str__(self):
        return "Contenido del Homepage (singleton)"

    @classmethod
    def get_singleton(cls):
        obj, created = cls.objects.get_or_create(pk=1, defaults={
            'features': [
                {"icon": "Calendar", "title": "Reserva Flexible", "description": "Elige el horario que más te acomode. Reprograma fácilmente si surgen imprevistos."},
                {"icon": "UserCheck", "title": "Profesores Expertos", "description": "Aprende de músicos profesionales activos en la escena. Todos los niveles bienvenidos."},
                {"icon": "Music", "title": "Tu Ritmo, Tu Estilo", "description": "Clásico, Jazz, Pop o teoría musical. Adaptamos el contenido a tus objetivos."}
            ],
            'method_items': [
                {"title": "Evaluación Personalizada", "desc": "Entendemos tus metas antes de tocar la primera nota."},
                {"title": "Técnica Orgánica", "desc": "Desarrollo de postura y digitación sin tensiones."},
                {"title": "Repertorio Evolutivo", "desc": "Piezas seleccionadas para desafiarte en el punto justo."}
            ],
            'testimonials': [
                {"quote": "Increíble experiencia. El sistema de reservas es súper fácil y mi profesor es un genio.", "author": "Carolina R."},
                {"quote": "Nunca creí que aprendería tan rápido. La metodología es completamente diferente.", "author": "Matías V."},
                {"quote": "Lo mejor de Santiago para aprender piano. Instalaciones de primer nivel.", "author": "Sofía M."}
            ],
            'gallery_images': [
                "/imagesfooter/1.png",
                "/imagesfooter/2.png",
                "/imagesfooter/3.png",
                "/imagesfooter/4.png"
            ]
        })
        return obj

def normalize_phone(phone):
    if not phone:
        return phone
    cleaned = "".join(c for c in phone if c.isdigit())
    if cleaned.startswith("56") and len(cleaned) == 11:
        return cleaned
    if len(cleaned) == 9:
        return f"56{cleaned}"
    return cleaned

# ─── CRM (LEADS) ───

class Lead(models.Model):
    SERVICE_CHOICES = [
        ('PIANO_NINOS', 'Piano Niños'),
        ('PIANO_ADULTOS', 'Piano Adultos'),
        ('CANTO', 'Canto'),
        ('CLASE_GRUPAL', 'Clase Grupal'),
        ('CLASE_PRUEBA', 'Clase de Prueba'),
    ]
    SOURCE_CHOICES = [
        ('WEB', 'Web'),
        ('WHATSAPP', 'WhatsApp'),
        ('INSTAGRAM', 'Instagram'),
        ('REFERIDO', 'Referido'),
        ('GOOGLE', 'Google'),
        ('OTRO', 'Otro'),
    ]
    STATUS_CHOICES = [
        ('NUEVO', 'Nuevo Lead'),
        ('CONTACTADO', 'Contactado'),
        ('SEGUIMIENTO', 'Seguimiento'),
        ('PRE_RESERVA', 'Pre-reserva'),
        ('RESERVA_CONFIRMADA', 'Reserva Confirmada'),
        ('CONCRETADO', 'Concretado (Alumno)'),
        ('SIN_RESPUESTA', 'Sin Respuesta'),
        ('LISTA_ESPERA', 'Lista de Espera'),
        ('NO_CONCRETADO', 'No Concretado'),
    ]

    nombre = models.CharField(max_length=255)
    telefono = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    edad = models.PositiveIntegerField(blank=True, null=True)
    servicio = models.CharField(max_length=50, choices=SERVICE_CHOICES, default='CLASE_PRUEBA')
    fuente = models.CharField(max_length=50, choices=SOURCE_CHOICES, default='WEB')
    estado = models.CharField(max_length=50, choices=STATUS_CHOICES, default='NUEVO')
    asignado_a = models.CharField(max_length=100, blank=True, null=True, default='Recepción')
    fecha_ingreso = models.DateTimeField(auto_now_add=True)
    fecha_ultimo_contacto = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nombre} - {self.estado}"

    def save(self, *args, **kwargs):
        self.telefono = normalize_phone(self.telefono)
        super().save(*args, **kwargs)

class LeadNote(models.Model):
    lead = models.ForeignKey(Lead, related_name='notas', on_delete=models.CASCADE)
    texto = models.TextField()
    autor = models.CharField(max_length=100, default='Sistema')
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Nota para {self.lead.nombre} por {self.autor}"

# ─── ACADEMY CORE ───

class Specialty(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Specialties"

class Teacher(models.Model):
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
    ]
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    photo = models.ImageField(upload_to='teachers/', blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ACTIVE')
    specialties = models.ManyToManyField(Specialty, related_name='teachers', blank=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.phone_number:
            self.phone_number = normalize_phone(self.phone_number)
        super().save(*args, **kwargs)

class Availability(models.Model):
    DAYS_CHOICES = [
        ('MONDAY', 'Monday'),
        ('TUESDAY', 'Tuesday'),
        ('WEDNESDAY', 'Wednesday'),
        ('THURSDAY', 'Thursday'),
        ('FRIDAY', 'Friday'),
        ('SATURDAY', 'Saturday'),
        ('SUNDAY', 'Sunday'),
    ]
    day = models.CharField(max_length=10, choices=DAYS_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    teacher = models.ForeignKey(Teacher, related_name='availabilities', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.day} {self.start_time}-{self.end_time} ({self.teacher.name})"

class Student(models.Model):
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
    ]
    LEVEL_CHOICES = [
        ('BEGINNER', 'Beginner'),
        ('INTERMEDIATE', 'Intermediate'),
        ('ADVANCED', 'Advanced'),
    ]
    name = models.CharField(max_length=255)
    rut = models.CharField(max_length=20, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    guardian_name = models.CharField(max_length=255, blank=True, null=True)
    guardian_phone = models.CharField(max_length=20, blank=True, null=True)
    
    photo = models.ImageField(upload_to='students/', blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ACTIVE')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    
    level = models.CharField(max_length=50, choices=LEVEL_CHOICES, default='BEGINNER')
    start_date = models.DateField(default=timezone.now)
    # The instrument they are currently studying
    primary_instrument = models.ForeignKey('Instrument', related_name='students', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.phone_number:
            self.phone_number = normalize_phone(self.phone_number)
        if self.guardian_phone:
            self.guardian_phone = normalize_phone(self.guardian_phone)
        super().save(*args, **kwargs)

class Instrument(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Room(models.Model):
    STATUS_CHOICES = [
        ('AVAILABLE', 'Available'),
        ('OCCUPIED', 'Occupied'),
        ('MAINTENANCE', 'Maintenance'),
    ]
    name = models.CharField(max_length=255)
    capacity = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AVAILABLE')
    instruments = models.ManyToManyField(Instrument, related_name='rooms', blank=True)

    def __str__(self):
        return self.name

class Lesson(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    TYPE_CHOICES = [
        ('INDIVIDUAL', 'Individual'),
        ('MASTERCLASS', 'Masterclass'),
        ('THEORY', 'Theory'),
        ('ENSEMBLE', 'Ensemble'),
    ]
    teacher = models.ForeignKey(Teacher, related_name='lessons', on_delete=models.CASCADE)
    student = models.ForeignKey(Student, related_name='lessons', on_delete=models.CASCADE)
    room = models.ForeignKey(Room, related_name='lessons', on_delete=models.SET_NULL, null=True)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING')
    lesson_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='INDIVIDUAL')
    
    # Soporte para pre-reservas
    is_pre_reservation = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.lesson_type} - {self.student.name} with {self.teacher.name} on {self.date}"

# ─── BILLING & PACKS ───
class Plan(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.PositiveIntegerField(help_text="Duration in months")
    classes_count = models.PositiveIntegerField(default=4, help_text="Number of classes included in this pack (e.g., 4, 12, 24)")
    is_featured = models.BooleanField(default=False, help_text="Mark as recommended plan on landing page")
    benefits = models.JSONField(default=list, blank=True)

    def __str__(self):
        return self.name

class StudentPack(models.Model):
    student = models.ForeignKey(Student, related_name='packs', on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.RESTRICT)
    total_classes = models.PositiveIntegerField()
    remaining_classes = models.PositiveIntegerField()
    purchase_date = models.DateField(default=timezone.now)
    expiration_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.pk: # Only on creation
            self.total_classes = self.plan.classes_count
            self.remaining_classes = self.plan.classes_count
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.plan.name} for {self.student.name} ({self.remaining_classes} left)"

class Payment(models.Model):
    METHOD_CHOICES = [
        ('TRANSFER', 'Transferencia'),
        ('CASH', 'Efectivo'),
        ('CARD', 'Tarjeta'),
    ]
    student = models.ForeignKey(Student, related_name='payments', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(default=timezone.now)
    method = models.CharField(max_length=50, choices=METHOD_CHOICES, default='TRANSFER')
    description = models.TextField(blank=True, null=True)
    # Optional link to a specific pack
    pack = models.ForeignKey(StudentPack, related_name='payments', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"${self.amount} by {self.student.name} on {self.payment_date}"

class AcademyTask(models.Model):
    PRIORITY_CHOICES = [
        ('URGENTE', 'Urgente'),
        ('IMPORTANTE', 'Importante'),
        ('RECORDATORIO', 'Recordatorio'),
        ('INFORMATIVO', 'Informativo'),
    ]
    ROLE_CHOICES = [
        ('VENTAS', 'Ventas'),
        ('RECEPCION', 'Recepción'),
        ('ADMINISTRACION', 'Administración'),
    ]
    
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    assigned_to = models.CharField(max_length=50, choices=ROLE_CHOICES, default='RECEPCION')
    priority = models.CharField(max_length=50, choices=PRIORITY_CHOICES, default='RECORDATORIO')
    log = models.TextField(blank=True, null=True, help_text="Bitácora de acciones")
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['is_completed', '-created_at']

    def __str__(self):
        return f"[{self.priority}] {self.title}"

# ─── ACADEMY RESOURCES & STUDENT PORTAL ───

class Material(models.Model):
    TYPE_CHOICES = [
        ('PDF', 'PDF / Documento'),
        ('VIDEO', 'Video YouTube'),
        ('AUDIO', 'Audio'),
        ('LINK', 'Enlace Web'),
    ]
    title = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='PDF')
    url = models.URLField(max_length=500)
    teacher = models.ForeignKey(Teacher, related_name='materials', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.type}] {self.title}"

class StudentPrivateNote(models.Model):
    student = models.ForeignKey(Student, related_name='private_notes', on_delete=models.CASCADE)
    text = models.TextField()
    author = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Private Note for {self.student.name} by {self.author}"

class StudentWallMessage(models.Model):
    student = models.ForeignKey(Student, related_name='wall_messages', on_delete=models.CASCADE)
    text = models.TextField()
    author = models.CharField(max_length=100)
    attached_material = models.ForeignKey(Material, related_name='wall_messages', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Wall Message for {self.student.name} by {self.author}"


class ClassType(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    duration_minutes = models.IntegerField(default=45)
    price = models.IntegerField(default=0)
    currency = models.CharField(max_length=10, default='CLP')
    allowed_levels = models.JSONField(default=list)  # e.g. ["BEGINNER"]
    allowed_modalities = models.JSONField(default=list)  # e.g. ["ONLINE", "IN_PERSON"]
    what_you_will_learn = models.JSONField(default=list)  # e.g. ["Técnica", "Lectura"]
    teachers = models.ManyToManyField(Teacher, blank=True, related_name='class_types')

    def __str__(self):
        return self.name


class AboutContent(models.Model):
    """Singleton model – only one row ever exists (id=1)."""
    # Hero
    hero_image = models.CharField(max_length=500, default='/imagesfooter/4.png')
    hero_title_highlight_1 = models.CharField(max_length=255, default='Aprender')
    hero_title_text_1 = models.CharField(max_length=255, default='música debe ser una experiencia')
    hero_title_highlight_2 = models.CharField(max_length=255, default='clara y motivadora.')

    # Historia
    history_image = models.CharField(max_length=500, default='/imagesfooter/2.png')
    history_title = models.CharField(max_length=255, default='Nuestra Historia')
    history_subtitle = models.TextField(default='Academia Detaché nació para transformar la frustración de aprender música en un camino claro y disfrutable.')
    history_description = models.TextField(default='Cansados de la improvisación, creamos en el sector sur de Santiago un método estructurado, cercano y apasionado que garantiza un avance real, poniendo siempre el progreso y el bienestar del alumno en el centro de nuestra historia.')

    # Lo que nos mueve
    moving_title = models.CharField(max_length=255, default='Lo que nos Mueve')
    moving_description = models.TextField(default='Nuestra forma de enseñar nace del amor por la música y del compromiso con cada estudiante.')
    moving_cards = models.JSONField(default=list)

    # Equipo
    team_title = models.CharField(max_length=255, default='Nuestro Equipo')
    team_description = models.TextField(default='Detrás de cada clase hay personas que disfrutan enseñar y compartir su pasión por la música.')
    team_images = models.JSONField(default=list)

    # CTA Final
    final_title_1 = models.CharField(max_length=255, default='Conoce una')
    final_title_2 = models.CharField(max_length=255, default='nueva forma')
    final_title_3 = models.CharField(max_length=255, default='de aprender')
    final_image = models.CharField(max_length=500, default='/nosotros/4.png')

    class Meta:
        verbose_name = "Contenido de Nosotros"

    def __str__(self):
        return "Contenido de Nosotros (singleton)"

    @classmethod
    def get_singleton(cls):
        obj, created = cls.objects.get_or_create(pk=1, defaults={
            'moving_cards': [
                {"title": "La música y las personas primero", "description": "Valoramos a cada alumno y respetamos sus objetivos, intereses y ritmo de aprendizaje."},
                {"title": "Enseñanza cercana y apasionada", "description": "Nuestro equipo está comprometido con brindarte una experiencia de aprendizaje cálida y motivadora."},
                {"title": "Aprender con dirección", "description": "Contamos con un método claro y estructurado para asegurar tu progreso paso a paso."},
                {"title": "Disfrutar el proceso", "description": "Hacemos que cada etapa del aprendizaje sea una experiencia positiva y enriquecedora."}
            ],
            'team_images': [
                "/nosotros/1.png",
                "/nosotros/2.png",
                "/nosotros/3.png"
            ]
        })
        return obj


class ContactContent(models.Model):
    """Singleton model – only one row ever exists (id=1)."""
    # Mid-page Banner
    banner_title_1 = models.CharField(max_length=255, default='Sigamos')
    banner_title_2 = models.CharField(max_length=255, default='compartiendo')
    banner_title_3 = models.CharField(max_length=255, default='el lenguaje de')
    banner_title_4 = models.CharField(max_length=255, default='la música')

    # Ubicación e Info
    location_title = models.CharField(max_length=255, default='Estamos cerca de ti')
    location_description = models.TextField(default='Nuestra academia se encuentra en una ubicación estratégica y de fácil acceso, para que llegar a tus clases sea cómodo y sencillo.')
    location_address_title = models.CharField(max_length=255, default='Dirección Sede')
    location_address = models.TextField(default='Gran Avenida José Miguel Carrera 8520, Oficina C, La Cisterna.')
    location_map_iframe_url = models.TextField(default='https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3326.2307849187313!2d-70.6622543!3d-33.5217965!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x9662dae3cbf5df1f%3A0xe54fb7a71fbd4fdf!2sGran%20Av.%20Jos%C3%A9%20Miguel%20Carrera%208520%2C%20La%20Cisterna%2C%20Regi%C3%B3n%20Metropolitana!5e0!3m2!1ses-419!2scl!4v1700000000000!5m2!1ses-419!2scl')

    class Meta:
        verbose_name = "Contenido de Contacto"

    def __str__(self):
        return "Contenido de Contacto (singleton)"

    @classmethod
    def get_singleton(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

