import random
from decimal import Decimal
from datetime import timedelta, datetime
from django.utils import timezone
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.managers.models import Manager
from apps.teachers.models import Teacher
from apps.students.models import Student
from apps.groups.models import Group, Enrollment, ScheduleType, CourseType, SundayEvent
from apps.payments.models import Payment
from apps.attendance.models import Attendance, AttendanceStatus


# ─── Реалистичные узбекские/русские имена ───
STUDENT_NAMES = [
    'Ситора Рахимова', 'Бехруз Юсупов', 'Дильноза Мирзаева', 'Жасур Каримов',
    'Мадина Хасанова', 'Шерзод Турсунов', 'Гулноза Абдуллаева', 'Азизбек Норматов',
    'Нигора Султанова', 'Отабек Рашидов', 'Фарангиз Усманова', 'Сардор Ахмедов',
    'Зарина Бабаева', 'Достон Мирзакаримов', 'Шахло Назарова', 'Ислом Тошпулатов',
    'Камола Файзуллаева', 'Абдулла Холматов', 'Лола Эргашева', 'Умид Джалилов',
    'Севара Исмаилова', 'Бобур Маматкулов', 'Навруза Олимова', 'Элдор Содиков',
    'Дилором Тургунова', 'Феруз Хамидов', 'Нилуфар Мухамедова', 'Акмал Валиев',
    'Саида Жураева', 'Тимур Набиев', 'Хуршида Кадырова', 'Алишер Эшматов',
    'Муниса Ибрагимова', 'Равшан Рузиев', 'Озода Шарипова', 'Нодирбек Пулатов',
    'Малика Мирсаидова', 'Собир Мамадалиев', 'Гулрух Тошматова', 'Санжар Усаров',
]

MANAGER_DATA = [
    {'name': 'Малика Каримова', 'phone': '+998905797956', 'username': 'manager1'},
    {'name': 'Азиз Нишанов', 'phone': '+998905039317', 'username': 'manager2'},
]

TEACHER_DATA = [
    {'name': 'Диёра Рашидова', 'phone': '+998933668051', 'spec': 'English', 'username': 'teacher1'},
    {'name': 'Камолиддин Хошимов', 'phone': '+998939967506', 'spec': 'English', 'username': 'teacher2'},
    {'name': 'Шахзод Абдуллаев', 'phone': '+998935230985', 'spec': 'IELTS', 'username': 'teacher3'},
    {'name': 'Нодира Усманова', 'phone': '+998936591814', 'spec': 'Math', 'username': 'teacher4'},
]

GROUPS_DATA = [
    ('Kids English Starter', CourseType.KIDS_ENGLISH, ScheduleType.EVEN, '14:00 - 15:30', 'К-1', 0, 400000),
    ('General English Pre-Int', CourseType.GENERAL_ENGLISH, ScheduleType.EVEN, '16:00 - 17:30', 'К-2', 1, 450000),
    ('IELTS Reading & Writing', CourseType.IELTS, ScheduleType.EVEN, '18:00 - 19:30', 'К-3', 2, 600000),
    ('Kids English Level 1', CourseType.KIDS_ENGLISH, ScheduleType.ODD, '15:00 - 16:30', 'К-1', 0, 400000),
    ('General English Intermediate', CourseType.GENERAL_ENGLISH, ScheduleType.ODD, '17:00 - 18:30', 'К-2', 1, 450000),
    ('SAT Math Prep', CourseType.SAT, ScheduleType.ODD, '16:00 - 18:00', 'К-4', 3, 400000),
]

GROUP_COLORS = ['bg-t-1', 'bg-t-2', 'bg-t-3', 'bg-t-4', 'bg-t-5', 'bg-t-6']

PAYMENT_COMMENTS = [
    'Оплата за месяц', 'Ежемесячная оплата', 'Оплата за обучение',
    'Наличные', 'Перевод', 'Оплата через Payme', 'Оплата через Click',
]


