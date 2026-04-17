import re
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum, Count
from django.db.models.functions import TruncMonth
from django.db import models
import json
from datetime import datetime, timedelta
from django.utils import timezone

from apps.students.models import Student
from apps.groups.models import Group
from apps.teachers.models import Teacher
from apps.payments.models import Payment
from apps.managers.models import Manager
from apps.groups.models import CourseType

@login_required
def global_search(request):
    q = request.GET.get('q', '').strip()
    if not q:
        return render(request, 'components/search_results.html', {'results': []})
        
    def highlight(text, query):
        if not query: return text
        pattern = re.compile(re.escape(query), re.IGNORECASE)
        return pattern.sub(lambda m: f'<span class="text-primary">{m.group(0)}</span>', str(text))
        
    students = Student.objects.filter(Q(name__icontains=q) | Q(phone__icontains=q))[:5]
    groups = Group.objects.filter(Q(name__icontains=q) | Q(course_type__icontains=q))[:5]
    teachers = Teacher.objects.filter(Q(name__icontains=q) | Q(phone__icontains=q))[:5]
    
    results = []
    
    for s in students:
        results.append({
            'title': highlight(s.name, q),
            'subtitle': f'Ученик • {highlight(s.phone, q)}',
            'url': f'/students/{s.id}/',
            'icon': 'bi-person',
            'is_active': s.is_active
        })
        
    for g in groups:
        results.append({
            'title': highlight(g.name, q),
            'subtitle': f'Группа • {g.get_course_type_display()}',
            'url': f'/groups/{g.id}/',
            'icon': 'bi-collection',
            'is_active': g.is_active
        })
        
    for t in teachers:
        results.append({
            'title': highlight(t.name, q),
            'subtitle': f'Учитель • {highlight(t.phone, q)}',
            'url': f'/teachers/{t.id}/',
            'icon': 'bi-person-workspace',
            'is_active': t.is_active
        })
        
    return render(request, 'components/search_results.html', {'results': results, 'q': q})

@login_required
def dashboard(request):
    """Главная страница — дашборд с основной статистикой."""
    if hasattr(request.user, 'manager'):
        return redirect('managers:dashboard')
    if hasattr(request.user, 'teacher'):
        return redirect('teachers:dashboard')

    # Фильтр дат
    period = request.GET.get('period', '30') # 30, 180, 365
    try:
        days = int(period)
    except ValueError:
        days = 30
        
    start_date = timezone.now() - timedelta(days=days)

    total_students = Student.objects.filter(is_active=True).count()
    total_groups = Group.objects.filter(is_active=True).count()
    total_teachers = Teacher.objects.count()
    total_managers = Manager.objects.count()
    
    # Ожидаемый доход (MRR): Сумма(цена_группы * ученики)
    # Итерируемся по активным группам для точного подсчета (учитывая активные enrollments)
    expected_mrr = 0
    active_groups = Group.objects.filter(is_active=True).annotate(
        active_students=Count('enrollments', filter=Q(enrollments__is_active=True))
    )
    for g in active_groups:
        expected_mrr += g.active_students * g.monthly_fee
    
    # Фактический доход за период
    period_revenue = Payment.objects.filter(date__gte=start_date).aggregate(total=Sum('amount'))['total'] or 0
    # Исторический общий доход
    total_revenue = Payment.objects.aggregate(total=Sum('amount'))['total'] or 0

    # Последние платежи
    recent_payments = Payment.objects.select_related('student').order_by('-date')[:5]

    # Группы с местами
    groups_with_capacity = []
    for group in Group.objects.filter(is_active=True).select_related('teacher')[:7]:
        groups_with_capacity.append({
            'group': group,
            'students_count': group.students_count,
            'max_students': group.max_students,
        })

    # 1. Доходы по месяцам (за выбранный период 'days')
    # Для графика лучше всегда брать минимум 6 мес для красивой кривой, если период > 180.
    chart_start_date = timezone.now() - timedelta(days=max(days, 180))
    monthly_revenue = Payment.objects.filter(date__gte=chart_start_date).annotate(
        month=TruncMonth('date')
    ).values('month').annotate(
        total=Sum('amount')
    ).order_by('month')
    
    revenue_labels = [r['month'].strftime('%b %Y') for r in monthly_revenue]
    revenue_data = [float(r['total']) for r in monthly_revenue]

    # 2. Рост студентов по месяцам
    from apps.groups.models import Enrollment
    enrollments_data = Enrollment.objects.filter(enrolled_date__gte=chart_start_date).annotate(
        month=TruncMonth('enrolled_date')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')
    
    enrollment_labels = [r['month'].strftime('%b %Y') for r in enrollments_data]
    enrollment_data = [int(r['count']) for r in enrollments_data]

    # 3. Распределение по типам курсов
    course_data_qs = active_groups.values('course_type').annotate(
        count=Count('enrollments', filter=Q(enrollments__is_active=True))
    )
    course_labels = []
    course_counts = []
    for c in course_data_qs:
        label = dict(CourseType.choices).get(c['course_type'], c['course_type'])
        course_labels.append(label)
        course_counts.append(c['count'])
        
    # Топ учителей
    top_teachers = Teacher.objects.filter(is_active=True).annotate(
        total_students=Count('groups__enrollments', filter=Q(groups__enrollments__is_active=True, groups__is_active=True))
    ).order_by('-total_students')[:4]

    context = {
        'total_students': total_students,
        'total_groups': total_groups,
        'total_teachers': total_teachers,
        'total_managers': total_managers,
        'expected_mrr': expected_mrr,
        'total_revenue': total_revenue,
        'period_revenue': period_revenue,
        'period': period,
        'recent_payments': recent_payments,
        'groups_with_capacity': groups_with_capacity,
        'top_teachers': top_teachers,
        
        # Chart Data
        'revenue_labels': revenue_labels,
        'revenue_data': revenue_data,
        'course_labels': course_labels,
        'course_counts': course_counts,
        'enrollment_labels': enrollment_labels,
        'enrollment_data': enrollment_data,
    }
    
    if request.headers.get('HX-Request'):
        return render(request, 'includes/dashboard_charts.html', context)
        
    return render(request, 'dashboard.html', context)

def custom_logout(request):
    if request.method == 'POST':
        from django.contrib.auth import logout
        logout(request)
        return redirect('login')
    return render(request, 'auth/logout.html')
