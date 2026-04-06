from decimal import Decimal
from django.db.models import Sum
from django.utils import timezone
from apps.students.models import Student
from apps.groups.models import Enrollment
from apps.payments.models import Payment


def get_months_between(start_date, end_date):
    """Рассчитать количество месяцев обучения (минимум 1)."""
    months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
    return max(1, months + 1)


def get_student_debt_info(student):
    """Полная информация о долге ученика с учетом длительности обучения."""
    enrollments = Enrollment.objects.filter(
        student=student,
        is_active=True
    ).select_related('group')

    today = timezone.localdate()
    total_expected = Decimal('0')
    
    # Расчет по каждой группе отдельно (потому что даты зачисления могут быть разные)
    group_details = []
    for e in enrollments:
        months = get_months_between(e.enrolled_date, today)
        expected_for_group = e.group.monthly_fee * months
        total_expected += expected_for_group
        group_details.append({
            'group': e.group,
            'months': months,
            'expected': expected_for_group
        })

    paid = Payment.objects.filter(
        student=student
    ).aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0')

    return {
        'student': student,
        'expected': total_expected,
        'paid': paid,
        'debt': total_expected - paid,
        'groups_info': group_details,
    }


def calculate_student_debt(student):
    """Рассчитать только итоговую цифру долга."""
    info = get_student_debt_info(student)
    return info['debt']


def get_all_students_debts():
    """Долги всех активных учеников."""
    students = Student.objects.filter(is_active=True)
    results = []
    for student in students:
        info = get_student_debt_info(student)
        # Добавляем всех, но помечаем должников
        results.append(info)
    # Сортируем: сначала самые большие долги
    return sorted(results, key=lambda x: x['debt'], reverse=True)