class Command(BaseCommand):
    help = 'Засеивает базу данных реалистичными тестовыми данными для EduCRM'

    def handle(self, *args, **options):
        self.stdout.write('[*] Очистка существующих данных CRM...')
        Attendance.objects.all().delete()
        Payment.objects.all().delete()
        Enrollment.objects.all().delete()
        SundayEvent.objects.all().delete()
        Group.objects.all().delete()
        Student.objects.all().delete()
        Teacher.objects.all().delete()
        Manager.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

        # ─── Менеджеры ───
        self.stdout.write('[+] Создание менеджеров...')
        managers = []
        for data in MANAGER_DATA:
            user = User.objects.create_user(
                username=data['username'], password='123',
                first_name=data['name'].split()[0],
                last_name=data['name'].split()[1] if len(data['name'].split()) > 1 else ''
            )
            managers.append(Manager.objects.create(
                name=data['name'], phone=data['phone'], user=user
            ))

        # ─── Учителя ───
        self.stdout.write('[+] Создание учителей...')
        teachers = []
        for data in TEACHER_DATA:
            user = User.objects.create_user(
                username=data['username'], password='123',
                first_name=data['name'].split()[0],
                last_name=data['name'].split()[1] if len(data['name'].split()) > 1 else ''
            )
            teachers.append(Teacher.objects.create(
                name=data['name'], phone=data['phone'],
                specialization=data['spec'], user=user
            ))

        # ─── Группы ───
        self.stdout.write('[+] Создание групп...')
        created_groups = []
        for i, (name, c_type, s_type, time_slot, room, teacher_idx, fee) in enumerate(GROUPS_DATA):
            g = Group.objects.create(
                name=name, course_type=c_type, schedule_type=s_type,
                time_slot=time_slot, room=room, teacher=teachers[teacher_idx],
                monthly_fee=fee, max_students=12, color=GROUP_COLORS[i % len(GROUP_COLORS)]
            )
            created_groups.append(g)

        # ─── Ученики ───
        self.stdout.write('[+] Создание 40 учеников с реальными именами...')
        students = []
        for i, name in enumerate(STUDENT_NAMES):
            s = Student.objects.create(
                name=name,
                phone=f'+99899{random.randint(1000000, 9999999)}',
                manager=managers[i % len(managers)]
            )
            students.append(s)

        # ─── Зачисления ───
        self.stdout.write('[+] Зачисление учеников в группы...')
        today = timezone.localdate()
        enrollments = []
        for student in students:
            num_groups = random.choices([1, 2], weights=[65, 35])[0]
            student_groups = random.sample(created_groups, num_groups)
            for group in student_groups:
                enrolled_date = today - timedelta(days=random.randint(14, 75))
                enrollment = Enrollment(
                    student=student, group=group, enrolled_date=enrolled_date
                )
                enrollments.append(enrollment)
        Enrollment.objects.bulk_create(enrollments)

        # ─── Платежи (за последние 3 месяца, реалистичные суммы и даты) ───
        self.stdout.write('[+] Генерация платежей за 3 месяца...')
        payments = []
        for enrollment in Enrollment.objects.select_related('student', 'group').all():
            months_enrolled = max(1, (today - enrollment.enrolled_date).days // 30)
            # 75% шанс что оплатил каждый месяц
            for month_offset in range(months_enrolled):
                if random.random() < 0.75:
                    payment_date = timezone.make_aware(
                        datetime.combine(
                            enrollment.enrolled_date + timedelta(days=month_offset * 30 + random.randint(0, 5)),
                            datetime.min.time()
                        ) + timedelta(hours=random.randint(9, 18), minutes=random.randint(0, 59))
                    )
                    payments.append(Payment(
                        student=enrollment.student,
                        amount=enrollment.group.monthly_fee,
                        date=payment_date,
                        comment=random.choice(PAYMENT_COMMENTS)
                    ))
        Payment.objects.bulk_create(payments)
        self.stdout.write(f'   -> Создано {len(payments)} платежей')

        # ─── Посещаемость (за последние 3 недели) ───
        self.stdout.write('[+] Генерация посещаемости за 3 недели...')
        attendance_records = []
        for days_ago in range(21):
            date = today - timedelta(days=days_ago)
            weekday = date.weekday()

            if weekday == 6:  # Воскресенье — пропускаем
                continue

            if weekday in [1, 3, 5]:  # Вт, Чт, Сб — чётные
                day_groups = [g for g in created_groups if g.schedule_type == 'EVEN']
            elif weekday in [0, 2, 4]:  # Пн, Ср, Пт — нечётные
                day_groups = [g for g in created_groups if g.schedule_type == 'ODD']
            else:
                continue

            for group in day_groups:
                group_enrollments = Enrollment.objects.filter(
                    group=group, is_active=True,
                    enrolled_date__lte=date
                )
                for enr in group_enrollments:
                    # 85% присутствие, 15% отсутствие
                    status = 'PRESENT' if random.random() < 0.85 else 'ABSENT'
                    attendance_records.append(Attendance(
                        student=enr.student, group=group,
                        date=date, status=status
                    ))

        # Bulk create, игнорируя дубликаты
        Attendance.objects.bulk_create(attendance_records, ignore_conflicts=True)
        self.stdout.write(f'   -> Создано {len(attendance_records)} записей посещаемости')

        # ─── Воскресные ивенты ───
        self.stdout.write('[+] Создание воскресных ивентов...')
        days_ahead = 6 - today.weekday()
        if days_ahead < 0:
            days_ahead += 7
        next_sunday = today + timedelta(days=days_ahead)

        SundayEvent.objects.create(
            title='Speaking Club B1-B2', date=next_sunday,
            time_slot='11:00 - 13:00', room='К-1', teacher=teachers[1],
            description='Дискуссии на актуальные темы для уровней Pre-Intermediate и Intermediate.'
        )
        SundayEvent.objects.create(
            title='Mock IELTS Exam', date=next_sunday,
            time_slot='09:00 - 12:00', room='Большой зал', teacher=teachers[2],
            description='Полная симуляция экзамена IELTS (Listening, Reading, Writing).'
        )
        SundayEvent.objects.create(
            title='SAT Practice Test', date=next_sunday + timedelta(days=7),
            time_slot='10:00 - 13:00', room='К-4', teacher=teachers[3],
            description='Пробный SAT тест с разбором ошибок.'
        )

        # ─── Итоги ───
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('База данных успешно засеяна!'))
        self.stdout.write(f'   Менеджеров: {len(managers)}')
        self.stdout.write(f'   Учителей: {len(teachers)}')
        self.stdout.write(f'   Групп: {len(created_groups)}')
        self.stdout.write(f'   Учеников: {len(students)}')
        self.stdout.write(f'   Платежей: {Payment.objects.count()}')
        self.stdout.write(f'   Записей посещаемости: {Attendance.objects.count()}')
        self.stdout.write(f'   Воскресных ивентов: {SundayEvent.objects.count()}')
        self.stdout.write('')
        self.stdout.write('   Логин для менеджеров/учителей: username / пароль: 123')
