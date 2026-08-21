from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Teacher, Specialty, Availability, Plan, Student, Instrument, Room, Lesson,
    Lead, LeadNote, StudentPack, Payment, AcademyTask, LandingPage, HomepageContent,
    ClassType, AboutContent, ContactContent, GlobalSettings, UserProfile, AuditLog,
    ChatMessage, Announcement, Material, StudentPrivateNote, StudentWallMessage, Holiday
)

# ─── INLINES ──────────────────────────────────────────────────

class LeadNoteInline(admin.TabularInline):
    model = LeadNote
    extra = 1
    readonly_fields = ('fecha',)

class StudentPrivateNoteInline(admin.TabularInline):
    model = StudentPrivateNote
    extra = 1
    readonly_fields = ('created_at',)

class StudentWallMessageInline(admin.TabularInline):
    model = StudentWallMessage
    extra = 1
    readonly_fields = ('created_at',)

class StudentPackInline(admin.TabularInline):
    model = StudentPack
    extra = 0
    fields = ('plan', 'total_classes', 'remaining_classes', 'is_active', 'purchase_date', 'expiration_date')

class AvailabilityInline(admin.TabularInline):
    model = Availability
    extra = 1

class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ('payment_date',)

# ─── MODEL ADMINS ─────────────────────────────────────────────

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'telefono', 'email', 'servicio', 'fuente', 'estado', 'asignado_a', 'fecha_ingreso', 'fecha_ultimo_contacto')
    list_filter = ('estado', 'servicio', 'fuente')
    search_fields = ('nombre', 'telefono', 'email', 'asignado_a')
    inlines = [LeadNoteInline]
    date_hierarchy = 'fecha_ingreso'
    ordering = ('-fecha_ingreso',)

@admin.register(LeadNote)
class LeadNoteAdmin(admin.ModelAdmin):
    list_display = ('lead', 'autor', 'texto_preview', 'fecha')
    list_filter = ('autor', 'fecha')
    search_fields = ('lead__nombre', 'texto', 'autor')
    date_hierarchy = 'fecha'
    ordering = ('-fecha',)

    def texto_preview(self, obj):
        return obj.texto[:60] + ('...' if len(obj.texto) > 60 else '')
    texto_preview.short_description = 'Nota'

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'rut', 'email', 'phone_number', 'status', 'level', 'primary_instrument', 'start_date', 'has_user')
    list_filter = ('status', 'level', 'primary_instrument')
    search_fields = ('name', 'rut', 'email', 'phone_number', 'guardian_name')
    filter_horizontal = ('assigned_teachers',)
    inlines = [StudentPackInline, StudentPrivateNoteInline, StudentWallMessageInline, PaymentInline]
    date_hierarchy = 'start_date'
    ordering = ('name',)

    def has_user(self, obj):
        return bool(obj.user)
    has_user.boolean = True
    has_user.short_description = 'Cuenta Portal'

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('name', 'rut', 'email', 'phone_number', 'status', 'has_user')
    search_fields = ('name', 'rut', 'email', 'phone_number')
    list_filter = ('status', 'specialties')
    filter_horizontal = ('specialties',)
    inlines = [AvailabilityInline]
    ordering = ('name',)

    def has_user(self, obj):
        return bool(obj.user)
    has_user.boolean = True
    has_user.short_description = 'Cuenta Portal'

@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Availability)
class AvailabilityAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'day', 'start_time', 'end_time')
    list_filter = ('day', 'teacher')
    ordering = ('teacher', 'day', 'start_time')

@admin.register(Instrument)
class InstrumentAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'capacity', 'status')
    list_filter = ('status',)
    filter_horizontal = ('instruments',)
    search_fields = ('name',)

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('id', 'lesson_type', 'student', 'lead', 'teacher', 'room', 'date', 'start_time', 'end_time', 'status', 'is_pre_reservation')
    list_filter = ('status', 'lesson_type', 'is_pre_reservation', 'date', 'teacher', 'room')
    search_fields = ('student__name', 'lead__nombre', 'teacher__name')
    date_hierarchy = 'date'
    ordering = ('-date', '-start_time')

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'classes_count', 'duration', 'is_featured')
    list_filter = ('is_featured',)
    search_fields = ('name',)

@admin.register(StudentPack)
class StudentPackAdmin(admin.ModelAdmin):
    list_display = ('student', 'plan', 'total_classes', 'remaining_classes', 'is_active', 'purchase_date', 'expiration_date')
    list_filter = ('is_active', 'plan')
    search_fields = ('student__name', 'plan__name')
    date_hierarchy = 'purchase_date'
    ordering = ('-purchase_date',)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('student', 'amount', 'method', 'payment_date', 'pack')
    list_filter = ('method', 'payment_date')
    search_fields = ('student__name', 'description')
    date_hierarchy = 'payment_date'
    ordering = ('-payment_date',)

