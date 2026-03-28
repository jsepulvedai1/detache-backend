import graphene
from graphene_django import DjangoObjectType
from .models import Teacher, Specialty, Availability, Plan, Student, Instrument, Room, Lesson

# --- Object Types ---

class TeacherType(DjangoObjectType):
    class Meta:
        model = Teacher
        fields = ("id", "name", "description", "photo", "status", "specialties", "availabilities")

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
        fields = ("id", "name", "photo", "status")

    def resolve_photo(self, info):
        if self.photo:
            return info.context.build_absolute_uri(self.photo.url)
        return None

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
        fields = ("id", "teacher", "student", "room", "date", "start_time", "end_time", "status", "lesson_type")

class PlanType(DjangoObjectType):
    class Meta:
        model = Plan
        fields = ("id", "name", "price", "duration")

# --- Queries ---

class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Hello, this is the Detache backend with GraphQL!")
    
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

    teacher = graphene.Field(TeacherType)

    def mutate(self, info, name, description="", status="ACTIVE"):
        teacher = Teacher.objects.create(name=name, description=description, status=status)
        return CreateTeacher(teacher=teacher)

class CreateStudent(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        status = graphene.String()

    student = graphene.Field(StudentType)

    def mutate(self, info, name, status="ACTIVE"):
        student = Student.objects.create(name=name, status=status)
        return CreateStudent(student=student)

class Mutation(graphene.ObjectType):
    create_lesson = CreateLesson.Field()
    create_student = CreateStudent.Field()
    create_teacher = CreateTeacher.Field()
