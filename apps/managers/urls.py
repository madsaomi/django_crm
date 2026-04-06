from django.urls import path
from . import views

app_name = 'managers'

urlpatterns = [
    path('dashboard/', views.ManagerDashboardView.as_view(), name='dashboard'),
    path('recruit/', views.ManagerRecruitView.as_view(), name='recruit'),
    path('', views.ManagerListView.as_view(), name='list'),
    path('create/', views.ManagerCreateView.as_view(), name='create'),
    path('<int:pk>/edit/', views.ManagerUpdateView.as_view(), name='edit'),
    path('<int:pk>/profile/', views.ManagerDetailView.as_view(), name='detail'),
    path('<int:pk>/delete/', views.ManagerDeleteView.as_view(), name='delete'),
    path('archive/', views.ArchiveDashboardView.as_view(), name='archive'),
    path('toggle_status/', views.ToggleActiveStatusView.as_view(), name='toggle_status'),
]
