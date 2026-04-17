"""
Сервисный слой для аналитики посещаемости.
Вынесено из views.py для чистой архитектуры.
"""
import calendar
from datetime import date, timedelta
from decimal import Decimal

from django.utils import timezone
from apps.attendance.models import Attendance
from apps.groups.models import Group, Enrollment
from apps.payments.services import get_bulk_student_debts


def get_subscription_info(enrollment):
    """
    Вычислить обратный отсчет подписки для enrollment.
    
    Returns: {
        'total_days': int,
        'elapsed_days': int,
        'remaining_days': int,
        'percent_used': float,
        'status': 'active' | 'warning' | 'expired'
    }
    """
    today = timezone.localdate()
    duration_months = enrollment.group.duration_months or 3
    
    # Вычисляем дату окончания: enrolled_date + duration_months месяцев
    start = enrollment.enrolled_date
    end_year = start.year + (start.month + duration_months - 1) // 12
    end_month = (start.month + duration_months - 1) % 12 + 1
    try:
        end_date = date(end_year, end_month, start.day)
    except ValueError:
        # Если день не существует в целевом месяце (напр. 31 февраля)
        last_day = calendar.monthrange(end_year, end_month)[1]
        end_date = date(end_year, end_month, last_day)
    
    total_days = (end_date - start).days
    elapsed_days = (today - start).days
    remaining_days = (end_date - today).days
    
    if total_days <= 0:
        total_days = 1
    
    percent_used = round(min(elapsed_days / total_days * 100, 100), 1)
    
    if remaining_days <= 0:
        status = 'expired'
    elif remaining_days <= 14:
        status = 'warning'
    else:
        status = 'active'
    
    return {
        'total_days': total_days,
        'elapsed_days': elapsed_days,
        'remaining_days': max(0, remaining_days),
        'percent_used': percent_used,
        'end_date': end_date,
        'status': status,
    }


def get_attendance_stats(student_id, group_id, dates, records_map):
    """
    Вычислить статистику посещаемости для ученика за период.
    
    Returns: {
        'total_lessons': int,
        'present': int,
        'absent': int,
        'unmarked': int,
        'rate': float (0-100),
        'absent_streak': int (последние пропуски подряд),
    }
    """
    present = 0
    absent = 0
    unmarked = 0
    
    for d in dates:
        record = records_map.get((student_id, d))
        if record:
            if record.status == 'PRESENT':
                present += 1
            else:
                absent += 1
        else:
            unmarked += 1
    
    total = present + absent
    rate = round((present / total) * 100, 1) if total > 0 else 0
    
    # Подсчёт пропусков подряд с конца
    absent_streak = 0
    for d in reversed(dates):
        record = records_map.get((student_id, d))
        if record and record.status == 'ABSENT':
            absent_streak += 1
        elif record and record.status == 'PRESENT':
            break
        # unmarked — не считаем streak
    
    return {
        'total_lessons': total,
        'present': present,
        'absent': absent,
        'unmarked': unmarked,
        'rate': rate,
        'absent_streak': absent_streak,
    }


def get_group_attendance_matrix(group, year, month):
    """
    Полная сборка матрицы посещаемости для группы.
    Оптимизировано: один запрос на enrollments, один на attendance, batch-долги.
    
    Returns: {
        'dates': list[date],
        'matrix': list[dict],  # каждый dict = {student, enrolled_date, debt, subscription, stats, attendances}
        'group_stats': dict,   # агрегированная статистика по группе
    }
    """
    num_days = calendar.monthrange(year, month)[1]
    all_dates = [date(year, month, d) for d in range(1, num_days + 1)]
    
    # Фильтруем по типу расписания
    active_dates_set = set()
    for d in all_dates:
        weekday = d.weekday()
        if group.schedule_type == 'ODD' and weekday in [0, 2, 4]:
            active_dates_set.add(d)
        elif group.schedule_type == 'EVEN' and weekday in [1, 3, 5]:
            active_dates_set.add(d)
    
    # Добавляем даты, на которые есть фактические записи посещаемости
    actual_dates = Attendance.objects.filter(
        group=group,
        date__year=year,
        date__month=month
    ).values_list('date', flat=True).distinct()
    active_dates_set.update(actual_dates)
    
    dates = sorted(list(active_dates_set))
    
    # Загрузка attendance за один запрос
    attendances = Attendance.objects.filter(
        group=group,
        date__year=year,
        date__month=month
    )
    records_map = {}
    for a in attendances:
        records_map[(a.student_id, a.date)] = a
    
    # Загрузка enrollments
    enrollments = list(
        Enrollment.objects.filter(
            group=group,
            is_active=True
        ).select_related('student')
    )
    
    if not enrollments:
        return {'dates': dates, 'matrix': [], 'group_stats': _empty_group_stats()}
    
    # Batch-долги
    student_ids = [e.student_id for e in enrollments]
    from apps.students.models import Student
    students_qs = Student.objects.filter(id__in=student_ids)
    bulk_debts = get_bulk_student_debts(students_qs)
    
    # Сборка матрицы
    matrix = []
    total_present = 0
    total_absent = 0
    
    for enrollment in enrollments:
        student = enrollment.student
        
        # Долг
        debt_info = bulk_debts.get(student.id, {})
        debt_value = float(debt_info.get('debt', 0))
        
        # Подписка
        subscription = get_subscription_info(enrollment)
        
        # Статистика посещаемости
        stats = get_attendance_stats(student.id, group.id, dates, records_map)
        total_present += stats['present']
        total_absent += stats['absent']
        
        # Ячейки посещаемости
        attendance_cells = []
        for d in dates:
            attendance_cells.append({
                'date': d,
                'record': records_map.get((student.id, d))
            })
        
        matrix.append({
            'student': student,
            'enrolled_date': enrollment.enrolled_date,
            'debt': debt_value,
            'subscription': subscription,
            'stats': stats,
            'attendances': attendance_cells,
        })
    
    # Агрегированная статистика по группе
    total_lessons_tracked = total_present + total_absent
    group_rate = round((total_present / total_lessons_tracked) * 100, 1) if total_lessons_tracked > 0 else 0
    
    group_stats = {
        'total_students': len(enrollments),
        'total_lessons': len(dates),
        'total_present': total_present,
        'total_absent': total_absent,
        'group_rate': group_rate,
        'debtors_count': sum(1 for row in matrix if row['debt'] > 0),
    }
    
    return {
        'dates': dates,
        'matrix': matrix,
        'group_stats': group_stats,
    }


def _empty_group_stats():
    return {
        'total_students': 0,
        'total_lessons': 0,
        'total_present': 0,
        'total_absent': 0,
        'group_rate': 0,
        'debtors_count': 0,
    }
