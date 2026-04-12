from django.views import View
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from .models import Attendance, AttendanceStatus
from apps.groups.models import Group, Enrollment
import calendar


class AttendanceMarkView(LoginRequiredMixin, View):
    """Отметка посещаемости для группы."""

    def get(self, request):
        groups = Group.objects.filter(is_active=True).select_related('teacher')
        group_id = request.GET.get('group')
        date = request.GET.get('date', timezone.now().date().isoformat())
        students = []
        selected_group = None
        existing_attendance = {}
        comments = {}
        is_valid_day = True

        if group_id:
            selected_group = get_object_or_404(Group, pk=group_id)
            enrollments = Enrollment.objects.filter(
                group=selected_group,
                is_active=True
            ).select_related('student')
            students = [e.student for e in enrollments]

            # Загружаем существующие записи посещаемости
            existing = Attendance.objects.filter(
                group=selected_group,
                date=date
            )
            existing_attendance = {a.student_id: a.status for a in existing}
            comments = {a.student_id: a.comment for a in existing}

            # Проверка дня недели
            from datetime import datetime
            dt = datetime.strptime(date, '%Y-%m-%d')
            weekday = dt.weekday() # 0 = Monday
            if selected_group.schedule_type == 'ODD' and weekday not in [0, 2, 4]:
                is_valid_day = False
            elif selected_group.schedule_type == 'EVEN' and weekday not in [1, 3, 5]:
                is_valid_day = False

        return render(request, 'attendance/attendance_mark.html', {
            'groups': groups,
            'selected_group': selected_group,
            'students': students,
            'date': date,
            'existing_attendance': existing_attendance,
            'comments': comments,
            'is_valid_day': is_valid_day,
        })

    def post(self, request):
        group_id = request.POST.get('group_id')
        date = request.POST.get('date')
        group = get_object_or_404(Group, pk=group_id)

        enrollments = Enrollment.objects.filter(
            group=group,
            is_active=True
        ).select_related('student')

        for enrollment in enrollments:
            status = request.POST.get(f'status_{enrollment.student.id}', 'ABSENT')
            comment = request.POST.get(f'comment_{enrollment.student.id}', '')
            Attendance.objects.update_or_create(
                student=enrollment.student,
                group=group,
                date=date,
                defaults={'status': status, 'comment': comment}
            )

        messages.success(request, f'Посещаемость для группы «{group.name}» за {date} сохранена!')
        return redirect(f'/attendance/?group={group_id}&date={date}')


class AttendanceHistoryView(LoginRequiredMixin, View):
    """Журнал посещаемости и успеваемости."""
    
    def get(self, request):
        groups = Group.objects.filter(is_active=True).select_related('teacher')
        group_id = request.GET.get('group')
        month_str = request.GET.get('month', timezone.now().strftime('%Y-%m'))
        
        try:
            year, month = map(int, month_str.split('-'))
        except ValueError:
            year, month = timezone.now().year, timezone.now().month

        selected_group = None
        matrix = []
        dates = []

        if group_id:
            selected_group = get_object_or_404(Group, pk=group_id)
            
            num_days = calendar.monthrange(year, month)[1]
            all_dates_in_month = [timezone.datetime(year, month, d).date() for d in range(1, num_days + 1)]
            
            attendances = Attendance.objects.filter(
                group=selected_group, 
                date__year=year, 
                date__month=month
            )
            
            records_by_student_date = {}
            active_dates_set = set()
            for a in attendances:
                records_by_student_date[(a.student_id, a.date)] = a
                active_dates_set.add(a.date)
                
            for d in all_dates_in_month:
                weekday = d.weekday()
                if selected_group.schedule_type == 'ODD' and weekday in [0, 2, 4]:
                    active_dates_set.add(d)
                elif selected_group.schedule_type == 'EVEN' and weekday in [1, 3, 5]:
                    active_dates_set.add(d)
                    
            dates = sorted(list(active_dates_set))
            
            enrollments = Enrollment.objects.filter(
                group=selected_group,
                is_active=True
            ).select_related('student')
            
            for enrollment in enrollments:
                student = enrollment.student
                student_data = {
                    'student': student,
                    'attendances': []
                }
                for d in dates:
                    student_data['attendances'].append({
                        'date': d,
                        'record': records_by_student_date.get((student.id, d))
                    })
                matrix.append(student_data)
                
        return render(request, 'attendance/attendance_history.html', {
            'groups': groups,
            'selected_group_id': int(group_id) if group_id else None,
            'selected_group': selected_group,
            'selected_month': month_str,
            'matrix': matrix,
            'dates': dates,
        })

import json
from django.http import JsonResponse

class AttendanceToggleAPIView(LoginRequiredMixin, View):
    """API для интерактивного переключения посещаемости (для AJAX из матрицы)."""
    def post(self, request):
        try:
            data = json.loads(request.body)
            student_id = data.get('student_id')
            group_id = data.get('group_id')
            date = data.get('date')
            status = data.get('status')
            comment = data.get('comment', '')
            
            student = get_object_or_404(Enrollment.objects.select_related('student'), student_id=student_id, group_id=group_id).student
            group = get_object_or_404(Group, pk=group_id)
            
            record, created = Attendance.objects.update_or_create(
                student=student,
                group=group,
                date=date,
                defaults={'status': status, 'comment': comment}
            )
            return JsonResponse({'status': 'success', 'attendance_status': record.status, 'comment': record.comment})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
