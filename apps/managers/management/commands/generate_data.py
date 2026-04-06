from django.core.management.base import BaseCommand
from apps.teachers.models import Teacher
from apps.managers.models import Manager
from apps.students.models import Student
from faker import Faker
import random

class Command(BaseCommand):
    help = 'Generates dummy data'

    def handle(self, *args, **kwargs):
        fake = Faker('ru_RU')
        
        self.stdout.write('Generating 70 managers...')
        managers = []
        for _ in range(70):
            manager = Manager(name=fake.name(), phone=fake.phone_number(), is_active=True)
            managers.append(manager)
        Manager.objects.bulk_create(managers)

        self.stdout.write('Generating 50 teachers...')
        teachers = []
        for _ in range(50):
            teacher = Teacher(name=fake.name(), phone=fake.phone_number(), specialization=fake.job(), is_active=True)
            teachers.append(teacher)
        Teacher.objects.bulk_create(teachers)

        self.stdout.write('Generating 50,000 students... this may take a bit')
        managers_db = list(Manager.objects.all())
        students = []
        batch_size = 5000
        total = 50000
        for i in range(total):
            # Select random manager
            manager = random.choice(managers_db)
            student = Student(name=fake.name(), phone=fake.phone_number(), manager=manager, is_active=True)
            students.append(student)
            
            if len(students) == batch_size:
                Student.objects.bulk_create(students)
                self.stdout.write(f'Created {i + 1} students...')
                students = []
        
        if students:
            Student.objects.bulk_create(students)
            
        self.stdout.write(self.style.SUCCESS(f'Successfully generated 70 managers, 50 teachers, and {total} students!'))
