import os
import sys
import django
from datetime import date, time, timedelta, datetime

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from api.models import (
    Teacher, Student, Plan, Room, Specialty, Availability, 
    Lesson, Lead, LeadNote, StudentPack, Payment, 
    AcademyTask, StudentWallMessage, Material, GlobalSettings
)

def seed_data():
    print("🌱 Iniciando carga de datos de prueba para Détaché...")

    # 1. Especialidades
    specialties_data = [
        "Piano Clásico", "Piano Popular", "Piano Niños", 
        "Piano Adultos", "Canto Popular", "Teoría & Armonía", "Iniciación Musical"
    ]
    specialty_objs = {}
    for name in specialties_data:
        spec, _ = Specialty.objects.get_or_create(name=name)
        specialty_objs[name] = spec

    # 2. Salas
    rooms_data = [
        {"name": "Sala 1 - Steinway & Sons (Cola)", "capacity": 3},
        {"name": "Sala 2 - Yamaha U3 (Vertical)", "capacity": 2},
        {"name": "Sala 3 - Kawai Acústico", "capacity": 2},
        {"name": "Sala 4 - Canto y Ensayos", "capacity": 4},
    ]
    room_objs = []
    for r in rooms_data:
        room, _ = Room.objects.get_or_create(name=r["name"], defaults={"capacity": r["capacity"]})
        room_objs.append(room)

    # 3. Planes
    plans_data = [
        {"name": "Plan 4 Clases (Mensual)", "classes_count": 4, "price": 65000, "duration": 1},
        {"name": "Plan 8 Clases (Bimestral)", "classes_count": 8, "price": 120000, "duration": 2},
        {"name": "Plan 12 Clases (Trimestral)", "classes_count": 12, "price": 170000, "duration": 3},
    ]
    plan_objs = {}
    for p in plans_data:
        plan, _ = Plan.objects.get_or_create(
            name=p["name"], 
            defaults={"classes_count": p["classes_count"], "price": p["price"], "duration": p["duration"]}
        )
        plan_objs[p["name"]] = plan

    # 4. Profesores y Cuentas de Acceso al Portal Docente
    teachers_info = [
        {
            "name": "Roberto Arancibia",
            "email": "roberto@detache.cl",
            "username": "profe_roberto",
            "password": "password123",
            "phone": "+56981112233",
            "bio": "Pianista clásico formado en la Universidad de Chile con más de 10 años de experiencia docente en repertorio clásico y técnica pianística.",
            "specs": ["Piano Clásico", "Piano Adultos", "Teoría & Armonía"],
            "days": ["MONDAY", "WEDNESDAY", "FRIDAY"],
            "hours": [(time(9, 0), time(13, 0)), (time(14, 0), time(19, 0))]
        },
        {
            "name": "Valentina Morales",
            "email": "valentina@detache.cl",
            "username": "profe_valentina",
            "password": "password123",
            "phone": "+56984445566",
            "bio": "Cantante lírica y popular, pianista acompañante. Especialista en técnica vocal, respiración diafragmática e iniciación musical para niños.",
            "specs": ["Canto Popular", "Iniciación Musical", "Piano Niños"],
            "days": ["TUESDAY", "THURSDAY", "SATURDAY"],
            "hours": [(time(10, 0), time(14, 0)), (time(15, 0), time(20, 0))]
        },
        {
            "name": "Felipe Soto",
            "email": "felipe@detache.cl",
            "username": "profe_felipe",
            "password": "password123",
            "phone": "+56987778899",
            "bio": "Compositor y arreglista. Enseña piano popular, improvisación jazz, pop moderno y armonía contemporánea.",
            "specs": ["Piano Popular", "Teoría & Armonía", "Piano Adultos"],
            "days": ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY"],
            "hours": [(time(14, 0), time(21, 0))]
        }
    ]

    teacher_objs = {}
    for t_data in teachers_info:
        # User
        user, created = User.objects.get_or_create(username=t_data["username"], defaults={"email": t_data["email"], "first_name": t_data["name"]})
        user.set_password(t_data["password"])
        user.save()

        # Teacher profile
        teacher, _ = Teacher.objects.get_or_create(
            name=t_data["name"],
            defaults={
                "email": t_data["email"],
                "phone_number": t_data["phone"],
                "description": t_data["bio"],
                "status": "ACTIVE",
                "user": user
            }
        )
        if not teacher.user:
            teacher.user = user
            teacher.save()

        # Assign specialties
        for sp_name in t_data["specs"]:
            if sp_name in specialty_objs:
                teacher.specialties.add(specialty_objs[sp_name])

        # Assign availability
        Availability.objects.filter(teacher=teacher).delete()
        for day in t_data["days"]:
            for start_h, end_h in t_data["hours"]:
                Availability.objects.create(
                    teacher=teacher,
                    day=day,
                    start_time=start_h,
                    end_time=end_h
                )

        teacher_objs[t_data["name"]] = teacher
        print(f"  ✓ Profesor creado: {teacher.name} (Usuario: {t_data['username']} / {t_data['password']})")

    # 5. Alumnos, Packs, Pagos y Cuentas de Acceso al Portal Alumno
    today = date.today()
    students_info = [
        {
            "name": "Camila Edwards",
            "email": "camila.edwards@gmail.com",
            "username": "alumno_camila",
            "password": "password123",
            "phone": "+56987654321",
            "plan_name": "Plan 8 Clases (Bimestral)",
            "classes_total": 8,
            "classes_remaining": 6,
            "teacher_name": "Roberto Arancibia",
            "payment_amount": 120000,
            "payment_method": "CARD"
        },
        {
            "name": "Matías Carrasco",
            "email": "matias.carrasco@gmail.com",
            "username": "alumno_matias",
            "password": "password123",
            "phone": "+56911223344",
            "plan_name": "Plan 4 Clases (Mensual)",
            "classes_total": 4,
            "classes_remaining": 2,
            "teacher_name": "Valentina Morales",
            "payment_amount": 65000,
            "payment_method": "TRANSFER"
        },
        {
            "name": "Francisca Valenzuela",
            "email": "francisca.valenzuela@gmail.com",
            "username": "alumno_francisca",
            "password": "password123",
            "phone": "+56999887766",
            "plan_name": "Plan 12 Clases (Trimestral)",
            "classes_total": 12,
            "classes_remaining": 11,
            "teacher_name": "Felipe Soto",
            "payment_amount": 170000,
            "payment_method": "CARD"
        }
    ]

    for s_data in students_info:
        # User
        user, _ = User.objects.get_or_create(username=s_data["username"], defaults={"email": s_data["email"], "first_name": s_data["name"]})
        user.set_password(s_data["password"])
        user.save()

        # Student
        student, _ = Student.objects.get_or_create(
            name=s_data["name"],
            defaults={
                "email": s_data["email"],
                "phone_number": s_data["phone"],
                "status": "ACTIVE",
                "user": user
            }
        )
        if not student.user:
            student.user = user
            student.save()

        # Student Pack
        plan = plan_objs.get(s_data["plan_name"], list(plan_objs.values())[0])
        pack, _ = StudentPack.objects.get_or_create(
            student=student,
            plan=plan,
            defaults={
                "total_classes": s_data["classes_total"],
                "remaining_classes": s_data["classes_remaining"],
                "purchase_date": today - timedelta(days=5),
                "expiration_date": today + timedelta(days=30),
                "is_active": True
            }
        )

        # Payment
        Payment.objects.get_or_create(
            student=student,
            amount=s_data["payment_amount"],
            payment_date=today - timedelta(days=5),
            defaults={
                "method": s_data["payment_method"],
                "description": f"Pago de {plan.name} (Aprobado)",
                "pack": pack
            }
        )

        # Agendar Clases de Ejemplo
        teacher = teacher_objs.get(s_data["teacher_name"], list(teacher_objs.values())[0])
        room = room_objs[0]

        # Clase pasada (Completada)
        Lesson.objects.get_or_create(
            student=student,
            teacher=teacher,
            date=today - timedelta(days=3),
            start_time=time(16, 0),
            defaults={
                "end_time": time(16, 50),
                "room": room,
                "status": "COMPLETED",
                "lesson_type": "INDIVIDUAL"
            }
        )

        # Clase próxima (Hoy / Mañana)
        Lesson.objects.get_or_create(
            student=student,
            teacher=teacher,
            date=today + timedelta(days=1),
            start_time=time(17, 0),
            defaults={
                "end_time": time(17, 50),
                "room": room,
                "status": "PENDING",
                "lesson_type": "INDIVIDUAL"
            }
        )

        # Mensaje de Muro de Ejemplo
        StudentWallMessage.objects.get_or_create(
            student=student,
            text=f"¡Hola {student.name.split()[0]}! Excelente avance en la última sesión. Recuerda practicar la escala de Do Mayor y los acordes con metrónomo a 80 BPM.",
            author=teacher.name,
            defaults={"created_at": timezone.now()}
        )

        print(f"  ✓ Alumno creado: {student.name} (Usuario: {s_data['username']} / {s_data['password']})")

    # 6. Leads de CRM de prueba
    leads_data = [
        {"nombre": "Andrés Morales", "telefono": "+56912341234", "email": "andres@gmail.com", "servicio": "PIANO_ADULTOS", "fuente": "WEB", "estado": "NUEVO"},
        {"nombre": "Loreto Castro", "telefono": "+56955667788", "email": "loreto@gmail.com", "servicio": "CANTO", "fuente": "INSTAGRAM", "estado": "CONTACTADO"},
        {"nombre": "Ignacio Rivas", "telefono": "+56933445566", "email": "ignacio@gmail.com", "servicio": "CLASE_PRUEBA", "fuente": "WEB", "estado": "PRE_RESERVA"},
    ]
    for ld in leads_data:
        lead, _ = Lead.objects.get_or_create(
            nombre=ld["nombre"],
            defaults={
                "telefono": ld["telefono"],
                "email": ld["email"],
                "servicio": ld["servicio"],
                "fuente": ld["fuente"],
                "estado": ld["estado"]
            }
        )
        LeadNote.objects.get_or_create(lead=lead, texto="Interesado en comenzar clases la próxima semana.", autor="Recepción")

    # 7. Tareas de Academia
    tasks_data = [
        {"title": "Confirmar sala de ensayo para el sábado", "priority": "URGENTE", "assigned_to": "RECEPCION"},
        {"title": "Revisar stock de partituras de iniciación", "priority": "IMPORTANTE", "assigned_to": "ADMINISTRACION"},
        {"title": "Llamar a lead Ignacio Rivas para confirmar clase de prueba", "priority": "RECORDATORIO", "assigned_to": "VENTAS"},
    ]
    for td in tasks_data:
        AcademyTask.objects.get_or_create(
            title=td["title"],
            defaults={"priority": td["priority"], "assigned_to": td["assigned_to"], "due_date": today + timedelta(days=2)}
        )

    print("✨ ¡Datos de prueba sembrados exitosamente!")

if __name__ == "__main__":
    seed_data()
