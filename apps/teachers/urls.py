from django.urls import path
from . import views

app_name = 'teachers'

urlpatterns = [
    path('dashboard/', views.TeacherDashboardView.as_view(), name='dashboard'),
    path('', views.TeacherListView.as_view(), name='list'),
    path('create/', views.TeacherCreateView.as_view(), name='create'),
    path('<int:pk>/edit/', views.TeacherUpdateView.as_view(), name='edit'),
    path('<int:pk>/profile/', views.TeacherDetailView.as_view(), name='detail'),
    path('<int:pk>/delete/', views.TeacherDeleteView.as_view(), name='delete'),
]
