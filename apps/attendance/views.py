from django.views import View
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from .models import Attendance, AttendanceStatus
from apps.groups.models import Group, Enrollment


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


class AttendanceHistoryView(LoginRequiredMixin, ListView):
    model = Attendance
    template_name = 'attendance/attendance_history.html'
    context_object_name = 'records'
    paginate_by = 30

    def get_queryset(self):
        qs = super().get_queryset().select_related('student', 'group')
        group_id = self.request.GET.get('group')
        if group_id:
            qs = qs.filter(group_id=group_id)
        date = self.request.GET.get('date')
        if date:
            qs = qs.filter(date=date)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['groups'] = Group.objects.filter(is_active=True)
        context['selected_group'] = self.request.GET.get('group', '')
        context['selected_date'] = self.request.GET.get('date', '')
        return context
