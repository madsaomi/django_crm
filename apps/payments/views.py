from django.views.generic import ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import HttpResponse
import openpyxl
from .models import Payment
from .forms import PaymentForm
from .services import get_all_students_debts
from apps.managers.mixins import ManagerRequiredMixin


class PaymentListView(ManagerRequiredMixin, ListView):
    model = Payment
    template_name = 'payments/payment_list.html'
    context_object_name = 'payments'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset().select_related('student')
        search = self.request.GET.get('search', '')
        if search:
            qs = qs.filter(student__name__icontains=search)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        return context


class PaymentCreateView(ManagerRequiredMixin, CreateView):
    model = Payment
    form_class = PaymentForm
    template_name = 'payments/payment_form.html'
    success_url = reverse_lazy('payments:list')

    def render_to_response(self, context, **response_kwargs):
        if 'HX-Request' in self.request.headers:
            context['modal_title'] = 'Принять оплату'
            return super().render_to_response(context, **response_kwargs)
        return super().render_to_response(context, **response_kwargs)

    def get_template_names(self):
        if 'HX-Request' in self.request.headers:
            return ['components/modal_form.html']
        return [self.template_name]

    def form_valid(self, form):
        response = super().form_valid(form)
        if 'HX-Request' in self.request.headers:
            # Tell HTMX to refresh the current page to show the new payment
            res = HttpResponse()
            res['HX-Refresh'] = 'true'
            return res
        return response


class DebtListView(ManagerRequiredMixin, ListView):
    template_name = 'payments/debt_list.html'
    context_object_name = 'debts'

    def get_queryset(self):
        # Только те, у кого долг > 0
        return [d for d in get_all_students_debts() if d['debt'] > 0]


class FinanceDashboardView(ManagerRequiredMixin, ListView):
    """Общий финансовый реестр (вид Google Таблицы)"""
    template_name = 'payments/finance_dashboard.html'
    context_object_name = 'reports'

    def get_queryset(self):
        reports = get_all_students_debts()
        for r in reports:
            r['abs_debt'] = abs(r['debt'])
        return reports


class FinanceExportView(ManagerRequiredMixin, ListView):
    """Экспорт финансового дашборда в Excel"""
    def get(self, request, *args, **kwargs):
        reports = get_all_students_debts()
        
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Финансовый отчет"
        
        # Заголовки
        headers = ['Ученик', 'Менеджер', 'Ожидаемая оплата', 'Оплачено', 'Долг']
        ws.append(headers)
        
        # Данные
        for r in reports:
            manager_name = r['student'].manager.name if r['student'].manager else '—'
            ws.append([
                r['student'].name,
                manager_name,
                float(r['expected']),
                float(r['paid']),
                float(r['debt'])
            ])
            
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="finance_report.xlsx"'
        wb.save(response)
        return response
