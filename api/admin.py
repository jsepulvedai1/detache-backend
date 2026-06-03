from django.contrib import admin
from .models import Teacher, Specialty, Availability, Plan, Student, Instrument, Room, Lesson, Lead, LeadNote, StudentPack, Payment, AcademyTask, LandingPage, HomepageContent

class LeadNoteInline(admin.TabularInline):
    model = LeadNote
    extra = 1

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'telefono', 'servicio', 'fuente', 'estado', 'fecha_ingreso')
    list_filter = ('estado', 'servicio', 'fuente')
    search_fields = ('nombre', 'telefono', 'email')
    inlines = [LeadNoteInline]

@admin.register(StudentPack)
class StudentPackAdmin(admin.ModelAdmin):
    list_display = ('student', 'plan', 'remaining_classes', 'is_active', 'expiration_date')
    list_filter = ('is_active', 'plan')
    search_fields = ('student__name',)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('student', 'amount', 'method', 'payment_date')
    list_filter = ('method', 'payment_date')
    search_fields = ('student__name',)

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('name', 'status')
    search_fields = ('name',)
    list_filter = ('status', 'specialties')
    filter_horizontal = ('specialties',)

@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    

@admin.register(Availability)
class AvailabilityAdmin(admin.ModelAdmin):
    list_display = ('day', 'start_time', 'end_time', 'teacher')
    list_filter = ('day', 'teacher')

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'status')
    search_fields = ('name',)
    list_filter = ('status',)

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
    list_display = ('id', 'lesson_type', 'student', 'teacher', 'date', 'start_time', 'status')
    list_filter = ('status', 'lesson_type', 'date', 'teacher', 'room')
    search_fields = ('student__name', 'teacher__name')
    date_hierarchy = 'date'

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'duration')

@admin.register(AcademyTask)
class AcademyTaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'assigned_to', 'priority', 'is_completed', 'created_at')
    list_filter = ('assigned_to', 'priority', 'is_completed')
    search_fields = ('title', 'description')

@admin.register(LandingPage)
class LandingPageAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug')

@admin.register(HomepageContent)
class HomepageContentAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'hero_title_1', 'hero_title_2')
