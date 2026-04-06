from django.urls import path
from . import views

app_name = 'kpi'

urlpatterns = [
    path('managers/', views.ManagerKPIView.as_view(), name='manager_kpi'),
    path('teachers/', views.TeacherKPIView.as_view(), name='teacher_kpi'),
]
