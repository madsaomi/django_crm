from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('', views.PaymentListView.as_view(), name='list'),
    path('create/', views.PaymentCreateView.as_view(), name='create'),
    path('debts/', views.DebtListView.as_view(), name='debts'),
    path('finance/', views.FinanceDashboardView.as_view(), name='finance'),
    path('finance/export/', views.FinanceExportView.as_view(), name='finance_export'),
]
