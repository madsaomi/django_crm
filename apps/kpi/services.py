from decimal import Decimal
from django.db.models import Sum, Count, Q
from apps.managers.models import Manager
from apps.teachers.models import Teacher
from apps.students.models import Student
from apps.groups.models import Enrollment
from apps.payments.models import Payment
from apps.attendance.models import Attendance
from apps.payments.services import get_bulk_student_debts


def get_manager_kpi():
    """
    KPI по каждому менеджеру (оптимизированная версия — без N+1).
    
    Собирает всю информацию за 3 запроса:
    1. Managers с annotated counts
    2. Batch debt calculation
    3. Revenue aggregation
    """
    managers = Manager.objects.all()
    
    # 1) Аннотируем менеджеров количествами учеников
    managers_annotated = managers.annotate(
        total_students=Count(
            'students',
            distinct=True
        ),
        active_students=Count(
            'students',
            filter=Q(students__is_active=True),
            distinct=True
        ),
        total_revenue=Sum(
            'students__payments__amount',
            default=Decimal('0')
        )
    )
    
    # 2) Batch-долги всех активных учеников
    all_debts = get_bulk_student_debts()
    
    # 3) Группируем долги по менеджерам
    manager_debts = {}
    for sid, info in all_debts.items():
        student = info['student']
        mgr_id = student.manager_id
        if mgr_id and info['debt'] > 0:
            manager_debts[mgr_id] = manager_debts.get(mgr_id, Decimal('0')) + info['debt']
    
    kpi_data = []
    for manager in managers_annotated:
        total = manager.total_students
        active = manager.active_students
        conversion_rate = (active / total * 100) if total > 0 else 0
        
        kpi_data.append({
            'manager': manager,
            'total_students': total,
            'active_students': active,
            'total_revenue': manager.total_revenue or Decimal('0'),
            'total_debt': manager_debts.get(manager.id, Decimal('0')),
            'conversion_rate': round(conversion_rate, 1),
        })

    return kpi_data


def get_teacher_kpi():
    """
    KPI по каждому учителю (оптимизированная версия — без N+1).
    
    Собирает информацию за несколько SQL-запросов вместо O(N*M) циклов.
    """
    teachers = Teacher.objects.filter(is_active=True)
    
    # 1) Аннотируем учителей агрегатами
    teachers_annotated = list(teachers.annotate(
        total_groups=Count(
            'groups',
            filter=Q(groups__is_active=True),
            distinct=True
        ),
        total_ever_enrolled=Count(
            'groups__enrollments__student',
            filter=Q(groups__is_active=True),
            distinct=True
        ),
        active_students_count=Count(
            'groups__enrollments__student',
            filter=Q(groups__is_active=True, groups__enrollments__is_active=True),
            distinct=True
        ),
        total_attendance=Count(
            'groups__attendances',
            filter=Q(groups__is_active=True)
        ),
        present_count=Count(
            'groups__attendances',
            filter=Q(groups__is_active=True, groups__attendances__status='PRESENT')
        ),
    ))
    
    # 2) Batch-долги всех активных учеников
    all_debts = get_bulk_student_debts()
    
    # 3) Маппинг: teacher_id → set(student_ids) для активных enrollments
    teacher_student_map = {}
    active_enrollments = Enrollment.objects.filter(
        is_active=True,
        group__is_active=True,
        group__teacher__isnull=False
    ).values_list('group__teacher_id', 'student_id')
    
    for teacher_id, student_id in active_enrollments:
        teacher_student_map.setdefault(teacher_id, set()).add(student_id)
    
    kpi_data = []
    for teacher in teachers_annotated:
        total_att = teacher.total_attendance
        present = teacher.present_count
        attendance_rate = (present / total_att * 100) if total_att > 0 else 0
        
        total_ever = teacher.total_ever_enrolled
        active_count = teacher.active_students_count
        retention_rate = (active_count / total_ever * 100) if total_ever > 0 else 0
        
        # % учеников с долгом — через batch
        student_ids = teacher_student_map.get(teacher.id, set())
        students_with_debt = 0
        for sid in student_ids:
            debt_info = all_debts.get(sid)
            if debt_info and debt_info['debt'] > 0:
                students_with_debt += 1
        
        debt_percentage = (students_with_debt / len(student_ids) * 100) if student_ids else 0
        
        kpi_data.append({
            'teacher': teacher,
            'total_groups': teacher.total_groups,
            'total_students': active_count,
            'attendance_rate': round(attendance_rate, 1),
            'retention_rate': round(retention_rate, 1),
            'debt_percentage': round(debt_percentage, 1),
        })

    return kpi_data
