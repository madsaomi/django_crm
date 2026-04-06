import random
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.teachers.models import Teacher
from apps.students.models import Student
from apps.groups.models import Group, CourseType, ScheduleType, Enrollment

class Command(BaseCommand):
    help = 'Distribute students into groups of 12 and setup schedules'

    def handle(self, *args, **kwargs):
        teachers = list(Teacher.objects.all())
        if not teachers:
            self.stdout.write(self.style.ERROR('No teachers found. Run generate_data first.'))
            return
            
        students = list(Student.objects.all())
        if not students:
            self.stdout.write(self.style.ERROR('No students found. Run generate_data first.'))
            return

        time_slots = ["09:00-10:30", "10:30-12:00", "14:00-15:30", "15:30-17:00", "17:00-18:30", "18:30-20:00"]
        rooms = [f"Room {i}" for i in range(1, 21)]
        levels = ["Beginner", "Elementary", "Pre-Intermediate", "Intermediate", "Upper-Intermediate", "Advanced"]
        
        self.stdout.write(f'Got {len(students)} students. Creating groups & enrollments...')

        enrollments_to_create = []

        chunk_size = 12
        group_number = 1
        
        with transaction.atomic():
            # Clear existing groups to start fresh if needed (optional but let's just append)
            for i in range(0, len(students), chunk_size):
                chunk = students[i:i + chunk_size]
                
                course = random.choice([c[0] for c in CourseType.choices])
                level = random.choice(levels) if course == 'GENERAL_ENGLISH' else ""
                
                group = Group(
                    name=f'Group-{group_number}',
                    course_type=course,
                    level=level,
                    teacher=random.choice(teachers),
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
                    
        self.stdout.write('Saving enrollments to database...')
        Enrollment.objects.bulk_create(enrollments_to_create, batch_size=5000)
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {group_number - 1} groups and enrolled {len(enrollments_to_create)} students!'))
