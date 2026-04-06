from decimal import Decimal
from django.db.models import Sum, Count, Q, F
from apps.managers.models import Manager
from apps.teachers.models import Teacher
from apps.students.models import Student
from apps.groups.models import Enrollment
from apps.payments.models import Payment
from apps.attendance.models import Attendance
from apps.payments.services import calculate_student_debt


def get_manager_kpi():
    """
    KPI по каждому менеджеру:
    - total_students: общее кол-во учеников
    - active_students: активные ученики
    - total_revenue: общий доход от учеников менеджера
    - total_debt: общий долг учеников менеджера
    - conversion_rate: % активных учеников
    """
    managers = Manager.objects.all()
    kpi_data = []

    for manager in managers:
        students = Student.objects.filter(manager=manager)
        total_students = students.count()
        active_students = students.filter(is_active=True).count()

        total_revenue = Payment.objects.filter(
            student__manager=manager
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

        # Рассчитываем долг для каждого ученика
        total_debt = Decimal('0')
        for student in students.filter(is_active=True):
            debt = calculate_student_debt(student)
            if debt > 0:
                total_debt += debt

        conversion_rate = (active_students / total_students * 100) if total_students > 0 else 0

        kpi_data.append({
            'manager': manager,
            'total_students': total_students,
            'active_students': active_students,
            'total_revenue': total_revenue,
            'total_debt': total_debt,
            'conversion_rate': round(conversion_rate, 1),
        })

    return kpi_data


def get_teacher_kpi():
    """
    KPI по каждому учителю:
    - total_groups: кол-во групп
    - total_students: общее кол-во учеников
    - attendance_rate: % посещаемости
    - retention_rate: % удержания (активных / всего зачисленных)
    - debt_percentage: % учеников с долгом
    """
    teachers = Teacher.objects.all()
    kpi_data = []

    for teacher in teachers:
        groups = teacher.groups.filter(is_active=True)
        total_groups = groups.count()

        # Все ученики учителя через enrollment
        enrollments = Enrollment.objects.filter(group__teacher=teacher)
        total_ever_enrolled = enrollments.values('student').distinct().count()
        active_enrollments = enrollments.filter(is_active=True)
        active_students_count = active_enrollments.values('student').distinct().count()

        # Посещаемость
        total_attendance = Attendance.objects.filter(group__teacher=teacher).count()
        present_count = Attendance.objects.filter(
            group__teacher=teacher,
            status='PRESENT'
        ).count()
        attendance_rate = (present_count / total_attendance * 100) if total_attendance > 0 else 0

        # Удержание
        retention_rate = (active_students_count / total_ever_enrolled * 100) if total_ever_enrolled > 0 else 0

        # % учеников с долгом
        students_with_debt = 0
        student_ids = active_enrollments.values_list('student', flat=True).distinct()
        for student_id in student_ids:
            student = Student.objects.get(id=student_id)
            if calculate_student_debt(student) > 0:
                students_with_debt += 1

        debt_percentage = (students_with_debt / active_students_count * 100) if active_students_count > 0 else 0

        kpi_data.append({
            'teacher': teacher,
            'total_groups': total_groups,
            'total_students': active_students_count,
            'attendance_rate': round(attendance_rate, 1),
            'retention_rate': round(retention_rate, 1),
            'debt_percentage': round(debt_percentage, 1),
        })

    return kpi_data
