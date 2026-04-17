from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView
from django.views import View
from django.http import JsonResponse
import json
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .models import Group, Enrollment, SundayEvent
from .forms import GroupForm, AddStudentToGroupForm, SundayEventForm





class GroupListView(LoginRequiredMixin, ListView):
    model = Group
    template_name = 'groups/group_list.html'
    context_object_name = 'groups'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset().select_related('teacher').filter(is_active=True)
        course_type = self.request.GET.get('course_type', '')
        if course_type:
            qs = qs.filter(course_type=course_type)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course_type'] = self.request.GET.get('course_type', '')
        context['status'] = self.request.GET.get('status', '')
        from .models import CourseType
        context['course_types'] = CourseType.choices
        return context


class GroupDetailView(LoginRequiredMixin, DetailView):
    model = Group
    template_name = 'groups/group_detail.html'
    context_object_name = 'group'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['enrollments'] = self.object.enrollments.filter(
            is_active=True
        ).select_related('student')
        context['add_student_form'] = AddStudentToGroupForm(group=self.object)
        
        from apps.attendance.models import Attendance
        dates_queryset = Attendance.objects.filter(group=self.object).values_list('date', flat=True).distinct().order_by('-date')[:5]
        
        # In SQLite, distinct() might not guarantee ordering correctly without a specific setup, 
        # but this simple values_list distinct usually works. If not, python side dedup is safe.
        dates = []
        for d in dates_queryset:
            if d not in dates:
                dates.append(d)
        
        atts_qs = Attendance.objects.filter(group=self.object, date__in=dates)
        atts_list = list(atts_qs)
        recent_log = []
        for d in dates:
            present = sum(1 for a in atts_list if a.date == d and a.status == 'PRESENT')
            absent = sum(1 for a in atts_list if a.date == d and a.status == 'ABSENT')
            recent_log.append({'date': d, 'present': present, 'absent': absent})
        context['recent_attendance'] = recent_log
        
        context['materials'] = self.object.materials.all()
        context['progress_tests'] = self.object.tests.all().prefetch_related('results__student')
        
        return context


class GroupCreateView(LoginRequiredMixin, CreateView):
    model = Group
    form_class = GroupForm
    template_name = 'groups/group_form.html'

    def get_success_url(self):
        return reverse('groups:detail', kwargs={'pk': self.object.pk})

    def render_to_response(self, context, **response_kwargs):
        if 'HX-Request' in self.request.headers:
            context['modal_title'] = 'Создать группу'
            return super().render_to_response(context, **response_kwargs)
        return super().render_to_response(context, **response_kwargs)

    def get_template_names(self):
        if 'HX-Request' in self.request.headers:
            return ['includes/modal_form.html']
        return [self.template_name]

    def form_valid(self, form):
        response = super().form_valid(form)
        if 'HX-Request' in self.request.headers:
            from django.http import HttpResponse
            res = HttpResponse()
            res['HX-Refresh'] = 'true'
            return res
        return response


class GroupUpdateView(LoginRequiredMixin, UpdateView):
    model = Group
    form_class = GroupForm
    template_name = 'groups/group_form.html'

    def get_success_url(self):
        return reverse('groups:detail', kwargs={'pk': self.object.pk})

    def render_to_response(self, context, **response_kwargs):
        if 'HX-Request' in self.request.headers:
            context['modal_title'] = 'Редактировать группу'
            return super().render_to_response(context, **response_kwargs)
        return super().render_to_response(context, **response_kwargs)

    def get_template_names(self):
        if 'HX-Request' in self.request.headers:
            return ['includes/modal_form.html']
        return [self.template_name]

    def form_valid(self, form):
        response = super().form_valid(form)
        if 'HX-Request' in self.request.headers:
            from django.http import HttpResponse
            res = HttpResponse()
            res['HX-Refresh'] = 'true'
            return res
        return response


class GroupDeleteView(LoginRequiredMixin, DeleteView):
    model = Group
    template_name = 'groups/group_confirm_delete.html'
    success_url = reverse_lazy('groups:list')


class AddStudentToGroupView(LoginRequiredMixin, View):
    def post(self, request, pk):
        group = get_object_or_404(Group, pk=pk)
        form = AddStudentToGroupForm(request.POST, group=group)
        if form.is_valid():
            student = form.cleaned_data['student']
            if group.is_full:
                messages.error(request, f'Группа заполнена! Макс. {group.max_students} учеников.')
            else:
                Enrollment.objects.get_or_create(student=student, group=group)
                messages.success(request, f'{student.name} добавлен в группу {group.name}')
        return redirect('groups:detail', pk=pk)


class RemoveStudentFromGroupView(LoginRequiredMixin, View):
    def post(self, request, pk, enrollment_id):
        enrollment = get_object_or_404(Enrollment, pk=enrollment_id, group_id=pk)
        student_name = enrollment.student.name
        group_name = enrollment.group.name
        enrollment.is_active = False
        enrollment.save()
        messages.success(request, f'{student_name} удалён из группы {group_name}')
        return redirect('groups:detail', pk=pk)

