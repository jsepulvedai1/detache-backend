from django.contrib import admin
from .models import Teacher, Specialty, Availability, Plan, Student, Instrument, Room, Lesson

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
