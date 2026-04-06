import random
from django.core.management.base import BaseCommand
from django.db import transaction
from faker import Faker

from apps.teachers.models import Teacher
from apps.managers.models import Manager
from apps.students.models import Student
from apps.groups.models import Group, CourseType, ScheduleType, Enrollment, SundayEvent
from apps.attendance.models import Attendance
from apps.payments.models import Payment

class Command(BaseCommand):
    help = 'Resets database with a smaller dummy dataset'

    def handle(self, *args, **kwargs):
        self.stdout.write('Deleting existing data (this might take 10-20 seconds for 50,000+ objects)...')
        Enrollment.objects.all().delete()
        Attendance.objects.all().delete()
        Payment.objects.all().delete()
        Group.objects.all().delete()
        Student.objects.all().delete()
        Manager.objects.all().delete()
        Teacher.objects.all().delete()
        SundayEvent.objects.all().delete()
        
        self.stdout.write('Database cleared. Generating new small dataset...')
        
        fake = Faker('ru_RU')
        
        # 1. Managers
        managers = []
        for _ in range(5):
            managers.append(Manager(name=fake.name(), phone=fake.phone_number(), is_active=True))
        Manager.objects.bulk_create(managers)
        managers_db = list(Manager.objects.all())

        # 2. Teachers
        teachers = []
        for _ in range(10):
            teachers.append(Teacher(name=fake.name(), phone=fake.phone_number(), specialization=fake.job(), is_active=True))
        Teacher.objects.bulk_create(teachers)
        teachers_db = list(Teacher.objects.all())

        # 3. Students
        students = []
        total_students = 500
        for _ in range(total_students):
            students.append(Student(name=fake.name(), phone=fake.phone_number(), manager=random.choice(managers_db), is_active=True))
        Student.objects.bulk_create(students)
        students_db = list(Student.objects.all())

        # 4. Groups & Enrollments
        time_slots = ["09:00-10:30", "14:00-15:30", "15:30-17:00", "17:00-18:30"]
        rooms = [f"Room {i}" for i in range(1, 6)]
        levels = ["Beginner", "Elementary", "Pre-Intermediate", "Intermediate"]

        enrollments_to_create = []
        chunk_size = 12
        group_number = 1
        
        with transaction.atomic():
            for i in range(0, len(students_db), chunk_size):
                chunk = students_db[i:i + chunk_size]
                course = random.choice([c[0] for c in CourseType.choices])
                level = random.choice(levels) if course == 'GENERAL_ENGLISH' else ""
                
                group = Group(
                    name=f'Group-{group_number}',
                    course_type=course,
                    level=level,
                    teacher=random.choice(teachers_db),
                    schedule_type=random.choice([s[0] for s in ScheduleType.choices]),
                    time_slot=random.choice(time_slots),
                    room=random.choice(rooms),
                    max_students=12,
                    is_active=True
                )
                group.save()
                group_number += 1
                
                for student in chunk:
                    enrollments_to_create.append(Enrollment(student=student, group=group))
                    
        Enrollment.objects.bulk_create(enrollments_to_create)
        
        self.stdout.write(self.style.SUCCESS(f'Successfully recreated: 5 Managers, 10 Teachers, {total_students} Students, {group_number - 1} Groups!'))
