from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.db import models
from apps.students.models import Student
from apps.groups.models import Group, Enrollment
from apps.payments.models import Payment
from apps.teachers.models import Teacher
from apps.managers.models import Manager
from .views import global_search, dashboard, custom_logout

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dashboard, name='dashboard'),
    path('search/', global_search, name='search'),
    path('students/', include('apps.students.urls')),
    path('groups/', include('apps.groups.urls')),
    path('teachers/', include('apps.teachers.urls')),
    path('managers/', include('apps.managers.urls')),
    path('payments/', include('apps.payments.urls')),
    path('attendance/', include('apps.attendance.urls')),
    path('kpi/', include('apps.kpi.urls')),
    path('academic/', include('apps.academic.urls')),
    # Auth
    path('login/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('logout/', custom_logout, name='logout'),
]
