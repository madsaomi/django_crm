from django.views.generic import ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Payment
from .forms import PaymentForm
from .services import get_all_students_debts


class PaymentListView(LoginRequiredMixin, ListView):
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


class PaymentCreateView(LoginRequiredMixin, CreateView):
    model = Payment
    form_class = PaymentForm
    template_name = 'payments/payment_form.html'
    success_url = reverse_lazy('payments:list')


class DebtListView(LoginRequiredMixin, ListView):
    template_name = 'payments/debt_list.html'
    context_object_name = 'debts'

    def get_queryset(self):
        # Только те, у кого долг > 0
        return [d for d in get_all_students_debts() if d['debt'] > 0]


class FinanceDashboardView(LoginRequiredMixin, ListView):
    """Общий финансовый реестр (вид Google Таблицы)"""
    template_name = 'payments/finance_dashboard.html'
    context_object_name = 'reports'

    def get_queryset(self):
        reports = get_all_students_debts()
        for r in reports:
            r['abs_debt'] = abs(r['debt'])
        return reports
