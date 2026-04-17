from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Student
from .forms import StudentForm
from apps.payments.services import calculate_student_debt, get_student_debt_info


class StudentListView(LoginRequiredMixin, ListView):
    model = Student
    template_name = 'students/student_list.html'
    context_object_name = 'students'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset().select_related('manager').filter(is_active=True)
        search = self.request.GET.get('search', '')
        if search:
            qs = qs.filter(name__icontains=search)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['status'] = self.request.GET.get('status', '')
        return context


class StudentDetailView(LoginRequiredMixin, DetailView):
    model = Student
    template_name = 'students/student_detail.html'
    context_object_name = 'student'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['debt_info'] = get_student_debt_info(self.object)
        
        payments = list(self.object.payments.all().order_by('-date')[:15])
        attendances = list(self.object.attendances.all().select_related('group').order_by('-date')[:15])
        enrollments = list(self.object.enrollments.all().select_related('group'))
        
        activities = []
        for p in payments:
            activities.append({'type': 'payment', 'date': p.date, 'obj': p})
        for a in attendances:
            activities.append({'type': 'attendance', 'date': a.date, 'obj': a})
        for e in enrollments:
            activities.append({'type': 'enrollment', 'date': e.enrolled_date, 'obj': e})
            
        activities.sort(key=lambda x: x['date'].date() if hasattr(x['date'], 'date') else x['date'], reverse=True)
        context['activities'] = activities[:30]
        
        context['active_enrollments'] = [e for e in enrollments if e.is_active]
        return context


class StudentCreateView(LoginRequiredMixin, CreateView):
    model = Student
    form_class = StudentForm
    template_name = 'students/student_form.html'
    success_url = reverse_lazy('students:list')

    def render_to_response(self, context, **response_kwargs):
        if 'HX-Request' in self.request.headers:
            context['modal_title'] = 'Добавить ученика'
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


class StudentUpdateView(LoginRequiredMixin, UpdateView):
    model = Student
    form_class = StudentForm
    template_name = 'students/student_form.html'
    success_url = reverse_lazy('students:list')

    def render_to_response(self, context, **response_kwargs):
        if 'HX-Request' in self.request.headers:
            context['modal_title'] = 'Редактировать ученика'
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


class StudentDeleteView(LoginRequiredMixin, DeleteView):
    model = Student
    template_name = 'students/student_confirm_delete.html'
    success_url = reverse_lazy('students:list')