@admin.register(AcademyTask)
class AcademyTaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'assigned_to', 'priority', 'is_completed', 'completed_at', 'created_at')
    list_filter = ('assigned_to', 'priority', 'is_completed')
    search_fields = ('title', 'description', 'assigned_to')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('title', 'scope', 'type', 'instrument', 'level', 'teacher', 'url', 'created_at')
    list_filter = ('scope', 'type', 'instrument', 'teacher', 'created_at')
    search_fields = ('title', 'description', 'teacher__name')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    actions = ['make_detache_official', 'make_teacher_scope']

    def make_detache_official(self, request, queryset):
        queryset.update(scope='DETACHE')
        self.message_user(request, "Materiales marcados como Oficial Détaché ✅")
    make_detache_official.short_description = "Convertir a Material Oficial Détaché"

    def make_teacher_scope(self, request, queryset):
        queryset.update(scope='TEACHER')
        self.message_user(request, "Materiales marcados como ámbito Profesor")
    make_teacher_scope.short_description = "Marcar como Material de Profesor"

@admin.register(StudentPrivateNote)
class StudentPrivateNoteAdmin(admin.ModelAdmin):
    list_display = ('student', 'author', 'text_preview', 'created_at')
    list_filter = ('author', 'created_at')
    search_fields = ('student__name', 'text', 'author')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

    def text_preview(self, obj):
        return obj.text[:60] + ('...' if len(obj.text) > 60 else '')
    text_preview.short_description = 'Nota Privada'

@admin.register(StudentWallMessage)
class StudentWallMessageAdmin(admin.ModelAdmin):
    list_display = ('student', 'author', 'text_preview', 'attached_material', 'created_at')
    list_filter = ('author', 'created_at')
    search_fields = ('student__name', 'text', 'author')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

    def text_preview(self, obj):
        return obj.text[:60] + ('...' if len(obj.text) > 60 else '')
    text_preview.short_description = 'Mensaje en Muro'

@admin.register(ClassType)
class ClassTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'duration_minutes')
    search_fields = ('name', 'description')
    filter_horizontal = ('teachers',)

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'target_audience', 'is_active', 'created_at')
    list_filter = ('target_audience', 'is_active', 'created_at')
    search_fields = ('title', 'content')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'allowed_sections')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__email', 'role')

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('username', 'action', 'details_preview', 'ip_address', 'timestamp')
    list_filter = ('action', 'timestamp')
    search_fields = ('username', 'action', 'details', 'ip_address')
    readonly_fields = ('user', 'username', 'action', 'details', 'ip_address', 'timestamp')
    date_hierarchy = 'timestamp'
    ordering = ('-timestamp',)

    def details_preview(self, obj):
        if not obj.details:
            return ""
        return obj.details[:60] + ('...' if len(obj.details) > 60 else '')
    details_preview.short_description = 'Detalles'

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'phone_number', 'lead', 'student', 'message_preview', 'timestamp')
    list_filter = ('sender', 'timestamp')
    search_fields = ('phone_number', 'message_text', 'lead__nombre', 'student__name')
    date_hierarchy = 'timestamp'
    ordering = ('-timestamp',)

    def message_preview(self, obj):
        return obj.message_text[:60] + ('...' if len(obj.message_text) > 60 else '')
    message_preview.short_description = 'Mensaje'

# ─── CMS / WEB CONTENT ────────────────────────────────────────

@admin.register(LandingPage)
class LandingPageAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'cta')
    search_fields = ('title', 'slug')

@admin.register(HomepageContent)
class HomepageContentAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'hero_title_1', 'hero_title_2')

@admin.register(AboutContent)
class AboutContentAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'hero_title_text_1')

@admin.register(ContactContent)
class ContactContentAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'location_title')

@admin.register(GlobalSettings)
class GlobalSettingsAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'phone_number', 'email_contact', 'whatsapp_number')


@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ('date', 'name', 'is_active', 'is_custom', 'created_at')
    list_filter = ('is_active', 'is_custom')
    search_fields = ('name',)
    date_hierarchy = 'date'
    ordering = ('date',)
    actions = ['activate_holidays', 'deactivate_holidays']

    def activate_holidays(self, request, queryset):
        queryset.update(is_active=True)
    activate_holidays.short_description = "Activar feriados seleccionados"

    def deactivate_holidays(self, request, queryset):
        queryset.update(is_active=False)
    deactivate_holidays.short_description = "Desactivar feriados seleccionados"


