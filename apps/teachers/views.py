from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from apps.groups.models import Group
from apps.attendance.models import Attendance
from .models import Teacher
from .forms import TeacherForm


class TeacherDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'teachers/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teacher = getattr(self.request.user, 'teacher', None)
        if teacher:
            context['my_groups'] = Group.objects.filter(teacher=teacher, is_active=True)
            context['recent_attendance'] = Attendance.objects.filter(group__teacher=teacher).order_by('-date')[:5]
        return context


class TeacherListView(LoginRequiredMixin, ListView):
    model = Teacher
    template_name = 'teachers/teacher_list.html'
    context_object_name = 'teachers'
    paginate_by = 20

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)

class TeacherDetailView(LoginRequiredMixin, DetailView):
    model = Teacher
    template_name = 'teachers/teacher_detail.html'
    context_object_name = 'teacher'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teacher = self.get_object()
        context['groups'] = Group.objects.filter(teacher=teacher)
        context['recent_attendance'] = Attendance.objects.filter(group__teacher=teacher).order_by('-date')[:10]
        return context


class TeacherCreateView(LoginRequiredMixin, CreateView):
    model = Teacher
    form_class = TeacherForm
    template_name = 'teachers/teacher_form.html'
    success_url = reverse_lazy('teachers:list')

    def render_to_response(self, context, **response_kwargs):
        if 'HX-Request' in self.request.headers:
            context['modal_title'] = 'Добавить учителя'
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


class TeacherUpdateView(LoginRequiredMixin, UpdateView):
    model = Teacher
    form_class = TeacherForm
    template_name = 'teachers/teacher_form.html'
    success_url = reverse_lazy('teachers:list')

    def render_to_response(self, context, **response_kwargs):
        if 'HX-Request' in self.request.headers:
            context['modal_title'] = 'Редактировать учителя'
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


class TeacherDeleteView(LoginRequiredMixin, DeleteView):
    model = Teacher
    template_name = 'teachers/teacher_confirm_delete.html'
    success_url = reverse_lazy('teachers:list')
