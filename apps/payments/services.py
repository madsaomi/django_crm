from decimal import Decimal
from django.db.models import Sum, Q, F, Value, DecimalField
from django.db.models.functions import Coalesce
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


# ============================================================
# BATCH / OPTIMIZED METHODS (eliminate N+1 queries)
# ============================================================

def get_bulk_student_debts(students_qs=None):
    """
    Батчевый расчёт долгов для всех (или переданных) активных учеников.
    Заменяет Python-цикл на 2 оптимизированных запроса.
    
    Возвращает dict: {student_id: {'student', 'expected', 'paid', 'debt', 'groups_info'}}
    """
    if students_qs is None:
        students_qs = Student.objects.filter(is_active=True)
    
    students = list(students_qs.select_related('manager'))
    student_ids = [s.id for s in students]
    today = timezone.localdate()
    
    # 1) Все активные enrollments за один запрос
    enrollments = list(
        Enrollment.objects.filter(
            student_id__in=student_ids,
            is_active=True
        ).select_related('group')
    )
    
    # 2) Все оплаты за один запрос
    payments_agg = dict(
        Payment.objects.filter(
            student_id__in=student_ids
        ).values('student_id').annotate(
            total=Coalesce(Sum('amount'), Value(0), output_field=DecimalField())
        ).values_list('student_id', 'total')
    )
    
    # 3) Сборка результата в Python
    enrollment_map = {}
    for e in enrollments:
        enrollment_map.setdefault(e.student_id, []).append(e)
    
    results = {}
    for student in students:
        student_enrollments = enrollment_map.get(student.id, [])
        total_expected = Decimal('0')
        group_details = []
        
        for e in student_enrollments:
            months = get_months_between(e.enrolled_date, today)
            expected_for_group = e.group.monthly_fee * months
            total_expected += expected_for_group
            group_details.append({
                'group': e.group,
                'enrollment': e,
                'months': months,
                'expected': expected_for_group,
            })
        
        paid = payments_agg.get(student.id, Decimal('0'))
        debt = total_expected - paid
        
        results[student.id] = {
            'student': student,
            'expected': total_expected,
            'paid': paid,
            'debt': debt,
            'groups_info': group_details,
        }
    
    return results


def get_all_students_debts():
    """Долги всех активных учеников (оптимизированная версия)."""
    bulk = get_bulk_student_debts()
    results = list(bulk.values())
    # Сортируем: сначала самые большие долги
    return sorted(results, key=lambda x: x['debt'], reverse=True)


def get_financial_summary():
    """
    Финансовая сводка по всем активным ученикам.
    Возвращает: total_expected, total_paid, total_debt, debtors_count,
                overpaid_count, avg_debt, collection_rate
    """
    debts = get_all_students_debts()
    
    total_expected = sum(d['expected'] for d in debts)
    total_paid = sum(d['paid'] for d in debts)
    total_debt = sum(d['debt'] for d in debts if d['debt'] > 0)
    debtors_count = sum(1 for d in debts if d['debt'] > 0)
    overpaid_count = sum(1 for d in debts if d['debt'] < 0)
    paid_count = sum(1 for d in debts if d['debt'] == 0)
    
    avg_debt = (total_debt / debtors_count) if debtors_count > 0 else Decimal('0')
    collection_rate = (float(total_paid) / float(total_expected) * 100) if total_expected > 0 else 0
    
    return {
        'total_expected': total_expected,
        'total_paid': total_paid,
        'total_debt': total_debt,
        'debtors_count': debtors_count,
        'overpaid_count': overpaid_count,
        'paid_count': paid_count,
        'avg_debt': avg_debt,
        'collection_rate': round(collection_rate, 1),
        'total_students': len(debts),
    }


def get_overdue_students(days_threshold=30):
    """
    Ученики, у которых последняя оплата была более `days_threshold` дней назад
    И при этом есть долг > 0.
    """
    cutoff_date = timezone.now() - timezone.timedelta(days=days_threshold)
    bulk = get_bulk_student_debts()
    
    # Последний платёж каждого ученика
    student_ids = list(bulk.keys())
    from django.db.models import Max
    last_payments = dict(
        Payment.objects.filter(
            student_id__in=student_ids
        ).values('student_id').annotate(
            last_date=Max('date')
        ).values_list('student_id', 'last_date')
    )
    
    overdue = []
    for sid, info in bulk.items():
        if info['debt'] > 0:
            last_pay = last_payments.get(sid)
            days_since = None
            if last_pay:
                days_since = (timezone.now() - last_pay).days
                if days_since >= days_threshold:
                    info['days_since_payment'] = days_since
                    info['last_payment_date'] = last_pay
                    overdue.append(info)
            else:
                # Никогда не платил
                info['days_since_payment'] = None
                info['last_payment_date'] = None
                overdue.append(info)
    
    return sorted(overdue, key=lambda x: x['debt'], reverse=True)
