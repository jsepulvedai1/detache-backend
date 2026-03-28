from django.db import models

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

    def __str__(self):
        return self.name

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
    name = models.CharField(max_length=255)
    photo = models.ImageField(upload_to='students/', blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ACTIVE')

    def __str__(self):
        return self.name

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

    def __str__(self):
        return f"{self.lesson_type} - {self.student.name} with {self.teacher.name} on {self.date}"

class Plan(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.PositiveIntegerField(help_text="Duration in months")

    def __str__(self):
        return self.name
