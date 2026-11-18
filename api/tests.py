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

    def test_pack_does_not_rollover_and_expires_independently_exact_scenario(self):
        from types import SimpleNamespace
        from dateutil.relativedelta import relativedelta

        today = StudentPack.get_chile_today()
        student_user = User.objects.create_user(username="alumno_pack", password="pw", email="pack@detache.cl")
        UserProfile.objects.create(user=student_user, role="ALUMNO")
        student = Student.objects.create(name="Alumno Pack", email="pack@detache.cl", user=student_user)
        teacher = Teacher.objects.create(name="Profe Pack")

        # 1) Compra Pack A de 4 clases (1 mes). Verifica creación independiente y vencimiento por relativedelta.
        initial_purchase = today - datetime.timedelta(days=20)
        res_pack_a = schema.execute(
            """
            mutation($studentId: Int!, $planId: Int!, $purchaseDate: Date) {
              createStudentPack(studentId: $studentId, planId: $planId, purchaseDate: $purchaseDate) {
                pack { id totalClasses remainingClasses purchaseDate expirationDate isActive isExpired }
              }
            }
            """,
            variable_values={
                "studentId": student.id,
                "planId": self.plan.id,
                "purchaseDate": initial_purchase.isoformat(),
            },
        )
        self.assertIsNone(res_pack_a.errors)
        pack_a_data = res_pack_a.data["createStudentPack"]["pack"]
        pack_a = StudentPack.objects.get(pk=pack_a_data["id"])
        self.assertEqual(pack_a.total_classes, 4)
        self.assertEqual(pack_a.remaining_classes, 4)
        self.assertEqual(pack_a.expiration_date, initial_purchase + relativedelta(months=1))

        # Ajustar vencimiento de Pack A a mañana (simulando 1 día antes de su vencimiento).
        d1 = today + datetime.timedelta(days=1)
        pack_a.expiration_date = d1
        pack_a.save(update_fields=["expiration_date"])

        # 2) Consume 3 clases del Pack A -> queda 1 clase restante.
        for idx in range(3):
            lesson = Lesson.objects.create(
                teacher=teacher,
                student=student,
                room=self.room,
                date=today - datetime.timedelta(days=idx + 1),
                start_time=datetime.time(10 + idx, 0),
                end_time=datetime.time(11 + idx, 0),
                status="CONFIRMED",
            )
            res_complete = schema.execute(
                "mutation($id: Int!) { updateLessonStatus(lessonId: $id, status: \"COMPLETED\") { success } }",
                variable_values={"id": lesson.id},
            )
            self.assertIsNone(res_complete.errors)
            self.assertTrue(res_complete.data["updateLessonStatus"]["success"])

        pack_a.refresh_from_db()
        self.assertEqual(pack_a.remaining_classes, 1)

        # 3) Un día antes de que venza Pack A, compra Pack B de 4 clases (1 mes).
        res_pack_b = schema.execute(
            """
            mutation($studentId: Int!, $planId: Int!, $purchaseDate: Date) {
              createStudentPack(studentId: $studentId, planId: $planId, purchaseDate: $purchaseDate) {
                pack { id totalClasses remainingClasses purchaseDate expirationDate isActive isExpired }
              }
            }
            """,
            variable_values={
                "studentId": student.id,
                "planId": self.plan.id,
                "purchaseDate": today.isoformat(),
            },
        )
        self.assertIsNone(res_pack_b.errors)
        pack_b = StudentPack.objects.get(pk=res_pack_b.data["createStudentPack"]["pack"]["id"])

        # Deben coexistir 2 packs independientes sin fusionarse ni renovar vencimiento.
        self.assertEqual(StudentPack.objects.filter(student=student).count(), 2)
        pack_a.refresh_from_db()
        self.assertEqual(pack_a.remaining_classes, 1)
        self.assertEqual(pack_a.expiration_date, d1)
        self.assertEqual(pack_b.total_classes, 4)
        self.assertEqual(pack_b.remaining_classes, 4)
        self.assertEqual(pack_b.expiration_date, today + relativedelta(months=1))

        # 4) Antes de vencer Pack A: el portal del alumno (myPacks) tiene 1 + 4 = 5 créditos vigentes.
        student_ctx = SimpleNamespace(user=student_user)
        my_packs_query = "{ myPacks { id totalClasses remainingClasses expirationDate isActive isExpired } }"
        res_before = schema.execute(my_packs_query, context_value=student_ctx)
        self.assertIsNone(res_before.errors)
        packs_before = {int(p["id"]): p for p in res_before.data["myPacks"]}
        self.assertTrue(packs_before[pack_a.id]["isActive"])
        self.assertFalse(packs_before[pack_a.id]["isExpired"])
        self.assertTrue(packs_before[pack_b.id]["isActive"])
        self.assertFalse(packs_before[pack_b.id]["isExpired"])
        total_valid_before = sum(
            p["remainingClasses"] for p in packs_before.values() if p["isActive"] and not p["isExpired"]
        )
        self.assertEqual(total_valid_before, 5)
        self.assertEqual(sum(p.remaining_classes for p in StudentPack.valid_packs_for_student(student)), 5)

        # 5) Al día siguiente (Pack A ya venció ayer): Pack A se desactiva automáticamente y quedan solo 4 créditos.
        pack_a.expiration_date = today - datetime.timedelta(days=1)
        pack_a.save(update_fields=["expiration_date"])

        res_after = schema.execute(my_packs_query, context_value=student_ctx)
        self.assertIsNone(res_after.errors)
        packs_after = {int(p["id"]): p for p in res_after.data["myPacks"]}
        self.assertFalse(packs_after[pack_a.id]["isActive"])
        self.assertTrue(packs_after[pack_a.id]["isExpired"])
        self.assertEqual(packs_after[pack_a.id]["remainingClasses"], 1)
        self.assertTrue(packs_after[pack_b.id]["isActive"])
        self.assertFalse(packs_after[pack_b.id]["isExpired"])
        total_valid_after = sum(
            p["remainingClasses"] for p in packs_after.values() if p["isActive"] and not p["isExpired"]
        )
        self.assertEqual(total_valid_after, 4)
        self.assertEqual(sum(p.remaining_classes for p in StudentPack.valid_packs_for_student(student)), 4)

        pack_a.refresh_from_db()
        self.assertFalse(pack_a.is_active)

        # No se puede descontar manualmente de un pack vencido.
        res_manual = schema.execute(
            "mutation($id: Int!) { manualDeductClass(packId: $id) { success error pack { isActive } } }",
            variable_values={"id": pack_a.id},
        )
        self.assertIsNone(res_manual.errors)
        self.assertFalse(res_manual.data["manualDeductClass"]["success"])
        self.assertIn("vencido", res_manual.data["manualDeductClass"]["error"].lower())

    def test_pack_fifo_deduction_and_date_aware_scheduling(self):
        today = StudentPack.get_chile_today()
        student = Student.objects.create(name="Alumno FIFO")
        teacher = Teacher.objects.create(name="Profe FIFO")

        pack_a = StudentPack.objects.create(
            student=student,
            plan=self.plan,
            purchase_date=today - datetime.timedelta(days=25),
            expiration_date=today + datetime.timedelta(days=2),
        )
        pack_a.remaining_classes = 1
        pack_a.save(update_fields=["remaining_classes"])

        pack_b = StudentPack.objects.create(
            student=student,
            plan=self.plan,
            purchase_date=today,
            expiration_date=today + datetime.timedelta(days=30),
        )

        create_lesson_mut = """
        mutation($teacherId: Int!, $studentId: Int!, $roomId: Int!, $date: Date!, $start: Time!, $end: Time!) {
          createLesson(teacherId: $teacherId, studentId: $studentId, roomId: $roomId, date: $date, startTime: $start, endTime: $end) {
            lesson { id date status }
          }
        }
        """
        after_pack_a = today + datetime.timedelta(days=10)
        for idx in range(4):
            res_ok = schema.execute(
                create_lesson_mut,
                variable_values={
                    "teacherId": teacher.id,
                    "studentId": student.id,
                    "roomId": self.room.id,
                    "date": after_pack_a.isoformat(),
                    "start": f"{10 + idx:02d}:00:00",
                    "end": f"{11 + idx:02d}:00:00",
                },
            )
            self.assertIsNone(res_ok.errors)

        # Una 5ta clase después del vencimiento de Pack A debe fallar, pues el crédito restante de Pack A vence antes.
        res_fail_after_exp = schema.execute(
            create_lesson_mut,
            variable_values={
                "teacherId": teacher.id,
                "studentId": student.id,
                "roomId": self.room.id,
                "date": after_pack_a.isoformat(),
                "start": "16:00:00",
                "end": "17:00:00",
            },
        )
        self.assertIsNotNone(res_fail_after_exp.errors)
        self.assertIn("vencen antes", str(res_fail_after_exp.errors[0]).lower())

        # Sin embargo, agendar esa 5ta clase antes del vencimiento de Pack A sí debe permitirse.
        before_pack_a_exp = today + datetime.timedelta(days=1)
        res_ok_before_exp = schema.execute(
            create_lesson_mut,
            variable_values={
                "teacherId": teacher.id,
                "studentId": student.id,
                "roomId": self.room.id,
                "date": before_pack_a_exp.isoformat(),
                "start": "12:00:00",
                "end": "13:00:00",
            },
        )
        self.assertIsNone(res_ok_before_exp.errors)
        early_lesson_id = int(res_ok_before_exp.data["createLesson"]["lesson"]["id"])

        # Completar la clase temprana descuenta del pack que vence primero (Pack A), no de Pack B.
        res_complete_early = schema.execute(
            "mutation($id: Int!) { updateLessonStatus(lessonId: $id, status: \"COMPLETED\") { success } }",
            variable_values={"id": early_lesson_id},
        )
        self.assertIsNone(res_complete_early.errors)
        self.assertTrue(res_complete_early.data["updateLessonStatus"]["success"])
        pack_a.refresh_from_db()
        pack_b.refresh_from_db()
        self.assertEqual(pack_a.remaining_classes, 0)
        self.assertEqual(pack_b.remaining_classes, 4)

        # Completar una clase posterior descuenta de Pack B, y revertir a EXCUSED devuelve el crédito a Pack B.
        later_lesson = Lesson.objects.filter(student=student, date=after_pack_a).order_by("id").first()
        res_complete_later = schema.execute(
            "mutation($id: Int!) { updateLessonStatus(lessonId: $id, status: \"COMPLETED\") { success } }",
            variable_values={"id": later_lesson.id},
        )
        self.assertIsNone(res_complete_later.errors)
        pack_b.refresh_from_db()
        self.assertEqual(pack_b.remaining_classes, 3)

        res_refund_later = schema.execute(
            "mutation($id: Int!) { updateLessonStatus(lessonId: $id, status: \"EXCUSED\") { success } }",
            variable_values={"id": later_lesson.id},
        )
        self.assertIsNone(res_refund_later.errors)
        pack_b.refresh_from_db()
        self.assertEqual(pack_b.remaining_classes, 4)


