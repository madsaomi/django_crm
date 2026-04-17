from django.urls import path
from . import views

app_name = 'academic'

urlpatterns = [
    path('group/<int:group_id>/add-material/', views.add_material, name='add_material'),
    path('group/<int:group_id>/conduct-test/', views.conduct_test, name='conduct_test'),
]
