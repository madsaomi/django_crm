from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from apps.groups.models import Group
from apps.students.models import Student
from apps.payments.models import Payment
from .models import Manager
from .forms import ManagerForm
from apps.teachers.models import Teacher


class ManagerDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'managers/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        manager = getattr(self.request.user, 'manager', None)
        context['my_students'] = Student.objects.filter(manager=manager).count() if manager else 0
        context['recent_payments'] = Payment.objects.order_by('-date')[:5]
        return context


class ManagerRecruitView(LoginRequiredMixin, TemplateView):
    template_name = 'managers/recruit.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['groups'] = Group.objects.filter(is_active=True)
        return context


class ManagerListView(LoginRequiredMixin, ListView):
    model = Manager
    template_name = 'managers/manager_list.html'
    context_object_name = 'managers'
    paginate_by = 20

class ManagerDetailView(LoginRequiredMixin, DetailView):
    model = Manager
    template_name = 'managers/manager_detail.html'
    context_object_name = 'manager_obj'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        manager = self.get_object()
        # Retrieve students assigned to this manager
        context['students'] = Student.objects.filter(manager=manager)
        return context


class ManagerCreateView(LoginRequiredMixin, CreateView):
    model = Manager
    form_class = ManagerForm
    template_name = 'managers/manager_form.html'
    success_url = reverse_lazy('managers:list')


class ManagerUpdateView(LoginRequiredMixin, UpdateView):
    model = Manager
    form_class = ManagerForm
    template_name = 'managers/manager_form.html'
    success_url = reverse_lazy('managers:list')


class ManagerDeleteView(LoginRequiredMixin, DeleteView):
    model = Manager
    template_name = 'managers/manager_confirm_delete.html'
    success_url = reverse_lazy('managers:list')

class ArchiveDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'managers/archive.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['archived_students'] = Student.objects.filter(is_active=False)
        context['archived_teachers'] = Teacher.objects.filter(is_active=False)
        context['archived_managers'] = Manager.objects.filter(is_active=False)
        context['archived_groups'] = Group.objects.filter(is_active=False)
        return context

from django.shortcuts import get_object_or_404, redirect
from django.views import View

class ToggleActiveStatusView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        entity_type = request.POST.get('entity_type')
        entity_id = request.POST.get('entity_id')
        make_active = request.POST.get('make_active') == 'true'
        
        obj = None
        if entity_type == 'student':
            obj = get_object_or_404(Student, id=entity_id)
        elif entity_type == 'teacher':
            obj = get_object_or_404(Teacher, id=entity_id)
        elif entity_type == 'manager':
            obj = get_object_or_404(Manager, id=entity_id)
        elif entity_type == 'group':
            obj = get_object_or_404(Group, id=entity_id)
            
        if obj:
            obj.is_active = make_active
            obj.save()
            
        # redirect back to referrer
        return redirect(request.META.get('HTTP_REFERER', 'managers:archive'))
