from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .services import get_manager_kpi, get_teacher_kpi


class ManagerKPIView(LoginRequiredMixin, TemplateView):
    template_name = 'kpi/manager_kpi.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['kpi_data'] = get_manager_kpi()
        return context


class TeacherKPIView(LoginRequiredMixin, TemplateView):
    template_name = 'kpi/teacher_kpi.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['kpi_data'] = get_teacher_kpi()
        return context
