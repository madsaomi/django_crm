from django.contrib import admin
from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'manager', 'is_active', 'created_at']
    list_filter = ['is_active', 'manager']
    search_fields = ['name', 'phone']
