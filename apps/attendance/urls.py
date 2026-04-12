from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('', views.AttendanceMarkView.as_view(), name='mark'),
    path('history/', views.AttendanceHistoryView.as_view(), name='history'),
    path('api/toggle/', views.AttendanceToggleAPIView.as_view(), name='toggle_api'),
]
