import datetime
import json
import os
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase

from api.models import (
    AcademyTask,
    AuditLog,
    Availability,
    GlobalSettings,
    Instrument,
    Lead,
    Lesson,
    Material,
    Plan,
    Room,
    Specialty,
    Student,
    StudentPack,
    Teacher,
    UserProfile,
)
from core.schema import schema


class DetacheCoreMutationsAndMediaTests(TestCase):
    def setUp(self):
        self.instrument = Instrument.objects.create(name="Piano")
        self.specialty = Specialty.objects.create(name="Piano")
        self.room = Room.objects.create(name="Sala 1", capacity=1)
        self.plan = Plan.objects.create(name="Plan Mensual 4", price=80000, duration=1, classes_count=4)

    def test_delete_teacher_with_lessons_materials_students_and_protected_user(self):
        teacher_user = User.objects.create_user(username="profe_uno", password="pw", email="uno@detache.cl")
        UserProfile.objects.create(user=teacher_user, role="PROFESOR")
        teacher = Teacher.objects.create(
            name="Profe Uno",
            email="uno@detache.cl",
            phone_number="+56912345678",
            user=teacher_user,
        )
        teacher.specialties.add(self.specialty)
        Availability.objects.create(
            teacher=teacher,
            day="MONDAY",
            start_time=datetime.time(10, 0),
            end_time=datetime.time(11, 0),
        )
        student = Student.objects.create(name="Alumno Uno", primary_instrument=self.instrument)
        student.assigned_teachers.add(teacher)
        lesson = Lesson.objects.create(
            teacher=teacher,
            student=student,
            room=self.room,
            date=datetime.date(2026, 12, 1),
            start_time=datetime.time(10, 0),
            end_time=datetime.time(11, 0),
        )
        material = Material.objects.create(
            title="Escalas",
            type="PDF",
            url="/media/materials/escalas.pdf",
            scope="TEACHER",
            teacher=teacher,
        )
        AuditLog.objects.create(user=teacher_user, action="TEST", details="test")
        AcademyTask.objects.create(title="Tarea", assigned_user=teacher_user)

        res = schema.execute(
            "mutation($id: Int!) { deleteTeacher(id: $id) { success error } }",
            variable_values={"id": teacher.id},
        )
        self.assertIsNone(res.errors)
        self.assertTrue(res.data["deleteTeacher"]["success"])
        self.assertFalse(Teacher.objects.filter(pk=teacher.id).exists())
        self.assertFalse(User.objects.filter(pk=teacher_user.id).exists())

        lesson.refresh_from_db()
        material.refresh_from_db()
        self.assertIsNone(lesson.teacher)
        self.assertIsNone(material.teacher)
        # Ensure __str__ no longer crashes when teacher is None
        self.assertIn("Sin profesor", str(lesson))

        # Superuser accidentally linked to a teacher must NOT be deleted when deleting the teacher
        superuser = User.objects.create_superuser(username="admin_boss", password="pw", email="boss@detache.cl")
        UserProfile.objects.create(user=superuser, role="SUPERADMIN")
        admin_teacher = Teacher.objects.create(name="Admin Profe", email="boss@detache.cl", user=superuser)
        res_admin = schema.execute(
            "mutation($id: Int!) { deleteTeacher(id: $id) { success error } }",
            variable_values={"id": admin_teacher.id},
        )
        self.assertIsNone(res_admin.errors)
        self.assertTrue(res_admin.data["deleteTeacher"]["success"])
        self.assertTrue(User.objects.filter(pk=superuser.id).exists())

    def test_create_teacher_does_not_hijack_superuser_or_student_account(self):
        superuser = User.objects.create_superuser(username="owner@detache.cl", password="pw", email="owner@detache.cl")
        UserProfile.objects.create(user=superuser, role="SUPERADMIN")

        res = schema.execute(
            "mutation($name: String!, $email: String, $specialtyIds: [Int]) { createTeacher(name: $name, email: $email, specialtyIds: $specialtyIds) { userCreated teacher { id user { id } specialties { id name } } } }",
            variable_values={"name": "Owner Teacher", "email": "owner@detache.cl", "specialtyIds": [self.instrument.id]},
        )
        self.assertIsNone(res.errors)
        self.assertFalse(res.data["createTeacher"]["userCreated"])
        self.assertIsNone(res.data["createTeacher"]["teacher"]["user"])
        self.assertEqual(res.data["createTeacher"]["teacher"]["specialties"][0]["name"], "Piano")

    def test_create_and_update_student_with_blank_optional_fields(self):
        teacher = Teacher.objects.create(name="Profe Dos")
        res = schema.execute(
            """
            mutation(
              $name: String!, $email: String, $rut: String, $birthDate: Date,
              $guardianName: String, $guardianPhone: String, $phoneNumber: String,
              $level: String, $primaryInstrumentId: Int, $assignedTeacherIds: [Int]
            ) {
              createStudent(
                name: $name, email: $email, rut: $rut, birthDate: $birthDate,
                guardianName: $guardianName, guardianPhone: $guardianPhone,
                phoneNumber: $phoneNumber, level: $level,
                primaryInstrumentId: $primaryInstrumentId, assignedTeacherIds: $assignedTeacherIds
              ) {
                success
                student { id name email rut status assignedTeachers { id name } }
              }
            }
            """,
            variable_values={
                "name": "  Sofía Test  ",
                "email": "",
                "rut": "",
                "birthDate": None,
                "guardianName": "   ",
                "guardianPhone": None,
                "phoneNumber": "+56 9 8888 7777",
                "level": "BEGINNER",
                "primaryInstrumentId": self.instrument.id,
                "assignedTeacherIds": [teacher.id],
            },
        )
        self.assertIsNone(res.errors)
        self.assertTrue(res.data["createStudent"]["success"])
        st_data = res.data["createStudent"]["student"]
        self.assertEqual(st_data["name"], "Sofía Test")
        self.assertIsNone(st_data["email"])
        self.assertIsNone(st_data["rut"])
        self.assertEqual(len(st_data["assignedTeachers"]), 1)

    def test_delete_plan_restricted_returns_friendly_error(self):
        student = Student.objects.create(name="Alumno Pack")
        StudentPack.objects.create(student=student, plan=self.plan)

        res = schema.execute(
            "mutation($id: Int!) { deletePlan(id: $id) { success error } }",
            variable_values={"id": self.plan.id},
        )
        self.assertIsNone(res.errors)
        self.assertFalse(res.data["deletePlan"]["success"])
        self.assertIn("packs asociados", res.data["deletePlan"]["error"])

    def test_create_lead_long_contact_payload_and_convert_to_student(self):
        long_msg = "Consulta muy larga " * 30
        email_payload = f"prospecto@detache.cl | Asunto: Clases | Mensaje: {long_msg}"
        res = schema.execute(
            "mutation($nombre: String!, $telefono: String!, $email: String) { createLead(nombre: $nombre, telefono: $telefono, email: $email) { lead { id email } } }",
            variable_values={"nombre": "Juan Lead", "telefono": "56911112222", "email": email_payload},
        )
        self.assertIsNone(res.errors)
        lead_id = res.data["createLead"]["lead"]["id"]
        self.assertEqual(res.data["createLead"]["lead"]["email"], "prospecto@detache.cl")

        conv = schema.execute(
            "mutation($leadId: ID!) { convertLeadToStudent(leadId: $leadId) { success student { id email } } }",
            variable_values={"leadId": lead_id},
        )
        self.assertIsNone(conv.errors)
        self.assertTrue(conv.data["convertLeadToStudent"]["success"])
        self.assertEqual(conv.data["convertLeadToStudent"]["student"]["email"], "prospecto@detache.cl")

    def test_pre_reservation_smtp_email_does_not_crash(self):
        GlobalSettings.objects.create(
            trial_class_email_template="Hola {nombre}, tu clase con {profesor} el {fecha} a las {hora} fue pre-reservada."
        )
        teacher = Teacher.objects.create(name="Profe Prueba", status="ACTIVE")
        res = schema.execute(
            """
            mutation($nombre: String!, $telefono: String!, $email: String, $profesorNombre: String!, $fecha: Date!, $hora: Time!, $servicio: String) {
              createPreReservation(nombre: $nombre, telefono: $telefono, email: $email, profesorNombre: $profesorNombre, fecha: $fecha, hora: $hora, servicio: $servicio) {
                success
                lesson { id status }
              }
            }
            """,
            variable_values={
                "nombre": "Lead Mail",
                "telefono": "+56933334444",
                "email": "leadmail@detache.cl",
                "profesorNombre": teacher.name,
                "fecha": "2026-12-10",
                "hora": "15:00:00",
                "servicio": "PIANO",
            },
        )
        self.assertIsNone(res.errors)
        self.assertTrue(res.data["createPreReservation"]["success"])

    def test_media_upload_serve_xframe_exempt_and_teacher_photo_upload(self):
        from django.conf import settings as django_settings
        import pathlib

        client = Client(HTTP_HOST="localhost:8000")
        pdf_file = SimpleUploadedFile("partitura_test.pdf", b"%PDF-1.4\n1 0 obj\n", content_type="application/pdf")
        resp_upload = client.post("/api/media/upload/", {"file": pdf_file, "folder": "../../materials"})
        self.assertEqual(resp_upload.status_code, 200)
        payload = json.loads(resp_upload.content)
        self.assertEqual(payload["status"], "SUCCESS")
        self.assertTrue(payload["relativeUrl"].startswith("/media/materials/partitura_test_"))

        uploaded_rel = payload["relativeUrl"].replace("/media/", "", 1)
        uploaded_abs = pathlib.Path(django_settings.MEDIA_ROOT) / uploaded_rel
        try:
            resp_get = client.get(payload["relativeUrl"])
            self.assertEqual(resp_get.status_code, 200)
            self.assertNotEqual(resp_get.headers.get("X-Frame-Options"), "DENY")
        finally:
            if uploaded_abs.exists():
                uploaded_abs.unlink()

        teacher = Teacher.objects.create(name="Profe Foto")
        img = SimpleUploadedFile("avatar_test.jpg", b"\xff\xd8\xff\xe0\x00\x10JFIF", content_type="image/jpeg")
        resp_photo = client.post("/api/teachers/upload-photo/", {"teacher_id": str(teacher.id), "photo": img})
        self.assertEqual(resp_photo.status_code, 200)
        photo_data = json.loads(resp_photo.content)
        self.assertEqual(photo_data["status"], "SUCCESS")
        teacher.refresh_from_db()
        try:
            self.assertTrue(bool(teacher.photo.name))
        finally:
            if teacher.photo and os.path.exists(teacher.photo.path):
                os.unlink(teacher.photo.path)