class UpdateGroupScheduleView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        if not (request.user.is_superuser or getattr(request.user, 'manager', None)):
            return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)
            
        try:
            data = json.loads(request.body)
            group_id = data.get('group_id')
            new_schedule_type = data.get('schedule_type')
            new_time_slot = data.get('time_slot')
            
            group = get_object_or_404(Group, pk=group_id)
            
            check_schedule_type = new_schedule_type or group.schedule_type
            check_time_slot = new_time_slot or group.time_slot
            
            if group.room:
                conflict = Group.objects.filter(
                    schedule_type=check_schedule_type,
                    time_slot=check_time_slot,
                    room=group.room,
                    is_active=True
                ).exclude(pk=group.pk).exists()
                
                if conflict:
                    return JsonResponse({
                        'status': 'error', 
                        'message': f'Кабинет {group.room} уже занят в это время!'
                    }, status=400)

            if new_schedule_type:
                group.schedule_type = new_schedule_type
            if new_time_slot:
                group.time_slot = new_time_slot
                
            group.save()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


class UpdateGroupColorView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        if not (request.user.is_superuser or getattr(request.user, 'manager', None)):
            return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)
            
        try:
            data = json.loads(request.body)
            group_id = data.get('group_id')
            new_color = data.get('color')
            
            group = get_object_or_404(Group, pk=group_id)
            if new_color:
                group.color = new_color
                group.save()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


class ScheduleView(LoginRequiredMixin, ListView):
    template_name = 'groups/schedule.html'
    context_object_name = 'even_groups'

    def get_queryset(self):
        # We'll fetch everything in get_context_data, returning even groups here just to satisfy ListView
        return Group.objects.filter(is_active=True, schedule_type='EVEN').select_related('teacher').order_by('time_slot')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add odd groups
        context['odd_groups'] = Group.objects.filter(is_active=True, schedule_type='ODD').select_related('teacher').order_by('time_slot')
        
        # Add upcoming sunday events (from today onwards)
        today = timezone.localdate()
        context['sunday_events'] = SundayEvent.objects.filter(date__gte=today).select_related('teacher').order_by('date', 'time_slot')
        
        # Add current time calculation for highlighting
        now = timezone.localtime()
        context['current_time'] = now.strftime('%H:%M')
        weekday = now.weekday()
        if weekday == 6:
            context['current_schedule_type'] = 'SUNDAY'
        elif weekday in [1, 3, 5]: # Tue, Thu, Sat
            context['current_schedule_type'] = 'EVEN'
        else: # Mon, Wed, Fri
            context['current_schedule_type'] = 'ODD'
            
        # Calculate dates for the current week
        monday = today - timedelta(days=weekday)
        context['week_dates'] = {
            'mon': monday,
            'tue': monday + timedelta(days=1),
            'wed': monday + timedelta(days=2),
            'thu': monday + timedelta(days=3),
            'fri': monday + timedelta(days=4),
            'sat': monday + timedelta(days=5),
            'sun': monday + timedelta(days=6),
        }
            
        return context

class RoomOccupancyView(LoginRequiredMixin, TemplateView):
    template_name = 'groups/room_occupancy.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        groups = Group.objects.filter(is_active=True)
        events = SundayEvent.objects.all()

        # Собираем все уникальные комнаты
        rooms = set()
        for g in groups:
            if g.room: rooms.add(g.room)
        for e in events:
            if e.room: rooms.add(e.room)
        
        # Собираем все уникальные тайм-слоты
        slots = set()
        for g in groups:
            if g.time_slot: slots.add(g.time_slot)
        for e in events:
            if e.time_slot: slots.add(e.time_slot)
        
        sorted_rooms = sorted(list(rooms))
        sorted_slots = sorted(list(slots))

        # Матрица занятости
        occupancy = {}
        for room in sorted_rooms:
            occupancy[room] = {}
            for slot in sorted_slots:
                # Ищем группы в этом кабинете в это время
                room_groups = [g for g in groups if g.room == room and g.time_slot == slot]
                room_events = [e for e in events if e.room == room and e.time_slot == slot]
                occupancy[room][slot] = {
                    'groups': room_groups,
                    'events': room_events,
                    'is_occupied': bool(room_groups or room_events)
                }

        context['rooms'] = sorted_rooms
        context['slots'] = sorted_slots
        context['occupancy'] = occupancy
        return context

class SundayEventCreateView(LoginRequiredMixin, CreateView):
    model = SundayEvent
    form_class = SundayEventForm
    template_name = 'groups/event_form.html'
    success_url = reverse_lazy('groups:schedule')

    def form_valid(self, form):
        # Optional: ensure it's a Sunday (weekday == 6 in Python where Monday=0)
        if form.instance.date.weekday() != 6:
            messages.warning(self.request, 'Внимание: выбранная дата не является воскресеньем. Ивент всё равно сохранен.')
        messages.success(self.request, 'Ивент успешно создан.')
        return super().form_valid(form)


class SundayEventDeleteView(LoginRequiredMixin, DeleteView):
    model = SundayEvent
    template_name = 'groups/event_confirm_delete.html'
    success_url = reverse_lazy('groups:schedule')
