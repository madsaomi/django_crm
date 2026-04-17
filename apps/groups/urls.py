from django.urls import path
from . import views

app_name = 'groups'

urlpatterns = [
    path('', views.GroupListView.as_view(), name='list'),
    path('schedule/', views.ScheduleView.as_view(), name='schedule'),
    path('schedule/event/add/', views.SundayEventCreateView.as_view(), name='event_create'),
    path('schedule/event/<int:pk>/delete/', views.SundayEventDeleteView.as_view(), name='delete_event'),
    path('schedule/update/', views.UpdateGroupScheduleView.as_view(), name='update_schedule'),
    path('schedule/update-color/', views.UpdateGroupColorView.as_view(), name='update_color'),
    path('create/', views.GroupCreateView.as_view(), name='create'),
    path('<int:pk>/', views.GroupDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.GroupUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.GroupDeleteView.as_view(), name='delete'),
    path('<int:pk>/add-student/', views.AddStudentToGroupView.as_view(), name='add_student'),
    path('<int:pk>/remove-student/<int:enrollment_id>/', views.RemoveStudentFromGroupView.as_view(), name='remove_student'),
    path('rooms/', views.RoomOccupancyView.as_view(), name='room_occupancy'),
]
