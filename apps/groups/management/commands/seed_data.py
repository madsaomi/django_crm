import random
from datetime import timedelta
from django.utils import timezone
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.managers.models import Manager
from apps.teachers.models import Teacher
from apps.students.models import Student
from apps.groups.models import Group, Enrollment, ScheduleType, CourseType, SundayEvent
from apps.payments.models import Payment
from apps.attendance.models import Attendance, AttendanceStatus

class Command(BaseCommand):
    help = 'Seeds database with realistic mock data for the Educational CRM'

    def handle(self, *args, **options):
        self.stdout.write('Clearing existing CRM data...')
        Attendance.objects.all().delete()
        Payment.objects.all().delete()
        Enrollment.objects.all().delete()
        SundayEvent.objects.all().delete()
        Group.objects.all().delete()
        Student.objects.all().delete()
        Teacher.objects.all().delete()
        Manager.objects.all().delete()
        # Delete only non-superuser Users created by the seed
        User.objects.filter(is_superuser=False).delete()

        self.stdout.write('Creating managers...')
        managers = []
        for i, name in enumerate(['Малика Каримова', 'Азиз Нишанов']):
            user = User.objects.create_user(username=f'manager{i+1}', password='123')
            user.first_name = name.split()[0]
            user.last_name = name.split()[1] if len(name.split()) > 1 else ''
            user.save()
            managers.append(Manager.objects.create(name=name, phone=f'+99890{random.randint(1000000, 9999999)}', user=user))

        self.stdout.write('Creating teachers...')
        teachers = []
        teacher_names = ['Джон Смит', 'Елена Волкова', 'Рустам Валиев', 'Севара Алиева']
        specs = ['English', 'English', 'IELTS', 'Math']
        for i, (name, spec) in enumerate(zip(teacher_names, specs)):
            user = User.objects.create_user(username=f'teacher{i+1}', password='123')
            user.first_name = name.split()[0]
            user.last_name = name.split()[1] if len(name.split()) > 1 else ''
            user.save()
            teachers.append(Teacher.objects.create(name=name, phone=f'+99893{random.randint(1000000, 9999999)}', specialization=spec, user=user))

        self.stdout.write('Creating groups and enrollments...')
        groups_data = [
            ('Kids English Starter', CourseType.KIDS_ENGLISH, ScheduleType.EVEN, '14:00 - 15:30', 'К-1', teachers[0], 400000),
            ('General English Pre-Int', CourseType.GENERAL_ENGLISH, ScheduleType.EVEN, '16:00 - 17:30', 'К-2', teachers[1], 450000),
            ('IELTS Reading', CourseType.IELTS, ScheduleType.EVEN, '18:00 - 19:30', 'К-3', teachers[2], 600000),
            ('Kids English Level 1', CourseType.KIDS_ENGLISH, ScheduleType.ODD, '15:00 - 16:30', 'К-1', teachers[0], 400000),
            ('General English Int', CourseType.GENERAL_ENGLISH, ScheduleType.ODD, '17:00 - 18:30', 'К-2', teachers[1], 450000),
            ('SAT Prep', CourseType.SAT, ScheduleType.ODD, '16:00 - 18:00', 'К-4', teachers[3], 400000),
        ]

        created_groups = []
        for name, c_type, s_type, time_slot, room, teacher, fee in groups_data:
            g = Group.objects.create(
                name=name, course_type=c_type, schedule_type=s_type, time_slot=time_slot,
                room=room, teacher=teacher, monthly_fee=fee, max_students=12
            )
            created_groups.append(g)

        self.stdout.write('Creating students...')
        students = []
        for i in range(40):
            s = Student.objects.create(
                name=f'Ученик {i+1}', phone=f'+99899{random.randint(1000000, 9999999)}',
                manager=random.choice(managers)
            )
            students.append(s)

        self.stdout.write('Enrolling students & generating payments...')
        for student in students:
            # Pick 1-2 random groups
            student_groups = random.sample(created_groups, random.randint(1, 2))
            for group in student_groups:
                Enrollment.objects.create(student=student, group=group)
                # 80% chance they made a payment
                if random.random() < 0.8:
                    Payment.objects.create(
                        student=student,
                        amount=group.monthly_fee,
                        date=timezone.now(),
                        comment=f'Оплата за {group.name}'
                    )

        self.stdout.write('Creating sunday events...')
        today = timezone.localdate()
        # Find next sunday
        days_ahead = 6 - today.weekday()
        if days_ahead < 0:
            days_ahead += 7
        next_sunday = today + timedelta(days=days_ahead)

        SundayEvent.objects.create(
            title='Speaking Club B1-B2', date=next_sunday, time_slot='11:00 - 13:00',
            room='К-1', teacher=teachers[1], description='Дискуссии на разные темы для средних уровней.'
        )
        SundayEvent.objects.create(
            title='Mock IELTS Test', date=next_sunday, time_slot='09:00 - 12:00',
            room='Большой зал', teacher=teachers[2], description='Пробный экзамен.'
        )

        self.stdout.write(self.style.SUCCESS('Successfully seeded database!'))
