from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.db import models
from apps.students.models import Student
from apps.groups.models import Group, Enrollment
from apps.payments.models import Payment
from apps.teachers.models import Teacher
from apps.managers.models import Manager
from .views import global_search

@login_required
def dashboard(request):
    """Главная страница — дашборд с основной статистикой."""
    if hasattr(request.user, 'manager'):
        return redirect('managers:dashboard')
    if hasattr(request.user, 'teacher'):
        return redirect('teachers:dashboard')

    total_students = Student.objects.filter(is_active=True).count()
    total_groups = Group.objects.filter(is_active=True).count()
    total_teachers = Teacher.objects.count()
    total_managers = Manager.objects.count()
    total_revenue = Payment.objects.aggregate(total=Sum('amount'))['total'] or 0

    # Последние платежи
    recent_payments = Payment.objects.select_related('student').order_by('-date')[:5]

    # Группы с местами
    groups_with_capacity = []
    for group in Group.objects.filter(is_active=True).select_related('teacher')[:10]:
        groups_with_capacity.append({
            'group': group,
            'students_count': group.students_count,
            'available': group.available_spots,
        })

    # Данные для графиков
    from django.db.models.functions import TruncMonth
    import json

    # 1. Доходы по месяцам (последние 6 месяцев)
    monthly_revenue = Payment.objects.annotate(
        month=TruncMonth('date')
    ).values('month').annotate(
        total=Sum('amount')
    ).order_by('month')[:6]
    
    revenue_labels = [r['month'].strftime('%b %Y') for r in monthly_revenue]
    revenue_data = [float(r['total']) for r in monthly_revenue]

    # 2. Распределение по типам курсов
    course_data_qs = Group.objects.filter(is_active=True).values('course_type').annotate(
        count=Count('enrollments', filter=models.Q(enrollments__is_active=True))
    )
    from apps.groups.models import CourseType
    course_labels = []
    course_counts = []
    for c in course_data_qs:
        label = dict(CourseType.choices).get(c['course_type'], c['course_type'])
        course_labels.append(label)
        course_counts.append(c['count'])

    context = {
        'total_students': total_students,
        'total_groups': total_groups,
        'total_teachers': total_teachers,
        'total_managers': total_managers,
        'total_revenue': total_revenue,
        'recent_payments': recent_payments,
        'groups_with_capacity': groups_with_capacity,
        # Chart Data
        'revenue_labels': revenue_labels,
        'revenue_data': revenue_data,
        'course_labels': course_labels,
        'course_counts': course_counts,
    }
    return render(request, 'dashboard.html', context)


def custom_logout(request):
    if request.method == 'POST':
        from django.contrib.auth import logout
        logout(request)
        return redirect('login')
    return render(request, 'auth/logout.html')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dashboard, name='dashboard'),
    path('search/', global_search, name='search'),
    path('students/', include('apps.students.urls')),
    path('groups/', include('apps.groups.urls')),
    path('teachers/', include('apps.teachers.urls')),
    path('managers/', include('apps.managers.urls')),
    path('payments/', include('apps.payments.urls')),
    path('attendance/', include('apps.attendance.urls')),
    path('kpi/', include('apps.kpi.urls')),
    # Auth
    path('login/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('logout/', custom_logout, name='logout'),
]
